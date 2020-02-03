import osbrain
from osbrain import Agent
import tables as tb
import pandas as pd

def log_message(self, message):
  self.log_info('{}'.format(message))

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
                      Takes the form of nested dict: {name: {exp_num: (a,b,c), validated: Bool, Pareto: Bool}}
        lvl_2 (dict): Dictionary of entries for the level 2 abstract level.
                      Takes the form of nested dict: {name: {exp_num: (a,b,c), valid_core: Bool}}
        lvl_3 (dict): Dictionary of entries for the level 3 abstract level.
                      Takes the form of nested dict: {name: {parameters: DataFrame, xc_set: str}}
        lvl_4 (dict): Dictionary of entires for the level 4 abstract level.
                      Takes the form of a dict: {name: xc_set (file?)}
        trained_models (class): Reference to train_surrogate_model module, which contains multiple models to choose frome.
        agents (list): List of agents currently active in the multi-agent system.
    """
    def on_init(self):
        self.agents = []
        self.trained_models = None
        
        self.lvl_1 = {}
        self.lvl_2 = {}
        self.lvl_3 = {}
        self.lvl_4 = {}
        self.abstract_levels = {'level 1': self.lvl_1, 'level 2': self.lvl_2, 'level 3': self.lvl_3, 'level 4': self.lvl_4}
        #pd.DataFrame(cols = ['Design ID', 'Exp A', 'Exp B', 'Exp C',  'k-eff', 'doppler', 'void', 'rod worth', 'LHGR', 'Assembly Map', 'Flux Map', 'Power Map'])

    def get_agents(self):
        return self.agents
   
    def get_trained_models(self):
        return self.trained_models
    
    def get_abstract_lvl(self, level):
        if level in self.abstract_levels:
            return self.abstract_levels[level]
        else:
            print("Warning: Abstract {} does not exist.".format(level))
            return None
        
    def add_abstract_lvl_1(self, name, exp_nums, validated=False, pareto=False):
        "Add an entry for abstract level 1"
        self.lvl_1[name] = {'exp_num': exp_nums, 'validated': validated, 'pareto': pareto}
    
    def update_abstract_lvl_1(self, name, updated_params):
        "Update an entry for abstract level 1"
        for k,v in updated_params.items():
            self.lvl_1[name][k] = v

    def add_abstract_lvl_2(self, name, exp_nums, valid):
        "Add an entry for abstract level 2"
        self.lvl_2[name] = {'exp_num': exp_nums, 'valid_core': valid}
    
    def update_abstract_lvl_2(self, name, updated_params):
        "Update an entry for abstract level 2 "
        #TODO: Make sure we update this level if Serpent tells us the core is not valid
        for k,v in updated_params.items():
            self.lvl_2[name][k] = v

    def add_abstract_lvl_3(self, name, params, xs_set):
        "Add an entry for abstract level 3"
        self.lvl_3[name] = {'reactor_parameters': params, 'xs_set': xs_set}
    
    def update_abstract_lvl_3(self, name, updated_params):
        "Update an entry for abstract level 3 "
        for k,v in updated_params.items():
            self.lvl_3[name][k] = v

    def add_abstract_lvl_4(self, name, file):
        "Add an entry for abstract level 4"
        self.lvl_4[name] = {'xs_set': file}
        
    def update_abstract_lvl_4(self, name, updated_params):
        "Update an entry for abstract level 4"
        for k,v in updated_params.items():
            self.lvl_4[name][k] = v