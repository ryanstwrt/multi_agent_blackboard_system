import osbrain
from osbrain import Agent
from osbrain import run_agent
from osbrain import proxy
import numpy as np
import time
import h5py
import os
import sys
import re
from osbrain import run_nameserver

class Blackboard(Agent):
    """
    This is a class for holding all information regardng the solutions to the problem.
    The blackboard class inherets from osBrain's agent class.
    This allows for communication between the blackbaord and the other varous knowledge agents.
    
    The blackboard  (BB) holds information from knowledge agents (KAs) on muultiple abstract levels.
    All information for abstract levels are stored in memory, in the form of nested dictionaries.
    Abstract levels must be created via the `add_abstract_lvl` method, and can be updated using the `update_abstract_lvl` or `remove_bb_entry`.
    
    
    Attributes:
        agent_addrs : list
            List of agents currently active in the multi-agent system, along with each line of communication that is currently set up.
        _new_entry : bool
            Toggle to determine if BB should be write to archive while it is waiting.
        archive_name : str
            Name of the hdf5 file that will store abstract levels long term.
        _sleep_limit : int
            Number of seconds to wait if it doesn't hear from an agent before it sends another trigger event.
        abstract_lvls : dict 
            Dictionary of abstract levels on the blackboard, which stores all data from KA.
        abstract_lvl_format : dict
            Dictionary of the abstract levels entry formt.
        _ka_to_execute : tuple (agent_name, trigger_value)
            Tuple containing the KA to trigger, and its associated trigger value.
        _trigger_event : int
            Counter for the number of trigger events that have occured.
        _kaar : dictionary
            Knoweldge Agent Activation Record - dictionary of trigger events, along with the agent `_ka_to_execute` for that trigger event to hold as a log.
        _pub_trigger_alias : str
            Alias to be used for the publish-subscribe channel of communication with agents.
        _pub_trigger_addr : str
            Address for the publish-subscribe channel to send to an agent when it connects.
        _shutdown_alias : str
            Alias for the shutdown request-reply channel.
    """
    def on_init(self):
        self.agent_addrs = {}
        self.required_agents = []
        self._proxy_server = proxy.NSProxy()
        self._agent_writing = False
        self._new_entry = False
        self.archive_name = '{}_archive.h5'.format(self.name)
        self._sleep_limit = 10
            
        self.abstract_lvls = {}
        self.abstract_lvls_format = {}
        
        self._ka_to_execute = (None, 0)
        self._trigger_event = 0
        self._kaar = {}
        self._pub_trigger_alias = 'trigger'
        self._pub_trigger_addr = self.bind('PUB', alias=self._pub_trigger_alias)
        
    def add_abstract_lvl(self, level, entry):
        """
        Add an abstract level to the blackboard.
        
        Parameters
        -----------
        level : int
            Abstract level to be added
        entry : dict
            Dictionary whose keys are the names of the items for the abstract level and values are the data types that will be stored there. 
            For example: {'entry 1': str, 'entry 2': int}.
        """
        self.abstract_lvls['level {}'.format(level)] = {}
        self.abstract_lvls_format['level {}'.format(level)] = entry

    def add_panel(self, level, panels):
        """
        Split a blackbaord abstract level into multiple panels.
        
        Parameters
        -----------
        level : int
            Abstract level to add a panel
        panels : list
            List of panel names
        """        
        lvl = {panel_name : {} for panel_name in panels}
        lvl_format = self.abstract_lvls_format['level {}'.format(level)]
        self.abstract_lvls_format['level {}'.format(level)] = {panel_name: lvl_format for panel_name in panels}
        self.abstract_lvls['level {}'.format(level)].update(lvl)
        
    def connect_executor(self, agent_name):
        """
        Connects the BB's executor communication with the KA.
        
        Parameters
        -----------
        agent_name : str
            Alias of the agent to connect.
        
        Returns
        -------
        alias_name : str
            Alias of the executor line of communication.
        alias_addr : str
            Address for the KA to connect to for communication.
        """
        alias_name = 'executor_{}'.format(agent_name)
        executor_addr = self.bind('PUSH', alias=alias_name)
        self.agent_addrs[agent_name].update({'executor': (alias_name, executor_addr)})
        return (alias_name, executor_addr)
    
    def connect_agent(self, agent_type, agent_alias):
        """
        Connect a KA to the blackboard.
        This connects the writer, trigger, executor, and shutdown handlers.
        This also connnects any specific attributes associated with an agent type.
        
        
        Parameters
        ----------
        agent_type : class
            KA class to allow for the run_agent method to build a proxy to the KA
        agent_alias : str
            Alias of the agent to allow for convenient calling
        """
        ka = run_agent(name=agent_alias, base=agent_type)
        ka.add_blackboard(self)
        ka.connect_writer()
        ka.connect_trigger()
        ka.connect_executor()
        ka.connect_shutdown()
        self.connect_ka_specific(agent_alias)
        self.agent_addrs[agent_alias].update({'class': agent_type})
        self.log_info('Connected agent {} of agent type {}'.format(agent_alias, agent_type))
        
    def connect_trigger(self, message):
        """
        Connects teh BB's trigger communication with the KA.
        
        Parameters
        ----------
        message : tupple (agent_name, response_addr, response_alias)
            agent_name : str
                Alias of the agent to connect.
            response_addr : str
                Address of the KA's trigger response line of communication tor BB to connect with.
            response_alias : str
                Alias of the KA's trigger response line of communication.
                
        Returns
        -------
        alias_name : str
            Alias of the executor line of communication.
        alias_addr : str
            Address for the KA to connect to for communication.        
        """
        agent_name, response_addr, response_alias = message
        self.agent_addrs[agent_name].update({'trigger_response': (response_alias, response_addr)})
        self.connect(response_addr, alias=response_alias, handler=self.handler_trigger_response)
        return (self._pub_trigger_alias, self._pub_trigger_addr)
    
    def connect_writer(self, agent_name):
        """
        Connects the KA's writter communication with the BB.
        
        Parameters
        -----------
        agent_name : str
            Alias of the agent to connect.
        
        Returns
        -------
        alias_name : str
            Alias of the writer line of communication.
        alias_addr : str
            Address for the KA to connect to for communication.
        """
        alias_name = 'writer_{}'.format(agent_name)
        write_addr = self.bind('REP', alias=alias_name, handler=self.handler_writer)
        self.agent_addrs[agent_name].update({'writer': (alias_name, write_addr)})
        return (alias_name, write_addr)
    
    def connect_shutdown(self, agent_name):
        """
        Connects the KA's shutdown communication with the BB
        
        Parameters:
        message : str
            Alias of the agent connecting
            
        Returns
        -------
        alias_name : str
            Alias of the shutdown line of communication.
        alias_addr : str
            Address for the KA to connect to for shutdown communication.
        """
        alias_name = 'shutdown_{}'.format(agent_name)
        shutdown_addr = self.bind('PUSH', alias=alias_name)        
        self.agent_addrs[agent_name].update({'shutdown': (alias_name, shutdown_addr)})
        return (alias_name, shutdown_addr)
    
    def connect_ka_specific(self, agent):
        """Holder for implementing and connect a specific knowledge agent."""
        pass
        
        
    def controller(self):
        """Determines which KA to select after a trigger event."""
        self.log_debug('Determining which KA to execute')
        self._ka_to_execute = (None, 0)
        for k,v in self._kaar[self._trigger_event].items():
            if v > self._ka_to_execute[1]:
                self._ka_to_execute = (k,v)                
    
    
    def diagnostics_agent_present(self, agent):
        """
        Diagnostics test to determine if the agent is still running.
        If the agent is running it returns true.
        If the agent does not exist or if the agent exists but is not running return false.
        
        Parameters
        ----------
        agent : str
            alias of the agent to check
        
        """
        try:
            ka = self._proxy_server.proxy(agent)
            if ka.get_attr('_running'):
                return True
            else:
                ka.kill()
                return False
        except:
            return False
    
    def diagnostics_replace_agent(self):
        """
        Dioagnostics test repalce an essential agent.
        If the agent is in the required_agents list, and the it is not present, the BB creates an instance of the agent.
        """
        for agent_name, addrs in self.agent_addrs.items():
            present = self.diagnostics_agent_present(agent_name)
            agent_type = addrs['class']
            if not present and agent_type in self.required_agents:
                self.log_info('Found agent ({}) of type {} not connect. Reconnecting agent.'.format(agent_name, agent_type))
                self.connect_agent(agent_type, agent_name)
                
    def determine_complete(self):
        """Holder for determining when a problem will be completed."""
        pass
                
    def determine_h5_type(self, data_type, data_val):
        """
        Converts a data value into an appropriate H5 format for storage.
        
        Parameters
        ----------
        data_type : class
            Class of data type.
        data_val : data_type
            Transforms the class of data into a useable formato for H5.
            
            
        Returns
        -------
        dava_val : varies
            Value of data in a H5 specific format (i.e. convert str to np.string_ and bool/int/float/tuple to a list)
        """
        if data_type == str:
            return [np.string_(data_val)]
        elif data_type in (bool, int, float, tuple):
            return [data_val]
        elif data_type == list:
            return data_val
        elif data_type == dict:
            return data_val
        else:
            self.log_warning('Data {} was not a recongnized data type ({}), please add statment requiring how to store it.'.format(data_name, data_type))
            return None

    def dict_writer(self, data_name, data_dict, group_level):
        """
        Recursively write dictionary results to the H5 file.
        
        Parameters:
        data_name : str
            name of the H5 group
        data_dict : dict
            dictionary of data that will be written to the H5 file
        group_level : HDF group
            group that will be accessed for placing the data from the dictionary
        """
        group_level.create_group(data_name)
        group_level[data_name].attrs['type'] = repr(type(data_dict))
        for k,v in data_dict.items():
            if type(v) == dict:
                self.dict_writer(k, v, group_level[data_name])
            elif None:
                pass
            else:
                group_level[data_name][k] = self.determine_h5_type(type(v), v)
                group_level[data_name][k].attrs['type'] = repr(type(v))
        
    def finish_writing_to_bb(self):
        """Update _agent_writing to False when agent is finished writing"""
        self._agent_writing = False
        self.log_debug('Finished writing to BB')
        
    def get_data_types(self, entry_data):
        """
        Determine the data types required for each H5 dataset.
        This is done by checking the attributes for each dataset and converting the string to a class via `str_to_data_types`.
        
        Parameters
        ----------
        entry_data : varies
            Data contained in an H5 group
        Returns
        -------
        data_dict : dict
            Dictionary of data to be added to the blackbaord
        """
        data_dict = {}
        for k,v in entry_data.items():
            type_ = self.str_to_data_types(v.attrs.get('type'))
            if type_ == dict:
                data_dict[k] = self.get_data_types(entry_data[k])
            else:
                data_dict[k] = type_
        return data_dict
         
    def handler_trigger_response(self, message):
        """
        Handler for KAs trigger response, stores all responses in `trigger_evemts`.
        
        Parameters
        ----------
        message: tuple (agent_name, trigger_val)
            agent_name : str
                Alias for the KA
            trigger_val : int
                Trigger value for the agent
        """
        agent_name, trig_val = message
        self.log_debug('Logging trigger response ({}) for agent {}.'.format(trig_val, agent_name))
        self._kaar[self._trigger_event].update({agent_name: trig_val})
        
    def handler_writer(self, message):
        """
        Handler to determine if it is acceptable for a KA to write to the blackboard
        
        Parameters
        ----------
        message : tuple (str, bool)
            str : Alias for the KA sending request
            bool : Boolean logic to determine if the KA is done writing to the BB
            
        Returns
        -------
        bool
            True if agent can write, false if agent must wait
        """
        agent_name, bb_lvl, entry_name, entry, complete, panel, remove = message
        self._new_entry = complete
        
        if not self._agent_writing:
            self._agent_writing = True
            self.log_debug('Agent {} given permission to write'.format(agent_name))
            if remove:
                self.log_debug('Removing BB Entry {} on BB Level {}, panel {}'.format(entry_name, bb_lvl, panel))
                self.remove_bb_entry(bb_lvl, entry_name, panel=panel)
            else:
                self.log_debug('Writing to BB Level {}'.format(bb_lvl))
                self.update_abstract_lvl(bb_lvl, entry_name, entry, panel=panel)
            self.finish_writing_to_bb()
            return True
        else:
            self._new_entry = False
            self.log_debug('Agent {} waiting to write'.format(agent_name))
            return False
       
    def load_dataset(self, data_name, data, data_dict):
        """
        Load the H5 data sets to their appropriate format for the blackboard
        
        Parameters
        ----------
        data_name : str
            name of data entry
        data : dict
            dictionary of data that has been pulled from the H5 file
            
        Returns
        -------
        data_dict : dict
            dictionary of data to be added to the blackboard
        """
        if data_dict[data_name] == list:
            return data_dict[data_name](data)
        elif type(data_dict[data_name]) == dict:
            sub_dataset = self.get_data_types(data)
            for d_names, d in data.items():
                sub_dataset[d_names] = self.load_dataset(d_names, d, data_dict[data_name])
            return sub_dataset
        elif data_dict[data_name] == str:
            return data[0].decode('UTF-8')
        else:
            return data_dict[data_name](data[0])

    def load_h5(self, panels={}):
        """
        Load an H5 archive of the blackboard
        Loops through each H5 group and pulls all of the data into a dictionary for the BB
        Determines data type based on group attribute
        """
        self.log_info("Loading H5 archive: {}".format(self.archive_name))
        h5 = h5py.File(self.archive_name, 'r')
        for level, level_entry in h5.items():
            lvl_num = int(level.split(' ')[1])
            for entry_name, entry in level_entry.items():
                if lvl_num in panels.keys():
                    if [x for x in entry.keys()] == [] and entry_name not in self.abstract_lvls[level]:
                        self.add_panel(lvl_num, [entry_name])
                    else:
                        for panel_entry_name, panel_entry in entry.items():
                            self.some_sub_class(lvl_num, panel_entry_name, panel_entry, panel=entry_name)
                else:
                    self.some_sub_class(lvl_num, entry_name, entry)
        h5.close()

    def some_sub_class(self, lvl_num, entry_name, entry, panel=False):
        data_dict = self.get_data_types(entry)
        if not self.abstract_lvls.get('level {}'.format(lvl_num), False):
            sub_data_dict = {}
            for data_name, data_type in data_dict.items():
                sub_data_dict[data_name] = self.get_data_types(entry[data_name]) if data_type == dict else data_dict[data_name]
            self.add_abstract_lvl(lvl_num, sub_data_dict)
        temp_dict = {data_name: self.load_dataset(data_name, data, data_dict) for data_name, data in entry.items()}
        if panel:
            if panel not in self.abstract_lvls['level {}'.format(lvl_num)].keys():
                self.add_panel(lvl_num, [panel])
            self.update_abstract_lvl(lvl_num, entry_name, temp_dict, panel=panel)        
        else:
            self.update_abstract_lvl(lvl_num, entry_name, temp_dict)        
        
    def publish_trigger(self):
        """Send a trigger event message to all KAs."""
        self._trigger_event += 1
        self.log_debug('\n\nPublishing Trigger Event {}'.format(self._trigger_event))
        self._kaar[self._trigger_event] = {}
        self.send(self._pub_trigger_alias, 'publishing trigger')

    def remove_bb_entry(self, level, name, panel=None):
        """
        Remove a BB entry on a given abstract level.
        
        Parameters
        ----------
        level : int
            Abstract level to access.
        name : str
            BB entry to remove from the abstract level.
        panel : str
            Panel name if present
        """
        if panel:
            del self.abstract_lvls['level {}'.format(level)][panel][name]
        else:
            del self.abstract_lvls['level {}'.format(level)][name]
        self.log_debug('Removing entry {} from BB abstract level {}.'.format(name, level))
        
    def send_executor(self):
        """Send an executor message to the triggered KA."""
        if self._ka_to_execute != (None, 0):
            self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self._ka_to_execute[0], self._ka_to_execute[1], self._trigger_event))
            self.send('executor_{}'.format(self._ka_to_execute[0]), self._ka_to_execute)
        else:
            self.log_info('No KA to execute, waiting to sends trigger again.')
            
    def str_to_data_types(self, string):
        """
        Evaluate a string to return the appropriate data type class
        
        Parameters
        ----------
        string : str
            string formation of a data type
        
        Returns
        -------
        join_str : class
            class of the evaluated data type 'string'
        """
        split_str = string.split(' ')
        re_str = re.findall('[a-z]', split_str[1])
        join_str = ''.join(re_str)
        return eval(join_str)
    
    def recursive_dict(self, dict_, lvl_format):
        """
        Allows the use of nested dicts in the abstract levels
        
        Parameters
        ----------
        dict_ : dict
            dictionary of abstract level
        lvl_format :
            expected data format for the BB level
            
        Returns
        -------
        formatted_dict : dict
            dictionary of data for the blackboard
        """
        formatted_dict = {}
        for x,y in dict_.items():
            if type(y) == dict:
                formatted_dict[x] = self.recursive_dict(y, lvl_format[x])
            else:
                formatted_dict[x] = type(y)
                try:
                    assert type(y) == lvl_format
                except (TypeError, AssertionError):
                    assert type(y) == lvl_format[x]
        return formatted_dict
            
    def update_abstract_lvl(self, level, name, entry, panel=None):
        """
        Update an abstract level with a new entry
        
        Parameters
        ----------
        level : int
            Abstract level to access.
        name : str
            Name of the entry
        entry : dict
            Data to be added to the abstract level (must be in format associated with `level`)
        panel : bool
            boolean logic to determine if we are writing to a panel on an abstract level
        """
        lvl_name = 'level {}'.format(level)
        if not panel:
            abstract_lvl = self.abstract_lvls[lvl_name]
            lvl_format = self.abstract_lvls_format[lvl_name]
        else:
            abstract_lvl = self.abstract_lvls[lvl_name][panel]
            lvl_format = self.abstract_lvls_format[lvl_name][panel]
        for entry_name, entry_type in entry.items():
            try:
                assert entry_name in lvl_format.keys()
                if type(entry_type) == dict:                        
                    a = self.recursive_dict(entry_type, lvl_format[entry_name])
                else:
                    assert type(entry_type) == lvl_format[entry_name]
            except AssertionError:
                self.log_warning('Entry {} is inconsistent with level {}.\n Entry keys are: {} \n with value types: {}.\n Abstract level expected keys: {}\n with value types: {}.\n Entry was not added.'.format(name, level, entry.keys(), entry.values(), lvl_format.keys(), lvl_format.values()))
                self.finish_writing_to_bb()
                return
        
        abstract_lvl[name] = entry
        
    def wait_for_ka(self):
        """Write to H5 file and sleep while waiting for agents."""
        sleep_time = 0
        if self._new_entry == False and len(self._kaar) % 10 == 0:
            self.write_to_h5()
        while not self._new_entry:
            time.sleep(1)
            sleep_time += 1
            if sleep_time > self._sleep_limit:
                break
        self._new_entry = False
                            
    def write_to_h5(self):
        """BB will convert data from abstract levels to H5 file.
        
        Root directory will have a sub dicrectory for each abstract level.
        Each abstract level will then have a number of subdirectories, based on what results are written to them.
        Below is an exampled.
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
                            self.dict_writer(data_name, data_val, group_level[name])
                        elif None:
                            pass
                        else:
                            group_level[name][data_name] = self.determine_h5_type(data_type, data_val)
                            group_level[name][data_name].attrs['type'] = repr(data_type)
        self.log_info("Finished writing to archive")
        h5.close()
