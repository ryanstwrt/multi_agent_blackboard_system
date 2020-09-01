import blackboard
import ka_rp as karp
import ka_br as kabr
import osbrain
from osbrain import proxy
from osbrain import run_agent
import time
import os 
import glob
import database_generator as dg
import numpy as np
import train_surrogate_models as tm
import scipy.interpolate
import plotly.express as px
import performance_measure as pm


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

        self.objectives = {'cycle length':     {'ll':100, 'ul':550,  'goal':'gt', 'variable type': float},
                           'reactivity swing': {'ll':0,   'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,   'ul':200,  'goal':'gt', 'variable type': float},
                           'pu mass':          {'ll':0,   'ul':1500, 'goal':'lt', 'variable type': float}}
        self.design_variables = {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}

        self.total_solutions = 50
        self.objectives_ll = []
        self.objectives_ul = []
        
        self.hv_list = [0]
        self.hv_convergence = 1e-6
        self.num_calls = 25
        self._sm = None
        self.sm_type = 'interpolate'
        self._nadir_point = {}
        self._ideal_point = {}
        
        # Initialize an abstract level which holds meta-data about the problem
        self.add_abstract_lvl(100, {'hvi indicator': float, 'time': float})

    def initialize_abstract_level_3(self, objectives=None, design_variables=None):
        """
        Initialze BB abstract level three with problem specific objectives and design variables
        """
        if objectives:
            self.objectives = objectives
        if design_variables:
            self.design_variables = design_variables
        
#        self.objectives_ll = [0 for x in self.objectives.values()]
 #       self.objectives_ul = [1 for x in self.objectives.values()]
        
        for obj, obj_dict in self.objectives.items():
            if obj_dict['goal'] == 'lt':
                self._nadir_point.update({obj: obj_dict['ll']})
                self._ideal_point.update({obj: obj_dict['ul']})
            else:
                self._nadir_point.update({obj: -obj_dict['ul']})
                self._ideal_point.update({obj: -obj_dict['ll']})

        self.objectives_ll = [self._nadir_point[x] for x in self.objectives.keys()]
        self.objectives_ul = [self._ideal_point[x] for x in self.objectives.keys()]
    

        dv = {iv: iv_dict['variable type'] for iv, iv_dict in self.design_variables.items()}
        obj = {obj: obj_dict['variable type'] for obj, obj_dict in self.objectives.items()}
        self.add_abstract_lvl(3, {'design variables': dv, 'objective functions': obj})        

        self.add_panel(3, ['new','old'])
        
    def clear_data_levels(self):
        """
        Remove solutions that are in a data level to reduce the time required to sort through them.
        """
        
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
        if 'search' in agent_class:
            ka.set_attr(_sm=self._sm)
            ka.set_attr(sm_type=self.sm_type)
            ka.set_attr(design_variables=self.design_variables)
        elif 'reader' in agent_class:
            if 'lvl1' in agent_class:
                nadir_point = {}
                ideal_point = {}
                ka.set_attr(_lower_objective_reference_point=[0 for x in self.objectives.keys()])
                ka.set_attr(_upper_objective_reference_point=[1 for x in self.objectives.keys()])
                # Check this to ensure we are doing this right for ul and ll
 #               for obj, obj_dict in self.objectives.items():
 #                   if obj_dict['goal'] == 'lt':
 #                       nadir_point.update({obj: obj_dict['ll']})
 #                       ideal_point.update({obj: obj_dict['ul']})
 #                   else:
 #                       nadir_point.update({obj: -obj_dict['ul']})
 #                       ideal_point.update({obj: -obj_dict['ll']})
                ka.set_attr(_nadir_point=self._nadir_point)
                ka.set_attr(_ideal_point=self._ideal_point)
        else:
            self.log_info('Agent type ({}) does not match a known agent type.'.format(agent))
            return

    def determine_complete(self):
        """
        Determine when the problem has finished to send the shutdown communication.
        Complete for the traditional system is determined  when a set number of solutions has been placed on abstract level 1 on the blackboard.
        """
        pareto_solutions = 0
        for panel in self.abstract_lvls['level 1'].values():
            for core in panel.values():
                pareto_solutions += 1
        
        if pareto_solutions > self.total_solutions:
            self.log_info('Problem complete, shutting agents down')
            for agent_name, connections in self.agent_addrs.items():
                self.send(connections['shutdown'][0], "shutdown")
            self._complete = True
        else:
            pass
        
    def determine_complete_hv(self):
        """
        Determine if the problem is complete using the convergence of the hypervolume
        """
        
        recent_hv = self.hv_list[-self.num_calls:]
        prev_hv = self.hv_list[-2*self.num_calls:-self.num_calls]
        hv_average = abs(sum(recent_hv) / self.num_calls - sum(prev_hv) / self.num_calls)
        try:
            hv_max = abs(min(recent_hv) - max(prev_hv))
            hv_indicator = hv_average#max([hv_average, hv_max])
        except ValueError:
            hv_indicator = 1
        self.log_info('Convergence Rate: {} '.format(hv_indicator))
        if hv_indicator < self.hv_convergence and len(self.abstract_lvls['level 1']) > self.total_solutions:
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
            pf_ = []
            for obj,val in bb_lvl3[core]['objective functions'].items():
                pf_.append(val if self.objectives[obj]['goal'] == 'lt' else -val)
            pf.append(pf_)
        self.hv_list.append(pm.hypervolume_indicator(pf, self.objectives_ll, self.objectives_ul))
        
    def generate_sm(self):
        objectives = [x for x in self.objectives.keys()]
        design_var, objective_func = dg.get_data([x for x in self.design_variables.keys()], objectives)
        if self.sm_type == 'interpolate':
            self._sm = {}
            design_var, objective_func = np.asarray(design_var), np.asarray(objective_func)
            for num, objective in enumerate(objectives):
                self._sm[objective] = scipy.interpolate.LinearNDInterpolator(design_var, objective_func[:,num])
        else:
            self._sm = tm.Surrogate_Models()
            self._sm.random = 0
            self._sm.update_database(design_var, objective_func)
            self._sm.optimize_model(self.sm_type)
            
    def plot_progress(self):
        """
        Generate a plot of the hypervolume and Pareto front during the problem.
        """
        
        lvl_3 = {}
        for panel in self.abstract_lvls['level 3'].values():
            lvl_3.update(panel)

        lvl_1 = self.abstract_lvls['level 1']

        cycle_length = []
        rx_swing = []
        height = []
        smear = []
        pu_content = []
        bu = []
        pu_mass = []
        fitness = []

        obj_dict = {}
        for core, values in lvl_1.items():
            fitness.append(round(values['fitness function'],5))
            core_params = lvl_3[core]['objective functions']
        
            for obj in self.objectives.keys():
                if obj in obj_dict.keys():
                    obj_dict[obj].append(core_params[obj])
                else:
                    obj_dict[obj] = [core_params[obj]]
        objs = [x for x in self.objectives.keys()]
        obj_labels = {'fitness': 'fitness',
                      'burnup': 'Burnup (GWD/MTHM)',
                      'cycle length': 'Cycle Length(days)',
                      'pu mass': 'Pu Mass (kg/year)',
                      'reactivity swing' : 'Rx Swing (pcm/month)'}
        if len(obj_dict.keys()) == 2:
            fig1 = px.scatter(x=obj_dict[objs[0]], y=obj_dict[objs[1]], labels={'x':obj_labels[objs[0]], 'y': obj_labels[objs[1]]})
        elif len(obj_dict.keys()) == 3:
            fig1 = px.scatter_3d(x=obj_dict[objs[0]], y=obj_dict[objs[1]], z=obj_dict[objs[2]], labels={'x':obj_labels[objs[0]], 'y': obj_labels[objs[1]], 'z': obj_labels[objs[2]]})
        elif len(obj_dict.keys()) > 3:
            fig1 = px.scatter_3d(x=obj_dict[objs[0]], y=obj_dict[objs[1]], z=obj_dict[objs[2]], color=obj_dict[objs[3]], labels={'x':obj_labels[objs[0]], 'y': obj_labels[objs[1]], 'z': obj_labels[objs[2]], 'color': obj_labels[objs[3]]})
        try:
            fig1.show()
        except UnboundLocalError:
            pass
        # Plot HV Convergece
        fig2 = px.line(x=[x for x in range(len(self.hv_list))], y=self.hv_list, labels={'x':'Trigger Value', 'y':"Hyper Volume"})        
        fig2.show()
            
    def send_executor(self):
        """Send an executor message to the triggered KA."""
        if self._ka_to_execute != (None, 0):
            self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self._ka_to_execute[0], self._ka_to_execute[1], self._trigger_event))
            self._new_entry = False
            self.send('executor_{}'.format(self._ka_to_execute[0]), self._ka_to_execute)
        else:
            self.log_info('No KA to execute, waiting to sends trigger again.')