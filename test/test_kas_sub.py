import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import mabs.ka.ka_s.base as base
import time
from mabs.utils.problem import BenchmarkProblem
import pickle

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
    assert prime.get_attr('subagent_addrs') == {'ka_sub': {}}
   
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
    sub.connect_sub_executor()
    
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
    sub.connect_sub_shutdown()
    
    assert sub.get_attr('_shutdown_alias') == 'shutdown_ka_sub'
    assert prime.get_attr('subagent_addrs')['ka_sub']['shutdown'][0] == 'shutdown_ka_sub'
    
    ns.shutdown()
    time.sleep(0.1)    
    
def test_connect_sub_writer():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    sub = run_agent(name='ka_sub', base=base.KaSub)
    prime = run_agent(name='ka_prime', base=base.KaLocal)
    sub.add_prime_ka(prime)
    sub.connect_sub_writer()
    
    assert sub.get_attr('_writer_alias') == 'writer_ka_sub'
    assert prime.get_attr('subagent_addrs')['ka_sub']['writer'][0] == 'writer_ka_sub'
    
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
    assert prime.get_attr('subagent_addrs')['ka_sub1']['writer'][0] == 'writer_ka_sub1'
    assert prime.get_attr('subagent_addrs')['ka_sub1']['shutdown'][0] == 'shutdown_ka_sub1'
    
    ns.shutdown()
    time.sleep(0.1)  

def test_sub_write_to_prime():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    sub = run_agent(name='ka_sub', base=base.KaSub)
    prime = run_agent(name='ka_prime', base=base.KaLocal)
    sub.set_attr(_entry_name='test')
    sub.set_attr(_entry= {'test': 'test1'})
    
    sub.add_prime_ka(prime)
    sub.connect_sub_writer()
    
    sub.write_to_prime()
    assert prime.get_attr('subagent_addrs')['ka_sub']['performing action'] == False
    assert prime.get_attr('subagent_addrs')['ka_sub']['entry'] == {'test': 'test1'}
    assert prime.get_attr('subagent_addrs')['ka_sub']['entry name'] == 'test'    
    
    ns.shutdown()
    time.sleep(0.1)       
    
def test_sub_shutdown_handler():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()

    sub = run_agent(name='ka_sub', base=base.KaSub)
    prime = run_agent(name='ka_prime', base=base.KaLocal)

    sub.add_prime_ka(prime)
    sub.connect_sub_shutdown()

    assert ns.agents() == ['ka_sub','ka_prime']    
    prime.send_shutdown()
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
    prime.parallel_executor('core_[0.65,0.65,0.4]')
    
    sub = ns.proxy('ka_sub_core_[0.65,0.65,0.4]')
    assert sub.get_attr('problem').benchmark_name == 'dtlz1'
    assert sub.get_attr('_entry_name') == 'core_[0.65,0.65,0.4]'
    assert sub.get_attr('_entry') == {'design variables': {'x0': 0.65, 'x1': 0.65, 'x2': 0.4}, 
                                      'objective functions': {'f0': 0.4225000000000002, 'f1': 0.22750000000000012, 'f2': 0.35000000000000014}, 
                                      'constraints': {}}

    assert prime.get_attr('subagent_addrs')['ka_sub_core_[0.65,0.65,0.4]']['entry name'] == 'core_[0.65,0.65,0.4]'
    assert prime.get_attr('subagent_addrs')['ka_sub_core_[0.65,0.65,0.4]']['entry'] == {'design variables': {'x0': 0.65, 'x1': 0.65, 'x2': 0.4}, 
                                      'objective functions': {'f0': 0.4225000000000002, 'f1': 0.22750000000000012, 'f2': 0.35000000000000014}, 
                                      'constraints': {}}    
    
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
    prime.parallel_executor('core_[0.65,0.65,0.4]', debug_wait=True, debug_wait_time=.1)
    assert prime.parallel_executor_complete() == False
    time.sleep(0.1)
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
    prime.parallel_executor('core_[0.65,0.65,0.4]', debug_wait=True, debug_wait_time=.2)
    assert prime.parallel_executor_complete() == False
    prime.parallel_executor_complete_checker()
    assert prime.parallel_executor_complete() == True
    
    ns.shutdown()
    time.sleep(0.1)     
