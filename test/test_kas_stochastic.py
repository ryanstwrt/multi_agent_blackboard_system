import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import src.ka_s.stochastic as stochastic
import src.bb.blackboard_optimization as bb_opt
import numpy as np
import pickle
import time

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)

#----------------------------------------------------------
# Tests fopr KA-RP-Explore
#----------------------------------------------------------

def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=stochastic.Stochastic)
    
    assert rp.get_attr('_class') == 'global search stochastic'
    
    ns.shutdown()
    time.sleep(0.1)

def test_handler_trigger_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()    
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(stochastic.Stochastic, 'ka_rp')
    
    bb.publish_trigger()
    time.sleep(0.15)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0.250001}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 0.250001)
    
    bb.publish_trigger()
    time.sleep(0.15)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0.250001}, 2: {'ka_rp': 0.500002}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 0.500002)
    
    ns.shutdown()
    time.sleep(0.1)

def test_search_method():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=stochastic.Stochastic)
    rp.set_random_seed(seed=1)
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' : {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                  'experiments': {'length':         2, 
                                                  'dict':      {'0': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                                                'random variable': {'ll': 0,  'ul': 2,  'variable type': float}},
                                                  'variable type': dict}})
    
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.search_method()
    assert rp.get_attr('current_design_variables') == {'height': 62.51066, 'smear': 64.40649, 'pu_content': 0.00011, 'position': 'no_exp', 'experiments': {'0':'exp_a', 'random variable': 0.18468}}
    rp.set_random_seed(seed=2)
    #This entry is the first for seed 2, so we should skip it and get a new entry
    rp.set_attr(_lvl_data={'core_[63.07985,50.51852,0.54966,no_exp,exp_a,0.64107]': {}})
    rp.search_method()
    assert rp.get_attr('_entry_name') == 'core_[54.6328,63.97725,0.11995,no_exp,no_exp,1.24227]'
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_random_seed():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=stochastic.Stochastic)
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                 'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                 'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}})    
    rp.set_random_seed(seed=10983)
    rp.search_method()
    assert rp.get_attr('current_design_variables') == {'height': 77.10531, 'pu_content': 0.29587, 'smear': 64.46135}
    rp.set_random_seed()
    rp.search_method()
    assert rp.get_attr('current_design_variables') != {'height': 77.10531, 'pu_content': 0.29587, 'smear': 64.46135}
    
    ns.shutdown()
    time.sleep(0.1)    
    
def test_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(stochastic.Stochastic, 'ka_rp_explore')
    
    rp = ns.proxy('ka_rp_explore')
    rp.set_attr(_trigger_val=1)
    bb.set_attr(_ka_to_execute=('ka_rp_explore', 2))
    bb.send_executor()
    time.sleep(0.2)
    
    entry = rp.get_attr('_entry')
    core_name = rp.get_attr('_entry_name')
    bb_entry = {core_name: entry}
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == bb_entry
    assert rp.get_attr('_trigger_val') == 0    

    ns.shutdown()
    time.sleep(0.1)    