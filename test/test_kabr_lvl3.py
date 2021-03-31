from src.ka.ka_brs.level3 import KaBrLevel3
import src.bb.blackboard as blackboard
import src.bb.blackboard_optimization as bb_opt
import time
from osbrain import run_nameserver
from osbrain import run_agent
import pickle

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)
    
def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br3', base=KaBrLevel3)
    assert ka_br2.get_attr('bb_lvl_write') == 2
    assert ka_br2.get_attr('bb_lvl_read') == 3
    assert ka_br2.get_attr('_trigger_val_base') == 3.00000000001
    
    ns.shutdown()
    time.sleep(0.05)

def test_update_abstract_levels():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv)  
    
    bb.connect_agent(KaBrLevel3, 'ka_br_lvl3')
    br = ns.proxy('ka_br_lvl3')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.45]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11,'burnup' : 61.12}}, panel='new')
    bb.update_abstract_lvl(2, 'core_[65.0, 65.0, 0.45]', {'valid': True}, panel='old')
    
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11,'burnup' : 61.12}}, panel='old')
    bb.update_abstract_lvl(2, 'core_[65.0, 65.0, 0.42]', {'valid': True}, panel='new')
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})

    br.update_abstract_levels()
    assert [x for x in br.get_attr('lvl_read').keys()]  == ['core_[65.0, 65.0, 0.45]']
    assert [x for x in br.get_attr('lvl_write').keys()] == ['core_[65.0, 65.0, 0.42]']
    assert [x for x in br.get_attr('_lvl_data').keys()] == ['core_[65.0, 65.0, 0.45]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_determine_validity():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}    
    objs={'reactivity swing': {'ll':0, 'ul':20000, 'goal':'lt', 'variable type': float},
          'burnup':           {'ll':0,  'ul':200,  'goal':'gt', 'variable type': float},
          'num exp':          {'ll':0,  'ul':10,  'goal':'gt', 'variable type': int},}
    cons={'eol keff':    {'ll': 1.0, 'ul': 1.5, 'variable type': float},
          'power':       {'ll': 0.0, 'ul':1.0, 'variable type': list, 'goal type': 'max', 'length': 3}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv, constraints=cons) 

    bb.connect_agent(KaBrLevel3, 'ka_br3')
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br3')
    
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0, 'num exp': 9},
                                                          'constraints': {'eol keff': 1.1, 'power': [0.1,0.2,0.3]}}, panel='new')
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.50]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50},
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 250.0, 'num exp': 9},
                                                          'constraints': {'eol keff': 1.1, 'power': [0.1,0.2,0.3]}}, panel='new')
    
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.55]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0, 'num exp': 9},
                                                          'constraints': {'eol keff': 1.1, 'power': [0.1,0.2,1.1]}}, panel='new')  
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.65]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0, 'num exp': 12},
                                                          'constraints': {'eol keff': 1.1, 'power': [0.1,0.2,1.1]}}, panel='new')    
    bb.publish_trigger()          
    bb.publish_trigger()
    bool_ = br.determine_validity('core_[65.0, 65.0, 0.42]')
    assert bool_ == (True, None)
    bool_ = br.determine_validity('core_[70.0, 60.0, 0.50]')
    assert bool_ == (False, None)
    bool_ = br.determine_validity('core_[70.0, 60.0, 0.55]')
    assert bool_ == (False, None)
    bool_ = br.determine_validity('core_[70.0, 60.0, 0.65]')
    assert bool_ == (False, None)          
    ns.shutdown()
    time.sleep(0.05)
    
def test_determine_validity_constraint():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}    
    objs={'reactivity swing': {'ll':0, 'ul':20000, 'goal':'lt', 'variable type': float},
          'burnup':           {'ll':0,  'ul':200,  'goal':'gt', 'variable type': float}}
    cons={'eol keff':    {'ll': 1.0, 'ul': 1.5, 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv, constraints=cons) 
    bb.connect_agent(KaBrLevel3, 'ka_br3')
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br3')
    
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0},
                                                          'constraints': {'eol keff': 1.1}}, panel='new')
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.50]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50},
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0},
                                                          'constraints': {'eol keff': 0.9}}, panel='new')
    
    bb.publish_trigger()
    bool_ = br.determine_validity('core_[65.0, 65.0, 0.42]')
    assert bool_ == (True, None)
    bool_ = br.determine_validity('core_[70.0, 60.0, 0.50]')
    assert bool_ == (False, None)

    ns.shutdown()
    time.sleep(0.05)
    
def test_read_bb_lvl():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}    
    objs={'reactivity swing': {'ll':0, 'ul':20000, 'goal':'lt', 'variable type': float},
          'burnup':           {'ll':0,  'ul':200,  'goal':'gt', 'variable type': float}}
    cons={'eol keff':    {'ll': 1.0, 'ul': 1.5, 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv, constraints=cons) 
    bb.connect_agent(KaBrLevel3, 'ka_br3')
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br3')
    
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0},
                                                          'constraints': {'eol keff': 1.1}}, panel='new')
    
    bb.publish_trigger()
    time.sleep(0.05)
    br.read_bb_lvl()
    
    assert br.get_attr('_entry') == {'valid': True}
    assert br.get_attr('_entry_name') == 'core_[65.0, 65.0, 0.42]'

    ns.shutdown()
    time.sleep(0.05)    

def test_handler_trigger_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    br = run_agent(name='ka_br3', base=KaBrLevel3)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}    
    objs={'cycle length':     {'ll':300, 'ul':400,  'goal':'gt', 'variable type': float},
           'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
           'pu mass':          {'ll':500, 'ul':1000, 'goal':'lt', 'variable type': float},
           'burnup':           {'ll':25,  'ul':75,   'goal':'gt', 'variable type': float}}
    cons={'eol keff':    {'ll': 1.0, 'ul': 1.5, 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv, constraints=cons)     
    bb.initialize_abstract_level_3()
    br.add_blackboard(bb)
    br.connect_trigger()
    br.connect_writer()
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

    bb.remove_bb_entry(3, 'core_1', panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 250.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='new')
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br3': 0}, 2: {'ka_br3': 3.00000000001}, 3:{'ka_br3':0}}   
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_handler_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}    
    objs={'keff':          {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
          'void_coeff':    {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float},
          'doppler_coeff': {'ll':-1.0,  'ul':-0.6, 'goal':'lt', 'variable type': float}}
    cons={'eol keff':    {'ll': 1.0, 'ul': 1.5, 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv, constraints=cons)      
    
    bb.connect_agent(KaBrLevel3, 'ka_br3')
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br3')
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4},
                                         'objective functions': {'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.75},
                                        'constraints': {'eol keff': 1.1}}, panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.80},
                                        'constraints': {'eol keff': 1.1}}, panel='new')
    bb.update_abstract_lvl(3, 'core_3', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4},
                                         'objective functions': {'keff': 0.9, 'void_coeff': -150.0, 'doppler_coeff': -0.75},
                                        'constraints': {'eol keff': 1.1}}, panel='new')

    bb.set_attr(_ka_to_execute=('ka_br3', 10.0))
    bb.publish_trigger()
    time.sleep(0.05)
    bb.send_executor()
    time.sleep(0.05)    
    
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{'core_1': {'valid': True},
                                                              'core_2': {'valid': True}}, 'old': {}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [] 

    ns.shutdown()
    time.sleep(0.05)

def test_add_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br3 = run_agent(name='ka_br', base=KaBrLevel3)
    ka_br3.add_entry(('core_1', None))
    
    assert ka_br3.get_attr('_entry') == {'valid': True}
    assert ka_br3.get_attr('_entry_name') == 'core_1'
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_determine_validity_list():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}    
    objs={'keff':            {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
          'assembly power':  {'ll': 0.5, 'ul': 7.5, 'goal':'lt', 'variable type': list, 'goal type': 'avg'},
          'burnup':          {'ll': [0.0,0.0], 'ul': [100.0,100.0], 'goal': 'lt', 'goal type': 'max','variable type': list}}
    cons={'eol keff':    {'ll': 1.0, 'ul': 1.5, 'variable type': float},
          'burnup1':          {'ll': 0.0, 'ul': 100.0, 'goal type': 'max', 'variable type': list}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv, constraints=cons)     

    bb.connect_agent(KaBrLevel3, 'ka_br3')
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br3')

    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.05, 'assembly power': [0.6, 0.6, 0.8], 'burnup': [10.0, 10.0]},
                                         'constraints': {'eol keff': 1.1, 'burnup1': [10.0, 10.0]}}, panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.04, 'assembly power': [0.4, 0.6, 0.8], 'burnup': [10.0, 10.0]},
                                         'constraints': {'eol keff': 1.1, 'burnup1': [10.0, 10.0] }}, panel='new')    
    bb.update_abstract_lvl(3, 'core_3', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.05, 'assembly power': [0.6, 0.6, 0.8], 'burnup': [110.0, 10.0]},
                                         'constraints': {'eol keff': 1.1, 'burnup1': [10.0, 10.0]}}, panel='new')   
    bb.update_abstract_lvl(3, 'core_4', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.05, 'assembly power': [0.6, 0.6, 0.8], 'burnup': [10.0, 10.0]},
                                         'constraints': {'eol keff': 1.1, 'burnup1': [10.0, 110.0]}}, panel='new')   
    bb.publish_trigger()
    bool_ = br.determine_validity('core_1')
    assert bool_ == (True, None)
    bool_ = br.determine_validity('core_2')
    assert bool_ == (False, None)
    bool_ = br.determine_validity('core_3')
    assert bool_ == (False, None)
    bool_ = br.determine_validity('core_4')
    assert bool_ == (False, None)
    ns.shutdown()
    time.sleep(0.05)