from osbrain import run_nameserver
from osbrain import run_agent
from mabs.ka.ka_brs.base import KaBr
import time
import mabs.bb.blackboard as blackboard
import mabs.bb.blackboard_optimization as bb_opt

def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_b = run_agent(name='ka_br', base=KaBr)
    assert ka_b.get_attr('bb_lvl_read') == 0
    assert ka_b.get_attr('bb_lvl_write') == 0
    assert ka_b.get_attr('bb_lvl_data') == 3  
    assert ka_b.get_attr('new_panel') == 'new'
    assert ka_b.get_attr('old_panel') == 'old'
    assert ka_b.get_attr('_num_entries') == 0
    assert ka_b.get_attr('_num_allowed_entries') == 25
    assert ka_b.get_attr('_trigger_val_base') == 0
    assert ka_b.get_attr('_objectives') == None
    assert ka_b.get_attr('_constraints') == None
    assert ka_b.get_attr('lvl_read') == {}
    assert ka_b.get_attr('lvl_write') == {}
    assert ka_b.get_attr('_lvl_data') == {}
    assert ka_b.get_attr('_class') == 'reader'
    assert ka_b.get_attr('agent_time') == 0
    assert ka_b.get_attr('agent_time') == 0
    assert ka_b.get_attr('_trigger_event') == 0 
    ns.shutdown()
    time.sleep(0.05)
    
def test_clear_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_b = run_agent(name='ka_br', base=KaBr)
    ka_b.set_attr(_entry={'valid': True})
    ka_b.set_attr(_entry_name='core_1')
    assert ka_b.get_attr('_entry') == {'valid': True}
    assert ka_b.get_attr('_entry_name') == 'core_1'
    ka_b.clear_entry()
    assert ka_b.get_attr('_entry') == None
    assert ka_b.get_attr('_entry_name') == None 
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_update_abstract_level():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_br', base=KaBr)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_b.set_attr(bb_lvl_read=1)
    ka_b.set_attr(bb_lvl_write=2)
    bb.add_abstract_lvl(1, {'valid': bool})
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new','old'])
    bb.add_abstract_lvl(3, {'valid': bool})
    bb.add_panel(3, ['new','old'])

    bb.update_abstract_lvl(1, 'core_1', {'valid': True})
    bb.update_abstract_lvl(2, 'core_2', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_4', {'valid': True}, panel='old')
    bb.update_abstract_lvl(3, 'core_3', {'valid': True}, panel='new')
    bb.update_abstract_lvl(3, 'core_5', {'valid': True}, panel='new')
    assert ka_b.update_abstract_level(1) ==  {'core_1': {'valid': True}}
    assert ka_b.update_abstract_level(2,panels=['new']) == {'core_2': {'valid': True}}
    assert ka_b.update_abstract_level(3,panels=['new','old']) == {'core_3': {'valid': True}, 'core_5': {'valid': True}}
    ka_b.set_attr(lvl_dat={})
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_read_bb_lvl():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives={'reactivity swing': {'ll':0, 'ul':20000, 'goal':'lt', 'variable type': float},
                                               'burnup':           {'ll':0,  'ul':200,  'goal':'gt', 'variable type': float}},
                                   constraints={'eol keff':    {'ll': 1.0, 'ul': 1.5, 'variable type': float}})
    bb.connect_agent(KaBr, 'ka_br3')
    br = bb.get_attr('_proxy_server').proxy('ka_br3')
    br.set_attr(bb_lvl_write=2)
    br.set_attr(bb_lvl_read=3)
    bb_read = br.read_bb_lvl()
    assert bb_read == False    
    br.set_attr(lvl_read={'core_[65.0, 65.0, 0.42]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0},
                                                          'constraints': {'eol keff': 1.1}}})

    bb_read = br.read_bb_lvl()
    assert bb_read == True

    ns.shutdown()
    time.sleep(0.05)      
    
def test_handler_trigger_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    objs = {'cycle length':     {'ll':300, 'ul':400,  'goal':'gt', 'variable type': float},
            'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'pu mass':          {'ll':500, 'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':25,  'ul':75,   'goal':'gt', 'variable type': float}}

    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv)     
    bb.connect_agent(KaBr, 'ka_br3')
    br = bb.get_attr('_proxy_server').proxy('ka_br3')
    br.set_attr(bb_lvl_write=2)
    br.set_attr(bb_lvl_read=3)    
    br.set_attr(_trigger_val_base=3.00000000001)    
    
    br.set_attr(_objectives={'cycle length':     {'ll':300, 'ul':400,  'goal':'gt', 'variable type': float},
                             'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
                             'pu mass':          {'ll':500, 'ul':1000, 'goal':'lt', 'variable type': float},
                             'burnup':           {'ll':25,  'ul':75,   'goal':'gt', 'variable type': float}})
    br.set_attr(_num_allowed_entries=1)

    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br3': 0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='new')
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br3': 0}, 2: {'ka_br3': 3.00000000001}}   
    assert bb.get_attr('_ka_to_execute') == ('ka_br3', 3.00000000001)
    
    ns.shutdown()
    time.sleep(0.05) 