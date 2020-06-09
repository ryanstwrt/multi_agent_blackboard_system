import osbrain
from osbrain import Agent
from osbrain import run_agent
from osbrain import proxy
from osbrain import run_nameserver()



# Can the controller keep track of the BB levels and update the trigger values of different agents as needed?

class controller(Object):
    """The controller object wraps around the blackboard system to control when and how agents interact with the blackboard. 
    
    The controller sets up the problem by creating instances of the blackboard, which in turn creates an instance of the knowledge agents upon initialization."""
    
    def init(self, bb={}, ka={}, archive_name='bb_archive', agent_wait_time=30):
        self.bb_name = bb.keys()
        self.bb_type = bb.values()
        self.agent_wait_time = agent_wait_time
        ns = run_nameserver()
        self.bb = run_agent(name=self.bb_name, base=self.bb_type)
        
        for ka_name, ka_type in ka.items():
            self.bb.connect_agent(ka_type, ka_name)
            
            
    def run_single_agent_bb_problem(self):
        """Run a BB optimization problem single-agent mode."""
        
        while self.bb.get_attr('_complete'):
            self.bb.publish_trigger()
            # Can we add another while statement and have the BB sleep until it gets all triggers back?
            time.sleep(1.0)
            self.bb.controller()
            self.bb.send_executor()
            # Some type of dynamic sleeping until triggered agent starts execution?
            time.sleep(1.0)
            agent_wait = 0
            while self.bb.get_attr('_new_entry') == False:
                time.sleep(1.0)
                agent_wait += 1
                if agent_wait > self.agent_wait_time:
                    break
            self.bb.determine_complete()
            if len(bb.get_attr('_kaar')) % 50 == 0 or self.bb.get_attr('_complete') == True:
                self.bb.write_to_h5()
                self.bb.plot_progress()
                self.bb.diagnostices_replace_agent()
                
    def update_ka_trigger_val(self, ka):
        """
        Update a knowledge agents trigger value.
        
        If BB has too many entries on a abstract level, the KA trigger value gets increased by 1.
        If the BB has few entries on the abstract level, the KA trigger value is reduced by 1.
        """
        current_val = ka.get_attr('_trigger_val')
        ka.set_attr(_trigger_val=current_val+1)