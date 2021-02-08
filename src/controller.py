from osbrain import run_agent
from osbrain import proxy
from osbrain import run_nameserver
import time
import pickle
import src.utils.moo_benchmarks as mb
import src.bb.blackboard as blackboard
import src.bb.blackboard_optimization as bb_opt
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
                 min_agent_wait_time=0,
                 benchmark=None, 
                 plot_progress=False,
                 total_tvs=1E6,
                 skipped_tvs=200,
                 convergence_type='hvi',
                 convergence_rate=1E-5,
                 convergence_interval=25,
                 pf_size=200,
                 dci_div={},
                 function_evals=1E6,
                 surrogate_model={'sm_type': 'lr', 'pickle file': None},
                 random_seed=None):
        
        self.bb_name = bb_name
        self.bb_type = bb_type
        self.agent_wait_time = agent_wait_time
        self._ns = run_nameserver()
        self._proxy_server = proxy.NSProxy()
        self.bb = run_agent(name=self.bb_name, base=self.bb_type)
        self.bb.set_attr(archive_name='{}.h5'.format(archive))
        
        self.agent_time = 0
        self.progress_rate = convergence_interval
        self.plot_progress = plot_progress
        self.time = [time.time()]
        
        if bb_type == bb_opt.BbOpt:
            self.bb.initialize_abstract_level_3(objectives=objectives, design_variables=design_variables, constraints=constraints)
            self.bb.set_attr(sm_type=surrogate_model['sm_type'])
            self.bb.set_attr(total_tvs=total_tvs)
            self.bb.set_attr(skipped_tvs=skipped_tvs)
            self.bb.set_attr(pf_size=pf_size)
            self.bb.set_attr(convergence_type=convergence_type)
            self.bb.set_attr(function_evals=function_evals)
            self.bb.set_attr(convergence_rate=convergence_rate)
            self.bb.set_attr(convergence_interval=convergence_interval)            
            self.bb.set_attr(dci_div=dci_div)
            if random_seed:
                self.bb.set_attr(random_seed=random_seed)
            if surrogate_model['pickle file']:
                with open(surrogate_model['pickle file'], 'rb') as pickle_file:
                    sm = pickle.load(pickle_file)
                self.bb.set_attr(_sm=sm)            
            else:
                self.bb.generate_sm()
        
        for ka_name, ka_data in ka.items():
            attr = ka_data['attr'] if 'attr' in ka_data.keys() else {}
            self.bb.connect_agent(ka_data['type'], ka_name, attr=attr)
            
    def initialize_blackboard(self):
        self.bb.set_attr(total_tvs=total_tvs)
        self.bb.set_attr(skipped_tvs=skipped_tvs)
        self.bb.set_attr(pf_size=pf_size)
        self.bb.set_attr(convergence_type=convergence_type)
        self.bb.set_attr(convergence_rate=convergence_rate)
        self.bb.set_attr(convergence_interval=convergence_interval)            
        self.bb.set_attr(dci_div=dci_div)
            
    def run_single_agent_bb(self):
        """Run a BB optimization problem single-agent mode."""
        num_agents = len(self.bb.get_attr('agent_addrs'))
        while not self.bb.get_complete_status():
            self.bb.publish_trigger()
            trig_num = self.bb.get_current_trigger_value()
            responses = False
            # Wait until all responses have been recieved
            while not responses:
                try:
                    if len(self.bb.get_kaar()[trig_num]) == num_agents:
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
            if len(self.bb.get_kaar()) % self.progress_rate == 0 or self.bb.get_complete_status() == True:
                self.bb.convergence_indicator()
                self.bb.write_to_h5()
                if len(self.bb.get_hv_list()) > 2 * self.progress_rate:
                    self.bb.determine_complete()
                    if self.bb.get_complete_status():
                        while len(self.bb.get_attr('agent_addrs')) > 0:           
                            if True in [agent['performing action'] for agent in self.bb.get_attr('agent_addrs').values()]:
                                time.sleep(1)
                            else:
                                self.bb.send_shutdown()
                if self.plot_progress:
                    self.bb.plot_progress()
            else:
                self.bb.convergence_update()

        self.time.append(time.time())
        self.bb.update_abstract_lvl(100, 'final', {'agent': 'final', 'time': self.time[1]-self.time[0], 'hvi': self.bb.get_hv_list()[-1]})
        self.bb.write_to_h5()
        
        
    def run_multi_agent_bb(self):
        """Run a BB optimization problem single-agent mode."""
        num_agents = len(self.bb.get_attr('agent_addrs'))
        while not self.bb.get_complete_status():
            self.bb.publish_trigger()
            trig_num = self.bb.get_current_trigger_value()
            responses = False
            # Wait until a response has been recieved
            time_wait = time.time()
            bb_archived = True
            while time.time() - time_wait  < self.agent_wait_time:
                try:
                    kaar = self.bb.get_kaar()[trig_num]
                    kaar_val = [x for x in kaar.values()]
                    if kaar_val != []:
                        if max(kaar_val) > 0.0:
                            break
                    elif bb_archived:
                        self.bb.write_to_h5()
                        bb_archived = False
                except RuntimeError:
                    pass
                
            self.bb.controller()
            self.bb.send_executor()

            if len(self.bb.get_kaar()) % self.progress_rate == 0 or self.bb.get_complete_status() == True:
                self.bb.convergence_indicator()
                self.bb.write_to_h5()
                self.bb.diagnostics_replace_agent()
                if len(self.bb.get_hv_list()) > 2 * self.progress_rate:
                    self.bb.determine_complete()
                    if self.bb.get_complete_status():
                        while len(self.bb.get_attr('agent_addrs')) > 0:                                   
                            if True in [agent['performing action'] for agent in self.bb.get_attr('agent_addrs').values()]:
                                time.sleep(1)
                            else:
                                self.bb.send_shutdown()
                            
                if self.plot_progress:
                    self.bb.plot_progress()
            else:
                self.bb.convergence_update()
                agent_time = 0
            time.sleep(0.05)
        self.time.append(time.time())
        self.bb.update_abstract_lvl(100, 'final', {'agent': 'final', 'time': self.time[1]-self.time[0], 'hvi': self.bb.get_hv_list()[-1]})
        self.bb.write_to_h5()        
                
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
        
class BenchmarkController(Controller):
    """The controller object wraps around the blackboard system to control when and how agents interact with the blackboard. 
    
    The controller sets up the problem by creating instances of the blackboard, which in turn creates an instance of the knowledge agents upon initialization."""
    
    def __init__(self, bb_name='bb', 
                 benchmark=None,
                 bb_type=bb_opt.BenchmarkBbOpt, 
                 ka={}, 
                 objectives=None, 
                 design_variables=None,
                 constraints=None,
                 archive='bb_benchmark', 
                 agent_wait_time=30, 
                 min_agent_wait_time=0,
                 plot_progress=False,
                 total_tvs=1E6,
                 skipped_tvs=200,
                 convergence_type='hvi',
                 convergence_rate=1E-5,
                 convergence_interval=25,
                 pf_size=200,
                 dci_div={},
                 function_evals=1E6,
                 surrogate_model={'sm_type': 'lr', 'pickle file': None},
                 random_seed=None):

        self.bb_name = bb_name
        self.bb_type = bb_type
        self.agent_wait_time = agent_wait_time
        self._ns = run_nameserver()
        self._proxy_server = proxy.NSProxy()
        self.bb = run_agent(name=self.bb_name, base=self.bb_type)
        self.bb.set_random_seed(seed=random_seed)
        self.bb.set_attr(archive_name='{}.h5'.format(archive))

        self.bb.set_attr(total_tvs=total_tvs)
        self.bb.set_attr(skipped_tvs=skipped_tvs)
        self.bb.set_attr(pf_size=pf_size)
        self.bb.set_attr(convergence_type=convergence_type)
        self.bb.set_attr(convergence_rate=convergence_rate)
        self.bb.set_attr(convergence_interval=convergence_interval)            
        self.bb.set_attr(dci_div=dci_div)
        self.bb.set_attr(function_evals=function_evals)
        
        self.agent_time = 0
        self.progress_rate = convergence_interval
        self.plot_progress = plot_progress
        self.time = [time.time()]
 
        self.bb.initialize_abstract_level_3(objectives=objectives, design_variables=design_variables,constraints=constraints)
        self.bb.set_attr(sm_type='{}_benchmark'.format(benchmark))
        self.bb.set_attr(_sm=mb.optimization_test_functions(benchmark))
        
        for ka_name, ka_data in ka.items():
            attr = ka_data['attr'] if 'attr' in ka_data.keys() else {}
            self.bb.connect_agent(ka_data['type'], ka_name, attr=attr)
            

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
                                    objectives=None, 
                                    design_variables=None,
                                    constraints=None,
                                    archive='bb_archive', 
                                    agent_wait_time=30, 
                                    min_agent_wait_time=0,
                                    plot_progress=False,
                                    total_tvs=1E6,
                                    skipped_tvs=200,
                                    convergence_type='hvi',
                                    convergence_rate=1E-5,
                                    convergence_interval=25,
                                    pf_size=200,
                                    dci_div={},
                                    surrogate_model={'sm_type': 'gpr', 'pickle file': 'sm_gpr.pkl'},
                                    random_seed=None):
        
        self.bb_attr.update({bb_name: {'plot': plot_progress,
                                       'name': bb_name,
                                       'wait time': agent_wait_time}})
        setattr(self, bb, run_agent(name=bb_name, base=bb_type))
        bb = getattr(self, bb)
        bb.set_random_seed(seed=random_seed)
        bb.set_attr(archive_name='{}.h5'.format(archive))

        bb.initialize_abstract_level_3(objectives=objectives, design_variables=design_variables, constraints=constraints)
        bb.set_attr(sm_type=surrogate_model['sm_type'])

        bb.set_attr(total_tvs=total_tvs)
        bb.set_attr(skipped_tvs=skipped_tvs)
        bb.set_attr(pf_size=pf_size)
        bb.set_attr(convergence_type=convergence_type)
        bb.set_attr(convergence_rate=convergence_rate)
        bb.set_attr(convergence_interval=convergence_interval)            
        bb.set_attr(dci_div=dci_div)
        
        if surrogate_model['pickle file']:
            with open(surrogate_model['pickle file'], 'rb') as pickle_file:
                sm = pickle.load(pickle_file)
            bb.set_attr(_sm=sm)            
        else:
            bb.generate_sm()
 
        for ka_name, ka_data in ka.items():
            attr = ka_data['attr'] if 'attr' in ka_data.keys() else {}
            bb.connect_agent(ka_data['type'], ka_name, attr=attr)
                
            
    def run_sub_bb(self, bb):
        """Run a BB optimization problem single-agent mode."""
        time_1 = time.time()
        bb_name = bb.get_attr('name')
        num_agents = len(bb.get_attr('agent_addrs'))
        convergence_interval=bb.get_attr('convergence_interval')
        bb_attr = self.bb_attr[bb_name]
        if bb_name == 'bb_master':
            num_agents -= 1
            
        while not bb.get_complete_status():
            bb.publish_trigger()
            trig_num = bb.get_current_trigger_value()
            responses = False
            # Wait until all responses have been recieved
            while not responses:
                try:
                    if len(bb.get_kaar()[trig_num]) == num_agents:
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

            if len(bb.get_kaar()) % convergence_interval == 0:
                bb.convergence_indicator()
                bb.write_to_h5()
                if len(bb.get_hv_list()) > 2 * convergence_interval:
                    bb.determine_complete()
                    if bb.get_complete_status():
                        while len(bb.get_attr('agent_addrs')) > 0:
                            bb.send_shutdown()
                if bb_attr['plot']:
                    bb.plot_progress()
            else:
                bb.convergence_update()

        time_2 = time.time()

        bb.update_abstract_lvl(100, 'final', {'agent': 'final', 'hvi': bb.get_hv_list()[-1], 'time': time_2 - time_1})
        bb.write_to_h5()

        return
        
    def shutdown(self):
        self._ns.shutdown()