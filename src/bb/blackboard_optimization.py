import src.bb.blackboard as blackboard
import src.utils.utilities as utils
import src.utils.database_generator as dg
import src.utils.performance_measure as pm
import src.utils.train_surrogate_models as tm
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

        self.objectives = {'cycle length':     {'ll':100,   'ul':550,  'goal':'gt', 'variable type': float},
                           'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float},
                           'pu mass':          {'ll':0,     'ul':1500, 'goal':'lt', 'variable type': float},}
        self.design_variables = {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}

        self.constraints = {'eol keff':    {'ll': 1.0, 'ul': 2.5, 'variable type': float}}
        
        self.objectives_ll = []
        self.objectives_ul = []
        self.total_tvs = 1E6
        
        
        self.hv_list = [0.0]
        self._sm = None
        self.sm_type = 'interpolate'
        self._nadir_point = {}
        self._ideal_point = {}
        self._pareto_level = ['level 1']
        self.previous_pf = {}
        self.dci_convergence_list = [0.0]
        self.random_seed = None
        
        self.skipped_tvs = 200
        self.convergence_type = 'hvi'
        self.convergence_rate = 1E-6
        self.convergence_interval = 25
        self.pf_size = 200
        self.function_evals = 1E6
        self.dci_div = {}
        self.final_trigger = 3        
        
        # Initialize an abstract level which holds meta-data about the problem
        self.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
        
    def set_random_seed(self, seed=None):
        """
        Sets the random seed number to provide a reproducabel result
        """
        random.seed(seed=seed)
        self.random_seed = seed

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
        
    def create_level_format(self, level_entry):
        level_format = {}
        for dv, dv_dict in level_entry.items():
            if dv_dict['variable type'] == dict:
                level_format[dv] = self.create_level_format(dv_dict['dict'])
            else:
                level_format[dv] = dv_dict['variable type']
        return level_format
        
    def clear_data_levels(self):
        """
        Remove solutions that are in a data level to reduce the time required to sort through them.
        """
        pass
        
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
        for k,v in attr.items():
            ka.set_attr(**{k:v})
        
        if 'search' in agent_class:
            ka.set_random_seed(seed=self.random_seed)
            ka.set_attr(_sm=self._sm)
            ka.set_attr(sm_type=self.sm_type)
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
            self.hv_indicator()
        else:
            self.log_debug('convergence type ({}) not recognized, reverting to total TVs'.format(self.convergence_type))
            self.hv_list.append(0.0)
#            self.hv_indicator()
            
    def convergence_update(self):
        """
        Determine if any values need to be udpated after a trigger event
        """
        self.hv_list.append(self.hv_list[-1])       
        
    def determine_complete(self):
        """
        Determine if the problem has converged
        """
        if self.convergence_type == 'dci hvi':
            self.determine_complete_dci_hvi()
        elif self.convergence_type == 'hvi':
            self.determine_complete_hv()
        elif self.convergence_type == 'function evals':
            lvl3 = {}
            for panel in self.abstract_lvls['level 3'].values():
                lvl3.update(panel)
            self.log_info('Problem is at {} of {} total allowable function evals'.format(len(lvl3), self.function_evals))
                
            if len(lvl3) > self.function_evals:
                self.log_info('Problem is over total allowable function evals, shutting agents down')
                self._complete = True 
                return
        else:
            self.log_debug('convergence type ({}) not recognized, reverting to total TVs'.format(self.convergence_type))
            pass     
        # Determine if the problem is over our trigger value limit
        if len(self._kaar) >= self.total_tvs and self._complete == False:
            self.log_info('Problem is over total allowable TVs, shutting agents down')
            self._complete = True        
            
    def send_shutdown(self):
        """
        Tell each agent to shutdown
        """
        if True in [ka['performing action'] for ka in self.agent_addrs.values()]:
            return
        
        if self.final_trigger > 0:
            ka_ = [ka for ka, ka_dict in self.agent_addrs.items() if str(self.final_trigger) in ka_dict['class'].__name__]
            self._ka_to_execute=(ka_[0], 2)
            self.send_executor()
            self.final_trigger -= 1
            return

        agent_addrs = copy.copy(self.agent_addrs)      
        for agent_name, connections in self.agent_addrs.items():
        # If statement is for inter_BB agent who only have a write function assocaiated with the BB
            if 'shutdown' not in list(connections.keys()):
                agent_addrs.pop(agent_name)
            elif agent_name in agent_addrs.keys():  
                if connections['performing action']:
                    self.log_info((agent_name, connections['performing action']))
                elif not self.diagnostics_agent_present(agent_name):
                    agent_addrs.pop(agent_name)
                else:
                    self.send(connections['shutdown'][0], "shutdown")
                    agent_addrs.pop(agent_name)
                
        self.agent_addrs = agent_addrs
        
    def determine_complete_dci_hvi(self):
        """
        Determine if the problem is complete using the convergence of dci and the hvi
        """        
        if self.dci_convergence_list[-1] < self.convergence_rate:
            self.hv_indicator()
        else:
            self.convergence_update()
    
    def get_objective_value(self, core, obj):
        objective_value = self.abstract_lvls['level 3']['old'][core]['objective functions'][obj]
        goal = self.objectives[obj]['goal type'] if 'goal type' in self.objectives[obj] else None
        return utils.get_objective_value(objective_value, goal)
        
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
        
        
    def determine_complete_hv(self):
        """
        Determine if the problem is complete using the convergence of the hypervolume
        """
        num = self.convergence_interval
        recent_hv = self.hv_list[-num:]
        prev_hv = self.hv_list[-2*num:-num]
        hv_average = abs(sum(recent_hv) / num - sum(prev_hv) / num)
        hv_indicator = hv_average
        
        # Long term convergence
        #num = 5 * self.convergence_interval
        #recent_hv = self.hv_list[-num:]
        #prev_hv = self.hv_list[-2*num:-num]
        #hv_average_long_term = abs(sum(recent_hv) / num - sum(prev_hv) / num)
        #hv_indicator_long_term = hv_average        
        #self.log_info('Convergence Rate: {}, Long-Term Convergence Rate: {}'.format(hv_indicator, hv_average_long_term))
        
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
            self.log_info('Problem complete, shutting agents down')
            self._complete = True        

    def hv_indicator(self):
        """
        Calcualte the Hypervolume for the current pareto front
        """
        pf = []
        cores = list(self.abstract_lvls['level 1'].keys())
        lvl_3 = {}
        for panel in self.abstract_lvls['level 3'].values():
            lvl_3.update(panel)
        
        pf = utils.scale_pareto_front(cores, self.objectives, lvl_3)

        if self.convergence_type == 'dci hvi':
            self.hv_list[self._trigger_event] = round(pm.hypervolume_indicator(pf, self.objectives_ll, self.objectives_ul),10)
        else:
            self.hv_list.append(round(pm.hypervolume_indicator(pf, self.objectives_ll, self.objectives_ul),10))
            
    def get_hv_list(self):
        return self.hv_list
    
    def get_complete_status(self):
        return self._complete
            
    def generate_sm(self):
        """
        Generate a surrogate model for the search agents to use.
        """
        objectives = [x for x in self.objectives.keys()]
        objectives = objectives if not self.constraints else objectives + [x for x in self.constraints.keys()]
        design_var, objective_func, data_dict = dg.get_data([x for x in self.design_variables.keys()], objectives, database_name='SFR_DB_2', fixed_cycle_length=100)
        if self.sm_type == 'interpolate':
            self._sm = {}
            design_var, objective_func = np.asarray(design_var), np.asarray(objective_func)
            for num, objective in enumerate(objectives):
                self._sm[objective] = scipy.interpolate.LinearNDInterpolator(design_var, objective_func[:,num])
        else:
            self._sm = tm.Surrogate_Models()
            self._sm.random = self.random_seed
            self._sm.update_database([x for x in self.design_variables.keys()], objectives, database=data_dict)
            self._sm.optimize_model(self.sm_type)
            
    def plot_progress(self):
        """
        Generate a plot of the hypervolume and Pareto front during the problem.
        """
        lvl_1 = self.abstract_lvls['level 1']
        if lvl_1 == {}:
            return
        
        lvl_3 = {}
        for panel in self.abstract_lvls['level 3'].values():
            lvl_3.update(panel)
        
        fitness = []

        obj_dict = {}
        ind_dict = {}
        for core, values in lvl_1.items():
            fitness.append(round(values['fitness function'],5))
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
        obj_labels = {'fitness': 'fitness',
                      'burnup': 'Burnup (GWD/MTHM)',
                      'cycle length': 'Cycle Length (days)',
                      'pu mass': 'Pu Mass (kg/year)',
                      'reactivity swing' : 'Rx Swing (pcm/month)',
                      'eol keff': 'EOC k-eff',
                      'pu ratio': 'Pu239/Pu Ratio',
                      'pu disposed': 'Pu/cycle (kg)'}
        dv_labels = {'height' : 'Height (cm)',
                     'smear' : 'Smear',
                     'pu_content' : 'Pu Fraction'}
        if len(obj_dict.keys()) == 2:
            fig1 = px.scatter(x=obj_dict[objs[0]], y=obj_dict[objs[1]], labels={'x':obj_labels[objs[0]], 'y': obj_labels[objs[1]]})
        elif len(obj_dict.keys()) == 3:
            fig1 = px.scatter_3d(x=obj_dict[objs[0]], y=obj_dict[objs[1]], z=obj_dict[objs[2]], color=fitness, labels={'x':obj_labels[objs[0]], 'y': obj_labels[objs[1]], 'z': obj_labels[objs[2]], 'color': obj_labels['fitness']})
        elif len(obj_dict.keys()) > 3:
            fig1 = px.scatter_3d(x=obj_dict[objs[0]], y=obj_dict[objs[1]], z=obj_dict[objs[2]], color=obj_dict[objs[3]], labels={'x':obj_labels[objs[0]], 'y': obj_labels[objs[1]], 'z': obj_labels[objs[2]], 'color': obj_labels[objs[3]]})
        try:
            fig1.show()
        except UnboundLocalError:
            pass
        
        fig2 = px.scatter_3d(x=ind_dict[dvs[0]], y=ind_dict[dvs[1]], z=ind_dict[dvs[2]], labels={'x':dv_labels[dvs[0]], 'y': dv_labels[dvs[1]], 'z': dv_labels[dvs[2]]})
        try:
            fig2.show()
        except UnboundLocalError:
            pass
        
        # Plot HV Convergece
        fig2 = px.line(x=[x for x in range(len(self.hv_list))], y=self.hv_list, labels={'x':'Trigger Value', 'y':"Hyper Volume"})        
        fig2.show()

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
        
    def send_executor(self):
        """Send an executor message to the triggered KA."""
        if self._ka_to_execute != (None, 0):
            self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self._ka_to_execute[0], round(self._ka_to_execute[1],2), self._trigger_event))
            self.agent_addrs[self._ka_to_execute[0]].update({'performing action':True})
            self._new_entry = False
            self.send('executor_{}'.format(self._ka_to_execute[0]), (self._trigger_event,self.abstract_lvls))
        else:
            self.log_info('No KA to execute, waiting to sends trigger again.')

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

        
    def publish_trigger(self):
        """Send a trigger event message to all KAs."""
        self._trigger_event += 1
        self.log_debug('\n\nPublishing Trigger Event {}'.format(self._trigger_event))
        self._kaar[self._trigger_event] = {}
        self.send(self._pub_trigger_alias, self.abstract_lvls)
        
    def meta_data_entry(self, name, time, trigger_event):
        """
        Add an entry to abstract level 100 for meta-data
        
        Trigger events start at 1, not 0, so we offset by 1 when looking at the hv list
        """
        entry_name = str(trigger_event)

        entry = {'agent': name, 'time': float(time), 'hvi': self.hv_list[trigger_event-1]}
        self.update_abstract_lvl(100, entry_name, entry)


class MasterBbOpt(BbOpt):
    
    def on_init(self):
        super().on_init()
        self.objectives = {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'goal': 'gt', 'variable type': float},
                           'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
        self.design_variables = {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}

        self.constraints = {
                            'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                            'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
        
        self.total_tvs = 2E4
        self.convergence_type = 'hvi'
        self.convergence_rate = 1E-4
        self.convergence_interval = 25
        self.pf_size = 200
        self.dci_div = {}
        # Initialize an abstract level which holds meta-data about the problem
        self.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})




class SubBbOpt(BbOpt):
    
    def on_init(self):
        super().on_init()
        self.objectives = {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float},}
        self.design_variables = {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}

        self.constraints = {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'variable type': float},
                            'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
        
        self.objectives_ll = []
        self.objectives_ul = []

        self.total_tvs = 2E4
        self.convergence_type = 'hvi'
        self.convergence_rate = 1E-4
        self.convergence_interval = 25
        self.pf_size = 200
        self.dci_div = {}
        
        # Initialize an abstract level which holds meta-data about the problem
        self.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})


class BenchmarkBbOpt(BbOpt):
    
    def on_init(self):
        super().on_init()
        self._complete = False
        self.problem = 'benchmark'
        self.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
        self.add_abstract_lvl(2, {'valid': bool})
        self.add_panel(2, ['new', 'old'])

        self.objectives = {}
        self.design_variables =  {}
        self.constraints = {}
        # Initialize an abstract level which holds meta-data about the problem
        self.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
                
    def plot_progress(self):
        
        try:
            lvls = self.get_attr('abstract_lvls')
            objectives = self.get_attr('objectives')
            lvl_3 = {}
            for panel in lvls['level 3'].values():
                lvl_3.update(panel)    
            lvl_1 = lvls['level 1']

            obj_dict = {}
            objs = [x for x in objectives.keys()]
            for entry_name, entry in lvl_1.items():
                val = lvl_3[entry_name]['objective functions']
                for obj in objectives.keys():
                    if obj in obj_dict.keys():
                        obj_dict[obj].append(val[obj])
                    else:
                        obj_dict[obj] = [val[obj]]

            fig1 = px.scatter(x=obj_dict[objs[0]], y=obj_dict[objs[1]], labels={'x':'f1', 'y':'f2'})
            fig1.show()
        except KeyError:
            pass
        fig2 = px.line(x=[x for x in range(len(self.hv_list))], y=self.hv_list, labels={'x':'Trigger Value', 'y':"Hyper Volume"})        
        fig2.show()
        
    def encode_design(self, design):
        """
        Encode the design variables into a format which can be passed to train_surrogate_model
        """
        level_3 = {}
        for panel in self.abstract_lvls['level 3'].values():
            level_3.update(panel)
        encoded_design = []
        encoder_dict = utils.encode_dvs(self.design_variables)
        for dv in self.design_variables.keys():
            converted_dv = encoder_dict[dv].transform([[level_3[design]['design variables'][dv]]])
            for num, option in enumerate(self.design_variables[dv]['options']):
                encoded_design.append(converted_dv[0][num])
        return encoded_design

    def prepare_sm(self):
        """
        Convert the blackboard data to a format which can be interpreted by train_surrogate_model
        """
        self.dv_dict = {}
        self.obj_dict = {}
        for dv in self.design_variables:
            if self.design_variables[dv]['variable type'] != float:
                self.dv_dict.update({str(dv) + str(option) : [] for option in self.design_variables[dv]['options']})
            else:
                self.dv_dict.update({dv:[]})
        for obj in self.objectives.keys():
            if self.objectives[obj]['variable type'] == list:
                self.obj_dict.update({str(obj) + str(num) : [] for num in range(0,self.objectives[obj]['length'])})
            else:
                self.obj_dict.update({obj:[]})
        for constraint in self.constraints.keys():
            if self.constraints[constraint]['variable type'] == list:
                self.obj_dict.update({str(constraint) + str(num) : [] for num in range(0,self.constraints[constraint]['length'])})
            else:
                self.obj_dict.update({constraint:[]})      

    def convert_data_for_sm(self):
        """
        Convert data in the blackboard to be sent to a surrogate model
        """
        encoder_dict = utils.encode_dvs(self.design_variables)

        level_3 = {}
        for panel in self.abstract_lvls['level 3'].values():
            level_3.update(panel)

        for core in level_3.keys():
            for dv in self.design_variables:
                if self.design_variables[dv]['variable type'] == str:
                    encoded_dv = encoder_dict[dv].transform([[level_3[core]['design variables'][dv]]])
                    for num, option in enumerate(self.design_variables[dv]['options']):
                        name = str(dv) + str(option)
                        self.dv_dict[name].append(encoded_dv[0][num])
                else:
                    dv_dict[dv].append(level_3[core]['design variables'][dv])
            for obj in self.objectives.keys():
                if self.objectives[obj]['variable type'] == list:
                    for num, obj_val in enumerate(level_3[core]['objective functions'][obj]):
                        name = str(obj) + str(num)
                        self.obj_dict[name].append(obj_val)
                else:
                    self.obj_dict[obj].append(level_3[core]['objective functions'][obj])
            for constraint in self.constraints.keys():
                if self.constraints[constraint]['variable type'] == list:
                    for num, con_val in enumerate(level_3[core]['constraints'][constraint]):
                        name = str(constraint) + str(num)
                        self.obj_dict[name].append(con_val)
                else:
                    self.obj_dict[constraint].append(level_3[core]['constraints'][constraint])
 

