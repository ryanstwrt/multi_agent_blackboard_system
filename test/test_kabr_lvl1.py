from src.ka.ka_brs.level1 import KaBrLevel1
import time
import src.bb.blackboard as blackboard
import src.bb.blackboard_optimization as bb_opt
from osbrain import run_nameserver
from osbrain import run_agent
import src.utils.utilities as utils
    
def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=KaBrLevel1)
    assert ka_br1.get_attr('bb_lvl_write') == 1
    assert ka_br1.get_attr('bb_lvl_read') == 1
    assert ka_br1.get_attr('_trigger_val_base') == 6.00000000003
    assert ka_br1.get_attr('_pf_size') == 1
    assert ka_br1.get_attr('_upper_objective_reference_point') == None
    assert ka_br1.get_attr('_lower_objective_reference_point') == None
    assert ka_br1.get_attr('_hvi_dict') == {}
    assert ka_br1.get_attr('_lvl_data') == {}
    assert ka_br1.get_attr('_designs_to_remove') == []
    assert ka_br1.get_attr('_class') == 'reader level 1'
    assert ka_br1.get_attr('pf_increase') == 1.25
    assert ka_br1.get_attr('total_pf_size') == 100
    assert ka_br1.get_attr('_previous_pf') == {} 
    assert ka_br1.get_attr('dci') == False
    assert ka_br1.get_attr('dci_div') == None
    assert ka_br1.get_attr('_nadir_point') == None
    assert ka_br1.get_attr('_ideal_point') == None
    assert ka_br1.get_attr('pareto_sorter') == 'non-dominated'

    ns.shutdown()
    time.sleep(0.05)    

def test_update_abstract_levels():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)

    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv)      
    
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    br = ns.proxy('ka_br_lvl1')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.45]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11,'burnup' : 61.12}}, panel='new')
    bb.update_abstract_lvl(2, 'core_[65.0, 65.0, 0.45]', {'valid': True}, panel='old')
    
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11,'burnup' : 61.12}}, panel='old')
    bb.update_abstract_lvl(2, 'core_[65.0, 65.0, 0.42]', {'valid': True}, panel='new')
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})

    br.update_abstract_levels()
    assert [x for x in br.get_attr('lvl_read').keys()]  == ['core_[65.0, 65.0, 0.42]']
    assert [x for x in br.get_attr('lvl_write').keys()] == ['core_[65.0, 65.0, 0.42]']
    assert [x for x in br.get_attr('_lvl_data').keys()] == ['core_[65.0, 65.0, 0.45]', 'core_[65.0, 65.0, 0.42]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv)  
    
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    br = ns.proxy('ka_br_lvl1')
    br.set_attr(_num_allowed_entries=1)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.50]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50},
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 60.0, 0.50]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br_lvl1': 6.00000000003}}
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl1', 6.00000000003)

    ns.shutdown()
    time.sleep(0.05)       
    
def test_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv)  
    bb.initialize_metadata_level()
    
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    br = ns.proxy('ka_br_lvl1')
    br.set_attr(_lower_objective_reference_point=[0,0])
    br.set_attr(_upper_objective_reference_point=[1,1])
    br.set_attr(pareto_sorter='hvi')

    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.50]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50},
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[70.0, 60.0, 0.50]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[75.0, 55.0, 0.30]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                          'objective functions': {'reactivity swing' : 250.0, 'burnup' : 25.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[75.0, 55.0, 0.30]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    bb.send_executor()
    time.sleep(0.15) 
    assert br.get_attr('_hvi_dict') == {'core_[65.0, 65.0, 0.42]': 0.0625, 'core_[70.0, 60.0, 0.50]': 0.0625,
                                       'core_[75.0, 55.0, 0.30]': 0.0625}
    assert br.get_attr('_pf_size') == 3
    assert br.get_attr('_hvi_dict') == {'core_[65.0, 65.0, 0.42]': 0.0625, 'core_[70.0, 60.0, 0.50]': 0.0625,
                                       'core_[75.0, 55.0, 0.30]': 0.0625}
    
    bb.update_abstract_lvl(3, 'core_[55.0, 55.0, 0.30]', {'design variables': {'height': 55.0, 'smear': 55.0, 'pu_content': 0.50},
                                                          'objective functions': {'reactivity swing' : 300.0, 'burnup' : 24.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[55.0, 55.0, 0.30]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    bb.send_executor()
    time.sleep(0.05) 
    assert br.get_attr('_pf_size') == 3
    
    assert br.get_attr('_hvi_dict') == {'core_[65.0, 65.0, 0.42]': 0.0625, 'core_[70.0, 60.0, 0.50]': 0.0625,
                                       'core_[75.0, 55.0, 0.30]': 0.0625}
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[75.0, 55.0, 0.30]':{'pareto type' : 'pareto', 'fitness function' : 1.0},
                                                      'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                                                      'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}}

    ns.shutdown()
    time.sleep(0.05)  

    
def test_calculate_hvi():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=KaBrLevel1)
    ka_br1.set_attr(_lower_objective_reference_point=[0,0])
    ka_br1.set_attr(_upper_objective_reference_point=[1,1])
    pf = [[0.75,0.25], [0.5,0.5], [0.25,0.75]]
    hvi = ka_br1.calculate_hvi(pf)
    
    assert hvi == 0.375
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_calculate_hvi_contribution():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=KaBrLevel1)
    ka_br1.set_attr(_lower_objective_reference_point=[0,0])
    ka_br1.set_attr(_upper_objective_reference_point=[1,1])
    ka_br1.set_attr(lvl_read={'core_[75.0, 55.0, 0.30]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}})
    ka_br1.set_attr(_lvl_data={'core_[65.0, 65.0, 0.42]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                           'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0}},
                               'core_[70.0, 60.0, 0.50]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0}},
                               'core_[75.0, 55.0, 0.30]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 250.0, 'burnup' : 25.0}}})
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float}}
    ka_br1.set_attr(_objectives=objs)
    ka_br1.calculate_hvi_contribution()

    assert ka_br1.get_attr('_hvi_dict') == {'core_[65.0, 65.0, 0.42]': 0.0625, 
                                            'core_[70.0, 60.0, 0.50]': 0.0625,
                                            'core_[75.0, 55.0, 0.30]': 0.0625}
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_calculate_hvi_contribution_equal_to():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=KaBrLevel1)
    ka_br1.set_attr(_lower_objective_reference_point=[0,0,0])
    ka_br1.set_attr(_upper_objective_reference_point=[1,1,1])
    ka_br1.set_attr(lvl_read={'core_[75.0, 55.0, 0.30]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}})
    ka_br1.set_attr(_lvl_data={'core_[65.0, 65.0, 0.42]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                           'objective functions': {'reactivity swing' : 250.0, 'burnup' : 25.0, 'keff': 1.05}},
                               'core_[75.0, 55.0, 0.30]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 250.0, 'burnup' : 25.0, 'keff': 1.15}}})
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float},
            'keff':             {'ll':1.0,   'ul':1.2, 'target':1.10, 'goal':'et', 'variable type': float},}
    ka_br1.set_attr(_objectives=objs)
    ka_br1.calculate_hvi_contribution()

    assert ka_br1.get_attr('_hvi_dict') == {'core_[65.0, 65.0, 0.42]': 0.09375, 
                                            'core_[75.0, 55.0, 0.30]': 0.09375}
    
    ns.shutdown()
    time.sleep(0.05)

def test_calculate_hvi_contribution_list():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=KaBrLevel1)
    ka_br1.set_attr(_lower_objective_reference_point=[0,0,0])
    ka_br1.set_attr(_upper_objective_reference_point=[1,1,1])
    ka_br1.set_attr(lvl_read={'core_[75.0, 55.0, 0.30]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}})
    ka_br1.set_attr(_lvl_data={'core_[65.0, 65.0, 0.42]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                           'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0, 'power avg':[2.5,2.5,2.5]}},
                               'core_[70.0, 60.0, 0.50]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0, 'power avg':[5.0,5.0,5.0]}},
                               'core_[75.0, 55.0, 0.30]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 250.0, 'burnup' : 25.0, 'power avg':[7.5,7.5,7.5]}}})
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float},
            'power avg':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'avg'}}
    ka_br1.set_attr(_objectives=objs)
    ka_br1.calculate_hvi_contribution()

    assert ka_br1.get_attr('_hvi_dict') == {'core_[65.0, 65.0, 0.42]': 0.078125, 
                                            'core_[70.0, 60.0, 0.50]': 0.046875,
                                            'core_[75.0, 55.0, 0.30]': 0.015625}
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_remove_dominated_entries():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    ka_br1 = ns.proxy('ka_br_lvl1')
    ka_br1.set_attr(lvl_read={'core_[75.0, 55.0, 0.30]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}})
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(1, 'core_[70.0, 60.0, 0.50]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(1, 'core_[75.0, 55.0, 0.30]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    ka_br1.set_attr(_hvi_dict ={'core_[65.0, 65.0, 0.42]': 0.0625, 'core_[70.0, 60.0, 0.50]': 0.0625, 'core_[75.0, 55.0, 0.30]': 0.0})
    ka_br1.set_attr(_pf_size = 3)
    ka_br1.remove_dominated_entries(['core_[75.0, 55.0, 0.30]'])
    time.sleep(0.05)
    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                                                       'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    assert ka_br1.get_attr('_pf_size') == 2
    ns.shutdown()
    time.sleep(0.05)    
    
def test_prune_entries():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    bb.initialize_abstract_level_3()
    entry1 = {}
    entry2 = {}
    for num in range(15):
        bb.update_abstract_lvl(1, 'val_{}'.format(num), {'pareto type': 'pareto', 'fitness function': 1.0})

    ka_br1 = ns.proxy('ka_br_lvl1')
    ka_br1.set_attr(_pf_size = 15)
    ka_br1.set_attr(total_pf_size = 5)
    ka_br1.set_attr(lvl_read={'val_{}'.format(num): {'pareto type': 'pareto', 'fitness function': 1.0} for num in range(15)})
    ka_br1.set_attr(_hvi_dict={'val_{}'.format(num):num for num in range(15)})
    ka_br1.prune_pareto_front()
    
    assert [x for x in bb.get_attr('abstract_lvls')['level 1'].keys()] == ['val_10', 'val_11', 'val_12', 'val_13', 'val_14']
    
    ns.shutdown()
    time.sleep(0.05)

    
def test_calculate_dci():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv)  
    
    read = {'core_[71.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
            'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 0.99},
            'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 0.98},              
            'core_[60.0, 70.0, 0.65]': {'pareto type' : 'pareto', 'fitness function' : 0.97},
            'core_[55.0, 68.0, 0.75]': {'pareto type' : 'pareto', 'fitness function' : 0.96},
            'core_[63.0, 63.0, 0.83]': {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    
    data = {'core_[65.0, 65.0, 0.42]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                       'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0}},
            'core_[70.0, 60.0, 0.50]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.3}},
            'core_[71.0, 60.0, 0.50]': {'design variables': {'height': 71.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 500.1, 'burnup' : 50.5}},
            'core_[55.0, 68.0, 0.75]': {'design variables': {'height': 71.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 500.3, 'burnup' : 50.7}},
            'core_[63.0, 63.0, 0.83]': {'design variables': {'height': 71.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 500.4, 'burnup' : 50.9}},
            'core_[60.0, 70.0, 0.65]': {'design variables': {'height': 71.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 490.0, 'burnup' : 40.0}}}
    
    for core, entry in read.items():
        bb.update_abstract_lvl(1, core, entry)
    for core, entry in data.items():
        bb.update_abstract_lvl(3, core, entry, panel='old')
        
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    br = ns.proxy('ka_br_lvl1')
    br.set_attr(_lower_objective_reference_point=[0,0])
    br.set_attr(_upper_objective_reference_point=[1,1])
    br.set_attr(lvl_read=read)
    br.set_attr(_lvl_data=data)
    
    br.set_attr(_previous_pf=['core_[65.0, 65.0, 0.42]','core_[70.0, 60.0, 0.50]'])
    br.calculate_dci()
    assert [x for x in bb.get_attr('abstract_lvls')['level 1'].keys()] == ['core_[71.0, 60.0, 0.50]', 'core_[65.0, 65.0, 0.42]', 'core_[60.0, 70.0, 0.65]']

    
    read_1 = {'core_[72.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
            'core_[70.0, 63.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},}
    
    data_1 = {'core_[72.0, 60.0, 0.50]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                       'objective functions': {'reactivity swing' : 900.0, 'burnup' : 90.0}},
            'core_[70.0, 63.0, 0.50]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 220.0, 'burnup' : 30.4}},}
    

    read.update(read_1)
    data.update(data_1)
    for core, entry in read.items():
        bb.update_abstract_lvl(1, core, entry)
    for core, entry in data.items():
        bb.update_abstract_lvl(3, core, entry, panel='old')

    br.set_attr(lvl_read=read)
    br.set_attr(_lvl_data=data)
    
    br.set_attr(_previous_pf=['core_[65.0, 65.0, 0.42]','core_[70.0, 60.0, 0.50]'])
    br.calculate_dci()
    assert [x for x in bb.get_attr('abstract_lvls')['level 1'].keys()] == ['core_[71.0, 60.0, 0.50]', 'core_[65.0, 65.0, 0.42]', 'core_[60.0, 70.0, 0.65]', 'core_[72.0, 60.0, 0.50]', 'core_[70.0, 63.0, 0.50]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_calculate_dci_list():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float},
            'power':            {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type': 'avg'}}
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv) 
    
    read = {'core_[71.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
            'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 0.99},
            'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 0.98},              
            'core_[60.0, 70.0, 0.65]': {'pareto type' : 'pareto', 'fitness function' : 0.97},
            'core_[55.0, 68.0, 0.75]': {'pareto type' : 'pareto', 'fitness function' : 0.96},
            'core_[63.0, 63.0, 0.83]': {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    
    data = {'core_[65.0, 65.0, 0.42]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                       'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0, 'power': [2.5, 5.0, 7.5]}},
            'core_[70.0, 60.0, 0.50]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.3, 'power': [2.5, 5.0, 7.5]}},
            'core_[71.0, 60.0, 0.50]': {'design variables': {'height': 71.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 500.1, 'burnup' : 50.5, 'power': [2.5, 5.0, 7.5]}},
            'core_[55.0, 68.0, 0.75]': {'design variables': {'height': 71.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 500.3, 'burnup' : 50.7, 'power': [2.5, 5.0, 7.5]}},
            'core_[63.0, 63.0, 0.83]': {'design variables': {'height': 71.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 500.4, 'burnup' : 50.9, 'power': [2.5, 5.0, 7.5]}},
            'core_[60.0, 70.0, 0.65]': {'design variables': {'height': 71.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 525.0, 'burnup' : 45.0, 'power': [2.5, 5.0, 7.5]}}}
    
    for core, entry in read.items():
        bb.update_abstract_lvl(1, core, entry)
    for core, entry in data.items():
        bb.update_abstract_lvl(3, core, entry, panel='old')
        
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    br = ns.proxy('ka_br_lvl1')
    br.set_attr(_lower_objective_reference_point=[0,0])
    br.set_attr(_upper_objective_reference_point=[1,1])
    br.set_attr(lvl_read=read)
    br.set_attr(_lvl_data=data)
    
    br.set_attr(_previous_pf=['core_[65.0, 65.0, 0.42]','core_[70.0, 60.0, 0.50]'])
    br.calculate_dci()
    assert [x for x in bb.get_attr('abstract_lvls')['level 1'].keys()] == ['core_[71.0, 60.0, 0.50]', 'core_[65.0, 65.0, 0.42]', 'core_[60.0, 70.0, 0.65]']

    
    read_1 = {'core_[72.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
            'core_[70.0, 63.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},}
    
    data_1 = {'core_[72.0, 60.0, 0.50]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                       'objective functions': {'reactivity swing' : 900.0, 'burnup' : 90.0, 'power': [2.5, 5.0, 7.5]}},
            'core_[70.0, 63.0, 0.50]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                       'objective functions': {'reactivity swing' : 220.0, 'burnup' : 30.4, 'power': [2.5, 5.0, 7.5]}},}
    

    read.update(read_1)
    data.update(data_1)
    for core, entry in read.items():
        bb.update_abstract_lvl(1, core, entry)
    for core, entry in data.items():
        bb.update_abstract_lvl(3, core, entry, panel='old')

    br.set_attr(lvl_read=read)
    br.set_attr(_lvl_data=data)
    
    br.set_attr(_previous_pf=['core_[65.0, 65.0, 0.42]','core_[70.0, 60.0, 0.50]'])
    br.calculate_dci()
    assert [x for x in bb.get_attr('abstract_lvls')['level 1'].keys()] == ['core_[71.0, 60.0, 0.50]', 'core_[65.0, 65.0, 0.42]', 'core_[60.0, 70.0, 0.65]', 'core_[72.0, 60.0, 0.50]', 'core_[70.0, 63.0, 0.50]']
    
    ns.shutdown()
    time.sleep(0.05)