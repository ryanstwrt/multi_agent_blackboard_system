import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import ka
import pandas as pd
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
    
    ns.shutdown()
    time.sleep(0.2)

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
    
    ns.shutdown()
    time.sleep(0.2)
    
def test_kabr_trigger_handler_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    ka_b.add_blackboard(bb)
    ka_b.connect_trigger()
    
    bb.publish_trigger()
    
    assert ka_b.get_attr('_trigger_val') == 0
    assert bb.get_attr('_kaar') == {1: {'ka_br': 0}}
    
    ka_b.set_attr(_entry_name='test')
    bb.publish_trigger()

    assert ka_b.get_attr('_trigger_val') == 10
    assert bb.get_attr('_kaar') == {1: {'ka_br': 0},
                                    2: {'ka_br': 10}}
    ns.shutdown()
    time.sleep(0.2)
    
def test_kabr_lvl2_determine_valid_core():
    ns = run_nameserver()
    ka_br_lvl2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    
    ka_br_lvl2.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 0.6)})
    bool_ = ka_br_lvl2.determine_valid_core({'keff': 1.1, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.4})
    assert bool_ == True
    bool_ = ka_br_lvl2.determine_valid_core({'keff': 0.9, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.4})
    assert bool_ == False

    ns.shutdown()
    time.sleep(0.2)
    
def test_kabr_lvl2_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br_lvl2 = run_agent(name='ka_br', base=ka_br.KaBr_lvl2)
    ka_br_lvl2.add_blackboard(bb)
    ka_br_lvl2.connect_writer()
    ka_br_lvl2.connect_executor()
    
    ka_br_lvl2.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 0.6)})
    
    bb.add_abstract_lvl(1, {'valid': bool})
    bb.add_abstract_lvl(2, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'keff': float, 'void_coeff': float, 'doppler_coeff': float}})
    
    bb.update_abstract_lvl(2, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.75}})

    bb.set_attr(_ka_to_execute=('ka_br', 10.0))
    bb.send_executor()
    time.sleep(1.1)    

    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1': {'valid': True}}
    
    ns.shutdown()
    time.sleep(0.2)    

    