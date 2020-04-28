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
import bb_basic

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
    assert rp.get_attr('objectives') == ['keff', 'void', 'doppler']
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
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('objectives') == ['keff', 'void', 'doppler']
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
    
def test_create_sm_interpolate():
    """Create a test when we determine what type of SM we want to use"""
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    rp.create_sm()
    sm = rp.get_attr('_sm')
    keff = sm['keff']((61.37,51.58,0.7340))
    assert keff == 0.9992587833657331
    
    ns.shutdown()
    time.sleep(0.1)

def test_create_sm_regression():
    """Create a test when we determine what type of SM we want to use"""
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    rp.set_attr(sm_type='lr')
    rp.create_sm()
    sm = rp.get_attr('_sm')
    objs = sm.predict('lr', [[61.37,51.58,0.7340]])
    assert round(objs[0][0], 8) == 0.99992182
    assert sm.models['lr']['score'] == 0.93162733339492
    assert sm.models['lr']['mse_score'] == 0.06837266660508003
    
    ns.shutdown()
    time.sleep(0.1)
    
#----------------------------------------------------------
# Tests fopr KA-RP-Exploit
#----------------------------------------------------------

def test_karp_exploit_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExploit)
    
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
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('objectives') == ['keff', 'void', 'doppler']
    assert rp.get_attr('independent_variable_ranges') == OrderedDict({'height': (50,80),
                                                                     'smear': (50,70),
                                                                     'pu_content':(0,1)})
    assert rp.get_attr('perturbations') == [0.99, 1.01]
    assert rp.get_attr('perturbed_cores') == {}
    assert rp.get_attr('lvl1') == {}
    ns.shutdown()
    time.sleep(0.1)
    
def test_exploit_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExploit)
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_perturb_design():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_basic.BbSfrOpt)
    bb.connect_agent(ka_rp.KaRpExploit, 'ka_rp_exploit')
    
#    proxy_addrs = proxy.NSProxy()
 #   rp1 = proxy_addrs('ka_rp_exploit')
  #  bb.update_abstract_lvl(1, {'core1': {'Pareto' : 'pareto'}})
   # bb.update_abstract_lvl(3, {'core1': {'reactor parameters': {'height': 60, 'smear': 70, 'pu_content': 0.2, 'keff': 1.0, 'void_coeff': -110, 'doppler_coeff': -0.6}}})
    
    
    
    ns.shutdown()
    time.sleep(0.1)    
    