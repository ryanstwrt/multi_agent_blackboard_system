import osbrain
from osbrain import Agent
from osbrain import run_agent
from osbrain import proxy
import numpy as np
import h5py
import os
import re

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
        _panels : dict
            Dictionary with level numbers as keys and list of panel names as values.
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
        self.write_h5 = True
        self._panels = {}
        self._sub_bbs = {}
        self.agent_list = []        
        
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
        Update _panels to keep track of them
        
        Parameters
        -----------
        level : int
            Abstract level to add a panel
        panels : list
            List of panel names
        """        
        lvl = {panel_name : {} for panel_name in panels}
        self._panels['level {}'.format(level)] = [x for x in panels]
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
    
    def connect_agent(self, agent_type, agent_alias, attr={}):
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
        ka.connect_complete()
        self.connect_ka_specific(agent_alias, attr=attr)
        self.agent_addrs[agent_alias].update({'class': agent_type, 'performing action': False, '_class': ka.get_attr('_class')})
        self.agent_list.append(agent_alias)
        self.log_info('Connected agent {} of agent type {}'.format(agent_alias, agent_type))

    def connect_complete(self, message):
        """
        Connects the BB's compelte communication with the KA.
        
        Parameters
        ----------
        message : tupple (agent_name, complete_addr, complete_alias)
            agent_name : str
                Alias of the agent to connect.
            complete_addr : str
                Address of the KA's trigger complete line of communication tor BB to connect with.
            complete_alias : str
                Alias of the KA's trigger complete line of communication.       
        """
        agent_name, complete_addr, complete_alias = message
        self.agent_addrs[agent_name].update({'complete': (complete_alias, complete_addr)})
        self.connect(complete_addr, alias=complete_alias, handler=self.handler_agent_complete)
        
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
    
    def connect_ka_specific(self, agent, attr={}):
        """Holder for implementing and connect a specific knowledge agent."""
        ...

    def connect_sub_blackboard(self, name, bb_type):
        """
        Add a sub blackboard for a multi-tiered optimization problem
        """
        sub_bb = run_agent(name=name,base=bb_type)
        sub_bb.set_attr(archive_name='{}.h5'.format(name))
        self._sub_bbs[name] = sub_bb
    
    def controller(self):
        """Determines which KA to select after a trigger event."""
        self.log_debug('Determining which KA to execute')
        self._ka_to_execute = (None, 0)
        for k,v in self._kaar[self._trigger_event].items():
            if v > self._ka_to_execute[1]:
                self._ka_to_execute = (k,v)                
    
    def controller_update_kaar(self, trig_num, time):
        """Update the _kaar with the time required to run this KA"""
        self._kaar[trig_num].update({'time': (self._ka_to_execute[0], time)})
    
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
                self.log_info('Agent {} found non-responsive, killing agent.'.format(agent))
                return False
        except:
            self.log_info('Found no agent named {}'.format(agent))
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
                
    def convert_to_h5_type(self, data_type, data_val):
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
            if type(data_val[0]) == str:
                data_val == [np._string(x) for x in data_val]
            return data_val
        elif data_type == dict:
            return data_val
        else:
            self.log_warning('Data {} was not a recongnized data type ({}), please add statment requiring how to store it.'.format(data_val, data_type))
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
            elif type(v) == list:
                group_level[data_name][k] = [self.convert_to_h5_type(type(x), x) for x in v]
                group_level[data_name][k].attrs['type'] = repr(type(v))
            else:
                group_level[data_name][k] = self.convert_to_h5_type(type(v), v)
                group_level[data_name][k].attrs['type'] = repr(type(v))
        
    def finish_writing_to_bb(self):
        """Update _agent_writing to False when agent is finished writing"""
        self._agent_writing = False
        self.log_debug('Finished writing to BB')
        
    def get_blackboard(self):
        """
        Returns the current state of the blackboard
        """
        return self.abstract_lvls
    
    def get_current_trigger_value(self):
        """
        Returns the current trigger event
        """
        return self._trigger_event
    
    def get_kaar(self):
        """
        Get the KAAR
        """
        return self._kaar
    
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
         
    def handler_agent_complete(self, agent_name):
        """
        Handler for KAs complete response, i.e. when a KA has finished their action
        
        Parameters
        ----------
        agent_name : str
            Alias for the KA
        """
        self._new_entry = True
        self.log_debug('Logging agent {} complete.'.format(agent_name))
        self.agent_addrs[agent_name].update({'performing action':False})
        
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
        agent_name, bb_lvl, entry_name, entry, panel, remove = message
        
        if not self._agent_writing:
            self._agent_writing = True
            if remove:
                self.log_debug('Removing BB Entry {} on BB Level {}, panel {}'.format(entry_name, bb_lvl, panel))
                self.remove_bb_entry(bb_lvl, entry_name, panel=panel)
            else:
                self.log_debug('Writing to BB Level {}'.format(bb_lvl))
                self.update_abstract_lvl(bb_lvl, entry_name, entry, panel=panel)
            self.finish_writing_to_bb()
            return True
        else:
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
            data_list = data_dict[data_name](data)
            if len(data_list[0]) == 1:
                temp = [np.ndarray.tolist(x) for x in data_list]
                return [item for sublist in temp for item in sublist]
            else:
                return [np.ndarray.tolist(x) for x in data_list]

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
        self._panels = {'level {}'.format(lvl): names for lvl, names in panels.items()}
        self.log_info("Loading H5 archive: {}".format(self.archive_name))
        h5 = h5py.File(self.archive_name, 'r')
        for level, level_entry in h5.items():
            lvl_num = int(level.split(' ')[1])
            for entry_name, entry in level_entry.items():
                if lvl_num in panels.keys():
                    for panel_entry_name, panel_entry in entry.items():
                        self.load_h5_add_group(lvl_num, panel_entry_name, panel_entry, panel=entry_name)
                else:
                    self.load_h5_add_group(lvl_num, entry_name, entry)
        h5.close()

    def load_h5_add_group(self, lvl_num, entry_name, entry, panel=None):
        """
        Read a group level from teh H5 file and add it to the appropriate abstract level.
        
        Parameters
        ----------
        lvl_num : int
            Abstract level for this group
        entry_name : str
            Name of the entry to add to the group
        entry : dict
            Dictionary where keys are entry names, and values are entry values

        """
        data_dict = self.get_data_types(entry)
        lvl_name = 'level {}'.format(lvl_num)
        if lvl_name not in self.abstract_lvls.keys():
            data_type_dict = {}
            for data_name, data_type in data_dict.items():
                data_type_dict[data_name] = self.get_data_types(entry[data_name]) if data_type == dict else data_dict[data_name]
            self.add_abstract_lvl(lvl_num, data_type_dict)
        temp_dict = {data_name: self.load_dataset(data_name, data, data_dict) for data_name, data in entry.items()}
        if panel and (panel not in self.abstract_lvls[lvl_name].keys()):
            self.add_panel(lvl_num, [x for x in self._panels[lvl_name]])
        # If the BB is sent an null entry, don't add anything
        try:
            self.update_abstract_lvl(lvl_num, entry_name, temp_dict, panel=panel)
        except AttributeError:
            pass
        
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
        try:
            if panel:
                del self.abstract_lvls['level {}'.format(level)][panel][name]
            else:
                del self.abstract_lvls['level {}'.format(level)][name]
            self.log_debug('Removing entry {} from BB abstract level {}.'.format(name, level))
        except KeyError:
            pass
        
    def send_executor(self):
        """Send an executor message to the triggered KA."""
        if self._ka_to_execute != (None, 0):
            self.log_info('Selecting agent {} (TV: {}) to execute (TE: {})'.format(self._ka_to_execute[0], self._ka_to_execute[1], self._trigger_event))
            self.send('executor_{}'.format(self._ka_to_execute[0]), self._ka_to_execute)
            self.agent_addrs[self._ka_to_execute[0]].update({'performing action':True})
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
        data_type_str : class
            class of the evaluated data type 'string'
        """
        split_str = string.split(' ')
        re_str = re.findall('[a-z]', split_str[1])
        data_type_str = ''.join(re_str)
        return eval(data_type_str)
    
    def dict_type_checker(self, dict_, lvl_format):
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
        for k,v in dict_.items():
            if type(v) == dict:
                formatted_dict[k] = self.dict_type_checker(v, lvl_format[k])
            else:
                formatted_dict[k] = type(v)
                try:
                    assert formatted_dict[k] == lvl_format
                except (TypeError, AssertionError, KeyError):
                    try:
                        assert formatted_dict[k] == lvl_format[k]
                    except(AssertionError, KeyError):
                        self.log_warning('Entry Name: {} not in BB level with entries {}. Entry Type: {} Valid Type: {}.'.format(k, [x for x in lvl_format.keys()], formatted_dict[k], lvl_format[k]))
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
        abstract_lvl = self.abstract_lvls[lvl_name][panel] if panel else self.abstract_lvls[lvl_name]
        lvl_format = self.abstract_lvls_format[lvl_name][panel] if panel else self.abstract_lvls_format[lvl_name]
        for entry_name, entry_type in entry.items():
            if entry_name in lvl_format.keys():
                if type(entry_type) == dict:
                    self.dict_type_checker(entry_type, lvl_format[entry_name])
                else:
                    try:
                        assert type(entry_type) == lvl_format[entry_name]
                    except AssertionError:
                        self.log_warning('Entry Name: {} with value: {} caused an error.\n'.format(entry_name, entry_type))
                        self.log_warning('Entry {} is inconsistent with level {}.\n Entry keys are: {} \n with value types: {}.\n Abstract level expected keys: {}\n with value types: {}.\n Entry was not added.'.format(entry_name, level, [x for x in entry.keys()], [x for x in entry.values()], [x for x in lvl_format.keys()], [x for x in lvl_format.values()]))
                        return
            else:
                self.log_warning('Entry Name: {} not found in level {}'.format(entry_name, [x for x in lvl_format.keys()]))
                return
        
        abstract_lvl[name] = entry
        return
                      
            
    def write_to_h5(self):
        """BB will convert data from abstract levels to H5 file.
        
        Root directory will have a sub dicrectory for each abstract level.
        Each abstract level will then have a number of subdirectories, based on what results are written to them.
        """
        if not self.write_h5:
            return
        
        if not os.path.isfile(self.archive_name):
            self.log_debug('Creating New Database: {}'.format(self.archive_name))
            h5 = h5py.File(self.archive_name, 'w')
            for level, entry in self.abstract_lvls.items():
                h5.create_group(level)
                if level in self._panels.keys():
                    for panel_name in self._panels[level]:
                        h5[level].create_group(panel_name)
            h5.close()
                
        self.log_debug("Writing blackboard to archive")
                    
        h5 = h5py.File(self.archive_name, 'r+')
        self.h5_delete_entries(h5)
        
        for level, entry in self.abstract_lvls.items():
            group_level = h5[level]
            for name, data in entry.items():
                if level in self._panels.keys():
                    panel_group = group_level[name]
                    # Loop over the entries in th epanel and add entries
                    for panel_data_name, panel_data in data.items():
                        if panel_data_name not in panel_group.keys():
                            self.h5_group_writer(panel_group, panel_data_name, panel_data)               
                elif name not in group_level.keys():
                    self.h5_group_writer(group_level, name, data)
        self.log_debug("Finished writing to archive")
        h5.close()
    
    def h5_delete_entries(self, h5):
        """
        Examine the H5 file and current blackbaord dabstract levels and remove entries in the H5 file that are no longer in the BB bastract levels. (likely this is due to solution no longer being on the Pareto front)
        
        Parameters
        ----------
        h5 : h5-group object
            H5 entry that is no longer in the abstract level
        
        """
        bb = self.abstract_lvls
        del_entries = []
        for level, entry in h5.items():
            for entry_name, entry_data in entry.items():
                if level in self._panels.keys():
                    panel_entries = [panel for panel in entry_data]
                    for panel_entry in panel_entries:
                        if panel_entry not in bb[level][entry_name]:
                            del_entries.append((level, entry_name, panel_entry))   
                if entry_name not in bb[level]:
                    del_entries.append((level, entry_name))

        for entry in del_entries:
            if len(entry) == 3:
                del h5[entry[0]][entry[1]][entry[2]]
                self.log_debug('Removing entry {} on level {} panel {}'.format(entry[2],entry[0],entry[1]))
            else:
                del h5[entry[0]][entry[1]]          
                self.log_debug('Removing entry {} on level {}'.format(entry[1],entry[0]))
    
    def h5_group_writer(self, group_level, name, data):
        """
        Add an entry to the H5 file. 
        Each entry will be a unique group in the H5 file on the specified level and panel (if necessary)
        
        Parameters
        ----------
        group level : h5 object for group level
        data : dict 
        name : str
        """
        group_level.create_group(name)
        for data_name, data_val in data.items():
            data_type = type(data_val)
            if data_type == dict:
                self.dict_writer(data_name, data_val, group_level[name])
            elif data_type == list:
                group_level[name][data_name] = [self.convert_to_h5_type(type(x), x) for x in data_val]
                group_level[name][data_name].attrs['type'] = repr(type(data_val))   
            else:
                group_level[name][data_name] = self.convert_to_h5_type(data_type, data_val)
                group_level[name][data_name].attrs['type'] = repr(data_type)        