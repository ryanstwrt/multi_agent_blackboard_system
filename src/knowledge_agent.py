import osbrain
from osbrain import Agent

def writer(agent, message):
    return 'Received ' + str(message)

class KaBase(Agent):
    """
    Base agent to define __init__ and basic functions
  
    Knowledge agents will inherit from base agent.
    
    Attributes:
      
      bb     (Agent) - Reference to the blackboard agent
      entry  (dict)  - Dicitonary of knowledge agents parameters to be added to the blackbaord
      rep_bb (addr)  - Address of the socket for the request-reply communication between the blackboard and the agent. The agent will request permission to write to the blackboard and wait until a reply has been given.
    """

    def on_init(self):
        """Initialize the knowledge agent"""
        self.bb = None
        self.entry = None
        self.rep_addr = None
        self.rep_alias = None
        
    def add_blackboard(self, blackboard):
        """Add a blackboard to the knowledge agent"""
        self.bb = blackboard

    def connect_REP_blackboard(self):
        if self.bb:
            self.rep_alias, self.rep_addr = self.bb.connect_REP_agent(self.name)
            self.connect(self.rep_addr, alias=self.rep_alias)
        else:
            print("Warning: Blackboard attribute not defined")
    
    def write_to_blackboard(self):
        pass
        
    def _write_to_blackboard(self):
        """Basic function for writing to the blackboard"""
        raise NotImplementedError
        
class KaReactorPhysics(KaBase):
    """
    Knowledge agent to solve portions reactor physics problems using Dakota & Mammoth
    
    Inherets from KaBase.
    
    Attibutes:
    
      core_name       (str)            - Name of the core
      xs_set          (str)            - File name of the xml cross-section set used
      rx_parameters   (dataframe)      - Pandas dataframe containing reactor core parameters from Mammoth
      surroage_models (SurroageModels) - SurrogaeModels class from surrogate_modeling, containes a set of trained surogate mdoels 
    """

    def on_init(self):
        super().on_init()
        self.core_name = None
        self.xs_set = None
        self.rx_parameters = None
        self.surrogate_models = None
        
    def _write_to_blackboard(self):
        #self.bb.add_abstract_lvl_3()
        pass
    
    def run_dakota(self):
        pass