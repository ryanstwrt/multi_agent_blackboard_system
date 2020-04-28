import blackboard
import ka_rp as karp
import ka_br as kabr
import osbrain
from osbrain import proxy
from osbrain import run_agent
import time
import os 
import glob

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
#        self.add_panel(1, ['new', 'old'])       
        self.add_abstract_lvl(2, {'valid': bool})
#        self.add_panel(2, ['new', 'old'])
        self.add_abstract_lvl(3, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'cycle length': float, 'reactivity swing': float, 'burnup': float, 'pu mass': float }})

    def determine_complete(self):
        if len(self.abstract_lvls['level 1']) > 10:
            self.log_info('Problem complete, shutting agents down')
            for agent_name, connections in self.agent_addrs.items():
                self.send(connections['shutdown'][0], "shutdown")
            self._complete = True
        else:
            pass
    
    def handler_writer(self, message):
        """
        Handler to determine if it is acceptable for a KA to write to the blackboard
        
        Parameters
        ----------
        message : str
            Alias for the KA sending request
            
        Returns
        -------
        bool
            True if agent can write, false if agent must wait
        """
        agent_name, self._new_entry = message if type(message) == list else (message, True)
            
        if not self._agent_writing:
            self._agent_writing = True
            self.log_info('Agent {} given permission to write'.format(agent_name))
            return True
        else:
            self.log_info('Agent {} waiting to write'.format(agent_name))
            return False
    
    def connect_ka_specific(self, agent):
<<<<<<< HEAD
        ns = proxy.NSProxy()
        ka = ns.proxy(agent)
        if 'rp' in agent:
            ka.set_attr(objectives=['cycle length', 'reactivity swing', 'burnup', 'pu mass'])
            ka.create_sm()
        elif 'lvl3' in agent:
            ka.set_attr(desired_results={'cycle length': (0, 1000), 'reactivity swing': (0, 7500), 'burnup': (0,200), 'pu mass': (0, 1000)})
        elif 'lvl2' in agent:
            ka.set_attr(desired_results={'cycle length': 'gt', 'reactivity swing': 'lt', 'burnup': 'gt', 'pu mass': 'lt'})
        else:
            self.log_info('Agent type ({}) does not match a known agent type.'.format(agent))
            return