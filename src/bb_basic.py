import blackboard
import ka_rp as karp
import ka_br as kabr
import osbrain
from osbrain import proxy
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
            ka.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 1.0)})                               
        else:
            self.log_info('Agent type ({}) does not match a known agent type.'.format(agent_type))
            return
        
    def determine_complete(self):
        if self.abstract_lvls['level 1'] != {}:
            self.log_info('Problem complete, shutting agents down')
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
    
    def connect_ka_specific(self, agent):
        """Connect a KA to the BB"""
        if 'explore' in agent:
            pass
        elif 'exploit' in agent:
            pass
        elif 'lvl3' in agent:
            ka = run_agent(name=agent_alias, base=KABR.KaBr_lvl3)
            ka.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 1.0)})
        elif 'lvl2' in agent:
            ka = run_agent(name=agent_alias, base=KABR.KaBr_lvl2)
            ka.set_attr(desired_results={'keff': 'gt', 'void_coeff': 'lt', 'pu_content': 'lt'})
        else:
            self.log_info('Agent type ({}) does not match a known agent type.'.format(agent_type))
            return