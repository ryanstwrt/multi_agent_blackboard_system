import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import src.blackboard as blackboard
import src.ka as ka
import time
import os
import src.ka_br as ka_br
import src.bb_opt as bb_opt
import pickle
import src.train_surrogate_models as tm

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)

def test_kabr_init():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    assert ka_b.get_attr('bb') == None
    assert ka_b.get_attr('bb_lvl_write') == 0
    assert ka_b.get_attr('_entry') == None
    assert ka_b.get_attr('_entry_name') == None
    assert ka_b.get_attr('_writer_addr') == None
    assert ka_b.get_attr('_writer_alias') == None
    assert ka_b.get_attr('_executor_addr') == None
    assert ka_b.get_attr('_executor_alias') == None
    assert ka_b.get_attr('_trigger_response_addr') == None
    assert ka_b.get_attr('_trigger_response_alias') == 'trigger_response_ka_br'
    assert ka_b.get_attr('_trigger_publish_addr') == None
    assert ka_b.get_attr('_trigger_publish_alias') == None
    assert ka_b.get_attr('_trigger_val') == 0
    assert ka_b.get_attr('_shutdown_addr') == None
    assert ka_b.get_attr('_shutdown_alias') == None
    assert ka_b.get_attr('new_panel') == 'new'
    assert ka_b.get_attr('old_panel') == 'old'
    assert ka_b.get_attr('_num_entries') == 0
    assert ka_b.get_attr('_num_allowed_entries') == 25
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_trigger_handler_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_b.set_attr(bb_lvl_read=1)
    ka_b.set_attr(bb_lvl_write=2)
    bb.add_abstract_lvl(1, {'valid': bool})
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new','old'])
    bb.add_abstract_lvl(3, {'valid': bool})
    bb.publish_trigger()
    time.sleep(0.25)
    
    assert ka_b.get_attr('_trigger_val') == 0
    assert bb.get_attr('_kaar') == {1: {'ka_br': 0}}
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_clear_entry():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    ka_b.set_attr(_entry={'valid': True})
    ka_b.set_attr(_entry_name='core_1')
    assert ka_b.get_attr('_entry') == {'valid': True}
    assert ka_b.get_attr('_entry_name') == 'core_1'
    ka_b.clear_entry()
    assert ka_b.get_attr('_entry') == None
    assert ka_b.get_attr('_entry_name') == None 
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_scale_objective():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    obj1 = ka_b.scale_objective(2,0,10)
    assert obj1 == 0.2
    obj1 = ka_b.scale_objective(0,-10,10)
    assert obj1 == 0.5
    obj1 = ka_b.scale_objective(0,29,5925)
    assert obj1 == None
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_scale_objective_list():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    obj1 = ka_b.scale_list_objective([3.0,5.0,7.0], 0.0, 10.0, 'avg')
    assert obj1 == 0.5
    obj1 = ka_b.scale_list_objective([2.0,5.0,7.0], 0.0, 10.0, 'min')
    assert obj1 == 0.2
    obj1 = ka_b.scale_list_objective([2.0,5.0,7.0], 0.0, 10.0, 'max')
    assert obj1 == 0.7
    obj1 = ka_b.scale_list_objective([2.0,5.0,8.0], [0.0,0.0,0.0], [4.0,10.0,10.0], 'avg')
    assert obj1 == 0.6
    obj1 = ka_b.scale_list_objective([2.0,5.0,8.0], [0.0,0.0,0.0], [4.0,10.0,10.0], 'min')
    assert obj1 == 0.5
    obj1 = ka_b.scale_list_objective([2.0,5.0,8.0], [0.0,0.0,0.0], [4.0,10.0,10.0], 'max')
    assert obj1 == 0.8   
    ns.shutdown()
    time.sleep(0.05)  
    
def test_kabr_update_abstract_level():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
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
    
#-----------------------------------------
# Test of KaBr_lvl1
#-----------------------------------------

def test_kabr_lvl1_init():
    ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=ka_br.KaBr_lvl1)
    assert ka_br1.get_attr('bb') == None
    assert ka_br1.get_attr('bb_lvl_write') == 1
    assert ka_br1.get_attr('_entry') == None
    assert ka_br1.get_attr('_entry_name') == None
    assert ka_br1.get_attr('_writer_addr') == None
    assert ka_br1.get_attr('_writer_alias') == None
    assert ka_br1.get_attr('_executor_addr') == None
    assert ka_br1.get_attr('_executor_alias') == None
    assert ka_br1.get_attr('_trigger_response_addr') == None
    assert ka_br1.get_attr('_trigger_response_alias') == 'trigger_response_ka_br_lvl1'
    assert ka_br1.get_attr('_trigger_publish_addr') == None
    assert ka_br1.get_attr('_trigger_publish_alias') == None
    assert ka_br1.get_attr('_trigger_val') == 0
    assert ka_br1.get_attr('bb_lvl_read') == 1
    assert ka_br1.get_attr('_objectives') == None
    assert ka_br1.get_attr('_shutdown_addr') == None
    assert ka_br1.get_attr('_shutdown_alias') == None
    assert ka_br1.get_attr('_trigger_val_base') == 6
    assert ka_br1.get_attr('_pf_size') == 1
    assert ka_br1.get_attr('_hvi_dict') == {}
    assert ka_br1.get_attr('_upper_objective_reference_point') == None
    assert ka_br1.get_attr('_lower_objective_reference_point') == None

    ns.shutdown()
    time.sleep(0.05)    

def test_kabr_lvl1_update_abstract_levels():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()
    
    bb.connect_agent(ka_br.KaBr_lvl1, 'ka_br_lvl1')
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
    
def test_kabr_lvl1_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()
    
    bb.connect_agent(ka_br.KaBr_lvl1, 'ka_br_lvl1')
    br = ns.proxy('ka_br_lvl1')
    br.set_attr(_num_allowed_entries=1)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.50]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50},
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 60.0, 0.50]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br_lvl1': 6}}
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl1', 6)

    ns.shutdown()
    time.sleep(0.05)       
    
def test_kabr_lvl1_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()
    
    bb.connect_agent(ka_br.KaBr_lvl1, 'ka_br_lvl1')
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
    time.sleep(0.5)
    bb.controller()
    bb.send_executor()
    time.sleep(2.5) 
    assert br.get_attr('_pf_size') == 3
    assert br.get_attr('_hvi_dict') == {'core_[65.0, 65.0, 0.42]': 0.0625, 'core_[70.0, 60.0, 0.50]': 0.0625,
                                       'core_[75.0, 55.0, 0.30]': 0.0625}
    
    bb.update_abstract_lvl(3, 'core_[55.0, 55.0, 0.30]', {'design variables': {'height': 55.0, 'smear': 55.0, 'pu_content': 0.50},
                                                          'objective functions': {'reactivity swing' : 300.0, 'burnup' : 24.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[55.0, 55.0, 0.30]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb.publish_trigger()
    time.sleep(0.5)
    bb.controller()
    bb.send_executor()
    time.sleep(0.5) 
    assert br.get_attr('_pf_size') == 3
    
    assert br.get_attr('_hvi_dict') == {'core_[65.0, 65.0, 0.42]': 0.0625, 'core_[70.0, 60.0, 0.50]': 0.0625,
                                       'core_[75.0, 55.0, 0.30]': 0.0625}
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[75.0, 55.0, 0.30]':{'pareto type' : 'pareto', 'fitness function' : 1.0},
                                                      'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                                                      'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}}

    ns.shutdown()
    time.sleep(0.05)  

def test_kabr_lvl1_scale_pareto_front():
    ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=ka_br.KaBr_lvl1)
    ka_br1.set_attr(lvl_read={'core_[75.0, 55.0, 0.30]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}})
    ka_br1.set_attr(_lvl_data={'core_[65.0, 65.0, 0.42]': {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                           'objective functions': {'reactivity swing' : 750.0, 'burnup' : 75.0, 'power avg':[2.5,5.0,7.5], 'power max':[2.5,5.0,7.5], 'power min':[2.5,5.0,7.5]}},
                               'core_[70.0, 60.0, 0.50]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0, 'power avg':[2.5,5.0,7.5], 'power max':[2.5,5.0,7.5], 'power min':[2.5,5.0,7.5]}},
                               'core_[75.0, 55.0, 0.30]': {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                           'objective functions': {'reactivity swing' : 250.0, 'burnup' : 25.0, 'power avg':[2.5,5.0,7.5], 'power max':[2.5,5.0,7.5], 'power min':[2.5,5.0,7.5]}}})
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float},
            'power avg':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'avg'},
            'power max':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'max'},
            'power min':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'min'}}
    ka_br1.set_attr(_objectives=objs)
    pf = ['core_[65.0, 65.0, 0.42]', 'core_[70.0, 60.0, 0.50]', 'core_[75.0, 55.0, 0.30]']
    scaled_pf = ka_br1.scale_pareto_front(pf)
    assert scaled_pf == [[0.75,0.25,0.5,0.75,0.25], [0.5,0.5,0.5,0.75,0.25], [0.25,0.75,0.5,0.75,0.25]]
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_lvl1_calculate_hvi():
    ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=ka_br.KaBr_lvl1)
    ka_br1.set_attr(_lower_objective_reference_point=[0,0])
    ka_br1.set_attr(_upper_objective_reference_point=[1,1])
    pf = [[0.75,0.25], [0.5,0.5], [0.25,0.75]]
    hvi = ka_br1.calculate_hvi(pf)
    
    assert hvi == 0.375
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_lvl1_calculate_hvi_contribution():
    ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=ka_br.KaBr_lvl1)
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

def test_kabr_lvl1_calculate_hvi_contribution_list():
    ns = run_nameserver()
    ka_br1 = run_agent(name='ka_br_lvl1', base=ka_br.KaBr_lvl1)
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
    
    
def test_kabr_lvl1_remove_dominated_entries():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.connect_agent(ka_br.KaBr_lvl1, 'ka_br_lvl1')
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
    time.sleep(0.1)
    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[70.0, 60.0, 0.50]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                                                       'core_[65.0, 65.0, 0.42]': {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    assert ka_br1.get_attr('_pf_size') == 2
    ns.shutdown()
    time.sleep(0.05)    
    
def test_kabr_lvl1_prune_entries():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.connect_agent(ka_br.KaBr_lvl1, 'ka_br_lvl1')
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

    
def test_kabr_lvl1_calculate_dci():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()
    
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
        
    bb.connect_agent(ka_br.KaBr_lvl1, 'ka_br_lvl1')
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
    
def test_kabr_lvl1_calculate_dci_list():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float},
            'power':            {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type': 'avg'}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()
    
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
        
    bb.connect_agent(ka_br.KaBr_lvl1, 'ka_br_lvl1')
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
    
#-----------------------------------------
# Test of KaBr_lvl2
#-----------------------------------------

def test_kabr_lvl2_init():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br2', base=ka_br.KaBr_lvl2)
    assert ka_br2.get_attr('bb') == None
    assert ka_br2.get_attr('bb_lvl_write') == 1
    assert ka_br2.get_attr('_entry') == None
    assert ka_br2.get_attr('_entry_name') == None
    assert ka_br2.get_attr('_writer_addr') == None
    assert ka_br2.get_attr('_writer_alias') == None
    assert ka_br2.get_attr('_executor_addr') == None
    assert ka_br2.get_attr('_executor_alias') == None
    assert ka_br2.get_attr('_trigger_response_addr') == None
    assert ka_br2.get_attr('_trigger_response_alias') == 'trigger_response_ka_br2'
    assert ka_br2.get_attr('_trigger_publish_addr') == None
    assert ka_br2.get_attr('_trigger_publish_alias') == None
    assert ka_br2.get_attr('_trigger_val') == 0
    assert ka_br2.get_attr('bb_lvl_read') == 2
    assert ka_br2.get_attr('_objectives') == None
    assert ka_br2.get_attr('_shutdown_addr') == None
    assert ka_br2.get_attr('_shutdown_alias') == None
    assert ka_br2.get_attr('_num_entries') == 0
    assert ka_br2.get_attr('_num_allowed_entries') == 10
    assert ka_br2.get_attr('_trigger_val_base') == 4
    assert ka_br2.get_attr('_fitness') == 0.0
    assert ka_br2.get_attr('_update_hv') == True
    
    ns.shutdown()
    time.sleep(0.05)

def test_kabr_lvl2_update_abstract_levels():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()
    
    bb.connect_agent(ka_br.KaBr_lvl2, 'ka_br_lvl2')
    br = ns.proxy('ka_br_lvl2')
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
    
def test_kabr_lvl2_add_entry():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2) 
    ka_br2.set_attr(_fitness=1.5)
    ka_br2.add_entry(('core_1', 'pareto'))
    
    assert ka_br2.get_attr('_entry') == {'pareto type': 'pareto', 'fitness function': 1.5}
    assert ka_br2.get_attr('_entry_name') == 'core_1'
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_kabr_lvl2_determine_validity():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    ka_br2.add_blackboard(bb)
    ka_br2.connect_writer()
    ka_br2.connect_trigger()
    ka_br2.connect_executor()
    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])
    bb.add_abstract_lvl(3, {'design variables': {'height': float, 'smear': float, 'pu_content': float}, 'objective functions': {'keff': float, 'void_coeff': float}})
    bb.add_panel(3, ['new','old'])
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 'objective functions': {'keff': 1.05, 'void_coeff': -150.0,}}, panel='old')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 'objective functions': {'keff': 1.05, 'void_coeff': -160.0}}, panel='old')
    bb.update_abstract_lvl(3, 'core_3', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 'objective functions': {'keff': 1.06, 'void_coeff': -100.0}}, panel='old')
    bb.update_abstract_lvl(3, 'core_4', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 'objective functions': {'keff': 1.00, 'void_coeff': -100.0}}, panel='old')

    bb.update_abstract_lvl(2, 'core_1', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_2', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_3', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_4', {'valid': True}, panel='new')
    
    bb.publish_trigger()
    time.sleep(0.25)
    
    bol, p_type = ka_br2.determine_validity('core_1')
    assert p_type == 'pareto'
    assert bol == True

    bb.update_abstract_lvl(1, 'core_1', {'pareto type': 'pareto', 'fitness function': 1.0})
    bb.publish_trigger()
    time.sleep(0.25)
    bol, p_type = ka_br2.determine_validity('core_2')
    assert p_type == 'pareto'
    assert bol == True

    bb.update_abstract_lvl(1, 'core_2', {'pareto type': 'pareto', 'fitness function': 1.0})
    bb.publish_trigger()
    time.sleep(0.25)
    bol, p_type = ka_br2.determine_validity('core_3')
    assert p_type == 'weak'
    assert bol == True

    bb.update_abstract_lvl(1, 'core_3', {'pareto type': 'weak', 'fitness function': 1.0})
    bb.publish_trigger()
    time.sleep(0.25)
    bol, p_type = ka_br2.determine_validity('core_4')
    assert p_type == None
    assert bol == False
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_move_curent_entry():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    ka_br2.add_blackboard(bb)
    ka_br2.connect_writer()

    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                           'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}, 
                                           'pu_content':  {'ll': 0,    'ul': 0.6, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
    bb.add_panel(1, ['new', 'old'])
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])

    bb.update_abstract_lvl(2, 'core_1', {'valid': True}, panel='new')
    
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_1' : {'valid' : True}}, 'old' : {}}
    ka_br2.move_entry(ka_br2.get_attr('bb_lvl_read'), 'core_1', {'valid': True}, ka_br2.get_attr('old_panel'), ka_br2.get_attr('new_panel'))
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old' : {'core_1' : {'valid' : True}}}
    
    ns.shutdown()
    time.sleep(0.05)

def test_kabr_lvl2_determine_optimal_type():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                           'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}, 
                                           'pu_content':  {'ll': 0,    'ul': 0.6, 'goal':'lt', 'variable type': float}})    
    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.10, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.3}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == 'pareto'

    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.10, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.3}, 
        {'keff': 1.10, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.3})
    assert bool_ == None
    
    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.02, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.3}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == 'weak'
    
    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.00, 'void_coeff': -100, 'doppler_coeff': -0.55, 'pu_content': 0.3}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == 'weak'

    
    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.02, 'void_coeff': -110, 'doppler_coeff': -0.55, 'pu_content': 0.6}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.5})
    assert bool_ == None
    
    ns.shutdown()
    time.sleep(0.05)

def test_determine_fitness_function():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -100, 'goal':'lt', 'variable type': float}, 
                                 'pu_content':  {'ll': 0.0, 'ul': 0.6, 'goal':'lt', 'variable type': float},
                                 'power avg':   {'ll': 0.0, 'ul': 1.0, 'goal': 'lt', 'variable type': list, 'goal type': 'avg'},
                                 'power min':   {'ll': 0.0, 'ul': 1.0, 'goal': 'lt', 'goal type': 'min', 'variable type': list},
                                 'power max':   {'ll': 0.0, 'ul': 1.0, 'goal': 'lt', 'goal type': 'max', 'variable type': list}})
    
    fitness = ka_br2.determine_fitness_function('core_1', {'keff': 1.2, 'void_coeff': -200.0, 'pu_content': 0.0, 'power avg': [0.25, 0.5, 0.75], 'power max': [0.25, 0.5, 0.75], 'power min': [0.25, 0.5, 0.75]})
    assert fitness == 4.5
    fitness = ka_br2.determine_fitness_function('core_2', {'keff': 1.0, 'void_coeff': -100.0, 'pu_content': 0.6, 'power avg': [0.25, 0.5, 0.75], 'power max': [0.25, 0.5, 0.75], 'power min': [0.25, 0.5, 0.75]})
    assert fitness == 1.5
    fitness = ka_br2.determine_fitness_function('core_2', {'keff': 1.1, 'void_coeff': -150.0, 'pu_content': 0.3, 'power avg': [0.25, 0.5, 0.75], 'power max': [0.25, 0.5, 0.75], 'power min': [0.25, 0.5, 0.75]})
    assert fitness == 3.0
    
    ns.shutdown()
    time.sleep(0.05)   
    
def test_kabr_lvl2_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(ka_br.KaBr_lvl2, 'ka_br2')
    br = ns.proxy('ka_br2')
    br.set_attr(_num_allowed_entries=1)
    bb.update_abstract_lvl(3, 'core 1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')    
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br2': 0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    bb.update_abstract_lvl(2, 'core 1', {'valid' : True}, panel='new')
    bb.publish_trigger()
    time.sleep(1.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br2': 0}, 2: {'ka_br2': 5}}   
    assert bb.get_attr('_ka_to_execute') == ('ka_br2', 5)
    
    ns.shutdown()
    time.sleep(0.05)

def test_kabr_lvl2_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    ka_br2.add_blackboard(bb)
    ka_br2.connect_writer()
    ka_br2.connect_trigger()
    ka_br2.connect_executor()
    ka_br2.connect_complete()
    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}, 
                                 'pu_content':  {'ll': 0,    'ul': 0.6, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])
    bb.add_abstract_lvl(3, {'design variables': {'height': float, 'smear': float, 'pu_content': float}, 
                            'objective functions': {'keff': float, 'void_coeff': float, 'pu_content': float}})
    bb.add_panel(3, ['new','old'])
    
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.3}, 
                                         'objective functions': {'keff': 1.05, 'void_coeff': -150.0, 'pu_content': 0.3}}, panel='old')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.3},
                                         'objective functions': {'keff': 1.05, 'void_coeff': -160.0, 'pu_content': 0.3}}, panel='old')
    bb.update_abstract_lvl(3, 'core_3', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.5},
                                         'objective functions': {'keff': 1.00, 'void_coeff': -100.0, 'pu_content': 0.5}}, panel='old')
    bb.update_abstract_lvl(3, 'core_4', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.2},
                                         'objective functions': {'keff': 1.00, 'void_coeff': -100.0, 'pu_content': 0.2}}, panel='old')  
    
    bb.update_abstract_lvl(2, 'core_1', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_2', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_3', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_4', {'valid': True}, panel='new')
    
    bb.set_attr(_ka_to_execute=('ka_br', 10.0))
    bb.publish_trigger()
    time.sleep(0.5)
    bb.send_executor()
    time.sleep(0.5)    

    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1' : {'pareto type' : 'pareto', 'fitness function' : 1.35},
                                                       'core_2' : {'pareto type' : 'pareto', 'fitness function' : 1.43},
                                                       'core_3' : {'pareto type' : 'pareto', 'fitness function' : 0.36667},
                                                       'core_4' : {'pareto type' : 'pareto', 'fitness function' : 0.86667}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new': {}, 
                                                       'old': {'core_1' : {'valid' : True}, 
                                                               'core_2' : {'valid' : True},
                                                               'core_3' : {'valid' : True},
                                                               'core_4' : {'valid' : True}}}
    bb.set_attr(_ka_to_execute=('ka_br', 10.0))
    bb.publish_trigger()
    time.sleep(0.25)
    bb.send_executor()
    time.sleep(0.25) 
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new': {}, 
                                                       'old': {'core_1' : {'valid' : True}, 
                                                               'core_2' : {'valid' : True},
                                                               'core_3' : {'valid' : True},
                                                               'core_4' : {'valid' : True}}} 
   
    ns.shutdown()
    time.sleep(0.05) 
    
#-----------------------------------------
# Test of KaBr_lvl3
#-----------------------------------------

def test_kabr_lvl3_init():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br3', base=ka_br.KaBr_lvl3)
    assert ka_br2.get_attr('bb') == None
    assert ka_br2.get_attr('bb_lvl_write') == 2
    assert ka_br2.get_attr('_entry') == None
    assert ka_br2.get_attr('_entry_name') == None
    assert ka_br2.get_attr('_writer_addr') == None
    assert ka_br2.get_attr('_writer_alias') == None
    assert ka_br2.get_attr('_executor_addr') == None
    assert ka_br2.get_attr('_executor_alias') == None
    assert ka_br2.get_attr('_trigger_response_addr') == None
    assert ka_br2.get_attr('_trigger_response_alias') == 'trigger_response_ka_br3'
    assert ka_br2.get_attr('_trigger_publish_addr') == None
    assert ka_br2.get_attr('_trigger_publish_alias') == None
    assert ka_br2.get_attr('_trigger_val') == 0
    assert ka_br2.get_attr('bb_lvl_read') == 3
    assert ka_br2.get_attr('_shutdown_addr') == None
    assert ka_br2.get_attr('_shutdown_alias') == None
    assert ka_br2.get_attr('_num_entries') == 0
    assert ka_br2.get_attr('_num_allowed_entries') == 25
    
    ns.shutdown()
    time.sleep(0.05)

def test_kabr_lvl3_update_abstract_levels():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()
    
    bb.connect_agent(ka_br.KaBr_lvl3, 'ka_br_lvl3')
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
    assert [x for x in br.get_attr('_lvl_data').keys()] == ['core_[65.0, 65.0, 0.45]']#, 'core_[65.0, 65.0, 0.42]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_lvl3_determine_validity():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br3 = run_agent(name='ka_br', base=ka_br.KaBr_lvl3)
    ka_br3.add_blackboard(bb)
    ka_br3.connect_trigger()
    ka_br3.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['old', 'new'])
    bb.add_abstract_lvl(3, {'design variables': {'height': float, 'smear': float, 'pu_content': float}, 
                            'objective functions': {'keff': float, 'void_coeff': float}})
    bb.add_panel(3, ['new','old'])
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.05, 'void_coeff': -150.0}}, panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 0.9, 'void_coeff': -150.0}}, panel='new')    
    
    bb.publish_trigger()
    bool_ = ka_br3.determine_validity('core_1')
    assert bool_ == (True, None)
    bool_ = ka_br3.determine_validity('core_2')
    assert bool_ == (False, None)

    ns.shutdown()
    time.sleep(0.1)
    
def test_kabr_lvl3_determine_validity_constraint():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives={'reactivity swing': {'ll':0, 'ul':20000, 'goal':'lt', 'variable type': float},
                                               'burnup':           {'ll':0,  'ul':200,  'goal':'gt', 'variable type': float}},
                                   constraints={'eol keff':    {'ll': 1.0, 'ul': 1.5, 'variable type': float}})
    bb.connect_agent(ka_br.KaBr_lvl3, 'ka_br3')
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
    time.sleep(0.1)
    
def test_kabr_lvl3_read_bb_lvl():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br3 = run_agent(name='ka_br', base=ka_br.KaBr_lvl3)
    ka_br3.add_blackboard(bb)
    ka_br3.connect_writer()
    ka_br3.connect_trigger()
    ka_br3.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])
    bb.add_abstract_lvl(3, {'design variables': {'height': float, 'smear': float, 'pu_content': float}, 
                            'objective functions': {'keff': float, 'void_coeff': float}})
    bb.add_panel(3, ['new', 'old'])
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.1, 'void_coeff': -150.0}}, panel='new')

    bb.publish_trigger()
    time.sleep(0.5)
    ka_br3.read_bb_lvl()
    
    assert ka_br3.get_attr('_entry') == {'valid': True}
    assert ka_br3.get_attr('_entry_name') == 'core_1'

    ns.shutdown()
    time.sleep(0.05)    

def test_kabr_lvl3_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    br = run_agent(name='ka_br3', base=ka_br.KaBr_lvl3)
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
    time.sleep(0.1)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br3': 0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='new')
    bb.publish_trigger()
    time.sleep(0.1)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br3': 0}, 2: {'ka_br3': 4}}   
    assert bb.get_attr('_ka_to_execute') == ('ka_br3', 4)

    bb.remove_bb_entry(3, 'core_1', panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 250.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='new')
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    bb.publish_trigger()
    time.sleep(0.1)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br3': 0}, 2: {'ka_br3': 4}, 3:{'ka_br3':0}}   
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_lvl3_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br3 = run_agent(name='ka_br', base=ka_br.KaBr_lvl3)
    ka_br3.add_blackboard(bb)
    ka_br3.connect_writer()
    ka_br3.connect_executor()
    ka_br3.connect_trigger()
    ka_br3.connect_complete()

    ka_br3.set_attr(_objectives={'keff':          {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                           'void_coeff':    {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float},
                                           'doppler_coeff': {'ll':-1.0,  'ul':-0.6, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])
    bb.add_abstract_lvl(3, {'design variables': {'height': float, 'smear': float, 'pu_content': float}, 
                            'objective functions': {'keff': float, 'void_coeff': float, 'doppler_coeff': float}})
    bb.add_panel(3, ['new', 'old'])
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4},
                                         'objective functions': {'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.75}}, panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.80}}, panel='new')
    bb.update_abstract_lvl(3, 'core_3', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4},
                                         'objective functions': {'keff': 0.9, 'void_coeff': -150.0, 'doppler_coeff': -0.75}}, panel='new')

    bb.set_attr(_ka_to_execute=('ka_br', 10.0))
    bb.publish_trigger()
    time.sleep(0.1)
    bb.send_executor()
    time.sleep(1.5)    
    
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{'core_1': {'valid': True},
                                                              'core_2': {'valid': True}}, 'old': {}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [] 

    ns.shutdown()
    time.sleep(0.05)

def test_kabr_lvl3_add_entry():
    ns = run_nameserver()
    ka_br3 = run_agent(name='ka_br', base=ka_br.KaBr_lvl3)
    ka_br3.add_entry(('core_1', None))
    
    assert ka_br3.get_attr('_entry') == {'valid': True}
    assert ka_br3.get_attr('_entry_name') == 'core_1'
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kabr_lvl3_determine_validity_list():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives={'keff':            {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                               'assembly power':  {'ll': 0.5, 'ul': 7.5, 'goal':'lt', 'variable type': list, 'goal type': 'avg'},
                                               'burnup':          {'ll': [0.0,0.0], 'ul': [100.0,100.0], 'goal': 'lt', 'goal type': 'max','variable type': list}})
    bb.connect_agent(ka_br.KaBr_lvl3, 'ka_br3')
    ka = bb.get_attr('_proxy_server')
    br = ka.proxy('ka_br3')

    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.05, 'assembly power': [0.6, 0.6, 0.8], 'burnup': [10.0, 10.0]},
                                         'constraints': {'eol keff': 1.1}}, panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.04, 'assembly power': [0.4, 0.6, 0.8], 'burnup': [10.0, 10.0]},
                                         'constraints': {'eol keff': 1.1}}, panel='new')    
    bb.update_abstract_lvl(3, 'core_3', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'keff': 1.05, 'assembly power': [0.6, 0.6, 0.8], 'burnup': [110.0, 10.0]},
                                         'constraints': {'eol keff': 1.1}}, panel='new')    
    bb.publish_trigger()
    bool_ = br.determine_validity('core_1')
    assert bool_ == (True, None)
    bool_ = br.determine_validity('core_2')
    assert bool_ == (False, None)
    bool_ = br.determine_validity('core_3')
    assert bool_ == (False, None)

    ns.shutdown()
    time.sleep(0.1)
    
#def test_timing():
#    ns = run_nameserver()
#    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
#    bb.initialize_abstract_level_3()
#    bb.connect_agent(ka_br.KaBr_lvl3, 'ka_br3')
#    ka = bb.get_attr('_proxy_server')
#    br = ka.proxy('ka_br3')
#        
#    for k in range(0,100):
#        bb.update_abstract_lvl(2, 'core {}'.format(k), {'valid': True}, panel='new')
#        bb.update_abstract_lvl(3, 'core {}'.format(k), {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
#                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0},
#                                                       'constraints': {'eol keff':1.1}}, panel='new')
#    for k in range(1000,1200):
#        bb.update_abstract_lvl(3, 'core {}'.format(k), {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
#                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0},
#                                                       'constraints': {'eol keff':1.1}}, panel='old')
#        
#    br.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 3']['new'])
#    br.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['new'])
#    br.set_attr(_entry_name='core_0')
#    a = time.time()
#    br.handler_executor('test')
#    print(time.time()-a)
    #br.handler_trigger_publish('test')
#    ns.shutdown()
#    time.sleep(0.05) 
#    assert 1 > 2
