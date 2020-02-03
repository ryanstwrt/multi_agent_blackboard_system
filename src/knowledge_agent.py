import osbrain
from osbrain import Agent

class KaBase(Agent):
    """
    Base agent to define __init__ and basic functions
  
    Knowledge agents will inherit from base agent.
    
    Attributes:
      
      bb    (Agent) - Reference to the blackboard agent
      entry (dict)  - Dicitonary of knowledge agents parameters to be added to the blackbaord
    """

    def on_init(self):
        """Initialize the knowledge agent"""
        self.bb = None
        self.entry = None
        
    def add_blackboard(self, blackboard):
        """Add a blackboard to the knowledge agent"""
        self.bb = blackboard

    def write_to_blackboard(self):
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
        
    def write_to_blackboard(self):
        #self.bb.add_abstract_lvl_3()
        pass
    
    def run_dakota(self):
        pass