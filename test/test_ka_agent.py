import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pandas as pd
import numpy as np
import blackboard
import knowledge_agent as ka
import time
import os

def test_ka_init_agent():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    assert ka_b.get_attr('entry') == None
    assert ka_b.get_attr('bb') == None
    assert ka_b.get_attr('rep_addr') == None
    assert ka_b.get_attr('rep_alias') == None
    ns.shutdown()
    time.sleep(0.1)
    
def test_ka_reactor_physics_init():
    ns = run_nameserver()
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    assert ka_rp.get_attr('entry') == None
    assert ka_rp.get_attr('bb') == None
    assert ka_rp.get_attr('rep_addr') == None
    assert ka_rp.get_attr('rep_alias') == None
    assert ka_rp.get_attr('core_name') == None
    assert ka_rp.get_attr('xs_set') == None
    assert ka_rp.get_attr('rx_parameters') == None
    assert ka_rp.get_attr('surrogate_models') == None
    ns.shutdown()
    time.sleep(0.1)

def test_add_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_b.add_blackboard(bb)
    ka_rp.add_blackboard(bb)
    
    ka_b_bb = ka_b.get_attr('bb')
    ka_b_rp = ka_rp.get_attr('bb')
    assert ka_b.get_attr('bb') == bb
    assert ka_b_bb.get_attr('trained_models') == None
    assert ka_rp.get_attr('bb') == bb
    assert ka_b_rp.get_attr('trained_models') == None
    bb.set_attr(trained_models=10)
    assert ka_b_bb.get_attr('trained_models') == 10
    assert ka_b_rp.get_attr('trained_models') == 10

    assert bb.get_attr('agent_addrs') == {'ka_rp': {}, 'ka_base': {}}
    ns.shutdown()
    time.sleep(0.1)

def test_connect_REP_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)

    ka_b.add_blackboard(bb)
    ka_b.connect_REP_blackboard()
    ka_rp.connect_REP_blackboard()
    assert ka_b.get_attr('rep_alias') == 'write_ka_base'
    assert ka_rp.get_attr('rep_alias') == 'write_ka_rp'
    assert bb.get_attr('agent_addrs')['ka_base'] == (ka_b.get_attr('rep_alias'), ka_b.get_attr('rep_addr'))
    assert bb.get_attr('agent_addrs')['ka_rp'] == (ka_rp.get_attr('rep_alias'), ka_rp.get_attr('rep_addr'))
    ns.shutdown()
    time.sleep(0.1)

def test_connect_trigger_event():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics_Proxy)
    ka_rp.add_blackboard(bb)
    
    ka_rp.connect_trigger_event()
    assert ka_rp.get_attr('trigger_alias') == 'trigger_event'
    assert bb.get_attr('agent_addrs')['ka_rp']['trigger'] == ('trigger_event', ka_rp.get_attr('trigger_addr'))
    ns.shutdown()
    time.sleep(0.1)
    
def test_write_to_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp2 = run_agent(name='ka_rp_2', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_REP_blackboard()
    ka_rp2.add_blackboard(bb)
    ka_rp2.connect_REP_blackboard()
    
    assert bb.get_attr('agent_writing') == False
    ka_rp.set_attr(core_name='core_1')
    ka_rp2.set_attr(core_name='core_2')
    ka_rp.write_to_blackboard()
    ka_rp2.write_to_blackboard()
    lvl_3 = bb.get_attr('lvl_3')
    assert bb.get_attr('agent_writing') == False
    assert lvl_3 == {'core_1': {'reactor_parameters': None, 'xs_set': None},
                     'core_2': {'reactor_parameters': None, 'xs_set': None}}

    ns.shutdown()
    time.sleep(0.1)
    
def test_read_dakota_results():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_REP_blackboard()
    ka_rp.set_attr(weights=[0,0,0,0])
    assert ka_rp.get_attr('weights') == [0,0,0,0]
    ka_rp.read_dakota_results()
    rx_parameters = {'height': 72.0, 'smear': 66.8, 'pu_content': 0.0025, 'keff': 0.965775, 'void': -128.43352, 'Doppler': -0.665306}
    mabs_rx_params = ka_rp.get_attr('rx_parameters')
    for k,v in rx_parameters.items():
        np.allclose(mabs_rx_params[k]['core_0_0_0_0'], v, 1e-4)

    ns.shutdown()
    time.sleep(0.1)

    
#Test Proxy & Ability to Add to DB

def test_proxy():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics_Proxy)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_REP_blackboard()
    ka_rp.objectives = ['keff', 'void_coeff', 'doppler_coeff', 'pu_content']
    ka_rp.design_variables = ['height', 'smear', 'pu_content']
    ka_rp.set_attr(function_evals=10)
    ka_rp.results_path = '/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/'
    
    assert ka_rp.get_attr('results_path') == '/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/'
    
    ka_rp.set_attr(weights=[0,0,0,0])
    ka_rp.run_dakota_proxy()
    ka_rp.read_dakota_results()
    ka_rp.write_to_blackboard()

    assert os.path.isfile('/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/soo_pareto_0000.h5') == True
    bb_lvl_2 = bb.get_attr('lvl_3')
    core = 'core_0000'
    bb_lvl_2 = bb_lvl_2[core]['reactor_parameters']
    assert bb_lvl_2['height'][core] == 50.85
    assert bb_lvl_2['smear'][core] == 69.10
    assert bb_lvl_2['pu_content'][core] == 0.3050
    assert round(bb_lvl_2['keff'][core],4) == 0.9786
    assert round(bb_lvl_2['void'][core],2) == -132.31
    assert round(bb_lvl_2['Doppler'][core],4) == -0.637
    assert bb_lvl_2['w_keff'][core] == 0
    assert bb_lvl_2['w_void'][core] == 0
    assert bb_lvl_2['w_dopp'][core] == 0
    assert bb_lvl_2['w_pu'][core] == 0

    ns.shutdown()
    time.sleep(0.1)

    
def test_add_second_entry():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics_Proxy)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_REP_blackboard()
    ka_rp.objectives = ['keff', 'void_coeff', 'doppler_coeff', 'pu_content']
    ka_rp.design_variables = ['height', 'smear', 'pu_content']
    ka_rp.set_attr(function_evals=10)
    ka_rp.results_path = '/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/'

    ka_rp.set_attr(weights=[0,0,0,0])
    ka_rp.run_dakota_proxy()
    ka_rp.read_dakota_results()
    ka_rp.write_to_blackboard()
    
    ka_rp.set_attr(weights=[1,1,1,1])
    ka_rp.run_dakota_proxy()
    ka_rp.read_dakota_results()
    ka_rp.write_to_blackboard()
    bb_lvl_2 = bb.get_attr('lvl_3')
    core = 'core_1111'
    bb_lvl_2 = bb_lvl_2[core]['reactor_parameters']
    assert bb_lvl_2['height'][core] == 57.95
    assert bb_lvl_2['smear'][core] == 54.00
    assert bb_lvl_2['pu_content'][core] == 0.05750
    assert round(bb_lvl_2['keff'][core],4) == 0.8288
    assert round(bb_lvl_2['void'][core],2) == -185.5
    assert round(bb_lvl_2['Doppler'][core],4) == -0.9269
    assert bb_lvl_2['w_keff'][core] == 1
    assert bb_lvl_2['w_void'][core] == 1
    assert bb_lvl_2['w_dopp'][core] == 1
    assert bb_lvl_2['w_pu'][core] == 1    

    ns.shutdown()
    time.sleep(0.1)
