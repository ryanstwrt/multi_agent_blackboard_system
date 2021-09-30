from osbrain import run_agent
from osbrain import proxy
from osbrain import run_nameserver
from osbrain import Agent
import time
import mabs.utils.moo_benchmarks as mb
import mabs.bb.blackboard as blackboard
import mabs.bb.blackboard_optimization as bb_opt            


class Controller(object):
    """The controller object wraps around the blackboard system to control when and how agents interact with the blackboard. 
    
    The controller sets up the problem by creating instances of the blackboard, which in turn creates an instance of the knowledge agents upon initialization.
    
    TO DO: Update this to allow for blackboards to be working in parallel
    """
    
    def __init__(self):
        self.prime_bb = None
        self.sub_bb = None
        self.bb_attr = {}
        self.controller_agent_attr = {}
        self._ns = run_nameserver()
        self._proxy_server = proxy.NSProxy()       
            
    def initialize_blackboard(self, 
                              blackboard={},
                              ka={}, 
                              problem=None,
                              agent_wait_time=30, 
                              min_agent_wait_time=0,
                              plot_progress=False,
                              random_seed=None):    
        
        setattr(self, blackboard['name'], run_agent(name=blackboard['name'], base=blackboard['type']))
        _bb = getattr(self, blackboard['name'])
        for k,v in blackboard['attr'].items():
            _bb.set_attr(**{k:v})

        _bb.set_attr(problem=problem)
        _bb.initialize_abstract_level_3(objectives=problem.objs, design_variables=problem.dvs, constraints=problem.cons)
        _bb.initialize_metadata_level()
        _bb.set_random_seed(seed=random_seed)
 
        for ka_name, ka_data in ka.items():
            attr = ka_data['attr'] if 'attr' in ka_data.keys() else {}
            _bb.connect_agent(ka_data['type'], ka_name, attr=attr)
            
        self.bb_attr.update({blackboard['name']: {'plot': plot_progress,
                                       'name': blackboard['name'],
                                       'agent_wait_time': agent_wait_time,
                                       'progress_rate': _bb.get_attr('convergence_interval'),
                                       'complete':False}})

    def run_single_agent_bb(self, bb):
        """Run a BB optimization problem single-agent mode."""
        bb_attr = self.bb_attr[bb]
        bb = getattr(self, bb) 
        bb_time = time.time()        
        
        num_agents = len(bb.get_attr('agent_addrs'))
        while not bb.get_complete_status():
            bb.publish_trigger()
            trig_num = bb.get_current_trigger_value()
            responses = False
            # Wait until all responses have been recieved
            i=0
            while not responses:
                try:
                    if len(bb.get_kaar()[trig_num]) == num_agents:
                        responses = True                      
                except RuntimeError:
                    ...
            bb.controller()
            bb.set_attr(_new_entry=False)
            bb.send_executor()
            agent_time = time.time()
            while bb.get_attr('_new_entry') == False:
                if time.time() - agent_time > bb_attr['agent_wait_time']:
                    break
            agent_time = time.time() - agent_time
            if len(bb.get_kaar()) %  bb_attr['progress_rate'] == 0 or bb.get_complete_status() == True:
                bb.determine_complete()
                bb.log_metadata()
                bb.write_to_h5()
                bb.diagnostics_replace_agent()
                bb.plot_progress()
                if bb.get_complete_status():
                    self.shutdown_agents(bb) 
            else:
                bb.convergence_update()

        entry = {md: array[trig_num] for md, array in bb.get_attr('meta_data').items()}
        entry.update({'agent': 'final', 'time': time.time()-bb_time})
        bb.update_abstract_lvl(100, 'final', entry)
        bb.write_to_h5()            
            
    def run_multi_agent_bb(self, bb):
        """Run a BB optimization problem single-agent mode."""
        bb_attr = self.bb_attr[bb]
        bb = getattr(self, bb) 
        bb_time = time.time()
        num_agents = len(bb.get_attr('agent_addrs'))
        
        while not bb.get_complete_status():
            bb.publish_trigger()
            trig_num = bb.get_current_trigger_value()
            responses = False
            # Wait until a response has been recieved
            time_wait = time.time()
            bb_archived = True
            while time.time() - time_wait < bb_attr['agent_wait_time']:
                try:
                    kaar = bb.get_kaar()[trig_num]
                    kaar_val = [x for x in kaar.values()]
                    if kaar_val != []:
                        if max(kaar_val) > 0.0:
                            break
                    elif bb_archived:
                        bb.write_to_h5()
#                        bb.diagnostics_replace_agent()
                        bb_archived = False
                #RuntimeError allowed if a KA gets added to kaar while the BB is checking it's length; which causes the error    
                except RuntimeError: 
                    pass
                
            bb.controller()
            bb.send_executor()

            if len(bb.get_kaar()) % bb_attr['progress_rate'] == 0 or bb.get_complete_status() == True:
                bb.determine_complete()
                bb.log_metadata()
                bb.write_to_h5()
                bb.diagnostics_replace_agent()
                bb.plot_progress()
                if bb.get_complete_status():
                    self.shutdown_agents(bb)     
            else:
                bb.convergence_update()
                agent_time = 0
            time.sleep(0.05)

        entry = {md: array[trig_num] for md, array in bb.get_attr('meta_data').items()}
        entry.update({'agent': 'final', 'time': time.time()-bb_time})
        bb.update_abstract_lvl(100, 'final', entry)
        bb.write_to_h5() 

    def shutdown_agents(self,bb):
        while len(bb.get_attr('agent_list')) > 0:  
            bb.send_shutdown()
            time.sleep(0.01)
        
    def run_multi_tiered(self):
        """
        Run a multi-tiered problem in parallel bu running the ControllerAgents simultaneously
        """
        for bb in reversed(list(self.bb_attr.values())):
            self.run_multi_agent_bb(bb['name'])
               
    def check_multi_tiered(self):
        """
        Check to see if all blackboards have ca compelte status
        """
        for bb, bb_dict in self.bb_attr.items():
            bb = getattr(self, bb)
            bb_dict['complete'] = bb.get_complete_status()

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
        
class ControllerAgent(Agent, Controller):
    
    def on_init(self):
        self.log_info('Connected {}'.format(self.name))
        self._run_bb_alias = None
        self._run_bb_addr = None
        self.prime_ca = None
        self.bb_attr = {}
        self.controller_agent_attr = {}        
        
    def connect_run_bb(self):
        """Create a push-pull communication channel to execute KA."""
        self._run_bb_alias, self._run_bb_addr = self.prime_ca.connect_run_bb(self.name)
        self.connect(self._run_bb_addr, alias=self._run_bb_alias, handler=self.handler_run_bb)
        self.log_info('Agent {} connected run BB to prime CA'.format(self.name))       
  
    def handler_run_bb(self, message):
        self.bb_attr = message
        self.run_multi_agent_bb(self.bb_attr[self.bb_name]['name'])
        
class PrimeControllerAgent(Agent, Controller):
    
    def on_init(self):
      
        self.log_info('Connected Prime Controller Agent')   
        self.bb_addrs = {}
        self.bb_attr = {}
        self.controller_agent_attr = {}        
        
    def connect_run_bb(self, agent_name):
        alias_name = 'run_bb_{}'.format(agent_name)
        executor_addr = self.bind('PUSH', alias=alias_name)
        self.bb_addrs[agent_name] = {'run_bb': (alias_name, executor_addr)}
        return (alias_name, executor_addr)     
    
    def initialize_blackboard(self, 
                              blackboard={},
                              ka={}, 
                              problem=None,
                              agent_wait_time=30, 
                              min_agent_wait_time=0,
                              plot_progress=False,
                              random_seed=None):    
        
        setattr(self, blackboard['name'], run_agent(name=blackboard['name'], base=blackboard['type']))
        _bb = getattr(self, blackboard['name'])
        for k,v in blackboard['attr'].items():
            _bb.set_attr(**{k:v})
            
        _bb.set_attr(problem=problem)
        _bb.initialize_abstract_level_3(objectives=problem.objs, design_variables=problem.dvs, constraints=problem.cons)
        _bb.set_random_seed(seed=random_seed)
        _bb.initialize_metadata_level()

 
        for ka_name, ka_data in ka.items():
            attr = ka_data['attr'] if 'attr' in ka_data.keys() else {}
            _bb.connect_agent(ka_data['type'], ka_name, attr=attr)
            
        self.bb_attr.update({blackboard['name']: {'plot': plot_progress,
                                                  'name': blackboard['name'],
                                                  'agent_wait_time': agent_wait_time,
                                                  'progress_rate': _bb.get_attr('convergence_interval'),
                                                  'complete':False}})

        ca_name = 'ca_{}'.format(blackboard['name'])
        ca = run_agent(name=ca_name, base=ControllerAgent)
        ca.set_attr(prime_ca=self)
        ca.set_attr(bb_name=blackboard['name'])
        setattr(ca, blackboard['name'], _bb)
        self.controller_agent_attr[ca_name] = {'controller agent': ca,
                                               'blackboard': blackboard['name'],
                                               'bb_attr': self.bb_attr}     
        ca.connect_run_bb()

    def run_multi_tiered(self):
        """
        Run a multi-tiered problem in parallel by sending a message to each CA the ControllerAgents simultaneously
        """
        for ca, ca_dict in self.controller_agent_attr.items():
            self.log_info('Began run for {}'.format(ca))    
            self.send_run_bb(ca, ca_dict['bb_attr'])
            
    def send_run_bb(self, agent_name, bb_attr):
        self.send('run_bb_{}'.format(agent_name), bb_attr)            
        
    def check_multi_tiered(self):
        """
        Check to see if all blackboards have ca compelte status
        """
        for ca_dict in self.controller_agent_attr.values():
            ca_bb = getattr(ca_dict['controller agent'], ca_dict['blackboard'])
            self.bb_attr[ca_dict['blackboard']]['complete'] = ca_bb.get_complete_status()