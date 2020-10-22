import src.blackboard as blackboard
import src.ka_rp as karp
import src.ka_br as kabr
import osbrain
from osbrain import proxy
from osbrain import run_agent
import time
import os 
import glob
import src.database_generator as dg
import numpy as np
import src.train_surrogate_models as tm
import scipy.interpolate
import plotly.express as px
import src.performance_measure as pm


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
                           'pu mass':          {'ll':0,     'ul':1500, 'goal':'lt', 'variable type': float}}
        self.design_variables = {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}

        self.constraints = {'eol keff':    {'ll': 1.0, 'ul': 2.5, 'variable type': float}}
        
        self.objectives_ll = []
        self.objectives_ul = []
        self.convergence_model = {'type': 'hvi', 'convergence rate': 1E-6, 'interval': 25, 'pf size': 50}

        self.hv_list = [0.0]
        self._sm = None
        self.sm_type = 'interpolate'
        self._nadir_point = {}
        self._ideal_point = {}
        self._pareto_level = ['level 1']
        self.previous_pf = {}
        self.dci_convergence_list = [0.0]
        self.random_seed = None
        
        # Initialize an abstract level which holds meta-data about the problem
        self.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})

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

        self.objectives_ll = [self._nadir_point[x] for x in self.objectives.keys()]
        self.objectives_ul = [self._ideal_point[x] for x in self.objectives.keys()]

        dv  = {dv:   dv_dict['variable type']   for dv,   dv_dict   in self.design_variables.items()}
        obj = {obj:  obj_dict['variable type']  for obj,  obj_dict  in self.objectives.items()}
        cnst  = {cnst: cnst_dict['variable type'] for cnst, cnst_dict in self.constraints.items()}
        self.add_abstract_lvl(3, {'design variables': dv, 'objective functions': obj, 'constraints' : cnst})
        self.add_panel(3, ['new','old'])
        
    def clear_data_levels(self):
        """
        Remove solutions that are in a data level to reduce the time required to sort through them.
        """
        pass
        
    def connect_ka_specific(self, agent):
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
        if 'search' in agent_class:
            ka.set_random_seed(seed=self.random_seed)
            ka.set_attr(_sm=self._sm)
            ka.set_attr(sm_type=self.sm_type)
            ka.set_attr(design_variables=self.design_variables)
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
        else:
            self.log_info('Agent type ({}) does not match a known agent type.'.format(agent))
            return
        
    def convergence_indicator(self):
        """
        Determine what to do after a trigger event has been processed
        """
        if self.convergence_model['type'] == 'dci hvi':
            self.dc_indicator()
        elif self.convergence_model['type'] == 'hvi':
            self.hv_indicator()
        else:
            self.log_info('convergence_model ({}) not recognized, reverting to hvi'.format(self.convergence_model['type']))
            self.hv_indicator()

    def convergence_update(self):
        """
        Determine if any values need to be udpated after a trigger event
        """
        self.hv_list.append(self.hv_list[-1])       
        
    def determine_complete(self):
        """
        Determine if the problem has converged
        """
        if self.convergence_model['type'] == 'dci hvi':
            self.determine_complete_dci_hvi()
        elif self.convergence_model['type'] == 'hvi':
            self.determine_complete_hv()
        else:
            self.log_info('convergence_model ({}) not recognized, reverting to hvi'.format(self.convergence_model['type']))
            pass           
        
    def determine_complete_dci_hvi(self):
        """
        Determine if the problem is complete using the convergence of dci and the hvi
        """        
        if self.dci_convergence_list[-1] < self.convergence_model['convergence rate']:
            self.hv_indicator()
        else:
            self.convergence_update()
        

    def list_objective_value(self, obj_list, goal_type):
        """
        Returns a single value to use as either a fitness function or Pareto indicator if our objective is a list
        """
        
        if goal_type == 'max':
            obj_val = max(obj_list)
        elif goal_type == 'min':
            obj_val = min(obj_list)
        else:
            obj_val = sum(obj_list)/len(obj_list)   
            
        return obj_val
    
    def get_objective_value(self, core, obj):
        objective_value = self.abstract_lvls['level 3']['old'][core]['objective functions'][obj]
        if (type(objective_value) == float) or (type(objective_value) == int):
            return objective_value
        elif type(objective_value) == list:
            return self.list_objective_value(objective_value, self.objectives[obj]['goal type']) 
        
        
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
        dci = pm.diversity_comparison_indicator(self._nadir_point, self._ideal_point, total_pf, self.convergence_model['div'])
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
        num = self.convergence_model['interval']
        recent_hv = self.hv_list[-num:]
        prev_hv = self.hv_list[-2*num:-num]
        hv_average = abs(sum(recent_hv) / num - sum(prev_hv) / num)
        try:
            hv_indicator = hv_average
        except ValueError:
            hv_indicator = 1.0
        self.log_info('Convergence Rate: {} '.format(hv_indicator))
        if hv_indicator < self.convergence_model['convergence rate'] and len(self.abstract_lvls['level 1']) > self.convergence_model['pf size']:
            self.log_info('Problem complete, shutting agents down')
            for agent_name, connections in self.agent_addrs.items():
                self.send(connections['shutdown'][0], "shutdown")
            self._complete = True
    
    def hv_indicator(self):
        """
        Calcualte the Hypervolume for the current pareto front
        """
        pf = []
        cores = [x for x in self.abstract_lvls['level 1']]
        bb_lvl3 = self.abstract_lvls['level 3']['old']
        for core in cores:
            pf.append([self.get_objective_value(core, obj) if self.objectives[obj]['goal'] == 'lt' else -self.get_objective_value(core, obj) for obj in self.objectives.keys()])
        if self.convergence_model['type'] == 'dci hvi':
            self.hv_list[self._trigger_event] = pm.hypervolume_indicator(pf, self.objectives_ll, self.objectives_ul)
        else:
            self.hv_list.append(pm.hypervolume_indicator(pf, self.objectives_ll, self.objectives_ul))
            
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
                      'reactivity swing' : 'Rx Swing (pcm/month)'}
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
        
#        fig2 = px.scatter_3d(x=ind_dict[dvs[0]], y=ind_dict[dvs[1]], z=ind_dict[dvs[2]], color=fitness, labels={'x':dv_labels[dvs[0]], 'y': dv_labels[dvs[1]], 'z': dv_labels[dvs[2]], 'color':'fitness'})
        fig2 = px.scatter_3d(x=ind_dict[dvs[0]], y=ind_dict[dvs[1]], z=ind_dict[dvs[2]], labels={'x':dv_labels[dvs[0]], 'y': dv_labels[dvs[1]], 'z': dv_labels[dvs[2]]})
        try:
            fig2.show()
        except UnboundLocalError:
            pass
        
        # Plot HV Convergece
        fig2 = px.line(x=[x for x in range(len(self.hv_list))], y=self.hv_list, labels={'x':'Trigger Value', 'y':"Hyper Volume"})        
        fig2.show()
            
    def send_executor(self):
        """Send an executor message to the triggered KA."""
        if self._ka_to_execute != (None, 0):
            self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self._ka_to_execute[0], round(self._ka_to_execute[1],2), self._trigger_event))
            agent_class = str(self.agent_addrs[self._ka_to_execute[0]]['class'])
            self._new_entry = False
            if 'Local' in agent_class:
                self.send('executor_{}'.format(self._ka_to_execute[0]), (self.abstract_lvls['level 1'],
                                                                         self.abstract_lvls['level 3']['old']))
            elif 'Br' in agent_class:
                self.send('executor_{}'.format(self._ka_to_execute[0]), self.abstract_lvls)
            else:
                self.send('executor_{}'.format(self._ka_to_execute[0]), self._ka_to_execute)
        else:
            self.log_info('No KA to execute, waiting to sends trigger again.')

    def publish_trigger(self):
        """Send a trigger event message to all KAs."""
        self._trigger_event += 1
        self.log_debug('\n\nPublishing Trigger Event {}'.format(self._trigger_event))
        self._kaar[self._trigger_event] = {}
        self.send(self._pub_trigger_alias, self.abstract_lvls)


#    def h5_delete_entries(self, h5):
#        """
#        Examine the H5 file and current blackbaord dabstract levels and remove entries in the H5 file that are no longer in the BB bastract levels. (likely this is due to solution no longer being on the Pareto front)
#        
#        Parameters
#        ----------
#        h5 : h5-group object
#            H5 entry that is no longer in the abstract level
#        
#        """
#        bb = self.abstract_lvls
#        del_entries = []
#        for level, entry in h5.items():
#            if level in self._pareto_level:
#                for entry_name, entry_data in entry.items():
#                    if level in self._panels.keys():
#                        panel_entries = [panel for panel in entry_data]
#                        for panel_entry in panel_entries:
#                            if panel_entry not in bb[level][entry_name]:
#                                del_entries.append((level, entry_name, panel_entry))   
#                    if entry_name not in bb[level]:
#                        del_entries.append((level, entry_name))


#        for entry in del_entries:
#            if len(entry) == 3:
#                del h5[entry[0]][entry[1]][entry[2]]
#                self.log_debug('Removing entry {} on level {} panel {}'.format(entry[2],entry[0],entry[1]))
#            else:
#                del h5[entry[0]][entry[1]]          
#                self.log_debug('Removing entry {} on level {}'.format(entry[1],entry[0]))
                
    def delete_data_entries(self):
        pf = [x for x in self.abstract_lvls['level 1'].keys()]
        lvl2 = self.abstract_lvls['level 2']['old']
        lvl3 = self.abstract_lvls['level 3']['old']
        
        lvl2_list = []
        lvl3_list = []
        for core, entry in lvl2.items():
            if core not in pf:
                lvl2_list.append(core)
        for core in lvl2_list:
            self.remove_bb_entry(2, core, 'old')

        for core, entry in lvl3.items():
            if core not in pf:
                lvl3_list.append(core)
        for core in lvl3_list:
            self.remove_bb_entry(3, core, 'old')
        
    def meta_data_entry(self, time):
        """
        Add an entry to abstract level 100 for meta-data
        """
        entry_name = str(self._trigger_event)
        entry = {'agent': self._ka_to_execute[0], 'time': float(time), 'hvi': self.hv_list[self._trigger_event]}
#        entry = {'agent': self._ka_to_execute[0], 'time': float(time), 'hvi': self.hv_list[-1]}

        
        self.update_abstract_lvl(100, entry_name, entry)