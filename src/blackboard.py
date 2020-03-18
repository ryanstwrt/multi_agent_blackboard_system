import osbrain
from osbrain import Agent
import pandas as pd
import train_surrogate_models as tm
import time
import h5py
import os
import numpy as np
import csv
import sys
import re
import copy

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
        abstract_lvls(nested dict): Dictionary of abstract levels on the blackboard. Each level will have their own corresponding data.
        agents (list): List of agents currently active in the multi-agent system.
    """
    def on_init(self):
        self.agent_addrs = {}
        self.agent_writing = False
        self.new_entry = False
        self.archive_name = '{}_archive.h5'.format(self.name)
        self.sleep_limit = 10
            
        self.abstract_lvls = {}
        self.abstract_lvls_format = {}
        
        self.ka_to_execute = (None, 0)
        self.trigger_event_num = 0
        self.trigger_events = {}
        self.pub_trigger_alias = 'trigger'
        self.pub_trigger_addr = self.bind('PUB', alias=self.pub_trigger_alias)
        
    def add_abstract_lvl(self, level, entry):
        """Add an abstract level for the blackboard.
        
        This creates a blank dictionary for the abstract level and a format requirement for the abstract level entry.
        entry is a dictionary whose keys are the names for items on the BB and values are the types of data that will be stored there. For example: {'entry 1': str, 'entry 2': int}.
        """
        self.abstract_lvls['level {}'.format(level)] = {}
        self.abstract_lvls_format['level {}'.format(level)] = entry

    def connect_executor(self, agent_name):
        alias_name = 'executor_{}'.format(agent_name)
        executor_addr = self.bind('PUSH', alias=alias_name)
        self.agent_addrs[agent_name].update({'executor': (alias_name, executor_addr)})
        return (alias_name, executor_addr)
        
    def connect_trigger(self, message):
        agent_name, response_addr, response_alias = message
        self.agent_addrs[agent_name].update({'trigger_response': (response_alias, response_addr)})
        self.connect(response_addr, alias=response_alias, handler=self.handler_trigger_response)
        return (self.pub_trigger_alias, self.pub_trigger_addr)
    
    def connect_writer(self, agent_name):
        """Connect the blackboard agent to a knolwedge agent for writing purposes"""
        alias_name = 'writer_{}'.format(agent_name)
        write_addr = self.bind('REP', alias=alias_name, handler=self.handler_writer)
        self.agent_addrs[agent_name].update({'writer': (alias_name, write_addr)})
        self.log_info('BB connected writer to {}'.format(agent_name))
        return (alias_name, write_addr)

    def controller(self):
        """
        Controls the which knowledge agent will be excuted for each trigger event.
        """
        self.log_info('Determining which KA to execute')
        self.ka_to_execute = (None, 0)
        for k,v in self.trigger_events[self.trigger_event_num].items():
            if v > self.ka_to_execute[1]:
                self.ka_to_execute = (k,v)

    def determine_h5_type(self, data_type, data_val):
        if data_type == str:
            return [np.string_(data_val)]
        elif data_type in (bool, int, float, tuple):
            return [data_val]
        elif data_type == list:
            return data_val
        elif data_type == dict:
            return data_val
        else:
            self.log_warning('Data {} was not a recongnized data type ({}), please add statment requiring how to store.'.format(data_name, data_type))
            return None
    
    def finish_writing_to_bb(self):
        """Update agent_writing to False when agent is finished writing"""
        self.agent_writing = False
        
    def handler_trigger_response(self, message):
        agent, trig_val = message
        self.log_debug('Logging trigger response ({}) for agent {}'.format(trig_val, agent))
        self.trigger_events[self.trigger_event_num].update({agent: trig_val})
        
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

    def publish_trigger(self):
        self.trigger_event_num += 1
        self.trigger_events[self.trigger_event_num] = {}
        self.send(self.pub_trigger_alias, 'publishing trigger')
        
    def send_executor(self):
        self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self.ka_to_execute[0], self.ka_to_execute[1], self.trigger_event_num))
        self.send('executor_{}'.format(self.ka_to_execute[0]), self.ka_to_execute)

    def str_to_data_types(self, string):
        """Convert a string to the appropriate data type class"""
        split_str = string.split(' ')
        re_str = re.findall('[a-z]', split_str[1])
        join_str = ''.join(re_str)
        return eval(join_str)
    
    def get_data_types(self, entry_data):
        """Determine the data types required for each H5 dataset.
        This is done by checking the attributes for each dataset and converting the string to a class via the str_to_data_types"""
        data_names = [x for x in entry_data.keys()]
        data_types = [self.str_to_data_types(x.attrs.get('type')) for x in entry_data.values()]
        data_dict = {data_names[i]: data_types[i] for i in range(len(data_names))}
        return data_dict
         
    def load_dataset(self, data_name, data, data_dict):
        """Load the H5 data sets to their appropriate format for the blackboard"""
        if data_dict[data_name] == list:
            return data_dict[data_name](data)
        elif data_dict[data_name] == dict:
            sub_data_dict = self.get_data_types(data)
            sub_dataset = {d_names: self.load_dataset(d_names, d, sub_data_dict) for d_names, d in data.items()}
            return sub_dataset
        elif data_dict[data_name] == str:
            return data[0].decode('UTF-8')
        else:
            return data_dict[data_name](data[0])
        
    def load_h5(self):
        """Load an H5 archive of the blackboard"""
        self.log_info("Loading H5 archive: {}".format(self.archive_name))
        h5 = h5py.File(self.archive_name, 'r')
        for level, entries in h5.items():
            for entry_name, entry in entries.items():  
                data_dict = self.get_data_types(entry)
                
                if not self.abstract_lvls.get(level, False):
                    sub_data_dict = {}
                    for data_name, data_type in data_dict.items():
                        sub_data_dict[data_name] = self.get_data_types(entry[data_name]) if data_type == dict else data_dict[data_name]
                    self.add_abstract_lvl(int(level.split(' ')[1]), sub_data_dict)
                temp_dict = {data_name: self.load_dataset(data_name, data, data_dict) for data_name, data in entry.items()}    
                self.update_abstract_lvl(int(level.split(' ')[1]), entry_name, temp_dict)
        h5.close()

    def remove_bb_entry(self, level, name):
        """Remove a BB entry on a given abstract level"""
        del self.abstract_lvls['level {}'.format(level)][name]
        self.log_debug('Removing entry {} from BB abstract level {}.'.format(name, level))
        self.finish_writing_to_bb()
        
    def update_abstract_lvl(self, level, name, entry):
        """Update an abstract level with new information from an entry"""
        lvl_name = 'level {}'.format(level)
        abstract_lvl = self.abstract_lvls[lvl_name]
        for entry_name, entry_type in entry.items():
            try:
                assert entry_name in self.abstract_lvls_format[lvl_name].keys()
                if type(entry_type) == dict:
                    a = {x: type(y) for x,y in entry_type.items()}
                    assert a == self.abstract_lvls_format[lvl_name][entry_name]
                else:
                    assert type(entry_type) == self.abstract_lvls_format[lvl_name][entry_name]
            except AssertionError:
                self.log_warning('Entry {} is inconsistent with level {}.\n Entry keys are: {} \n with value types: {}.\n Abstract level expected keys {}\n with value types {}.\n Entry was not added.'.format(name, level, entry.keys(), entry.values(), 
                self.abstract_lvls_format[lvl_name].keys(),
                self.abstract_lvls_format[lvl_name].values()))
                self.finish_writing_to_bb()
                return
        abstract_lvl[name] = entry
        self.finish_writing_to_bb()
        
    def wait_for_ka(self):
        """Function to performe while waiting for KAs to write to the blackboard."""
        sleep_time = 0
        if self.new_entry == False:
            self.write_to_h5()
        while not self.new_entry:
            time.sleep(1)
            sleep_time += 1
            if sleep_time > self.sleep_limit:
                break
        self.new_entry = False
                            
    def write_to_h5(self):
        """BB will convert data from abstract to H5 file.
        
        Root directory will have four sub dicrectories, one for each abstract level.
        Each abstract level will then have a number of subdirectories, bsed on what results are written to them.
        Each abstract is exampled below
        - level 1
          - entry 1
            - [1, 2 ,3]
            - True
        - level 2
          - entry 2
            - this_is_a_str
            - 3.1415
        """
        if not os.path.isfile(self.archive_name):
            self.log_info('Creating {}'.format(self.archive_name))
            h5 = h5py.File(self.archive_name, 'w')
            for level in self.abstract_lvls.keys():
                h5.create_group(level)
            h5.close()
            
        self.log_info("Writing blackboard to archive")
        h5 = h5py.File(self.archive_name, 'r+')
        for level, entry in self.abstract_lvls.items():
            group_level = h5[level]
            for name, data in entry.items():
                if name in group_level.keys():
                    pass
                else:
                    group_level.create_group(name)
                    for data_name, data_val in data.items():
                        data_type = type(data_val)
                        if data_type == dict:
                            group_level[name].create_group(data_name)
                            group_level[name][data_name].attrs['type'] = repr(data_type)
                            for k,v in data_val.items():
                                group_level[name][data_name][k] = self.determine_h5_type(type(v), v)
                                group_level[name][data_name][k].attrs['type'] = repr(type(v))
                        elif None:
                            pass
                        else:
                            group_level[name][data_name] = self.determine_h5_type(data_type, data_val)
                            group_level[name][data_name].attrs['type'] = repr(data_type)
        h5.close()