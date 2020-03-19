import osbrain
from osbrain import Agent
import run_sfr_opt_mabs
import h5py
import time
import os

from collections import OrderedDict

class KaBase(Agent):
    """
    Base agent to define __init__ and basic functions
  
    Knowledge agents will inherit from base agent.
    
    Attributes:
      
      bb     (Agent)  - Reference to the blackboard agent
      entry  (dict)   - Dicitonary of knowledge agents parameters to be added to the blackboard
      writer_addr (addr) - Address of the socket for the request-reply communication between the blackboard and the agent. 
                           The agent will request permission to write to the blackboard and wait until a reply has been given.
      writer_alias (str) - Alias for the sockect address in the request-reply communication for writting to the blackboard. 
                           Given in the form of `write_<name>`.
      executor_addr (addr) - Address of the socket for the push-pull communication between the blackboard and the agent for executing the trigger. 
                            If the agent has been selected, the blackboard will send an executor command to run their code.
      executor_alias (str) - Alias for the sockect address in the pull-push communication for executing the agent. 
                            Given in the form `executor <name>`.
      trigger_addr (addr) - Address of the socket for the push-pull communication between the blackboard and the agent for a trigger event. 
                            The blackboard sends out a request for triggers, if the agent is available, the agent replies with its trigger value.
      trigger_alias (str) - Alias for the sockect address in the pull-push communication for writting to the blackboard. Given in the form `executor <name>`.
      trigger_val (float) - value for the trigger to determine if it will be selected for execution.
                            The higher the trigger value, the higher the probability of being executed.
"""

    def on_init(self):
        """Initialize the knowledge agent"""
        self.bb = None
        self.bb_lvl = 0
        self.entry = None
        self.entry_name = None

        self.writer_addr = None
        self.writer_alias = None
        
        self.executor_addr = None
        self.executor_alias = None
        
        self.trigger_response_alias = 'trigger_response_{}'.format(self.name)
        self.trigger_response_addr = None
        self.trigger_publish_alias = None
        self.trigger_publish_addr = None
        self.trigger_val = 0
        
        
    def add_blackboard(self, blackboard):
        """Add a BB to to the KA, and update the BB's agent address dict.
        Ensures that updating the communication lines have a key to reference."""
        self.bb = blackboard
        bb_agent_addr = self.bb.get_attr('agent_addrs')
        bb_agent_addr[self.name] = {}
        self.bb.set_attr(agent_addrs=bb_agent_addr)

    def connect_executor(self):
        """Create a line of communication through the reply request format to allow writing to the blackboard."""
        if self.bb:
            self.executor_alias, self.executor_addr = self.bb.connect_executor(self.name)
            self.connect(self.executor_addr, alias=self.executor_alias, handler=self.handler_executor)
            self.log_info('Agent {} connected executor to BB'.format(self.name))
        else:
            self.log_warning('Warning: Agent {} not connected to blackboard agent'.format(self.name))

    def connect_trigger(self):
        """Create two lines of communication for the trigger.
        1. Create a push-pull for the KA to inform the BB of it's triger value (if it is available)
        2. Connect to the BB's publish-subscribe to be informed when trigger events are occuring."""
        if self.bb:
            self.trigger_response_addr = self.bind('PUSH', alias=self.trigger_response_alias)
            self.trigger_publish_alias, self.trigger_publish_addr = self.bb.connect_trigger((self.name, self.trigger_response_addr, self.trigger_response_alias))
            self.connect(self.trigger_publish_addr, alias=self.trigger_publish_alias, handler=self.handler_trigger_publish)

    def connect_writer(self):
        """Create a line of communiction through the reply-request format.
        This will allow for the KA to write to the BB when it can add to the problem."""
        if self.bb:
            self.writer_alias, self.writer_addr = self.bb.connect_writer(self.name)
            self.connect(self.writer_addr, alias=self.writer_alias)
            self.log_info('Agent {} connected writer to BB'.format(self.name))
        else:
            self.log_warning('Warning: Agent {} not connected to blackbaord agent'.format(self.name))

    def handler_executor(self, message):
        raise NotImplementedError

    def handler_trigger_publish(self, message):
        """Send a message to the BB indiciating it's trigger value."""
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self.trigger_val))
        self.send(self.trigger_response_alias, (self.name, self.trigger_val))
    
    def write_to_bb(self):
        """Write the KA's entry to the BB on the specified level."""
        self.log_debug('Sending writer trigger to BB.')
        write = False
        while not write:
            time.sleep(1)
            self.send(self.writer_alias, self.name)
            write = self.recv(self.writer_alias)
        else:
            self.log_debug('Writing to BB Level {}'.format(self.bb_lvl))
            self.bb.update_abstract_lvl(self.bb_lvl, self.entry_name, self.entry)