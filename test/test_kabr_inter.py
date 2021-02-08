from osbrain import run_nameserver
from osbrain import run_agent
import src.bb.blackboard as blackboard
import src.bb.blackboard_optimization as bb_opt
from src.ka.ka_brs.inter_bb import InterBB 
import time


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
    bb = run_agent(name='sub_bb', base=bb_opt.SubBbOpt)
    bb.initialize_abstract_level_3()
    bb_master = run_agent(name='bb', base=bb_opt.BbOpt)
    bb_master.initialize_abstract_level_3()    
    br = run_agent(name='ka_br_inter', base=InterBB)
    
    br.connect_bb_to_write(bb_master)    
    bb_writer = bb_master.get_attr('agent_addrs')['ka_br_inter']['writer']
    
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
    bb_master = run_agent(name='bb', base=bb_opt.MasterBbOpt)
    bb_master.initialize_abstract_level_3()  
    bb = run_agent(name='sub_bb', base=bb_opt.SubBbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_master})    
  
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')    

    assert br.get_attr('_design_variables') == {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                                'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                                'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    assert br.get_attr('_objectives') == {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                                          'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    assert br.get_attr('_constraints') ==  {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'variable type': float},
                                            'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
    assert br.get_attr('_new_entry_format') == {'design variables': {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}},
                                               'objective functions': {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'goal': 'gt', 'variable type': float},
                                                                       'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}},
                                               'constraints': {
                            'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                            'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}}
    assert br.get_attr('_writer_addr') == bb_master.get_attr('agent_addrs')['ka_br_inter']['writer'][1]

    ns.shutdown()
    time.sleep(0.05) 
    
def test_write_to_bb():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb_master = run_agent(name='bb', base=bb_opt.MasterBbOpt)
    bb_master.initialize_abstract_level_3()  
    bb = run_agent(name='sub_bb', base=bb_opt.SubBbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_master})    
  
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')    
    bb_writer = bb_master.get_attr('agent_addrs')['ka_br_inter']['writer']
    
    name = 'core_1'
    entry = {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
             'objective functions': {'eol keff': 1.1, 'pu mass': 290.2},
             'constraints': {
                             'burnup': 69.0,
                             'reactivity swing': 1000.0}}
    
    br.write_to_bb(3, name, entry, panel='new')
    br.get_attr('name')
    assert bb_master.get_attr('abstract_lvls')['level 3']['new']['core_1'] == {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
             'objective functions': {'eol keff': 1.1, 'pu mass': 290.2},
             'constraints': {
                             'burnup': 69.0,
                             'reactivity swing': 1000.0}}
    ns.shutdown()
    time.sleep(0.05) 
    
def test_format_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb_master = run_agent(name='bb', base=bb_opt.MasterBbOpt)
    bb_master.initialize_abstract_level_3()  
    bb = run_agent(name='sub_bb', base=bb_opt.SubBbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_master})    
  
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    data = {'core_[65.0,65.0,0.4]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
             'objective functions': {'burnup': 69.0,
                                     'reactivity swing': 1000.0},
             'constraints': {'eol keff': 1.1,
                             'pu mass': 290.2}}}
    
    br.set_attr(_lvl_data=data)
    entry = br.format_entry('core_[65.0,65.0,0.4]')
    assert entry == {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                     'objective functions': {'eol keff': 1.1, 'pu mass': 290.2},
                     'constraints': {
                                     'burnup': 69.0,
                                     'reactivity swing': 1000.0}}
    ns.shutdown()
    time.sleep(0.05) 
    
def test_handler_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb_master = run_agent(name='bb', base=bb_opt.MasterBbOpt)
    bb_master.initialize_abstract_level_3()  
    bb = run_agent(name='sub_bb', base=bb_opt.SubBbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_master})    
  
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0},
                                                          'constraints': {'eol keff': 1.1, 'pu mass': 1500.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb.publish_trigger()
    time.sleep(0.05)
    assert bb.get_attr('_kaar') == {1: {'ka_br_inter': 6.00000000001}}
    br.set_attr(_entries_moved=['core_[65.0, 65.0, 0.42]'])
    bb.publish_trigger()
    time.sleep(0.05)
    assert bb.get_attr('_kaar') == {1: {'ka_br_inter': 6.00000000001},
                                    2: {'ka_br_inter': 0.0}} 
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_handler_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb_master = run_agent(name='bb', base=bb_opt.MasterBbOpt)
    bb_master.initialize_abstract_level_3()  
    bb = run_agent(name='sub_bb', base=bb_opt.SubBbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(InterBB, 'ka_br_inter', attr={'bb': bb_master})    
  
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br_inter')   
    
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0},
                                                          'constraints': {'eol keff': 1.1, 'pu mass': 1500.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_ka_to_execute') == ('ka_br_inter', 6.00000000001)
    bb.send_executor()
    time.sleep(0.05) 
    
    assert bb_master.get_attr('abstract_lvls')['level 3']['new']['core_[65.0, 65.0, 0.42]'] == {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'eol keff': 1.1, 'pu mass': 1500.0},
                                                          'constraints': { 'reactivity swing' : 750.0, 'burnup' : 75.0}}
    
    bb.publish_trigger()
    time.sleep(0.05)

    
    ns.shutdown()
    time.sleep(0.05) 