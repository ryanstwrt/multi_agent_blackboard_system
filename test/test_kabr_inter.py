from osbrain import run_nameserver
from osbrain import run_agent
import mabs.bb.blackboard as blackboard
import mabs.bb.blackboard_optimization as bb_opt
from mabs.ka.ka_brs.inter_bb import InterBB 
from mabs.utils.problem import BenchmarkProblem
import time

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
    br = run_agent(name='ka_br_inter', base=InterBB)
    assert br.get_attr('bb_lvl_write') == 3
    assert br.get_attr('bb_lvl_read') == 1
    assert br.get_attr('_trigger_val_base') == 6.00000000001
    assert br.get_attr('_class') == 'reader inter'
    assert br.get_attr('_entries_moved') == []
    assert br.get_attr('_new_entry_format') == {}
    
    ns.shutdown()
    time.sleep(0.05)

def test_add_bb():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb_prime = run_agent(name='bb', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3()    
    br = run_agent(name='ka_br_inter', base=InterBB)
    
    br.connect_bb_to_write(bb_prime)    
    bb_writer = bb_prime.get_attr('agent_addrs')['ka_br_inter']['writer']
    
    assert br.get_attr('_writer_alias') == 'writer_ka_br_inter'
    assert br.get_attr('_writer_alias') == bb_writer[0]
    assert br.get_attr('_writer_addr') == bb_writer[1]

    ns.shutdown()
    time.sleep(0.05) 
    
def test_connect_ka():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    objs = {'f{}'.format(x+1): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}        
    cons = {'f0': {'ll':0.0, 'ul':1000, 'variable type': float}}           
    bb_prime = run_agent(name='bb_prime', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints=cons)
    bb_prime.set_attr(problem=problem)
    bb_prime.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    
    objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}        
    cons = {'f3': {'ll':0.0, 'ul':1000, 'variable type': float}}     
    bb_sub = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb_sub.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints=cons)
    bb_sub.set_attr(problem=problem)    
    bb_sub.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    bb_sub.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_prime})  
    
    ka = bb_sub.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')    

    assert br.get_attr('_design_variables') == {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
    assert br.get_attr('_objectives') == {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)} 
    assert br.get_attr('_constraints') ==  {'f3': {'ll':0.0, 'ul':1000, 'variable type': float}} 
    assert br.get_attr('_new_entry_format') == {'design variables': {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)},
                                                'objective functions': {'f{}'.format(x+1): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)},
                                                'constraints': {'f0': {'ll':0.0, 'ul':1000, 'variable type': float}}}
    
    assert br.get_attr('_writer_addr') == bb_prime.get_attr('agent_addrs')['ka_br_inter']['writer'][1]

    ns.shutdown()
    time.sleep(0.05) 
    
def test_write_to_bb():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb_prime = run_agent(name='bb_prime', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_prime.set_attr(problem=problem)
    bb_prime.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    
    bb_sub = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb_sub.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_sub.set_attr(problem=problem)    
    bb_sub.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    bb_sub.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_prime})           
  
    ka = bb_sub.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')    
    bb_writer = bb_prime.get_attr('agent_addrs')['ka_br_inter']['writer']
    
    name = 'core_1'
    entry = {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
             'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
             'constraints': {}}
    
    br.write_to_bb(3, name, entry, panel='new')
    br.get_attr('name')
    assert bb_prime.get_attr('abstract_lvls')['level 3']['new']['core_1'] == {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                              'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
                                                                              'constraints': {}}
    ns.shutdown()
    time.sleep(0.05) 
    
def test_format_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
        
    objs = {'f{}'.format(x+1): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}        
    cons = {'f0': {'ll':0.0, 'ul':1000, 'variable type': float}}           
    bb_prime = run_agent(name='bb_prime', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints=cons)
    bb_prime.set_attr(problem=problem)
    bb_prime.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}        
    cons = {'f3': {'ll':0.0, 'ul':1000, 'variable type': float}}     
    bb_sub = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb_sub.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints=cons)
    bb_sub.set_attr(problem=problem)    
    bb_sub.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    bb_sub.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_prime})     
  
    ka = bb_sub.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    data = {'core_[0.25, 0.5, 0.75]': {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
            'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
            'constraints': {'f3':100.0}}}
    
    br.set_attr(_lvl_data=data)
    entry = br.format_entry('core_[0.25, 0.5, 0.75]')
    assert entry == {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                     'objective functions': {f'f{num+1}':x for num,x in enumerate([50.0,75.0,100.0])},
                     'constraints': {'f0':25.0}}
    ns.shutdown()
    time.sleep(0.05) 
    
def test_format_entry_missing_values():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
        
    objs = {'f{}'.format(x+1): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}        
    cons = {'c3': {'ll':0.0, 'ul':1000, 'variable type': list, 'goal type': 'max', 'length': 3}}           
    bb_prime = run_agent(name='bb_prime', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints=cons)
    bb_prime.set_attr(problem=problem)
    bb_prime.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}        
    cons = {}     
    bb_sub = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb_sub.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints=cons)
    bb_sub.set_attr(problem=problem)    
    bb_sub.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    bb_sub.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_prime})     
  
    ka = bb_sub.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    data = {'core_[0.25, 0.5, 0.75]': {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
            'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
            'constraints': {'f3':100.0}}}
    
    br.set_attr(_lvl_data=data)
    entry = br.format_entry('core_[0.25, 0.5, 0.75]')
    assert entry == {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                     'objective functions': {f'f{num+1}':x for num,x in enumerate([50.0,75.0,100.0])},
                     'constraints': {'c3':[0.0,0.0,0.0]}}
    ns.shutdown()
    time.sleep(0.05)     
    
def test_handler_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb_prime = run_agent(name='bb_prime', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_prime.set_attr(problem=problem)
    bb_prime.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})

    bb_sub = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb_sub.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_sub.set_attr(problem=problem)    
    bb_sub.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    bb_sub.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_prime})     
  
    ka = bb_sub.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    bb_sub.update_abstract_lvl(3, 'core_[0.25, 0.5, 0.75]', {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
                                                                'constraints': {}},  panel='old')
    bb_sub.update_abstract_lvl(1, 'core_[0.25, 0.5, 0.75]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb_sub.publish_trigger()
    time.sleep(0.05)
    assert bb_sub.get_attr('_kaar') == {1: {'ka_br_inter': 6.00000000001}}
    br.set_attr(_entries_moved=['core_[0.25, 0.5, 0.75]'])
    bb_sub.publish_trigger()
    time.sleep(0.05)
    assert bb_sub.get_attr('_kaar') == {1: {'ka_br_inter': 6.00000000001},
                                        2: {'ka_br_inter': 0.0}} 
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_handler_executor_lower_to_upper():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb_prime = run_agent(name='bb_prime', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_prime.set_attr(problem=problem)
    bb_prime.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})

    bb_sub = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb_sub.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_sub.set_attr(problem=problem)    
    bb_sub.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    bb_sub.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_prime})    
  
    ka = bb_sub.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    bb_sub.update_abstract_lvl(3, 'core_[0.25, 0.5, 0.75]', {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
                                                                'constraints': {}},  panel='old')
    bb_sub.update_abstract_lvl(1, 'core_[0.25, 0.5, 0.75]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb_sub.publish_trigger()
    time.sleep(0.05)
    bb_sub.controller()
    assert bb_sub.get_attr('_ka_to_execute') == ('ka_br_inter', 6.00000000001)
    bb_sub.send_executor()
    time.sleep(0.05) 
    
    assert bb_prime.get_attr('abstract_lvls')['level 3']['new']['core_[0.25, 0.5, 0.75]'] == {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                                             'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
                                                                                             'constraints': {}}

    ns.shutdown()
    time.sleep(0.05) 
    
def test_handler_executor_upper_to_lower():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    
    bb_prime = run_agent(name='bb_prime', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_prime.set_attr(problem=problem)
    bb_prime.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})

    bb_sub = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb_sub.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_sub.set_attr(problem=problem)    
    bb_sub.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    bb_prime.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_sub})    
    
    ka = bb_sub.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    bb_prime.update_abstract_lvl(3, 'core_[0.25, 0.5, 0.75]', {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
                                                                'constraints': {}},  panel='old')
    bb_prime.update_abstract_lvl(1, 'core_[0.25, 0.5, 0.75]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb_prime.publish_trigger()
    time.sleep(0.05)
    bb_prime.controller()
    assert bb_prime.get_attr('_ka_to_execute') == ('ka_br_inter', 6.00000000001)
    bb_prime.send_executor()
    time.sleep(0.05) 
    
    assert bb_sub.get_attr('abstract_lvls')['level 3']['new']['core_[0.25, 0.5, 0.75]'] == {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                                             'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
                                                                                             'constraints': {}}

    ns.shutdown()
    time.sleep(0.05)     
    
def test_handler_executor_update_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    
    bb_prime = run_agent(name='bb_prime', base=bb_opt.BbOpt)
    bb_prime.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_prime.set_attr(problem=problem)
    bb_prime.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})

    bb_sub = run_agent(name='sub_bb', base=bb_opt.BbOpt)
    bb_sub.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb_sub.set_attr(problem=problem)    
    bb_sub.add_abstract_lvl(100, {'agent': str, 'hvi': float, 'time': float})
    bb_prime.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_sub})    
    
    ka = bb_sub.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    bb_prime.update_abstract_lvl(3, 'core_[0.25, 0.5, 0.75]', {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
                                                                'constraints': {}},  panel='old')
    bb_prime.update_abstract_lvl(1, 'core_[0.25, 0.5, 0.75]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb_sub.update_abstract_lvl(3, 'core_[0.25, 0.5, 0.75]', {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                'objective functions': {f'f{num}':x for num,x in enumerate([50.0,75.0,25.0])},
                                                                'constraints': {}},  panel='old')
    
    bb_prime.publish_trigger()
    time.sleep(0.05)
    bb_prime.controller()
    assert bb_prime.get_attr('_ka_to_execute') == ('ka_br_inter', 6.00000000001)
    bb_prime.send_executor()
    time.sleep(0.05) 
    
    assert bb_sub.get_attr('abstract_lvls')['level 3']['new']['core_[0.25, 0.5, 0.75]'] == {'design variables': {f'x{num}':x for num,x in enumerate([0.25,0.5,0.75])},
                                                                                             'objective functions': {f'f{num}':x for num,x in enumerate([25.0,50.0,75.0])},
                                                                                             'constraints': {}}

    ns.shutdown()
    time.sleep(0.05)         