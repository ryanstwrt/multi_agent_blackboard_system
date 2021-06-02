from osbrain import Agent

class KaBase(Agent):
    """
    Base agent to define __init__ and basic functions
  
    Knowledge agents will inherit from base agent.
    
    Attributes
    ----------
        bb : Agent
            Reference to the blackboard agent
        _entry : dict
            Dicitonary of knowledge agents parameters to be added to the blackboard
        _entry_name : str
            Entry name.
        _writer_addr : str
            Socket address for the request-reply writer communication between the BB. 
        _writer_alias : str
            Alias for the sockect address in the writer communication for the BB. Given in the form of `write_<name>`.
        _executor_addr : str
            Socket address for the push-pull executor communication between the BB. 
        _executor_alias : str
            Alias for the sockect address in the executor communication for the BB. Given in the form `executor_<name>`.
        _trigger_response_addr : str
            Socket address for the push-pull trigger communication for the BB.
        _trigger_response_alias : str
            Alias for the socket address in the trigger communication for the BB. Given in the form `trigger_response_<name>`.
        _trigger_publish_alias : str
            Alias for the socket address in the trigger communication with the BB. Takes the form `trigger`.
        _trigger_publish_addr : str
            Socket address for the publish-subscribe trigger communication for the BB.
        _trigger_val : int 
            Value for the trigger to determine if it will be selected for execution.
        _shutdown_addr : str
            Socket address for the request-reply shutdown communication between the BB.
        _shutdown_alias : str
            Alias for the socket address in the shutdown communication. Takes the form `shutdown`.
"""

    def on_init(self):
        """Initialize the knowledge agent"""
        self.bb = None
        self.bb_lvl = 0
        self._entry = None
        self._entry_name = None
        self._writer_addr = None
        self._writer_alias = None
        self._executor_addr = None
        self._executor_alias = None
        self._trigger_response_alias = 'trigger_response_{}'.format(self.name)
        self._complete_alias = 'complete_{}'.format(self.name)
        self._complete_addr = None
        self._trigger_response_addr = None
        self._trigger_publish_alias = None
        self._trigger_publish_addr = None
        self._trigger_val = 0
        self._class = 'base'
        self.kill_switch = False
        
        self._shutdown_addr = None
        self._shutdown_alias = None
        
    def add_blackboard(self, blackboard):
        """
        Add a BB to to the KA, and update the BB's agent address dict.
        Ensures that updating the communication lines have a key to reference.
        
        Parameters
        ----------
        blackboard : Agent
            Reference for the BB
        """
        self.bb = blackboard
        bb_agent_addr = self.bb.get_attr('agent_addrs')
        bb_agent_addr[self.name] = {}
        self.bb.set_attr(agent_addrs=bb_agent_addr)
    
    def connect_complete(self):
        """Create a push-pull communication channel to execute KA."""
        if self.bb:
            self._complete_addr = self.bind('PUSH', alias=self._complete_alias)
            self.bb.connect_complete((self.name, self._complete_addr, self._complete_alias))
            self.log_debug('Agent {} connected complete to BB'.format(self.name))
        else:
            self.log_warning('Warning: Agent {} not connected to blackboard agent'.format(self.name))        

    def connect_executor(self):
        """Create a push-pull communication channel to execute KA."""
        if self.bb:
            self._executor_alias, self._executor_addr = self.bb.connect_executor(self.name)
            self.connect(self._executor_addr, alias=self._executor_alias, handler=self.handler_executor)
            self.log_debug('Agent {} connected executor to BB'.format(self.name))
        else:
            self.log_warning('Warning: Agent {} not connected to blackboard agent'.format(self.name))
            
    def connect_shutdown(self):
        """Creates a reply-requst communication channel for the KA to be shutdown by the BB"""
        if self.bb:
            self._shutdown_alias, self._shutdown_addr = self.bb.connect_shutdown(self.name)
            self.connect(self._shutdown_addr, alias=self._shutdown_alias, handler=self.handler_shutdown)
            self.log_debug('Agent {} connected shutdown to BB'.format(self.name))
        else:
            self.log_warning('Warning: Agent {} not connected to blackboard agent'.format(self.name))

    def connect_trigger(self):
        """
        Create two lines of communication for the trigger.
        1. Create a push-pull for the KA to inform the BB of it's triger value (if it is available)
        2. Connect to the BB's publish-subscribe to be informed when trigger events are occuring.
        """
        if self.bb:
            self._trigger_response_addr = self.bind('PUSH', alias=self._trigger_response_alias)
            self._trigger_publish_alias, self._trigger_publish_addr = self.bb.connect_trigger((self.name, self._trigger_response_addr, self._trigger_response_alias))
            self.connect(self._trigger_publish_addr, alias=self._trigger_publish_alias, handler=self.handler_trigger_publish)
        else:
            self.log_warning('Warning: Agent {} not connected to blackboard agent'.format(self.name))

    def connect_writer(self):
        """Create a reply-request communication channel for KA to write to BB."""
        if self.bb:
            self._writer_alias, self._writer_addr = self.bb.connect_writer(self.name)
            self.connect(self._writer_addr, alias=self._writer_alias)
            self.log_debug('Agent {} connected writer to BB'.format(self.name))
        else:
            self.log_warning('Warning: Agent {} not connected to blackboard agent'.format(self.name))
            
    def handler_shutdown(self, message):
        """
        Shutdown the KA.
        
        Parameter
        ---------
        message : str
            message sent by BB 
        """
        self.log_info('Agent {} shutting down'.format(self.name))
        self.kill_switch = True
        self.shutdown()
            
    def handler_executor(self, message):
        """
        Executor handler, not implemented for base KA
        Each Ka will have a unique executor
        """
        raise NotImplementedError

    def handler_trigger_publish(self, message):
        """
        Send a message to the BB indiciating it's trigger value.
        
        Parameters
        ----------
        message : str
            Containts unused message, but required for agent communication.
        """
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
    
    def action_complete(self):
        """
        Send a message to the BB indicating it's completed its action
        """
        self.send(self._complete_alias, (self.name))
    
    def move_entry(self, bb_lvl, entry_name, entry, new_panel, old_panel):
        """
        Move an entry on a blackboard level from one blackbaord panel to another.
        
        Parameters
        ----------
        bb_lvl : int
            Abstract level of the entry to be move
        entry_name : str
            Name of the entry to be moved
        entry : varies
            Entry detail for the entry to be moved
        new_panel : str
            Panel to move the entry to
        old_panel : str
            Panel that will remove old entry
        """
        self.write_to_bb(bb_lvl, entry_name, entry, panel=new_panel)
        self.write_to_bb(bb_lvl, entry_name, entry, panel=old_panel, remove=True)
        
    def write_to_bb(self, bb_lvl, entry_name, entry, panel=None, remove=False):
        """
        Write the KA's entry to the BB on the specified level.
        
        Parameters
        ----------
        bb_lvl : int
            Abstract level for writing to
        complete : bool
            Used to determine if the KA is done writing to the BB
        panel : str
            Used to allow the KA to write to a specific panel
        remove : Bool
            Used to determine if the entry needs to be removed from the BB
        """
        self.log_debug('Sending writer trigger to BB.')
        write = False
        while not write:
            bb_data = (self.name, bb_lvl, entry_name, entry, panel, remove)
            self.send(self._writer_alias, (bb_data))
            write = self.recv(self._writer_alias)