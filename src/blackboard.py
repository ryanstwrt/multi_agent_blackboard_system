import osbrain
from osbrain import Agent
import tables as tb
import pandas as pd

def log_message(self, message):
  self.log_info('{}'.format(message))

class Blackboard(Agent):
    """This is a class for holding all information regardng the solutions to the problem.
    The blackboard class inherets from osBrain's agent class.
    This allows for communication between the blackbaord and the other varous knowledge agents.
    
    
    The blackboard holds information on four different abstract levels (described below).
    All information for abstract levels are stored in memory.
    Abstract levels 3 and 4 are also stored in an H5 file to maintain data between runs, and allow for restart of a proble should failure arise.
    
    Attributes:
        lvl_1 (dict): Dictionary of results for the level 1 abstract level.
                      Takes the form of nested dict: {name: {exp_num: (a,b,c), validated: Bool, Pareto: Bool}}
        lvl_2 (dict): Dictionary of results for the level 2 abstract level.
                      Takes the form of nested dict: {name: {exp_num: (a,b,c), valid: Bool}}
        lvl_3 (dict): Dictionary of results for the level 3 abstract level.
                      Takes the form of nested dict: {name: {parameters: DataFrame, xc_set: str}}
        lvl_4 (dict): Dictionary of results for the level 4 abstract level.
                      Takes the form of a dict: {name: xc_set (file?)}
        trained_models (class): Reference to train_surrogate_model module, which contains multiple models to choose frome.
        agents (list): List of agents currently active in the multi-agent system.
    """
    def on_init(self):
        self.agents = []
        self.trained_models = None
        #db = tb.open_file("blackboard_db", "w")
        #db.close()
    
        self.lvl_1 = {}
        self.lvl_2 = {}
        self.lvl_3 = {}
        self.lvl_4 = {}
        #pd.DataFrame(cols = ['Design ID', 'Exp A', 'Exp B', 'Exp C',  'k-eff', 'doppler', 'void', 'rod worth', 'LHGR', 'Assembly Map', 'Flux Map', 'Power Map'])

    def get_agents(self):
        return self.agents
   
    def get_trained_models(self):
        return self.trained_models
    
    def get_abstract_lvl(self, level):
        if level == 1:
            return self.lvl_1
        elif level == 2:
            return self.lvl_2
        elif level == 3:
            return self.lvl_3
        elif level == 4:
            return self.lvl_3
        else:
            print("Warning: Abstract Level {} does not exist.".format(level))
            return None
        