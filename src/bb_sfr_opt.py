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


class BbSfrOpt(blackboard.Blackboard):
    
    def on_init(self):
        super().on_init()
        self._complete = False
        self.problem = 'basic'
        self.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
        self.add_panel(1, ['new', 'old'])       
        self.add_abstract_lvl(2, {'valid': bool})
        self.add_panel(2, ['new', 'old'])
        
        self.objectives = {'cycle length':     {'ll':100, 'ul':550,  'goal':'gt', 'variable type': float},
                           'reactivity swing': {'ll':0,   'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,   'ul':200,  'goal':'gt', 'variable type': float},
                           'pu mass':          {'ll':0,   'ul':1500, 'goal':'lt', 'variable type': float}}
        self.design_variables = {'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                 'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                 'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}

        self.total_solutions = 50
        
        self.hv_dict = {0:0}
        self.hv_convergence = 0.05
        self.num_calls = 25
        self._sm = None
        self.sm_type = 'interpolate'

    def initialize_abstract_level_3(self, objectives=None, design_variables=None):
        """
        Initialze BB abstract level three with problem specific objectives and design variables
        """
        if objectives:
            self.objectives = objectives
        if design_variables:
            self.design_variables = design_variables
        
        rx_params = {iv: iv_dict['variable type'] for iv, iv_dict in self.design_variables.items()}
        rx_params.update({obj: obj_dict['variable type'] for obj, obj_dict in self.objectives.items()})
        self.add_abstract_lvl(3, {'reactor parameters': rx_params})        
        self.add_panel(3, ['new','old'])
        
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
        if 'rp' in agent:
            ka.set_attr(_sm=self._sm)
            ka.set_attr(sm_type=self.sm_type)
            ka.set_attr(objectives=self.objectives)
            ka.set_attr(design_variables=self.design_variables)
        elif 'lvl' in agent:
            ka.set_attr(_objective_ranges=self.objectives)
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
        pf = []
        old = []
        new = []
        hv_indicator = 1
        try:
            for num in range(self.num_calls):
                old.append(self.hv_dict[self._trigger_event-self.num_calls-num])
                new.append(self.hv_dict[self._trigger_event-num])
            hv_indicator = sum(new) / self.num_calls - sum(old) / self.num_calls
        except KeyError:
            pass
        if hv_indicator < self.hv_convergence:
            self._complete = True
    
    def hv_indicator(self):
        pf = []
        core_old = [x for x in self.abstract_lvls['level 1']['old'].keys()]
        core_new = [x for x in self.abstract_lvls['level 1']['new'].keys()]
        cores = core_old + core_new
        bb_lvl3 = self.abstract_lvls['level 3']['old']
        ll = [x['ll'] for x in self.objectives.values()]
        ul = [x['ul'] for x in self.objectives.values()]
        for core in cores:
            rx_params = [bb_lvl3[core]['reactor parameters'][param] for param in self.objectives.keys()]
            pf.append(rx_params)
        self.hv_dict[self._trigger_event] = pm.hypervolume_indicator(pf, ll, ul)
        
    
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
        
        lvl_3 = {}
        for panel in self.abstract_lvls['level 3'].values():
            lvl_3.update(panel)

        lvl_1 = {}
        for panel in self.abstract_lvls['level 1'].values():
            lvl_1.update(panel)

        cycle_length = []
        rx_swing = []
        height = []
        smear = []
        pu_content = []
        bu = []
        pu_mass = []
        fitness = []
        
        if self.problem == 'prelims':
            for core, values in lvl_1.items():
                core_params = lvl_3[core]['reactor parameters']
                cycle_length.append(core_params['keff'])
                height.append(core_params['doppler'])
                smear.append(core_params['void'])            
                pu_content.append(core_params['pu_content'])
            fig = px.scatter_3d(x=smear, y=height, z=cycle_length, color=pu_content, labels={'y':'Doppler Coeff', 'x': 'Void Coeff', 'z':'k-eff','color':'Pu Frac.'})
            fig.show()
            
        else:
            obj_dict = {}
            for core, values in lvl_1.items():
                fitness.append(round(values['fitness function'],5))
                core_params = lvl_3[core]['reactor parameters']
                height.append(core_params['height'])
                smear.append(core_params['smear'])
                pu_content.append(core_params['pu_content'])
        
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
                fig1 = px.scatter(x=obj_dict[objs[0]], y=obj_dict[objs[1]], color=pu_content, labels={'x':obj_labels[objs[0]], 'y': obj_labels[objs[1]], 'color': 'pu_content'})
                fig2 = px.scatter_3d(x=height, y=smear, z=pu_content, color=obj_dict[objs[1]], labels={'x':'Height (cm)', 'y': 'Smear', 'z':'Pu Content','color':objs[1]})

            else:
                fig1 = px.scatter_3d(x=obj_dict[objs[0]], y=obj_dict[objs[1]], z=obj_dict[objs[2]], color=obj_dict[objs[3]], labels={'x':obj_labels[objs[0]], 'y': obj_labels[objs[1]], 'z': obj_labels[objs[2]], 'color': obj_labels[objs[3]]})
            fig1.show()
#            fig2.show()

        # Plot HV Convergece
        x = [x for x in self.hv_dict.keys()]
        y = [y for y in self.hv_dict.values()]
        fig1 = px.line(x=x, y=y, labels={'x':'Trigger Value', 'y':"Hyper Volume"})        
        fig1.show()
            
    def send_executor(self):
        """Send an executor message to the triggered KA."""
        if self._ka_to_execute != (None, 0):
            self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self._ka_to_execute[0], self._ka_to_execute[1], self._trigger_event))
            self._new_entry = False
            self.send('executor_{}'.format(self._ka_to_execute[0]), self._ka_to_execute)
        else:
            self.log_info('No KA to execute, waiting to sends trigger again.')