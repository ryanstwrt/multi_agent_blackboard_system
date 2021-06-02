import src.bb.blackboard as blackboard
import src.utils.utilities as utils
import src.utils.benchmark_utils as bu

import src.utils.performance_measure as pm
import matplotlib.pyplot as plt
import osbrain
from osbrain import proxy
from osbrain import run_agent
import time
import os
import numpy as np
import scipy.interpolate
import plotly.express as px
from numpy import random
import copy

cur_dir = os.path.dirname(__file__)
test_path = os.path.join(cur_dir, '../test/')

class BbOpt(blackboard.Blackboard):

    def on_init(self):
        super().on_init()
        self._complete = False
        self.problem = 'basic'
        self.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
        self.add_abstract_lvl(2, {'valid': bool})
        self.add_panel(2, ['new', 'old'])
        self.objectives = {}
        self.design_variables = {}
        self.constraints = {}
        self.objectives_ll = []
        self.objectives_ul = []
        self.total_tvs = 1E6
        self.function_evals = 1E6

        self.hv_list = [0.0]
        self._nadir_point = {}
        self._ideal_point = {}
        self._pareto_level = ['level 1']
        self.previous_pf = {}
        self.dci_convergence_list = [0.0]
        self.random_seed = None
        self.plot = False

        self.skipped_tvs = 200
        self.convergence_type = 'hvi'
        self.convergence_rate = 1E-6
        self.convergence_interval = 25
        self.pf_size = 200
        self.dci_div = {}
        self.final_trigger = 3
        self.problem = None
        self.meta_data_to_log = ['hvi']
        self.meta_data = {}

    def controller(self):
        """Determines which KA to select after a trigger event."""
        self.log_debug('Determining which KA to execute')
        self._ka_to_execute = (None, 0)
        cur_tv = self._kaar[self._trigger_event]
        if cur_tv:
            # We sort the current trigger values into alphabetical order and recreate the dictionary
            # This is done to allow for reproducability, due to the fact that the KAs respond at different times which can change the order of the current trigger values
            cur_tv = {k: cur_tv[k] for k in sorted(cur_tv)}
            max_ka = max(cur_tv, key=cur_tv.get)
            if cur_tv[max_ka] > 0:
                equal_vals = [k for k,v in cur_tv.items() if v == cur_tv[max_ka]]
                ka_ = str(random.choice(equal_vals))
                self._ka_to_execute = (ka_, cur_tv[ka_])

    def create_level_format(self, level_entry):
        level_format = {}
        for dv, dv_dict in level_entry.items():
            if dv_dict['variable type'] == dict:
                level_format[dv] = self.create_level_format(dv_dict['dict'])
            else:
                level_format[dv] = dv_dict['variable type']
        return level_format

    def connect_ka_specific(self, agent, attr={}):
        """
        Assigns specific variables for each KA type in the SFR optimization problem.

        Parameters
        ----------
        agent : str
            alias of the KA to be updated
        """
        ns = proxy.NSProxy()
        ka = ns.proxy(agent)
        agent_class = ka.get_attr('_class')

        ka.set_attr(_objectives=self.objectives)
        ka.set_attr(_constraints=self.constraints)
        ka.set_attr(problem=self.problem)
        for k,v in attr.items():
            ka.set_attr(**{k:v})

        if 'search' in agent_class:
            ka.set_random_seed(seed=self.random_seed)
            ka.set_attr(_design_variables=self.design_variables)
            if 'lhc' in agent_class:
                ka.generate_lhc()
        elif 'reader' in agent_class:
            if 'level 1' in agent_class:
                nadir_point = {}
                ideal_point = {}
                ka.set_attr(_lower_objective_reference_point=[0 for x in self.objectives.keys()])
                ka.set_attr(_upper_objective_reference_point=[1 for x in self.objectives.keys()])
                ka.set_attr(_nadir_point=self._nadir_point)
                ka.set_attr(_ideal_point=self._ideal_point)
            elif 'inter' in agent_class:
                ka.set_attr(_design_variables=self.design_variables)
                ka.connect_bb_to_write(attr['bb'])

        else:
            self.log_info('Agent type ({}) does not match a known agent type of BbOpt, no specific KA attributes'.format(agent))
            return

    def convergence_indicator(self):
        """
        Determine what to do after a trigger event has been processed
        """
        if self.convergence_type == 'dci hvi':
            self.dc_indicator()
        elif self.convergence_type == 'hvi':
            self.hv_list.append(self.hv_indicator())
        else:
            self.log_debug('convergence type ({}) not recognized, reverting to total TVs'.format(self.convergence_type))
            self.hv_list.append(0.0)

    def convergence_update(self):
        """
        Determine if any values need to be udpated after a trigger event
        """
        for md, array in self.meta_data.items():
            array.append(array[-1])
        self.hv_list.append(self.hv_list[-1])

    def dc_indicator(self):
        """
        Calculate the DCI
        """
        current_pf = {name: {obj: self.get_objective_value(name, obj) for obj in self.objectives.keys()} for name in self.abstract_lvls['level 1'].keys()}
        if self.previous_pf == {}:
            self.previous_pf = current_pf
            self.convergence_update()
            return

        total_pf = [current_pf, self.previous_pf]
        goal = {}
        for obj_name, obj in self.objectives.items():
            if obj['goal'] == 'et':
                goal.update({obj_name: (obj['goal'], obj['target'])})
            else:
                goal.update({obj_name: obj['goal']})

        dci = pm.diversity_comparison_indicator(self._nadir_point, self._ideal_point, total_pf, goal=goal, div=self.dci_div)
        dci._grid_generator()
        dci.compute_dci(current_pf)
        current_dci = dci.dci
        dci.compute_dci(self.previous_pf)
        previous_dci = dci.dci
        self.dci_convergence_list.append(current_dci - previous_dci)
        self.previous_pf = current_pf
        self.convergence_update()

    def determine_complete(self):
        """
        Determine if the problem has converged
        """
        if len(self.hv_list) < 2 * self.convergence_interval:
            return

        if self.convergence_type == 'dci hvi':
            self.determine_complete_dci_hvi()
        elif self.convergence_type == 'hvi':
            self.determine_complete_hv()
        else:
            self.log_warning('Convergence type ({}) not recognized, reverting to total TVs'.format(self.convergence_type))
            self.determine_complete_trigger_evals()

        self.determine_complete_function_evals()
        self.determine_complete_trigger_evals()


    def determine_complete_dci_hvi(self):
        """
        Determine if the problem is complete using the convergence of dci and the hvi
        """
        if self.dci_convergence_list[-1] < self.convergence_rate:
            self.hv_list[self._trigger_event] = self.hv_indicator()
            self.determine_complete_hv()
        else:
            self.convergence_update()

    def determine_complete_function_evals(self):
        self.log_info('Problem is at {} of {} total allowable trigger values'.format(len(self._kaar), self.total_tvs))
        lvl3 = {**self.abstract_lvls['level 3']['new'], **self.abstract_lvls['level 3']['old']}
        self.log_info('Problem is at {} of {} total allowable function evals'.format(len(lvl3), self.function_evals))
        if len(lvl3) > self.function_evals:
            self.log_info('Problem is over total allowable function evals, shutting agents down')
            self._complete = True

    def determine_complete_hv(self):
        """
        Determine if the problem is complete using the convergence of the hypervolume
        """
        num = self.convergence_interval
        recent_hv = self.hv_list[-num:]
        prev_hv = self.hv_list[-2*num:-num]
        hv_average = abs(sum(recent_hv) / num - sum(prev_hv) / num)
        hv_indicator = hv_average

        # Should we add the following to ensure there is something on the BB?
        if len(self._kaar.keys()) < self.skipped_tvs:
            self.log_info('Below minimum skipped trigger values, skipping convergence check')
            return
        if len(self.abstract_lvls['level 1']) < self.pf_size:
            self.log_info('Number of solutions on Pareto Front ({}) less than desired Pareto Front ({})'.format(len(self.abstract_lvls['level 1']), self.pf_size))
            return
        # Wait for a number of cycles before we check for convergence
        self.log_info('Convergence Rate: {} '.format(hv_indicator))

        if hv_indicator < self.convergence_rate:
            self.log_info('Problem complete via HV convergence, shutting agents down')
            self._complete = True

    def determine_complete_trigger_evals(self):
        # Determine if the problem is over our trigger value limit
        if len(self._kaar) >= self.total_tvs:
            self.log_info('Problem is over total allowable TVs, shutting agents down')
            self._complete = True

    def get_objective_value(self, core, obj):
        objective_value = self.abstract_lvls['level 3']['old'][core]['objective functions'][obj]
        goal = self.objectives[obj]['goal type'] if 'goal type' in self.objectives[obj] else None
        return utils.get_objective_value(objective_value, goal)

    def get_hv_list(self):
        return self.hv_list

    def get_complete_status(self):
        return self._complete

    def get_pf(self, scaled=True):
        cores = list(self.abstract_lvls['level 1'].keys())
        lvl_3 = {**self.abstract_lvls['level 3']['old'], **self.abstract_lvls['level 3']['new']}
        if scaled:
            return utils.scale_pareto_front(cores, self.objectives, lvl_3)
        else:
            return utils.convert_pf_to_list(cores, self.objectives, lvl_3)

    def handler_agent_complete(self, message):
        """
        Handler for KAs complete response, i.e. when a KA has finished their action

        Parameters
        ----------
        agent_name : str
            Alias for the KA
        """
        self._new_entry = True
        self.log_debug('Logging agent {} complete.'.format(message[0]))
        self.agent_addrs[message[0]].update({'performing action':False})
        self.meta_data_entry(message[0], message[1], message[2])

    def hv_indicator(self):
        """
        Calculate the Hypervolume for the current pareto front
        """
        pf = self.get_pf()
        return pm.hypervolume_indicator(pf, self.objectives_ul)

    def initialize_abstract_level_3(self, objectives=None, design_variables=None, constraints=None):
        """
        Initialze BB abstract level three with problem specific objectives and design variables
        """
        if objectives:
            self.objectives = objectives
        if design_variables:
            self.design_variables = design_variables
        if constraints:
            self.constraints = constraints

        # TODO: Do we need to do something for equal to goal?
        for obj, obj_dict in self.objectives.items():
            if obj_dict['goal'] == 'lt':
                self._nadir_point.update({obj: obj_dict['ll']})
                self._ideal_point.update({obj: obj_dict['ul']})
            else:
                self._nadir_point.update({obj: -obj_dict['ul']})
                self._ideal_point.update({obj: -obj_dict['ll']})

        self.objectives_ll = [0.0 for x in self.objectives.keys()]
        self.objectives_ul = [1.0 for x in self.objectives.keys()]

        dv  = self.create_level_format(self.design_variables)
        obj = self.create_level_format(self.objectives)
        cnst  = self.create_level_format(self.constraints)
        self.add_abstract_lvl(3, {'design variables': dv, 'objective functions': obj, 'constraints' : cnst})
        self.add_panel(3, ['new','old'])

    def initialize_metadata_level(self):
        """
        Create the abstract level for the meta data
        """
        md_entry = {md_type: float for md_type in self.meta_data_to_log}
        self.meta_data = {md_type: [0.0,] for md_type in self.meta_data_to_log}
        md_entry.update({'agent': str, 'time': float})
        self.add_abstract_lvl(100, md_entry)

    def log_metadata(self):
        """
        Log the any metadata values that the user wants in the metadata abstract level.
        """
        for md, array in self.meta_data.items():
            if md == 'hvi':
                array.append(float(self.hv_indicator()))
            elif md == 'dci-hvi':
                if self.dci_convergence_list[-1] < self.convergence_rate:
                    array[self._trigger_event] = self.hv_indicator()
                else:
                    self.convergence_update()
            elif md == 'gd':
                array.append(bu.get_indicator('gd', self.problem.benchmark_name, self.get_pf(scaled=False)))
            elif md == 'igd':
                array.append(bu.get_indicator('igd', self.problem.benchmark_name, self.get_pf(scaled=False)))
            elif md == 'function evals':
                function_evals = float(len({**self.abstract_lvls['level 3']['old'], **self.abstract_lvls['level 3']['new']}))
                array.append(function_evals)
            elif md == 'PF size':
                array.append(float(len(list(self.abstract_lvls['level 1'].keys()))))
            elif md == 'total time':
                array.append(float(len(list(self.abstract_lvls['level 1'].keys()))))



    def meta_data_entry(self, name, time, trigger_event):
        """
        Add an entry to abstract level 100 for meta-data

        Trigger events start at 1, not 0, so we offset by 1 when looking at the vals
        """
        entry = {md: array[trigger_event-1] for md, array in self.meta_data.items()}
        entry.update({'agent': name, 'time': float(time)})
        self.update_abstract_lvl(100, str(trigger_event), entry)

    def plot_progress(self):
        """
        Generate a plot of the hypervolume and Pareto front during the problem.
        """
        if self.plot == False:
            return

        lvl_1 = self.abstract_lvls['level 1']
        if lvl_1 == {}:
            return

        lvl_3 = {**self.abstract_lvls['level 3']['new'], **self.abstract_lvls['level 3']['old']}

        fitness = []

        obj_dict = {}
        ind_dict = {}
        for core, values in lvl_1.items():
            fitness.append(values['fitness function'])
            core_params = lvl_3[core]['objective functions']
            core_designs = lvl_3[core]['design variables']

            for obj in self.objectives.keys():
                if obj in obj_dict.keys():
                    obj_dict[obj].append(core_params[obj])
                else:
                    obj_dict[obj] = [core_params[obj]]
            for dv in self.design_variables.keys():
                if dv in ind_dict.keys():
                    ind_dict[dv].append(core_designs[dv])
                else:
                    ind_dict[dv] = [core_designs[dv]]
        objs = [x for x in self.objectives.keys()]
        dvs = [x for x in self.design_variables.keys()]

        if len(obj_dict.keys()) == 2:
            fig1 = px.scatter(x=obj_dict[objs[0]], y=obj_dict[objs[1]], labels={'x':objs[0], 'y': objs[1]})
        elif len(obj_dict.keys()) == 3:
            fig1 = px.scatter_3d(x=obj_dict[objs[0]], y=obj_dict[objs[1]], z=obj_dict[objs[2]], color=fitness, labels={'x':objs[0], 'y': objs[1], 'z': objs[2], 'color': 'fitness'})
        elif len(obj_dict.keys()) > 3:
            fig1 = px.scatter_3d(x=obj_dict[objs[0]], y=obj_dict[objs[1]], z=obj_dict[objs[2]], color=obj_dict[objs[3]], labels={'x':objs[0], 'y': objs[1], 'z': objs[2], 'color': objs[3]})
        try:
            fig1.show()
        except UnboundLocalError:
            pass

        fig2 = px.scatter_3d(x=ind_dict[dvs[0]], y=ind_dict[dvs[1]], z=ind_dict[dvs[2]], labels={'x':dvs[0], 'y': dvs[1], 'z': dvs[2]})
        try:
            fig2.show()
        except UnboundLocalError:
            pass

        # Plot HV Convergece
        for md, array in self.meta_data.items():
            try:
                fig2 = px.line(x=self.meta_data['function evals'], y=array, labels={'x':'Function Evals', 'y':"{}".format(md)})
            except:
                fig2 = px.line(x=[x for x in range(len(array))], y=array, labels={'x':'Trigger Value', 'y':"{}".format(md)})
            fig2.show()

    def publish_trigger(self):
        """Send a trigger event message to all KAs."""
        self._trigger_event += 1
        self.log_debug('\n\nPublishing Trigger Event {}'.format(self._trigger_event))
        self._kaar[self._trigger_event] = {}
        self.send(self._pub_trigger_alias, self.abstract_lvls)

    def send_executor(self):
        """Send an executor message to the triggered KA."""
        if self._ka_to_execute != (None, 0):
            self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self._ka_to_execute[0], round(self._ka_to_execute[1],2), self._trigger_event))
            self.agent_addrs[self._ka_to_execute[0]].update({'performing action':True})
            self._new_entry = False
            self.send('executor_{}'.format(self._ka_to_execute[0]), (self._trigger_event,self.abstract_lvls))
        else:
            self.log_info('No KA to execute, waiting to sends trigger again.')

    def send_shutdown(self):
        """
        We first shutdown all search agents in the proble.
        We follow this up by running the three blackboard reader agents, where we wait until each one is complete before moving to the next.
        We finish this by shutting down the blackboard reader agents.
        """

        search_agents = {ka: self.agent_addrs[ka] for ka in self.agent_list if 'reader' not in self.agent_addrs[ka]['_class']}

        if search_agents != {}:
            for agent_name, connections in search_agents.items():
                if not connections['shutdown']:
                    ...
                elif connections['performing action']:
                    agent = self._proxy_server.proxy(agent_name)
                    agent.unsafe.handler_shutdown('kill')
                elif not self.diagnostics_agent_present(agent_name):
                    ...
                else:
                    self.send(connections['shutdown'][0], "shutdown")
                try:
                    self.agent_list.remove(agent_name)
                except:
                    ...

        if True in [ka['performing action'] for ka in self.agent_addrs.values()]:
            #self.log_info('Waiting for agents to finish action')
            return

        if self.final_trigger > 0:
            ka_ = [ka for ka, ka_dict in self.agent_addrs.items() if str(self.final_trigger) in ka_dict['class'].__name__]
            self._ka_to_execute=(ka_[0], 2)
            self.send_executor()
            self.final_trigger -= 1
            return
        # Add something for inter-agent BB
        agent_addrs = copy.copy(self.agent_addrs)
        for agent_name in self.agent_list:
            self.send(self.agent_addrs[agent_name]['shutdown'][0], "shutdown")
            self.agent_list.remove(agent_name)

    def set_random_seed(self, seed=None):
        """
        Sets the random seed number to provide a reproducabel result
        """
        random.seed(seed=seed)
        self.random_seed = seed