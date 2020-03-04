import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import knowledge_agent as ka
import pandas as pd
import time
import os

def test_rp_proxy():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics_Proxy)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_writer()
    ka_rp.objectives = ['keff', 'void_coeff', 'doppler_coeff', 'pu_content']
    ka_rp.design_variables = ['height', 'smear', 'pu_content']
    ka_rp.set_attr(function_evals=10)
    ka_rp.results_path = '/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/'
    
    assert ka_rp.get_attr('results_path') == '/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/'
    
    ka_rp.set_attr(weights=[0,0,0,0])
    ka_rp.run_dakota_proxy()
    ka_rp.read_dakota_results()
    ka_rp.write_to_bb()

    assert os.path.isfile('/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/soo_pareto_0000.h5') == True
    bb_lvl_2 = bb.get_attr('lvl_3')
    core = 'core_0000'
    bb_lvl_2 = bb_lvl_2[core]['reactor_parameters']
    assert bb_lvl_2['height'][core] == 57.95
    assert bb_lvl_2['smear'][core] == 54.00
    assert bb_lvl_2['pu_content'][core] == 0.0575
    assert round(bb_lvl_2['keff'][core],4) == -539.3914
    assert round(bb_lvl_2['void'][core],2) == -198.81
    assert round(bb_lvl_2['Doppler'][core],4) == -0.981
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
    ka_rp.connect_writer()
    ka_rp.objectives = ['keff', 'void_coeff', 'doppler_coeff', 'pu_content']
    ka_rp.design_variables = ['height', 'smear', 'pu_content']
    ka_rp.set_attr(function_evals=10)
    ka_rp.results_path = '/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/'

    ka_rp.set_attr(weights=[0,0,0,0])
    ka_rp.run_dakota_proxy()
    ka_rp.read_dakota_results()
    ka_rp.write_to_bb()
    
    ka_rp.set_attr(weights=[1,1,1,1])
    ka_rp.run_dakota_proxy()
    ka_rp.read_dakota_results()
    ka_rp.write_to_bb()
    bb_lvl_3 = bb.get_attr('lvl_3')
    core = 'core_1111'
    bb_lvl_3 = bb_lvl_3[core]['reactor_parameters']
    assert bb_lvl_3['height'][core] == 57.95
    assert bb_lvl_3['smear'][core] == 54.00
    assert bb_lvl_3['pu_content'][core] == 0.05750
    assert round(bb_lvl_3['keff'][core],4) == -539.3914
    assert round(bb_lvl_3['void'][core],2) == -198.81
    assert round(bb_lvl_3['Doppler'][core],4) == -0.981
    assert bb_lvl_3['w_keff'][core] == 1
    assert bb_lvl_3['w_void'][core] == 1
    assert bb_lvl_3['w_dopp'][core] == 1
    assert bb_lvl_3['w_pu'][core] == 1    

    ns.shutdown()
    time.sleep(0.1)

def test_bb_lvl2_proxy():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_bb_lvl2 = run_agent(name='ka_bb_lvl2', base=ka.KaBbLvl2_Proxy)
    ka_bb_lvl2.add_blackboard(bb)
    ka_bb_lvl2.connect_writer()    

    rx_params_dict = {'core_0000': {'height': 55.00,
                                       'smear': 65.76,
                                       'pu_content': 0.5477,
                                       'keff': 1.0302,
                                       'void': -110.023,
                                       'Doppler': -0.6923,
                                       'w_keff': 0.6,
                                       'w_void': 0.15,
                                       'w_dopp': 0.15,
                                       'w_pu': 0.1}}
    rx_params = pd.DataFrame.from_dict(rx_params_dict, orient='index')
    
    lvl3_test = {'core_0000': {'reactor_parameters': rx_params, 'xs_Set': None}}
    
    bb.set_attr(lvl_3=lvl3_test)
    
    ka_bb_lvl2.read_bb_lvl_2()
    ka_bb_lvl2.write_to_bb()
    
    bb_lvl_2 = bb.get_attr('lvl_2')
    core = 'core_0000'
    bb_lvl_2 = bb_lvl_2[core]['exp_num']
    
    assert bb_lvl_2['w_keff'] == 0.6
    assert bb_lvl_2['w_void'] == 0.15
    assert bb_lvl_2['w_dopp'] == 0.15
    assert bb_lvl_2['w_pu'] == 0.1
    
    ns.shutdown()
    time.sleep(0.1)

    
def connect_agent(agent,bb):
    agent.add_blackboard(bb)
    agent.connect_writer()
    agent.connect_trigger()
    agent.connect_execute()
    if 'rp' in agent.get_attr('name'):
        agent.set_attr(objectives=['keff', 'void_coeff', 'doppler_coeff', 'pu_content'])
        agent.set_attr(design_variables=['height', 'smear', 'pu_content'])
        agent.set_attr(function_evals=10)
        agent.set_attr(results_path='/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/')


    
def test_execute():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp0 = run_agent(name='ka_rp0', base=ka.KaReactorPhysics_Proxy)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics_Proxy)
    ka_rp1 = run_agent(name='ka_rp1', base=ka.KaReactorPhysics_Proxy)

    connect_agent(ka_rp0, bb)
    connect_agent(ka_rp, bb)
    connect_agent(ka_rp1, bb)

    ka_rp0.weights = [0,0,0]
    ka_rp0.objectives = [0,0]

    assert ka_rp0.get_attr('execute_alias') == 'execute_ka_rp0'
    assert bb.get_attr('agent_addrs')['ka_rp0']['execute'] == (ka_rp0.get_attr('execute_alias'), ka_rp0.get_attr('execute_addr'))
    
    try:
        bb.send('execute_ka_rp0', 'test')
    except AssertionError:
        pass

    time.sleep(0.2)
    ka_rp.set_attr(core_name='core_1')    
    ka_rp1.set_attr(core_name='core_2')    
    ka_rp.objectives = ['keff', 'void_coeff', 'doppler_coeff', 'pu_content']
    ka_rp.design_variables = ['height', 'smear', 'pu_content']
    ka_rp.set_attr(function_evals=10)
    ka_rp.results_path = '/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/'  
    ka_rp.set_attr(weights=[0,0,0,0])
    
    ka_rp1.objectives = ['keff', 'void_coeff', 'doppler_coeff', 'pu_content']
    ka_rp1.design_variables = ['height', 'smear', 'pu_content']
    ka_rp1.set_attr(function_evals=10)
    ka_rp1.results_path = '/Users/ryanstewart/projects/Dakota_Interface/GA/mabs_results/'
    ka_rp1.set_attr(weights=[1,1,1,1])
    
    bb.set_attr(trigger_events={0: {}})
    
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    bb.send_execute()
    time.sleep(0.25)
    bb.send('execute_ka_rp1', ('ka_rp1', 1.0))

    time.sleep(5)
    bb_lvl_3 = bb.get_attr('lvl_3')
    core = 'core_1111'
#    bb_lvl_3 = bb_lvl_3[core]['reactor_parameters']
#    assert bb_lvl_3['height'][core] == 57.95
#    assert bb_lvl_3['smear'][core] == 54.00
#    assert bb_lvl_3['pu_content'][core] == 0.05750
#    assert round(bb_lvl_3['keff'][core],4) == 0.8288
#    assert round(bb_lvl_3['void'][core],2) == -185.5
#    assert round(bb_lvl_3['Doppler'][core],4) == -0.9269
#    assert bb_lvl_3['w_keff'][core] == 1
#    assert bb_lvl_3['w_void'][core] == 1
#    assert bb_lvl_3['w_dopp'][core] == 1
#    assert bb_lvl_3['w_pu'][core] == 1  

    bb_lvl_3 = bb.get_attr('lvl_3')
    core = 'core_0000'
#    bb_lvl_3 = bb_lvl_3[core]['reactor_parameters']
#    assert bb_lvl_3['height'][core] == 50.85
#    assert bb_lvl_3['smear'][core] == 69.10
#    assert bb_lvl_3['pu_content'][core] == 0.3050
#    assert round(bb_lvl_3['keff'][core],4) == 0.9786
#    assert round(bb_lvl_3['void'][core],2) == -132.31
#    assert round(bb_lvl_3['Doppler'][core],4) == -0.637
#    assert bb_lvl_3['w_keff'][core] == 0
#    assert bb_lvl_3['w_void'][core] == 0
#    assert bb_lvl_3['w_dopp'][core] == 0
#    assert bb_lvl_3['w_pu'][core] == 0
    
    ns.shutdown()
    time.sleep(0.2)