import blackboard

class BbTraditional(blackboard.Blackboard):
    
    def on_init():
        super.init()
        
    def determine_complete():
        if self.abstract_lvls('level 1') != {}:
            self.log_info('Problem complete, shutting agents down')
            self.send(self._shutdown_alias)
        pass
    
    def wait_for_ka(self):
        """Write to H5 file and sleep while waiting for agents."""
        sleep_time = 0
        if self._new_entry == False:
#            self.agent_writing = True
            self.write_to_h5()
            self.determine_complete()
#            self.agent_writing = False
        while not self._new_entry:
            time.sleep(1)
            sleep_time += 1
            if sleep_time > self._sleep_limit:
                break
        self._new_entry = False