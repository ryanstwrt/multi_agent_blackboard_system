import osbrain
from osbrain import Agent
from osbrain import run_agent
from osbrain import proxy
from osbrain import run_nameserver
import blackboard
import time
import bb_sfr_opt


# Can the controller keep track of the BB levels and update the trigger values of different agents as needed?

class Controller(object):
    """The controller object wraps around the blackboard system to control when and how agents interact with the blackboard. 
    
    The controller sets up the problem by creating instances of the blackboard, which in turn creates an instance of the knowledge agents upon initialization."""
    
    def __init__(self, bb_name='bb', bb_type=blackboard.Blackboard, ka={}, objectives=None, design_variables=None, archive='bb_archive', agent_wait_time=30, plot_progress=False):
        self.bb_name = bb_name
        self.bb_type = bb_type
        self.agent_wait_time = agent_wait_time
        self.ns = run_nameserver()
        self.bb = run_agent(name=self.bb_name, base=self.bb_type)
        self.bb.set_attr(archive_name='{}.h5'.format(archive))
        self.plot_progress = plot_progress

        if bb_type == bb_sfr_opt.BbSfrOpt:
            self.bb.initialize_abstract_level_3(objectives=objectives, design_variables=design_variables)
            self.bb.set_attr(_sm='gpr')
            self.bb.generate_sm()
        
        for ka_name, ka_type in ka.items():
            self.bb.connect_agent(ka_type, ka_name)
            
            
    def run_single_agent_bb(self):
        """Run a BB optimization problem single-agent mode."""
        
        while not self.bb.get_attr('_complete'):
            self.bb.publish_trigger()
            trig_num = self.bb.get_attr('_trigger_event')
            responses = False
            # Wait until all responses have been recieved
            while not responses:
                time.sleep(0.1)
                if len(self.bb.get_attr('_kaar')[trig_num]) == len(self.bb.get_attr('agent_addrs')):
                    responses = True
            self.bb.controller()
            self.bb.set_attr(_new_entry=False)
            self.bb.send_executor()
            # TODO Keep track of how long each agent takes to run, increase the agents TV based on how long it takes
            agent_wait = 0
            while self.bb.get_attr('_new_entry') == False:
                time.sleep(0.1)
                agent_wait += 0.1
                if agent_wait > self.agent_wait_time:
                    break
            self.bb.determine_complete()
            if len(self.bb.get_attr('_kaar')) % 50 == 0 or self.bb.get_attr('_complete') == True:
                self.bb.write_to_h5()
                if self.plot_progress:
                    self.bb.plot_progress()
                self.bb.diagnostics_replace_agent()
                
    def update_ka_trigger_val(self, ka):
        """
        Update a knowledge agents trigger value.
        
        If BB has too many entries on a abstract level, the KA trigger value gets increased by 1.
        If the BB has few entries on the abstract level, the KA trigger value is reduced by 1.
        """
        current_val = ka.get_attr('_trigger_val')
        ka.set_attr(_trigger_val=current_val+1)