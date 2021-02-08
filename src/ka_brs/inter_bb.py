from src.ka_brs.base import KaBr
import time

class InterBB(KaBr):
    """Reads BB Level and write results to secondary BB."""
    def on_init(self):
        super().on_init()
        self.bb_to_write = None
        self.bb_lvl_write = 3
        self.bb_lvl_read = 1
        self._trigger_val_base = 6.00000000001
        self._class = 'reader inter'
        self._entries_moved = []
        self._new_entry_format = {}

    def add_entry(self, core_name, entry):
        """
        Update the entr name and entry value.
        """
        self._entry_name = core_name
        self._entry = entry
        
    def connect_bb_to_write(self, bb):
        """Connect the BB and writer message to the BB we want to write to"""
        bb_agent_addr = bb.get_attr('agent_addrs')
        bb_agent_addr[self.name] = {'trigger response': None, 'executor': None, 'shutdown':None, 'performing action': False, 'class': InterBB}
        bb.set_attr(agent_addrs=bb_agent_addr)
        self._new_entry_format = {'design variables': bb.get_attr('design_variables'),
                                  'objective functions': bb.get_attr('objectives'),
                                  'constraints': bb.get_attr('constraints')}
        
        self._writer_alias, self._writer_addr = bb.connect_writer(self.name)
        self.connect(self._writer_addr, alias=self._writer_alias)
        self.log_info('Agent {} connected writer to {}'.format(self.name, bb.get_attr('name')))

    def format_entry(self, entry_name):
        """
        Transform the variables from the sub BB to allow them to be written to the master BB
        
        TODO: If we are missing an objective/constraint we should just place a number there
        """
        design = self._lvl_data[entry_name]['design variables']
        design.update({k:v for k,v in self._lvl_data[entry_name]['objective functions'].items()})
        design.update({k:v for k,v in self._lvl_data[entry_name]['constraints'].items()})
        new_design = {}
        
        for k,v in self._new_entry_format.items():
            new_design[k] = {param: design[param] for param, val in v.items()}
            
        return new_design        
        
    def handler_executor(self, message):
        
        t = time.time()
        self._lvl_data = {}
        self._trigger_event = message[0]
        self.log_debug('Executing agent {}'.format(self.name))

        self.lvl_read =  message[1]['level {}'.format(self.bb_lvl_read)]
        for panel in message[1]['level {}'.format(self.bb_lvl_data)].values():
            self._lvl_data.update(panel)        
        
        for entry_name in self.lvl_read.keys():
            self.clear_entry()
            if entry_name not in self._entries_moved:
                entry = self.format_entry(entry_name)
                self.add_entry(entry_name, entry)
                self.write_to_bb(self.bb_lvl_write, self._entry_name, self._entry, panel=self.new_panel)
                self._entries_moved.append(entry_name)

        self._trigger_val = 0
        self.agent_time = time.time() - t
        self.action_complete()     
            
    def handler_trigger_publish(self, message):
        """Read the BB level and determine if an entry is available."""
        self.lvl_read =  message['level {}'.format(self.bb_lvl_read)] 
        
        designs = [x for x in self.lvl_read.keys()]
        new_entry = set(designs).issubset(self._entries_moved)
        self._trigger_val = self._trigger_val_base if not new_entry else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))     
    