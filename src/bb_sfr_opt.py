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


cur_dir = os.path.dirname(__file__)
test_path = os.path.join(cur_dir, '../test/')

class BbTraditional(blackboard.Blackboard):
    
    def on_init(self):
        super().on_init()
        self._complete = False
        
    def connect_ka_specific(self, agent):
        """Connect a KA to the BB"""
        ns = proxy.NSProxy()
        ka = ns.proxy(agent)
        if 'rp' in agent:
            ka.set_attr(interp_path=test_path)
            ka.create_sm()
        elif 'br' in agent:
            ka.set_attr(desired_results={'keff': (1.0, 1.2), 'void': (-200, -75), 'doppler': (-1.0,-0.6), 'pu_content': (0, 1.0)})                               
        else:
            self.log_info('Agent type ({}) does not match a known agent type.'.format(agent))
            return
        
    def determine_complete(self):
        """
        Determine when the problem has finished to send the shutdown communication.
        Complete for the traditional system is determined if a solution has been placed in abstract level 1 on the blackboard.
        """
        if self.abstract_lvls['level 1'] != {}:
            self.log_info('Problem complete, shutting agents down')
            time.sleep(5)
            for agent_name, connections in self.agent_addrs.items():
                self.send(connections['shutdown'][0], "shutdown")
            self._complete = True
        else:
            pass
    
    def wait_for_ka(self):
        """Write to H5 file and sleep while waiting for agents."""
        if self._new_entry == False and len(self._kaar) % 10 == 0:
            self.write_to_h5()
        self.determine_complete()
        

class BbSfrOpt(BbTraditional):
    
    def on_init(self):
        super().on_init()
        self.add_abstract_lvl(1, {'pareto type': str})
        self.add_panel(1, ['new', 'old'])       
        self.add_abstract_lvl(2, {'valid': bool})
        self.add_panel(2, ['new', 'old'])
        self.add_abstract_lvl(3, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'cycle length': float, 'reactivity swing': float, 'burnup': float, 'pu mass': float }})
        self.add_panel(3, ['new','old'])
        # Add panel for level 3
        
        self.objectives = ['cycle length', 'reactivity swing', 'burnup', 'pu mass']
        self.objective_ranges = {'cycle length': (0, 1500), 'reactivity swing': (0, 7500), 'burnup': (0,175), 'pu mass': (0, 1750)}
        self.objective_goals = {'cycle length': 'gt', 'reactivity swing': 'lt', 'burnup': 'gt', 'pu mass': 'lt'}
        self.independent_variable_ranges = {'height': (50, 80), 'smear': (50,70), 'pu_content': (0,1)}
        
        self._sm = None
        self.sm_type = 'interpolate'
        
    def determine_complete(self):
        """
        Determine when the problem has finished to send the shutdown communication.
        Complete for the traditional system is determined  when a set number of solutions has been placed on abstract level 1 on the blackboard.
        """
        pareto_solutions = 0
        for panel in self.abstract_lvls['level 1'].values():
            for core in panel.values():
                pareto_solutions += 1 if core['pareto type'] == 'pareto' else 0
        
        if pareto_solutions > 2:
            self.log_info('Problem complete, shutting agents down')
            for agent_name, connections in self.agent_addrs.items():
                self.send(connections['shutdown'][0], "shutdown")
            self._complete = True
        else:
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
        if 'rp' in agent:
            ka.set_attr(objectives=self.objectives)
            #ka.create_sm()
            ka.set_attr(_sm=self._sm)
            ka.set_attr(sm_type=self.sm_type)
        elif 'lvl3' in agent:
            ka.set_attr(desired_results=self.objective_ranges)
        elif 'lvl2' in agent:
            ka.set_attr(desired_results=self.objective_goals)
        else:
            self.log_info('Agent type ({}) does not match a known agent type.'.format(agent))
            return
    
    def generate_sm(self):
        design_var, objective_func = dg.get_data([x for x in self.independent_variable_ranges.keys()], self.objectives)
        if self.sm_type == 'interpolate':
            self._sm = {}
            design_var, objective_func = np.asarray(design_var), np.asarray(objective_func)
            for num, objective in enumerate(self.objectives):
                self._sm[objective] = scipy.interpolate.LinearNDInterpolator(design_var, objective_func[:,num])
        else:
            self._sm = tm.Surrogate_Models()
            self._sm.random = 0
            self._sm.update_database(design_var, objective_func)
            self._sm.optimize_model(self.sm_type)        