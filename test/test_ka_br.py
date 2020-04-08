import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import ka
import time
import os
import ka_br

def test_kabr_init():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    assert ka_b.get_attr('bb') == None
    assert ka_b.get_attr('bb_lvl') == 0
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
    
    ns.shutdown()
    time.sleep(0.2)
    
def test_kabr_trigger_handler_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    ka_b.set_attr(bb_lvl_read=1)
    bb.add_abstract_lvl(1, {'valid': bool})
    bb.add_abstract_lvl(3, {'valid': bool})
    bb.publish_trigger()
    
    assert ka_b.get_attr('_trigger_val') == 0
    assert bb.get_attr('_kaar') == {1: {'ka_br': 0}}
    
    ns.shutdown()
    time.sleep(0.2)
    
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
    time.sleep(0.2)

#-----------------------------------------
# Test of Ka_Br_verify
#-----------------------------------------

    
def test_kabr_verify_init():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br_lvl2', base=ka_br.KaBr_verify)
    assert ka_br2.get_attr('bb') == None
    assert ka_br2.get_attr('bb_lvl') == 1
    assert ka_br2.get_attr('_entry') == None
    assert ka_br2.get_attr('_entry_name') == None
    assert ka_br2.get_attr('_writer_addr') == None
    assert ka_br2.get_attr('_writer_alias') == None
    assert ka_br2.get_attr('_executor_addr') == None
    assert ka_br2.get_attr('_executor_alias') == None
    assert ka_br2.get_attr('_trigger_response_addr') == None
    assert ka_br2.get_attr('_trigger_response_alias') == 'trigger_response_ka_br_lvl2'
    assert ka_br2.get_attr('_trigger_publish_addr') == None
    assert ka_br2.get_attr('_trigger_publish_alias') == None
    assert ka_br2.get_attr('_trigger_val') == 0
    assert ka_br2.get_attr('bb_lvl_read') == 2
    assert ka_br2.get_attr('desired_results') == None
    assert ka_br2.get_attr('_shutdown_addr') == None
    assert ka_br2.get_attr('_shutdown_alias') == None
    
    ns.shutdown()
    time.sleep(0.2)
    
def test_kabr_verify_determine_valid_core():
    ns = run_nameserver()
    ka_br_lvl2 = run_agent(name='ka_br', base=ka_br.KaBr_verify)
    
    ka_br_lvl2.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 0.6)})
    bool_ = ka_br_lvl2.determine_valid_core({'keff': 1.1, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.4})
    assert bool_ == True
    bool_ = ka_br_lvl2.determine_valid_core({'keff': 0.9, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.4})
    assert bool_ == False

    ns.shutdown()
    time.sleep(0.2)
    
def test_kabr_verify_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br_verify = run_agent(name='ka_br', base=ka_br.KaBr_verify)
    ka_br_verify.add_blackboard(bb)
    ka_br_verify.connect_writer()
    ka_br_verify.connect_executor()
    
    ka_br_verify.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 0.6)})
    
    bb.add_abstract_lvl(1, {'valid': bool})
    bb.add_abstract_lvl(2, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'keff': float, 'void_coeff': float, 'doppler_coeff': float}})
    
    bb.update_abstract_lvl(2, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.75}})

    bb.set_attr(_ka_to_execute=('ka_br', 10.0))
    bb.send_executor()
    time.sleep(1.1)    

    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1': {'valid': True}}
    
    ns.shutdown()
    time.sleep(0.2)    

    
#-----------------------------------------
# Test of KaBr_lvl2
#-----------------------------------------

def test_kabr_lvl2_init():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br_lvl2', base=ka_br.KaBr_lvl2)
    assert ka_br2.get_attr('bb') == None
    assert ka_br2.get_attr('bb_lvl') == 1
    assert ka_br2.get_attr('_entry') == None
    assert ka_br2.get_attr('_entry_name') == None
    assert ka_br2.get_attr('_writer_addr') == None
    assert ka_br2.get_attr('_writer_alias') == None
    assert ka_br2.get_attr('_executor_addr') == None
    assert ka_br2.get_attr('_executor_alias') == None
    assert ka_br2.get_attr('_trigger_response_addr') == None
    assert ka_br2.get_attr('_trigger_response_alias') == 'trigger_response_ka_br_lvl2'
    assert ka_br2.get_attr('_trigger_publish_addr') == None
    assert ka_br2.get_attr('_trigger_publish_alias') == None
    assert ka_br2.get_attr('_trigger_val') == 0
    assert ka_br2.get_attr('bb_lvl_read') == 2
    assert ka_br2.get_attr('desired_results') == None
    assert ka_br2.get_attr('_shutdown_addr') == None
    assert ka_br2.get_attr('_shutdown_alias') == None
    
    ns.shutdown()
    time.sleep(0.2)

def test_kabr_lvl2_add_entry():
    ns = run_nameserver()
    ka_br_lvl2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)

    ka_br_lvl2.add_entry(('core_1', 'pareto'))
    
    assert ka_br_lvl2.get_attr('_entry') == {'pareto type': 'pareto'}
    assert ka_br_lvl2.get_attr('_entry_name') == 'core_1'
    
    ns.shutdown()
    time.sleep(0.2) 
    
def test_kabr_lvl2_determine_validity():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br_lvl2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    ka_br_lvl2.add_blackboard(bb)
    ka_br_lvl2.connect_writer()
    ka_br_lvl2.connect_executor()
    ka_br_lvl2.set_attr(desired_results={'keff': 'gt', 'void_coeff': 'lt', 'pu_content': 'lt'})
    
    bb.add_abstract_lvl(1, {'pareto type': str})
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_abstract_lvl(3, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'keff': float, 'void_coeff': float}})
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.05, 'void_coeff': -150.0}})
    bb.update_abstract_lvl(3, 'core_2', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.05, 'void_coeff': -160.0}})

    bb.update_abstract_lvl(2, 'core_1', {'valid': True})
    bol, p_type = ka_br_lvl2.determine_validity('core_1')
    assert p_type == 'pareto'
    assert bol == True

    bb.update_abstract_lvl(1, 'core_1', {'pareto type': 'pareto'})
    bol, p_type = ka_br_lvl2.determine_validity('core_2')
    assert p_type == 'weak'
    assert bol == True

    ns.shutdown()
    time.sleep(0.2) 

def test_kabr_lvl2_determine_optimal_type():
    ns = run_nameserver()
    ka_br_lvl2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    
    ka_br_lvl2.set_attr(desired_results={'keff': 'gt', 'void_coeff': 'lt', 'doppler_coeff': 'lt', 'pu_content': 'lt'})
    
    bool_ = ka_br_lvl2.determine_optimal_type(
        {'keff': 1.10, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.4}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == 'pareto'
    
    bool_ = ka_br_lvl2.determine_optimal_type(
        {'keff': 1.02, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.4}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == 'weak'
    
    bool_ = ka_br_lvl2.determine_optimal_type(
        {'keff': 1.02, 'void_coeff': -110, 'doppler_coeff': -0.55, 'pu_content': 0.7}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == None
    
    ns.shutdown()
    time.sleep(0.2)
    
#-----------------------------------------
# Test of KaBr_lvl3
#-----------------------------------------

def test_kabr_lvl3_init():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br_lvl3', base=ka_br.KaBr_lvl3)
    assert ka_br2.get_attr('bb') == None
    assert ka_br2.get_attr('bb_lvl') == 2
    assert ka_br2.get_attr('_entry') == None
    assert ka_br2.get_attr('_entry_name') == None
    assert ka_br2.get_attr('_writer_addr') == None
    assert ka_br2.get_attr('_writer_alias') == None
    assert ka_br2.get_attr('_executor_addr') == None
    assert ka_br2.get_attr('_executor_alias') == None
    assert ka_br2.get_attr('_trigger_response_addr') == None
    assert ka_br2.get_attr('_trigger_response_alias') == 'trigger_response_ka_br_lvl3'
    assert ka_br2.get_attr('_trigger_publish_addr') == None
    assert ka_br2.get_attr('_trigger_publish_alias') == None
    assert ka_br2.get_attr('_trigger_val') == 0
    assert ka_br2.get_attr('bb_lvl_read') == 3
    assert ka_br2.get_attr('desired_results') == None
    assert ka_br2.get_attr('_shutdown_addr') == None
    assert ka_br2.get_attr('_shutdown_alias') == None
    
    ns.shutdown()
    time.sleep(0.2)
    
def test_kabr_lvl3_determine_validity():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br_lvl3 = run_agent(name='ka_br', base=ka_br.KaBr_lvl3)
    ka_br_lvl3.add_blackboard(bb)
    ka_br_lvl3.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'pu_content': (0, 0.6)})
    
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_abstract_lvl(3, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'keff': float, 'void_coeff': float}})
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.05, 'void_coeff': -150.0}})
    bb.update_abstract_lvl(3, 'core_2', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 0.9, 'void_coeff': -150.0}})
    
    bool_ = ka_br_lvl3.determine_validity('core_1')
    assert bool_ == (True, None)
    bool_ = ka_br_lvl3.determine_validity('core_2')
    assert bool_ == (False, None)

    ns.shutdown()
    time.sleep(0.2)
    
def test_kabr_lvl3_read_bb_lvl():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br_lvl3 = run_agent(name='ka_br', base=ka_br.KaBr_lvl3)
    ka_br_lvl3.add_blackboard(bb)
    
    ka_br_lvl3.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 0.6)})
    
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_abstract_lvl(3, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'keff': float, 'void_coeff': float, 'doppler_coeff': float}})
    
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.75}})

    ka_br_lvl3.read_bb_lvl()
    
    assert ka_br_lvl3.get_attr('_entry') == {'valid': True}
    assert ka_br_lvl3.get_attr('_entry_name') == 'core_1'

    ns.shutdown()
    time.sleep(0.2)    
    
    
def test_kabr_lvl3_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br_lvl3 = run_agent(name='ka_br', base=ka_br.KaBr_lvl3)
    ka_br_lvl3.add_blackboard(bb)
    ka_br_lvl3.connect_writer()
    ka_br_lvl3.connect_executor()
    
    ka_br_lvl3.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 0.6)})
    
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_abstract_lvl(3, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'keff': float, 'void_coeff': float, 'doppler_coeff': float}})
    
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.75}})
    

    bb.set_attr(_ka_to_execute=('ka_br', 10.0))
    ka_br_lvl3.read_bb_lvl()

    bb.send_executor()
    time.sleep(1.1)    
    
    assert bb.get_attr('abstract_lvls')['level 2'] == {'core_1': {'valid': True}}
    
    ns.shutdown()
    time.sleep(0.2) 

def test_kabr_lvl3_add_entry():
    ns = run_nameserver()
    ka_br_lvl3 = run_agent(name='ka_br', base=ka_br.KaBr_lvl3)

    ka_br_lvl3.add_entry(('core_1', None))
    
    assert ka_br_lvl3.get_attr('_entry') == {'valid': True}
    assert ka_br_lvl3.get_attr('_entry_name') == 'core_1'
    
    ns.shutdown()
    time.sleep(0.2) 