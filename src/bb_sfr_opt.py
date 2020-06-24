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
        
        self.objective_ranges = {'cycle length': (100, 550, 'gt'), 
                                 'reactivity swing': (0, 750, 'lt'), 
                                 'burnup': (0, 200, 'gt'), 
                                 'pu mass': (0, 1500, 'lt')}
        
        self.design_variable_ranges = {'height': (50, 80), 
                                       'smear': (50,70), 
                                       'pu_content': (0,1)}
        
        self.objectives = {'cycle length':     {'ll':100, 'ul':550,  'goal':'gt', 'variable type': float},
                           'reactivity swing': {'ll':0,   'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,   'ul':200,  'goal':'gt', 'variable type': float},
                           'pu mass':          {'ll':0,   'ul':1500, 'goal':'gt', 'variable type': float}}
        self.design_variables = {'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                 'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                 'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}
        
        rx_params = {iv: iv_dict['variable type'] for iv, iv_dict in self.design_variables.items()}
        rx_params.update({obj: obj_dict['variable type'] for obj, obj_dict in self.objectives.items()})
        self.add_abstract_lvl(3, {'reactor parameters': rx_params})        
        self.add_panel(3, ['new','old'])

        self.total_solutions = 50
        
        self._sm = None
        self.sm_type = 'interpolate'

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
            ka.set_attr(design_variable_ranges=self.design_variable_ranges)
        elif 'lvl' in agent:
            ka.set_attr(_objective_ranges=self.objective_ranges)
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
    
    def generate_sm(self):
        objectives = [x for x in self.objective_ranges.keys()]
        design_var, objective_func = dg.get_data([x for x in self.design_variable_ranges.keys()], objectives)
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
            for core, values in lvl_1.items():
                fitness.append(round(values['fitness function'],5))
                core_params = lvl_3[core]['reactor parameters']
                height.append(core_params['height'])
                smear.append(core_params['smear'])
                pu_content.append(core_params['pu_content'])
                cycle_length.append(round(core_params['cycle length'],0))
                rx_swing.append(round(core_params['reactivity swing'],1))
                bu.append(core_params['burnup'])
                pu_mass.append(round(core_params['pu mass'], 0))
        
            fig = px.scatter_3d(x=bu, y=rx_swing, z=cycle_length, color=pu_mass, labels={'x':'Burnup (GWd/MT)', 'y': 'Rx Swing (pcm/month)', 'z':'Cycle Length (days)','color':'Pu Mass (kg/cycle)'})
            fig.show()
            fig = px.scatter_3d(x=height, y=smear, z=pu_content, color=cycle_length, labels={'x':'Height (cm)', 'y': 'Smear', 'z':'Pu Content','color':'Cycle Length (days)'})
            fig.show()
            
    def send_executor(self):
        """Send an executor message to the triggered KA."""
        if self._ka_to_execute != (None, 0):
            self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self._ka_to_execute[0], self._ka_to_execute[1], self._trigger_event))
            self._new_entry = False
            self.send('executor_{}'.format(self._ka_to_execute[0]), self._ka_to_execute)
        else:
            self.log_info('No KA to execute, waiting to sends trigger again.')
            
    def wait_for_ka(self):
        """Write to H5 file and sleep while waiting for agents."""
        if len(self._kaar) % 25 == 0:
            self.write_to_h5()
            self.plot_progress()
            self.diagnostics_replace_agent()
        self.determine_complete()
        sleep_time=1
        while not self._new_entry: # Figure out a way to 'loopback' and determine if we have been written to
            time.sleep(1)
            sleep_time += 1
            if sleep_time > self._sleep_limit:
                break
        self._new_entry = False