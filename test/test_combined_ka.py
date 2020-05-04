import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import ka
import time
import os
import ka_br
import bb_sfr_opt as bb_sfr
import ka_rp
from collections import OrderedDict


#-----------------------------------------
# Test of Combined KaBr_lvl3 and KA_BR_lvl2
#-----------------------------------------

def test_combined_kabr_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_br_lvl3 = run_agent(name='ka_br_lvl3', base=ka_br.KaBr_lvl3)
    ka_br_lvl3.add_blackboard(bb)
    ka_br_lvl3.connect_writer()
    ka_br_lvl3.connect_executor()
    ka_br_lvl3.set_attr(desired_results={'keff': (1.0, 1.2), 'void_coeff': (-200, -75), 'doppler_coeff': (-1.0,-0.6), 'pu_content': (0, 0.6)})
    ka_br_lvl2 = run_agent(name='ka_br_lvl2', base=ka_br.KaBr_lvl2)
    ka_br_lvl2.add_blackboard(bb)
    ka_br_lvl2.connect_writer()
    ka_br_lvl2.connect_executor()
    ka_br_lvl2.set_attr(desired_results={'keff': 'gt', 'void_coeff': 'lt', 'pu_content': 'lt'})
    
    bb.add_abstract_lvl(1, {'pareto type': str})
    bb.add_panel(1, ['new', 'old'])    
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])
    bb.add_abstract_lvl(3, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'keff': float, 'void_coeff': float, 'doppler_coeff': float}})
    bb.add_panel(3, ['new', 'old'])


    
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.75}}, panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.80}}, panel='new')
    bb.update_abstract_lvl(3, 'core_3', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.15, 'void_coeff': -150.0, 'doppler_coeff': -0.70}}, panel='new')

    bb.set_attr(_ka_to_execute=('ka_br_lvl3', 10.0))
    ka_br_lvl3.read_bb_lvl()
    bb.send_executor()
    time.sleep(0.75)    
    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new':{}, 'old': {}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{'core_1': {'valid': True}}, 'old': {}}

    bb.set_attr(_ka_to_execute=('ka_br_lvl2', 10.0))
    ka_br_lvl2.read_bb_lvl()
    bb.send_executor()
    time.sleep(0.75)    

    assert bb.get_attr('abstract_lvls')['level 1'] == {'new':{'core_1' : {'pareto type' : 'pareto'}}, 'old': {}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{}, 'old': {'core_1': {'valid': True}}}

    bb.set_attr(_ka_to_execute=('ka_br_lvl3', 10.0))
    ka_br_lvl3.read_bb_lvl()
    bb.send_executor()
    time.sleep(0.75)

    assert bb.get_attr('abstract_lvls')['level 1'] == {'new':{'core_1' : {'pareto type' : 'pareto'}}, 'old': {}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{'core_2' : {'valid' : True}}, 'old': {'core_1': {'valid': True}}}
    
    bb.set_attr(_ka_to_execute=('ka_br_lvl3', 10.0))
    ka_br_lvl3.read_bb_lvl()
    bb.send_executor()
    time.sleep(0.75)    

    assert bb.get_attr('abstract_lvls')['level 1'] == {'new':{'core_1' : {'pareto type' : 'pareto'}}, 'old': {}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{'core_2' : {'valid' : True},
                                                              'core_3' : {'valid' : True}}, 
                                                       'old': {'core_1': {'valid': True}}}

    bb.set_attr(_ka_to_execute=('ka_br_lvl2', 10.0))
    ka_br_lvl2.read_bb_lvl()
    bb.send_executor()
    time.sleep(0.75) 

    assert bb.get_attr('abstract_lvls')['level 1'] == {'new': {'core_1' : {'pareto type' : 'pareto'},
                                                               'core_3' : {'pareto type' : 'pareto'}}, 'old': {}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new': {}, 
                                                       'old': {'core_1' : {'valid': True},
                                                               'core_2' : {'valid' : True},
                                                               'core_3' : {'valid' : True}}}
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_combined_kabr_karp():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.set_attr(objective_ranges={'cycle length': (0, 1500), 'reactivity swing': (0, 6000), 'burnup': (0,175), 'pu mass': (0, 1750)})
    bb.generate_sm()
    bb.connect_agent(ka_rp.KaRpExplore, 'ka_rp_explore')
    bb.connect_agent(ka_rp.KaRpExploit, 'ka_rp_exploit')
    bb.connect_agent(ka_br.KaBr_lvl3, 'ka_br_lvl3')
    bb.connect_agent(ka_br.KaBr_lvl2, 'ka_br_lvl2')

    # Test first trigger publish (ka_rp_explore)
    bb.publish_trigger()
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0}}
    time.sleep(1.0)
    bb.controller()
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_explore', 1.0)

    # Generate core and test second trigger publish (ka_br_lvl3)
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'cycle length': 375.0, 'reactivity swing': 750.0, 'burnup': 30.0, 'pu mass': 750.0}}, panel='new')
    
    bb.publish_trigger()
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 10.0}}
    bb.controller()
    bb.send_executor()
    time.sleep(0.75)
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl3', 10.0)
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_1': {'valid' : True}}, 'old': {}}
    
    # Test third trigger publish (ka_br_lvl2)
    bb.publish_trigger()
    time.sleep(2.5)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 10.0},
                                    3: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 10.0, 'ka_br_lvl3': 0}}
    bb.controller()
    bb.send_executor()
    time.sleep(0.75)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl2', 10.0)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new' : {'core_1': {'pareto type' : 'pareto'}}, 'old': {}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old': {'core_1': {'valid' : True}}}
    
    # Test fourth trigger publish (ka_rp_exploit)
    bb.publish_trigger()
    time.sleep(1.25)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 10.0},
                                    3: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 10.0, 'ka_br_lvl3': 0},
                                    4: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 2.0,
                                        'ka_br_lvl2': 0.0, 'ka_br_lvl3': 0}}
    bb.controller()
    bb.send_executor()
    time.sleep(5)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_exploit', 2.0)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new' : {}, 'old': {'core_1': {'pareto type' : 'pareto'}}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old': {'core_1': {'valid' : True}}}   
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[64.35, 65.0, 0.4]',
                                                           'core_[65.65, 65.0, 0.4]',
                                                           'core_[65.0, 64.35, 0.4]',
                                                           'core_[65.0, 65.65, 0.4]',
                                                           'core_[65.0, 65.0, 0.396]', 
                                                           'core_[65.0, 65.0, 0.404]',]
    # Test fifth trigger publish (ka_br_lvl3)
    bb.publish_trigger()
    time.sleep(1.25)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 10.0},
                                    3: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 10.0, 'ka_br_lvl3': 0},
                                    4: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 2.0,
                                        'ka_br_lvl2': 0.0, 'ka_br_lvl3': 0},
                                    5: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 10.0}}
    bb.controller()
    bb.send_executor()
    time.sleep(2)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl3', 10.0)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new' : {}, 'old': {'core_1': {'pareto type' : 'pareto'}}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_[64.35, 65.0, 0.4]': {'valid' : True}}, 'old': {'core_1': {'valid' : True}}}   
    
    ns.shutdown()
    time.sleep(0.1)   