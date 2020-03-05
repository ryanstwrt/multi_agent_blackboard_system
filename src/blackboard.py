import osbrain
from osbrain import Agent
import pandas as pd
import train_surrogate_models as tm
import time
import h5py
import os
import numpy as np
import csv

class Blackboard(Agent):
    """
    This is a class for holding all information regardng the solutions to the problem.
    The blackboard class inherets from osBrain's agent class.
    This allows for communication between the blackbaord and the other varous knowledge agents.
    
    The blackboard holds information on four different abstract levels (described below).
    All information for abstract levels are stored in memory.
    Abstract levels 3 and 4 are also stored in an H5 file to maintain data between runs, and allow for restart of a proble should failure arise.
    
    It is noted here that a 'get' function is added for each of the attributes associated with the blackboard.
    For the agent class, each agent is assigned a proxy, and as such, internal variables are hidden and not accessible.
    The 'get' function allows other agents to access these attributes when necessary, wihtout using the `get_attr` function built into osBrain's Agent class.
    
    Attributes:
        lvl_1 (dict): Dictionary of entries for the level 1 abstract level.
                      Takes the form of nested dict: {core_name: {exp_num: (a,b,c), validated: Bool, Pareto: Bool}}
        lvl_2 (dict): Dictionary of entries for the level 2 abstract level.
                      Takes the form of nested dict: {core_name: {exp_num: (a,b,c), valid_core: Bool}}
        lvl_3 (dict): Dictionary of entries for the level 3 abstract level.
                      Takes the form of nested dict: {core_name: {reactor_parameters: DataFrame, xc_set: str}}
        lvl_4 (dict): Dictionary of entires for the level 4 abstract level.
                      Takes the form of a dict: {name: xc_set (file?)}
        trained_models (class): Reference to train_surrogate_model module, which contains multiple models to choose frome.
        agents (list): List of agents currently active in the multi-agent system.
    """
    def on_init(self):
        self.agents = []
        self.trained_models = None
        self.agent_addrs = {}
        self.agent_writing = False
        self.new_entry = False
        self.blackboard_name = None
        
        self.lvl_1 = {}
        self.lvl_2 = {}
        self.lvl_3 = {}
        self.lvl_4 = {}
        self.abstract_levels = {'level 1': self.lvl_1, 'level 2': self.lvl_2, 'level 3': self.lvl_3, 'level 4': self.lvl_4}

        self.ka_to_execute = (None, 0)
        self.trigger_event_num = 0
        self.trigger_events = {}
        self.pub_trigger_alias = 'trigger'
        self.pub_trigger_addr = self.bind('PUB', alias=self.pub_trigger_alias)
        
        self.initialize_h5_file()
        
    def add_abstract_lvl_1(self, name, exp_nums, validated=False, pareto=False):
        "Add an entry for abstract level 1"
        self.lvl_1[name] = {'exp_num': exp_nums, 'validated': validated, 'pareto': pareto}
        self.finish_writing_to_bb()

    def add_abstract_lvl_2(self, name, exp_nums, valid):
        "Add an entry for abstract level 2"
        self.lvl_2[name] = {'exp_num': exp_nums, 'valid_core': valid}
        self.finish_writing_to_bb()
    
    def add_abstract_lvl_3(self, name, params, xs_set):
        "Add an entry for abstract level 3"
        self.lvl_3[name] = {'reactor_parameters': params, 'xs_set': xs_set}
        self.finish_writing_to_bb()

    def add_abstract_lvl_4(self, name, file):
        "Add an entry for abstract level 4"
        self.lvl_4[name] = {'xs_set': file}        
        self.finish_writing_to_bb()
    
    def get_abstract_lvl(self, level):
        if level in self.abstract_levels:
            return self.abstract_levels[level]
        else:
            self.log_warning("Warning: Abstract {} does not exist.".format(level))
            return None
    
    def connect_writer(self, agent_name):
        """Connect the blackboard agent to a knolwedge agent for writing purposes"""
        alias_name = 'write_{}'.format(agent_name)
        write_addr = self.bind('REP', alias=alias_name, handler=self.handler_writer)
        self.agent_addrs[agent_name].update({'writer': (alias_name, write_addr)})
        self.log_info('BB connected writer to {}'.format(agent_name))
        return (alias_name, write_addr)

    def handler_writer(self, agent_name):
        """Determine if it is acceptable to write to the blackboard"""
        if not self.agent_writing:
            self.agent_writing = True
            self.new_entry = True
            self.log_info('Agent {} given permission to write'.format(agent_name))
            return True
        else:
            self.log_info('Agent {} waiting to write'.format(agent_name))
            return False

    def connect_trigger(self, message):
        agent_name, response_addr, response_alias = message
        self.agent_addrs[agent_name].update({'trigger_response': (response_alias, response_addr)})
        self.connect(response_addr, alias=response_alias, handler=self.handler_trigger_response)
        return (self.pub_trigger_alias, self.pub_trigger_addr)

    def publish_trigger(self):
        self.trigger_event_num += 1
        self.trigger_events[self.trigger_event_num] = {}
        self.send(self.pub_trigger_alias, 'publishing trigger')

    def handler_trigger_response(self, message):
        agent, trig_val = message
        self.log_debug('Logging trigger response ({}) for agent {}'.format(trig_val, agent))
        self.trigger_events[self.trigger_event_num].update({agent: trig_val})
        
    def connect_execute(self, agent_name):
        alias_name = 'execute_{}'.format(agent_name)
        execute_addr = self.bind('PUSH', alias=alias_name)
        self.agent_addrs[agent_name].update({'execute': (alias_name, execute_addr)})
        return (alias_name, execute_addr)

    def send_execute(self):
        self.log_info('Selecting agent {} (trigger value: {}) to execute (Trigger Event: {})'.format(self.ka_to_execute[0], self.ka_to_execute[1], self.trigger_event_num))
        if 'rp' in self.ka_to_execute[0]:
            self.send('execute_{}'.format(self.ka_to_execute[0]), self.trained_models)
        else:
            self.send('execute_{}'.format(self.ka_to_execute[0]), self.ka_to_execute)
            
    def finish_writing_to_bb(self):
        """Update agent_writing to False when agent is finished writing"""
        self.agent_writing = False

    def get_agents(self):
        return self.agents
   
    def get_trained_models(self):
        return self.trained_models
                
    def update_abstract_lvl_1(self, name, updated_params):
        "Update an entry for abstract level 1"
        for k,v in updated_params.items():
            self.lvl_1[name][k] = v

    def update_abstract_lvl_2(self, name, updated_params):
        "Update an entry for abstract level 2 "
        #TODO: Make sure we update this level if Serpent tells us the core is not valid
        for k,v in updated_params.items():
            self.lvl_2[name][k] = v
    
    def update_abstract_lvl_3(self, name, updated_params):
        "Update an entry for abstract level 3 "
        for k,v in updated_params.items():
            self.lvl_3[name][k] = v

    def update_abstract_lvl_4(self, name, updated_params):
        "Update an entry for abstract level 4"
        for k,v in updated_params.items():
            self.lvl_4[name][k] = v
        
    def build_surrogate_models_proxy(self):
        """
        Proxy function for building surrogate models.
        
        Currently surrogate models are built off of H5 database of SFR core optimization. 
        """
        self.log_info('BB building surrogate models')
        sm = tm.Surrogate_Models()
        sm.random = 0
        des = []
        obj = []
        for k,v in self.lvl_3.items():
            base = v['reactor_parameters']
            des.append([base['w_keff'][k],base['w_void'][k],base['w_dopp'][k],base['w_pu'][k]])
            obj.append([base['keff'][k],base['void'][k],base['Doppler'][k],base['pu_content'][k]])
        sm.update_database(obj, des)
        model = 'lr'
        sm.update_model(model)
#        sm.optimize_model(model)
        self.trained_models = sm
        self.write_to_csv()
        self.log_info('Trained SM: {} wtih MSE: {}'.format(model, sm.models[model]['mse_score']))
        self.log_debug('BB finished building surrogate models')

    def write_to_csv(self):
        """Write surrogate model MSE to blackboard"""
        if not os.path.isfile('sm.csv'):    
            with open('sm.csv', 'w+', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow(['trigger number', 'MSE Score'])
                writer.writerow([self.trigger_event_num, self.trained_models.models['lr']['mse_score']])
        else:
            with open('sm.csv', 'a') as file:
                writer = csv.writer(file, delimiter=',')
                writer.writerow([self.trigger_event_num, self.trained_models.models['lr']['mse_score']])
            
        
    def controller(self):
        """
        Controls the which knowledge agent will be excuted for each trigger event.
        """
        self.log_info('Determining which KA to execute')
        self.ka_to_execute = (None, 0)
        for k,v in self.trigger_events[self.trigger_event_num].items():
            if v > self.ka_to_execute[1]:
                self.ka_to_execute = (k,v)

    def wait_for_ka(self):
        """Function to performe while waiting for KAs to write to the blackboard."""
        if self.new_entry == False:
            self.write_to_h5()
        if len(self.lvl_3.keys()) > 10:
            self.build_surrogate_models_proxy()
        while not self.new_entry:
            time.sleep(1)
        self.new_entry = False

    def initialize_h5_file(self):
        """Initilize and begin filling the H5 file"""
        if not os.path.isfile('{}_archive.h5'.format(self.name)):
            h5 = h5py.File('{}_archive.h5'.format(self.name), 'w')
            for level in self.abstract_levels.keys():
                h5.create_group(level)
            h5.close()
                
    def write_to_h5(self):
        """BB will convert data from abstract to H5 file.
        
        Root directory will have four sub dicrectories, one for each abstract level.
        Each abstract level will then have a number of subdirectories, bsed on what results are written to them.
        Each abstract is exampled below
        - Lvl_1
          - core_name
            - exp_num
            - validated
            - pareto
        - Lvl_2
          - core_name
            - exp_num
            - valid_core
        - Lvl_3
          - core_name
            - rx_parameters
            - xs_set
        """
        self.log_info("Writing blackboard to archive")
        h5 = h5py.File('{}_archive.h5'.format(self.name), 'r+')
        for level, entry in self.abstract_levels.items():
            group_level = h5[level]
            for name, data in entry.items():
                if name in group_level.keys():
                    pass
                else:
                    group_level.create_group(name)
                    for data_name, data_val in data.items():
                        if type(data_val) == str:
                            group_level[name][data_name] = [np.string_(data_val)]
                        elif type(data_val) == bool:
                            group_level[name][data_name] = [data_val]
                        elif type(data_val) == tuple:
                            group_level[name][data_name] = data_val
                        else:
                            group_level[name].create_group(data_name)
                            for k,v in data_val.items():
                                group_level[name][data_name][k] = v
        h5.close()