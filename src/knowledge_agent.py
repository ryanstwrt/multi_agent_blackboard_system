import osbrain
from osbrain import Agent
import run_sfr_opt_mabs
import pandas as pd
import h5py
import time
import math
import random
import os
import csv
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
      execute_addr (addr) - Address of the socket for the push-pull communication between the blackboard and the agent for executing the trigger. 
                            If the agent has been selected, the blackboard will send an execute command to run their code.
      execute_alias (str) - Alias for the sockect address in the pull-push communication for executing the agent. 
                            Given in the form `execute <name>`.
      trigger_addr (addr) - Address of the socket for the push-pull communication between the blackboard and the agent for a trigger event. 
                            The blackboard sends out a request for triggers, if the agent is available, the agent replies with its trigger value.
      trigger_alias (str) - Alias for the sockect address in the pull-push communication for writting to the blackboard. Given in the form `execute <name>`.
      trigger_val (float) - value for the trigger to determine if it will be selected for execution.
                            The higher the trigger value, the higher the probability of being executed.

"""

    def on_init(self):
        """Initialize the knowledge agent"""
        self.bb = None
        self.entry = None
        self.writer_addr = None
        self.writer_alias = None
        self.execute_addr = None
        self.execute_alias = None
        
        self.trigger_response_alias = 'trigger_response_{}'.format(self.name)
        self.trigger_response_addr = None
        self.trigger_publish_alias = None
        self.trigger_publish_addr = None
        self.trigger_val = 0
        
        try:
            if self.debug:
                self._DEBUG = True
        except AttributeError:
            pass
        
    def add_blackboard(self, blackboard):
        """Add a blackboard to the knowledge agent"""
        self.bb = blackboard
        bb_agent_addr = self.bb.get_attr('agent_addrs')
        bb_agent_addr[self.name] = {}
        self.bb.set_attr(agent_addrs=bb_agent_addr)

    def connect_writer(self):
        """Create a line of communiction through the reply request format to allow writing to the blackboard."""
        if self.bb:
            self.writer_alias, self.writer_addr = self.bb.connect_writer(self.name)
            self.connect(self.writer_addr, alias=self.writer_alias)
            self.log_debug('Agent {} connected writer to BB'.format(self.name))
        else:
            self.log_warning('Warning: Agent {} not connected to blackbaord agent'.format(self.name))

    def connect_execute(self):
        """Create a line of communication through the reply request format to allow writing to the blackboard."""
        if self.bb:
            self.execute_alias, self.execute_addr = self.bb.connect_execute(self.name)
            self.connect(self.execute_addr, alias=self.execute_alias, handler=self.handler_execute)
            self.log_debug('Agent {} connected execute to BB'.format(self.name))
        else:
            self.log_warning('Warning: Agent {} not connected to blackboard agent'.format(self.name))

    def connect_trigger(self):
        if self.bb:
            self.trigger_response_addr = self.bind('PUSH', alias=self.trigger_response_alias)
            self.trigger_publish_alias, self.trigger_publish_addr = self.bb.connect_trigger((self.name, self.trigger_response_addr, self.trigger_response_alias))
            self.connect(self.trigger_publish_addr, alias=self.trigger_publish_alias, handler=self.handler_trigger_publish)
    
    def handler_trigger_publish(self, message):
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self.trigger_val))
        self.send(self.trigger_response_alias, (self.name, self.trigger_val))
    
    def write_to_bb(self):
        raise NotImplementedError

    def handler_execute(self):
        raise NotImplementedError
        
class KaBbLvl2(KaBase):
    """
    Knowledge agent who examines the blackboard and determines if a solution should be move from abastract level 3 to abstract level 2.
    
    Inherits from KaBase
    
    Attributes:
    
    """
    
    def on_init(self):
        super().on_init()
        self.best_core = None 
        self.desired_error = 0.10
    
    def write_to_bb(self):
        self.log_debug('Attempting to write to blackboard')
        write = False
        while not write:
            time.sleep(1)
            self.send(self.writer_alias, self.name)
            write = self.recv(self.writer_alias)
        else:
            if self.best_core != None:
                self.bb.add_abstract_lvl_2(self.best_core, self.best_weights, True)
            else:
                self.bb.finish_writing_to_bb()
    
    def read_bb_lvl_2(self):
        pass

    def handler_trigger_publish(self, message):
        """Inform the BB of it's trigger value."""
        if self.bb.get_attr('trigger_event_num') % 10 == 0 and self.bb.get_attr('trigger_event_num') != 0:
            self.trigger_val = 2
        else:
            self.trigger_val = 0
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self.trigger_val))
        self.send(self.trigger_response_alias, (self.name, self.trigger_val)) 

class KaBbLvl2_verify(KaBbLvl2):
    """verify for KA to examine weights for a given blackboard entry."""

    def on_init(self):
        super().on_init()
        self.desired_results = {'keff': 1.0303, 'void': -110.023, 'Doppler': -0.6926, 'pu_content': 0.5475}
        self.best_weights = {}  
        self.err = 100
        self.best_core = None
        self.ind_err = {}

    def handler_trigger_publish(self, message):
        """Inform the BB of it's trigger value, determined if there is a value that should be transfered to Level 2"""
        self.read_bb_lvl_2()
        if self.best_core:
            self.trigger_val = 10
        else:
            self.trigger_val = 0
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self.trigger_val))
        self.send(self.trigger_response_alias, (self.name, self.trigger_val)) 
        
        
    def handler_execute(self, message):
        self.log_info('Executing agent {}'.format(self.name))
        self.read_bb_lvl_2(ideal=True)
        self.write_to_bb()

    def read_bb_lvl_2(self, ideal=False):
        """Read the information from the blackboard and determine if a new solution is better thatn the previous"""
        lvl_3 = self.bb.get_attr('lvl_3')
        best_core = None
        for k,v in lvl_3.items():
            ind_err = self.get_percent_errors(k, v['reactor_parameters'])
            tot_err = round(sum(ind_err),3)
            self.log_debug(k)
            self.log_debug('Height: {}, smear: {}'.format(round(v['reactor_parameters']['height'][k],2),
                                                         round(v['reactor_parameters']['smear'][k],2)))
            self.log_debug('keff: {}, void: {}, doppler: {}, pu: {}'.format(round(v['reactor_parameters']['keff'][k],5),
                                                                           round(v['reactor_parameters']['void'][k],2),
                                                                           round(v['reactor_parameters']['Doppler'][k],5),
                                                                           round(v['reactor_parameters']['pu_content'][k],4)))
            self.log_info('Core: {}, Solutions Errors: {}, Total Error: {}'.format(k, ind_err, tot_err))
            if ideal:
                self.write_to_csv(k, ind_err, tot_err, v['reactor_parameters'])
            if tot_err < self.err and tot_err < self.desired_error:
                self.err = tot_err
                self.ind_err = ind_err
                self.best_weights = {'w_keff': v['reactor_parameters']['w_keff'][k],
                                     'w_void': v['reactor_parameters']['w_void'][k],
                                     'w_dopp': v['reactor_parameters']['w_dopp'][k],
                                     'w_pu':   v['reactor_parameters']['w_pu'][k]}
                self.best_core = k

    def get_percent_errors(self, core, rx_params):
        """Return the percent error for each objective function"""
        pcm_core = (rx_params['keff'][core]-1.0)/(rx_params['keff'][core])*10E5
        pcm_given = (self.desired_results['keff']-1.0)/self.desired_results['keff']*10E5
        keff_error = abs(round((pcm_core-pcm_given)/pcm_given,4))
        void_error = abs(round((rx_params['void'][core]-self.desired_results['void'])/self.desired_results['void'],4))
        dopp_error = abs(round((rx_params['Doppler'][core]-self.desired_results['Doppler'])/self.desired_results['Doppler'],4))
        pu_error = abs(round((rx_params['pu_content'][core]-self.desired_results['pu_content'])/self.desired_results['pu_content'],4))

        return [keff_error, void_error, dopp_error, pu_error]

    def write_to_csv(self, core, ind_err, tot_err, rx_params):
        """Write Error to CSV"""
        if not os.path.isfile('core_error.csv'):    
            with open('core_error.csv', 'w+', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(['core_name', 'total', 'keff', 'void', 'doppler', 'pu', 'keff', 'void', 'doppler', 'pu'])
                writer.writerow([core, tot_err, ind_err[0], ind_err[1], ind_err[2], ind_err[3], round(rx_params['keff'][core],5),
                                                                           round(rx_params['void'][core],2),
                                                                           round(rx_params['Doppler'][core],5),
                                                                           round(rx_params['pu_content'][core],4)])
        else:
            with open('core_error.csv', 'a') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow([core, tot_err, ind_err[0], ind_err[1], ind_err[2], ind_err[3], round(rx_params['keff'][core],5),
                                                                           round(rx_params['void'][core],2),
                                                                           round(rx_params['Doppler'][core],5),
                                                                           round(rx_params['pu_content'][core],4)])

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
        self.log_debug('Attempting to write to blackboard')
        write = False
        while not write:
            time.sleep(1)
            self.send(self.writer_alias, self.name, wait=0.5, on_error='failed')
            write = self.recv(self.writer_alias)
        else:
            self.log_debug('Writing to blackboard')
            self.bb.add_abstract_lvl_3(self.core_name, self.rx_parameters, self.xs_set)

class KaReactorPhysics_verify(KaReactorPhysics):
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
        
        #For verify app
        self.weights = None
        self.desired_results = OrderedDict({'keff': 1.0303, 'void': -110.023, 'Doppler': -0.6926, 'pu_content': 0.5475})

    def handler_execute(self, sm):
        """Handler for when blackboard sends an execution signal to reactor physics knowledge agent. Requires agent to run Dakota, read the results, and write the results to the blackboard."""
        self.surrogate_models = sm
        self.log_info('Executing agent {}'.format(self.name))
        self.calc_weights()
        try:
            assert len(self.weights) == len(self.objectives)
            self.run_dakota_verify()
            self.read_dakota_results()
            self.write_to_bb()
            
        except AssertionError:
            self.log_error('Error: The number of weights ({}) does not match the number of objectives ({}). Make sure these match, as each objective must have a weight.'.format(len(self.weights), len(self.objectives)))
    
    def calc_weights(self):
        """Calculate the weights for the next Dakota run"""
        if self.surrogate_models:
            self.log_debug('Calculating weights via surrogate model')
            model = 'ann'
            des = [[x for x in self.desired_results.values()]]
            test_weights = self.surrogate_models.predict(model, des)
            test_weights = [abs(round(x,2)) for x in test_weights[0]]
            self.log_debug('Guessed Weights: {}'.format(test_weights))
            if sum(test_weights) < 4:
                self.weights = test_weights
            else:
                self.weights = [round(random.random(),2) for i in range(len(self.objectives))]
                self.log_info('Test weights too high ({}), using random weights instead ({})'.format(test_weights, self.weights))
        else:
            self.weights = [round(random.random(),2) for i in range(len(self.objectives))]
            self.log_debug('Calculated weights via random assignment, weights are {}'.format(self.weights))

    
    def run_dakota_verify(self):
        """Run Dakota using the SFR optimzation scheme"""
        self.log_debug('Running Dakota for SFR Optimization')
        """Run Dakota using a single objective genetic algorithm, with the given weights"""
        run_sfr_opt_mabs.run_dakota(self.weights, self.design_variables, self.objectives, self.function_evals)

            
    def read_dakota_results(self):
        """Read in the results from the Dakota H5 file, and turn this into the reactor paramters dataframe."""
        self.log_debug('Reading Dakota H5 output.')
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