import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import ka
import pandas as pd
import time
import os
import ka_rp
from collections import OrderedDict

def test_karp_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRp)
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 0
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 1.0
    
    ns.shutdown()
    time.sleep(0.1)
    
#----------------------------------------------------------
# Tests fopr KA-RP-verify
#----------------------------------------------------------
    
def test_karp_verify_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRp_verify)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 2
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 1.0
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('interp_path') == None
    assert rp.get_attr('interpolator_dict') == {}
    assert rp.get_attr('objectives') == ['keff', 'void_coeff', 'doppler_coeff']
    assert rp.get_attr('independent_variable_ranges') == OrderedDict({'height': (50,80),
                                                                     'smear': (50,70),
                                                                     'pu_content':(0,1)})
    ns.shutdown()
    time.sleep(0.1)

def test_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRp_verify)
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    assert rp.get_attr('_entry_name') == 'core_{}'.format([x for x in rp.get_attr('design_variables').values()])
    
    ns.shutdown()
    time.sleep(0.1)
    
#----------------------------------------------------------
# Tests fopr KA-RP-Explore
#----------------------------------------------------------

def test_karp_scout_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 1.0
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('interp_path') == None
    assert rp.get_attr('interpolator_dict') == {}
    assert rp.get_attr('objectives') == ['keff', 'void_coeff', 'doppler_coeff']
    assert rp.get_attr('independent_variable_ranges') == OrderedDict({'height': (50,80),
                                                                     'smear': (50,70),
                                                                     'pu_content':(0,1)})
    ns.shutdown()
    time.sleep(0.1)
    
def test_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_create_sm():
    """Create a test when we determine what type of SM we want to use"""
    pass

#----------------------------------------------------------
# Tests fopr KA-RP-Explore
#----------------------------------------------------------

def test_karp_scout_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 1.0
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('interp_path') == None
    assert rp.get_attr('interpolator_dict') == {}
    assert rp.get_attr('objectives') == ['keff', 'void_coeff', 'doppler_coeff']
    assert rp.get_attr('independent_variable_ranges') == OrderedDict({'height': (50,80),
                                                                     'smear': (50,70),
                                                                     'pu_content':(0,1)})
    ns.shutdown()
    time.sleep(0.1)
    
def test_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    
    ns.shutdown()
    time.sleep(0.1)