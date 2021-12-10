import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import mabs.ka.ka_s.base as base
import time
from mabs.utils.problem import BenchmarkProblem
import pickle
import mabs.bb.blackboard_optimization as bb_opt
import mabs.ka.ka_s.neighborhood_search as nhs




dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}    
        
problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')  
    
def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_sub', base=base.KaSub)
    assert rp.get_attr('bb') == None
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_sub'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    
    assert rp.get_attr('_trigger_val') == 0
    assert rp.get_attr('_base_trigger_val') == 0.250001   
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('_design_variables') == {}    
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('_lvl_data') == {}
    assert rp.get_attr('execute_once') == False
    assert rp.get_attr('ka') == None
    assert rp.get_attr('_class') == 'search subagent'
   
    ns.shutdown()
    time.sleep(0.1)
    
def test_add_prime_ka():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    sub = run_agent(name='ka_sub', base=base.KaSub)
    prime = run_agent(name='ka_prime', base=base.KaLocal)
    sub.add_prime_ka(prime)
    
    assert sub.get_attr('ka') == prime
   
    ns.shutdown()
    time.sleep(0.1)
    
def test_connect_sub_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    sub = run_agent(name='ka_sub', base=base.KaSub)
    prime = run_agent(name='ka_prime', base=base.KaLocal)
    sub.add_prime_ka(prime)
    prime.set_attr(subagent_addrs={'ka_sub': {}})
    prime.connect_sub_executor(sub, 'ka_sub')
    
    assert sub.get_attr('_executor_alias') == 'executor_ka_sub'
    assert prime.get_attr('subagent_addrs')['ka_sub']['executor'][0] == 'executor_ka_sub'
    
    ns.shutdown()
    time.sleep(0.1)    
    
def test_connect_sub_shutdown():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    sub = run_agent(name='ka_sub', base=base.KaSub)
    prime = run_agent(name='ka_prime', base=base.KaLocal)
    sub.add_prime_ka(prime)
    prime.set_attr(subagent_addrs={'ka_sub': {}})
    prime.connect_sub_shutdown(sub, 'ka_sub')
    
    assert sub.get_attr('_shutdown_alias') == 'shutdown_ka_sub'
    assert prime.get_attr('subagent_addrs')['ka_sub']['shutdown'][0] == 'shutdown_ka_sub'
    
    ns.shutdown()
    time.sleep(0.1)    
    
def test_connect_sub_heartbeat():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    sub = run_agent(name='ka_sub', base=base.KaSub)
    prime = run_agent(name='ka_prime', base=base.KaLocal)
    sub.add_prime_ka(prime)
    prime.set_attr(subagent_addrs={'ka_sub': {}})
    prime.connect_sub_heartbeat(sub, 'ka_sub')
    
    assert sub.get_attr('_heartbeat_alias') == 'heartbeat_ka_sub'
    assert prime.get_attr('subagent_addrs')['ka_sub']['heartbeat'][0] == 'heartbeat_ka_sub'
    
    ns.shutdown()
    time.sleep(0.1)     
   
    
def test_connect_sub_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    prime = run_agent(name='ka_prime', base=base.KaLocal)
    prime.connect_sub_agent('ka_sub1')
    time.sleep(0.1)
    assert prime.get_attr('subagent_addrs')['ka_sub1']['executor'][0] == 'executor_ka_sub1'
    assert prime.get_attr('subagent_addrs')['ka_sub1']['shutdown'][0] == 'shutdown_ka_sub1'
    assert prime.get_attr('subagent_addrs')['ka_sub1']['heartbeat'][0] == 'heartbeat_ka_sub1'
    
    ns.shutdown()
    time.sleep(0.1)  


def test_sub_shutdown_handler():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    prime = run_agent(name='ka_prime', base=base.KaLocal)

    prime.connect_sub_agent('ka_sub')


    assert ns.agents() == ['ka_prime','ka_sub']    
    prime.send_sub_shutdown()
    time.sleep(0.1)
    assert ns.agents() == ['ka_prime']
    
    ns.shutdown()
    time.sleep(0.1)      
    
def test_handler_sub_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    prime = run_agent(name='ka_prime', base=base.KaLocal)
    prime.connect_sub_agent('ka_sub1')
    prime.set_attr(problem=problem)
    prime.set_attr(_design_variables=dvs)
    prime.set_attr(current_design_variables={'x0': 0.650, 'x1': 0.650, 'x2': 0.4})
    prime.send_sub_executor('ka_sub1')
    
    sub = ns.proxy('ka_sub1')
    assert sub.get_attr('problem').benchmark_name == 'dtlz1'
    assert sub.get_attr('_entry_name') == 'core_[0.65,0.65,0.4]'
    assert sub.get_attr('_entry') == {'design variables': {'x0': 0.65, 'x1': 0.65, 'x2': 0.4}, 
                                      'objective functions': {'f0': 0.4225000000000002, 'f1': 0.22750000000000012, 'f2': 0.35000000000000014}, 
                                      'constraints': {}}   
    assert sub.get_attr('complete') == True

    ns.shutdown()
    time.sleep(0.1)
    
def test_parallel_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    prime = run_agent(name='ka_prime', base=base.KaLocal)
    prime.set_attr(problem=problem)
    prime.set_attr(_design_variables=dvs)
    prime.set_attr(current_design_variables={'x0': 0.650, 'x1': 0.650, 'x2': 0.4})
    prime.parallel_executor()
    
    sub = ns.proxy('ka_prime_sub_0')
    assert sub.get_attr('problem').benchmark_name == 'dtlz1'
    assert sub.get_attr('_entry_name') == 'core_[0.65,0.65,0.4]'
    assert sub.get_attr('_entry') == {'design variables': {'x0': 0.65, 'x1': 0.65, 'x2': 0.4}, 
                                      'objective functions': {'f0': 0.4225000000000002, 'f1': 0.22750000000000012, 'f2': 0.35000000000000014}, 
                                      'constraints': {}}
    assert sub.get_attr('complete') == True
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_parallel_executor_complete():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    prime = run_agent(name='ka_prime', base=base.KaLocal)
    prime.set_attr(problem=problem)
    prime.set_attr(_design_variables=dvs)
    prime.set_attr(current_design_variables={'x0': 0.650, 'x1': 0.650, 'x2': 0.4})

    prime.parallel_executor()
    assert prime.parallel_executor_complete() == True
    
    ns.shutdown()
    time.sleep(0.1)    
    
def test_parallel_executor_complete_checker():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    prime = run_agent(name='ka_prime', base=base.KaLocal)
    prime.set_attr(problem=problem)
    prime.set_attr(_design_variables=dvs)
    prime.set_attr(current_design_variables={'x0': 0.650, 'x1': 0.650, 'x2': 0.4})
    
    prime.parallel_executor()
    assert prime.parallel_executor_complete() == True
    
    ns.shutdown()
    time.sleep(0.1)     