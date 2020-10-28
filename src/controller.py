import osbrain
from osbrain import Agent
from osbrain import run_agent
from osbrain import proxy
from osbrain import run_nameserver
import src.blackboard as blackboard
import time
import src.bb_opt as bb_opt
import src.moo_benchmarks as mb
import src.bb_benchmark as bb_benchmark
import src.ka_br as kabr
import pickle

# Can the controller keep track of the BB levels and update the trigger values of different agents as needed?

class Controller(object):
    """The controller object wraps around the blackboard system to control when and how agents interact with the blackboard. 
    
    The controller sets up the problem by creating instances of the blackboard, which in turn creates an instance of the knowledge agents upon initialization."""
    
    def __init__(self, bb_name='bb', 
                 bb_type=blackboard.Blackboard, 
                 ka={}, 
                 objectives=None, 
                 design_variables=None,
                 constraints=None,
                 archive='bb_archive', 
                 agent_wait_time=30, 
                 benchmark=None, 
                 plot_progress=False,
                 convergence_model={'type': 'hvi', 'convergence rate': 1E-5, 'interval': 25, 'pf size': 200, 'total tvs': 1E6},
                 surrogate_model={'sm_type': 'lr', 'pickle file': None},
                 random_seed=None):
        
        self.bb_name = bb_name
        self.bb_type = bb_type
        self.agent_wait_time = agent_wait_time
        self._ns = run_nameserver()
        self._proxy_server = proxy.NSProxy()
        self.bb = run_agent(name=self.bb_name, base=self.bb_type)
        self.bb.set_attr(archive_name='{}.h5'.format(archive))
        self.bb.set_attr(convergence_model=convergence_model)
        
        self.agent_time = 0
        self.progress_rate = convergence_model['interval']
        self.plot_progress = plot_progress
        self.time = [time.time()]
        
        if bb_type == bb_opt.BbOpt:
            self.bb.initialize_abstract_level_3(objectives=objectives, design_variables=design_variables, constraints=constraints)
            self.bb.set_attr(sm_type=surrogate_model['sm_type'])
            self.bb.set_attr(convergence_model=convergence_model)
            if random_seed:
                self.bb.set_attr(random_seed=random_seed)
            if surrogate_model['pickle file']:
                with open(surrogate_model['pickle file'], 'rb') as pickle_file:
                    sm = pickle.load(pickle_file)
                self.bb.set_attr(_sm=sm)            
            else:
                self.bb.generate_sm()
        
        elif bb_type == bb_benchmark.BenchmarkBB:
            self.bb.initialize_abstract_level_3(objectives=objectives, design_variables=design_variables,constraints=constraints)
            self.bb.set_attr(sm_type='{}_benchmark'.format(benchmark))
            self.bb.set_attr(_sm=mb.optimization_test_functions(benchmark))
        
        ka_attributes = {}
        for ka_name, ka_type in ka.items():
            self.bb.connect_agent(ka_type, ka_name, attr=ka_attributes)
            
    def initialize_blackboard(self):
        pass
            
    def run_single_agent_bb(self):
        """Run a BB optimization problem single-agent mode."""
        num_agents = len(self.bb.get_attr('agent_addrs'))
        while not self.bb.get_attr('_complete'):
            self.bb.publish_trigger()
            trig_num = self.bb.get_attr('_trigger_event')
            responses = False
            # Wait until all responses have been recieved
            while not responses:
                try:
                    if len(self.bb.get_attr('_kaar')[trig_num]) == num_agents:
                        responses = True
                except RuntimeError:
                    pass
            self.bb.controller()
            self.bb.set_attr(_new_entry=False)
            self.bb.send_executor()
            agent_time = time.time()
            while self.bb.get_attr('_new_entry') == False:
                if time.time() - agent_time > self.agent_wait_time:
                    break
            agent_time = time.time() - agent_time
            if len(self.bb.get_attr('_kaar')) % self.progress_rate == 0 or self.bb.get_attr('_complete') == True:
                self.bb.convergence_indicator()
                self.bb.meta_data_entry(agent_time)
                self.bb.write_to_h5()
                if len(self.bb.get_attr('hv_list')) > 2 * self.progress_rate:
                    self.bb.determine_complete()
                if self.plot_progress:
                    self.bb.plot_progress()
            else:
                self.bb.convergence_update()
                self.bb.meta_data_entry(agent_time)

        self.time.append(time.time())
        self.bb.update_abstract_lvl(100, 'final', {'agent': 'final', 'time': self.time[1]-self.time[0], 'hvi': self.bb.get_attr('hv_list')[-1]})
        self.bb.write_to_h5()
        
        
    def run_multi_agent_bb(self):
        """Run a BB optimization problem single-agent mode."""
        
        while not self.bb.get_attr('_complete'):
            self.bb.publish_trigger()
            trig_num = self.bb.get_attr('_trigger_event')
            responses = False
            # Wait until a response has been recieved
            while len(self.bb.get_attr('_kaar')[trig_num]) < 1:
                pass
            
            self.bb.controller()
            self.bb.send_executor()

            if len(self.bb.get_attr('_kaar')) % self.progress_rate == 0 or self.bb.get_attr('_complete') == True:
                self.bb.convergence_indicator()
           #     self.bb.meta_data_entry(agent_time)
                self.bb.write_to_h5()
                self.bb.diagnostics_replace_agent()
                if len(self.bb.get_attr('hv_list')) > 2 * self.progress_rate:
                    self.bb.determine_complete()
                if self.plot_progress:
                    self.bb.plot_progress()
            else:
                self.bb.convergence_update()
                agent_time = 0
               # self.bb.meta_data_entry(agent_time)
                
    def update_bb_trigger_values(self, trig_num):
        """
        Update a knowledge agents trigger value.
        
        If BB has too many entries on a abstract level, the KA trigger value gets increased by 1.
        If the BB has few entries on the abstract level, the KA trigger value is reduced by 1.
        """
        self.bb.controller_update_kaar(trig_num, round(self.agent_time,2))
        self.agent_time = 0
        
    def shutdown(self):
        self._ns.shutdown()
        
class Multi_Tiered_Controller(Controller):
    """The controller object wraps around the blackboard system to control when and how agents interact with the blackboard. 
    
    The controller sets up the problem by creating instances of the blackboard, which in turn creates an instance of the knowledge agents upon initialization."""
    
    def __init__(self):
        self.master_bb = None
        self.sub_bb = None
        self.bb_attr = {}
        self._ns = run_nameserver()
        self._proxy_server = proxy.NSProxy()       

            
    def initialize_blackboard(self, bb,
                                    bb_name='bb', 
                                    bb_type=None, 
                                    ka={}, 
                                    ka_attr={},
                                    objectives=None, 
                                    design_variables=None,
                                    constraints=None,
                                    archive='bb_archive', 
                                    agent_wait_time=30, 
                                    benchmark=None, 
                                    plot_progress=False,
                                    convergence_model={'type': 'hvi', 'convergence rate': 1E-5, 'interval': 25, 'pf size': 200, 'total tvs': 1E6},
                                    surrogate_model={'sm_type': 'gpr', 'pickle file': 'sm_gpr.pkl'},
                                    random_seed=None):
        
        self.bb_attr.update({bb_name: {'plot': plot_progress,
                                       'name': bb_name,
                                       'wait time': agent_wait_time}})
        setattr(self, bb, run_agent(name=bb_name, base=bb_type))
        bb = getattr(self, bb)
        bb.set_random_seed(seed=random_seed)
        bb.set_attr(archive_name='{}.h5'.format(archive))
        bb.set_attr(convergence_model=convergence_model)

        bb.initialize_abstract_level_3(objectives=objectives, design_variables=design_variables, constraints=constraints)
        bb.set_attr(sm_type=surrogate_model['sm_type'])
        bb.set_attr(convergence_model=convergence_model)
        
        if surrogate_model['pickle file']:
            with open(surrogate_model['pickle file'], 'rb') as pickle_file:
                sm = pickle.load(pickle_file)
            bb.set_attr(_sm=sm)            
        else:
            bb.generate_sm()
        
        if kabr.KaBr_interBB in [x for x in ka.values()]:
            ka_attr.update({list(ka.keys())[list(ka.values()).index(kabr.KaBr_interBB)] : {'bb': self.master_bb}})
            
        for ka_name, ka_type in ka.items():
            bb.connect_agent(ka_type, ka_name, attr=ka_attr)
                
            
    def run_sub_bb(self, bb):
        """Run a BB optimization problem single-agent mode."""
        time_1 = time.time()
        bb_name = bb.get_attr('name')
        num_agents = len(bb.get_attr('agent_addrs'))
        conv_criteria = bb.get_attr('convergence_model')
        bb_attr = self.bb_attr[bb_name]
        if bb_name == 'bb_master':
            num_agents -= 1
            
        while not bb.get_attr('_complete'):
            bb.publish_trigger()
            trig_num = bb.get_attr('_trigger_event')
            responses = False
            # Wait until all responses have been recieved
            while not responses:
                try:
                    if len(bb.get_attr('_kaar')[trig_num]) == num_agents:
                        responses = True
                except RuntimeError:
                    pass

            bb.controller()
            bb.set_attr(_new_entry=False)
            bb.send_executor()
            
            agent_time = time.time()

            while bb.get_attr('_new_entry') == False:
                if time.time() - agent_time > bb_attr['wait time']:
                    break
            agent_time = time.time() - agent_time
            if len(bb.get_attr('_kaar')) % conv_criteria['interval'] == 0:
                bb.convergence_indicator()
                bb.meta_data_entry(agent_time)
                bb.write_to_h5()
                if len(bb.get_attr('hv_list')) > 2 * conv_criteria['interval']:
                    bb.determine_complete()
                if bb_attr['plot']:
                    bb.plot_progress()
            else:
                bb.convergence_update()
                bb.meta_data_entry(agent_time)


        time_2 = time.time()

        bb.update_abstract_lvl(100, 'final', {'agent': 'final', 'time': time_2 - time_1, 'hvi': bb.get_attr('hv_list')[-1]})
        bb.write_to_h5()

        return
        
    def shutdown(self):
        self._ns.shutdown()