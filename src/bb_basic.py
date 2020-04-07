import blackboard
import ka_rp as karp
import ka_br as kabr
import osbrain
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
        
    def connect_agent(self, agent_type, agent_alias):
        """Connect a KA to the BB"""
        if agent_type == 'rp':
            ka = run_agent(name=agent_alias, base=karp.KaRp_verify)
            ka.set_attr(interp_path=test_path)
            ka.create_interpolator()
        elif agent_type == 'br':
            ka = run_agent(name=agent_alias, base=kabr.KaBr_verify)
            ka.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 1.0)})
        else:
            self.log_info('Agent type ({}) does not match a known agent type.'.format(agent_type))
            return
        ka.add_blackboard(self)
        ka.connect_writer()
        ka.connect_trigger()
        ka.connect_executor()
        ka.connect_shutdown()
        self.log_info('Connected agent {} of agent type {}'.format(agent_alias, agent_type))
        
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