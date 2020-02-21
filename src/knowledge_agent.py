import osbrain
from osbrain import Agent
import run_sfr_opt_mabs
import pandas as pd
import h5py
import time
import math

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
        
        self.trigger_val = 0
        
    def add_blackboard(self, blackboard):
        """Add a blackboard to the knowledge agent"""
        self.bb = blackboard
        bb_agent_adders = self.bb.get_attr('agent_addrs')
        bb_agent_adders[self.name] = {}
        self.bb.set_attr(agent_addrs=bb_agent_adders)

    def connect_writer(self):
        """Create a line of communiction through the reply request format to allow writing to the blackboard."""
        if self.bb:
            self.rep_alias, self.rep_addr = self.bb.connect_writer(self.name)
            self.connect(self.rep_addr, alias=self.rep_alias)
        else:
            self.log_info("Warning: Blackboard attribute not defined")
    
    def write_to_bb(self):
        """Basic function for writing to the blackboard"""
        raise NotImplementedError
    
    def connect_trigger_event(self):
        """Create a line of communiction through the publish-subscribe format to determine if it is triggered."""
        if self.bb:
            self.trigger_alias, self.trigger_addr = self.bb.connect_trigger_event(self.name)
            self.connect(self.trigger_addr, alias=self.trigger_alias, handler=self.trigger_handler)
        else:
            self.log_warning('Warning: Agent {} not connected to blackbaord agent'.format(self.name))
    
    def trigger_handler(self, message):
        """Inform the BB of it's trigger value."""
        self.send(self.trigger_alias, (self.name, self.trigger_val), handler=self.log_trigger_handler)    
    
    def log_trigger_handler(self, poxy_obj, unk):
        "Mandatory handler for publication trigger event"
        self.log_info('{} triggered'.format(self.name))

class KaBbLvl2(KaBase):
    """
    Knowledge agent who examines the blackboard and determines if a solution should be move from abastract level 3 to abstract level 2.
    
    Inherits from KaBase
    
    Attributes:
    
    """
    
    def on_init(self):
        super().on_init()
        
    
    def write_to_bb(self):
        write = False
        while not write:
            time.sleep(1)
            self.send(self.rep_alias, self.name)
            write = self.recv(self.rep_alias)
        else:
            self.read_bb_lvl_2()
    
    def read_bb_lvl_2(self):
        pass

class KaBbLvl2_Proxy(KaBbLvl2):
    """Proxy for KA to examine weights for a given blackboard entry."""

    def on_init(self):
        super().on_init()
        self.desired_results = {'keff': 1.0303, 'void': -110.023, 'Doppler': -0.6926, 'pu_content': 0.5475}
        self.best_weights = {}  
        self.err = 100
        self.ind_err = {}

    def read_bb_lvl_2(self):
        lvl_3 = self.bb.get_attr('lvl_3')
        best_core = None
        for k,v in lvl_3.items():
            ind_err = self.get_percent_errors(k, v['reactor_parameters'])
            tot_err = sum(ind_err.values())
            if tot_err < self.err:
                self.err = tot_err
                self.ind_err = ind_err
                self.best_weights = {'w_keff': v['reactor_parameters']['w_keff'][k],
                                     'w_void': v['reactor_parameters']['w_void'][k],
                                     'w_dopp': v['reactor_parameters']['w_dopp'][k],
                                     'w_pu': v['reactor_parameters']['w_pu'][k]}
                best_core = k
        self.bb.add_abstract_lvl_2(best_core, self.best_weights, True)

    def get_percent_errors(self, core, rx_params):
        """Return the percent error for each objective function"""
        ind_err = {}
        for k,v in self.desired_results.items():
            ind_err[k] = abs((v - rx_params[k][core])/v)
        return ind_err
            
        

class KaReactorPhysics(KaBase):
    """
    Knowledge agent to solve portions reactor physics problems using Dakota & Mammoth
    
    Inherets from KaBase.
    
    Attibutes:
    
      core_name        (str)             - Name of the core
      rx_parameters    (dataframe)       - Pandas dataframe containing reactor core parameters from Mammoth
      surrogate_models (SurrogateModels) - SurrogateModels class from surrogate_modeling, containes a set of trained surogate mdoels
      objectives       (list)            - List of the desired objective functions to be examined
      design_variables (list)            - List of the design variables to be used
      results_path     (str)             - Path to the desired location for printing results
      weight           (tuple)           - Weights for the associated objectives, these will be optimized in an attempt to find a solution which resembles physical programming
    """
    def on_init(self):
        super().on_init()
        self.trigger_val = 1.0
        self.core_name = None
        self.xs_set = None
        self.rx_parameters = None
        self.surrogate_models = None

    def write_to_bb(self):
        """Write to abstract level three of the blackboard when the blackboard is not being written to.
        Force the KA to wait 1 second between sending message"""
        write = False
        while not write:
            time.sleep(1)
            self.send(self.rep_alias, self.name)
            write = self.recv(self.rep_alias)
        else:
            self.bb.add_abstract_lvl_3(self.core_name, self.rx_parameters, self.xs_set)

class KaReactorPhysics_Proxy(KaReactorPhysics):
    """
    Knowledge agent to solve portions reactor physics problems using Dakota & Mammoth
    
    Inherets from KaBase.
    
    Attibutes:
    
      core_name        (str)             - Name of the core
      rx_parameters    (dataframe)       - Pandas dataframe containing reactor core parameters from Mammoth
      surrogate_models (SurrogateModels) - SurrogateModels class from surrogate_modeling, containes a set of trained surogate mdoels
      objectives       (list)            - List of the desired objective functions to be examined
      design_variables (list)            - List of the design variables to be used
      results_path     (str)             - Path to the desired location for printing results
      weight           (tuple)           - Weights for the associated objectives, these will be optimized in an attempt to find a solution which resembles physical programming
    """

    def on_init(self):
        super().on_init()
        self.objectives = None
        self.design_variables = None
        self.results_path = None
        self.function_evals = 500
        
        #For proxy app
        self.weights = None
    
    def run_dakota_proxy(self):
        """Run Dakota using a single objective genetic algorithm, with the given weights"""
        try:
            assert len(self.weights) == len(self.objectives)
            run_sfr_opt_mabs.run_dakota(self.weights, self.design_variables, self.objectives, self.function_evals)
        except AssertionError:
            self.log_error('Error: The number of weights ({}) does not match the number of objectives ({}). Make sure these match, as each objective must have a weight.'.format(len(self.weights), len(self.objectives)))
            
    def read_dakota_results(self):
        """Read in the results from the Dakota H5 file, and turn this into the reactor paramters dataframe."""
        ws_int = '{}{}{}{}'.format(self.weights[0], self.weights[1], self.weights[2], self.weights[3])

        self.core_name = 'core_{}'.format(ws_int)
        file = h5py.File('{}/soo_pareto_{}.h5'.format(self.results_path,ws_int), 'r+')
        results_dir = file['methods']['soga_{}'.format(ws_int)]['results']['execution:1']
        design_list = list(results_dir['best_parameters']['discrete_real'])
        obj_list = results_dir['best_objective_functions']
 
        keff = (1-obj_list[0]) * (1.29863-0.75794) + 0.75794
        void = (1-obj_list[1]) * (-254.8-(-42.4)) - 42.4
        dopp = (1-obj_list[2]) * (-1.192057-(-0.365144)) - 0.365144
        
        rx_params_dict = {self.core_name: {'height': design_list[0],
                                           'smear': design_list[1],
                                           'pu_content': design_list[2],
                                           'keff': keff,
                                           'void': void,
                                           'Doppler': dopp,
                                           'w_keff': self.weights[0],
                                           'w_void': self.weights[1],
                                           'w_dopp': self.weights[2],
                                           'w_pu': self.weights[3]}}
        self.rx_parameters = pd.DataFrame.from_dict(rx_params_dict, orient='index')        