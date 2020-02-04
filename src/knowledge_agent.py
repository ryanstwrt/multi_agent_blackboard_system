import osbrain
from osbrain import Agent
import run_sfr_opt_mabs
import pandas as pd
import h5py

class KaBase(Agent):
    """
    Base agent to define __init__ and basic functions
  
    Knowledge agents will inherit from base agent.
    
    Attributes:
      
      bb     (Agent)  - Reference to the blackboard agent
      entry  (dict)   - Dicitonary of knowledge agents parameters to be added to the blackboard
      rep_addr (addr) - Address of the socket for the request-reply communication between the blackboard and the agent. The agent will request permission to write to the blackboard and wait until a reply has been given.
      rep_alias (str)   - Alias for the sockect address in the request-reply communication. Allows d
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
        """Create a line of communiction through the reply request format"""
        if self.bb:
            self.rep_alias, self.rep_addr = self.bb.connect_REP_agent(self.name)
            self.connect(self.rep_addr, alias=self.rep_alias)
        else:
            print("Warning: Blackboard attribute not defined")
    
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
        
        #For proxy app
        self.weights = None
        
    def write_to_blackboard(self):
        """Write to abstract level three of the blackboard when the blackboard is not being written to."""
        self.send(self.rep_alias, 'message')
        write = False
        while write:
            write = self.bb.write_to_blackboard()
        else:
            self.recv(self.rep_alias)
            self.bb.add_abstract_lvl_3(self.core_name, self.rx_parameters, self.xs_set)
            self.bb.finish_writing_to_blackboard()
    
    def run_dakota_proxy(self):
        """Run Dakota using a single objective genetic algorithm, with the given weights"""
        self.weights = (0,0,0,0)
        run_sfr_opt_mabs.main(self.weights[0], self.weights[1], self.weights[2], self.weights[3])
        
    def read_dakota_results(self):
        """Read in the results from the Dakota H5 file, and turn this into the reactor paramters dataframe."""
        weight_sequence = '{}_{}_{}_{}'.format(self.weights[0], self.weights[1], self.weights[2], self.weights[3])
        self.core_name = 'core_{}'.format(weight_sequence)
        file = h5py.File('/Users/ryanstewart/projects/Dakota_Interface/GA/results/soo_pareto_{}.h5'.format(weight_sequence), 'r+')
        design_list = list(file['methods']['soga_{}'.format('0')]['results']['execution:1']['best_parameters']['discrete_real'])
        obj_list = file['methods']['soga_{}'.format('0')]['results']['execution:1']['best_objective_functions']
 
        keff = (1-obj_list[0]) * (1.29863-0.75794) + 0.75794
        void = (1-obj_list[1]) * (-254.8-(-42.4)) - 42.4
        dopp = (1-obj_list[2]) * (-1.192057-(-0.365144)) - 0.365144
        
        rx_params_dict = {self.core_name: {'height': design_list[0],
                                                        'smear': design_list[1],
                                                       'pu_content': design_list[2],
                                                       'keff': keff,
                                                       'void': void,
                                                       'Doppler': dopp}}
        self.rx_parameters = pd.DataFrame.from_dict(rx_params_dict, orient='index')
        