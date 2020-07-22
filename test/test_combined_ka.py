import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pickle
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
    ka_br_lvl3.connect_trigger()
    ka_br_lvl3.set_attr(_objective_ranges={'keff':          {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                           'void_coeff':    {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}, 
                                           'pu_content':    {'ll': 0,    'ul': 0.6, 'goal':'lt', 'variable type': float},
                                           'doppler_coeff': {'ll':-1.0,  'ul':-0.6, 'goal':'lt', 'variable type': float}})
    ka_br_lvl2 = run_agent(name='ka_br_lvl2', base=ka_br.KaBr_lvl2)
    ka_br_lvl2.add_blackboard(bb)
    ka_br_lvl2.connect_writer()
    ka_br_lvl2.connect_executor()
    ka_br_lvl2.connect_trigger()
    ka_br_lvl2.set_attr(_objective_ranges={'keff':          {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                           'void_coeff':    {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}, 
                                           'pu_content':    {'ll': 0,    'ul': 0.6, 'goal':'lt', 'variable type': float},
                                           'doppler_coeff': {'ll':-1.0,  'ul':-0.6, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])
    bb.add_abstract_lvl(3, {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'keff': float, 'void_coeff': float, 'doppler_coeff': float}})
    bb.add_panel(3, ['new', 'old'])


    
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.75}}, panel='new')
    bb.update_abstract_lvl(3, 'core_2', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.1, 'void_coeff': -150.0, 'doppler_coeff': -0.80}}, panel='new')
    bb.update_abstract_lvl(3, 'core_3', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'keff': 1.15, 'void_coeff': -150.0, 'doppler_coeff': -0.70}}, panel='new')

    bb.publish_trigger()
    time.sleep(0.1)
    bb.set_attr(_ka_to_execute=('ka_br_lvl3', 10.0))
    bb.send_executor()
    time.sleep(1)    
    
    assert bb.get_attr('abstract_lvls')['level 1'] == {}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{'core_1': {'valid': True}}, 'old': {}}

    bb.publish_trigger()
    time.sleep(0.1)
    bb.set_attr(_ka_to_execute=('ka_br_lvl2', 10.0))
    bb.send_executor()
    time.sleep(1)    

    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1' : {'pareto type' : 'pareto', 'fitness function': 2.19167}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{}, 'old': {'core_1': {'valid': True}}}

    bb.publish_trigger()
    time.sleep(0.1)
    bb.set_attr(_ka_to_execute=('ka_br_lvl3', 10.0))
    bb.send_executor()
    time.sleep(1)

    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1' : {'pareto type' : 'pareto', 'fitness function': 2.19167}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{'core_2' : {'valid' : True}}, 'old': {'core_1': {'valid': True}}}
    
    bb.publish_trigger()
    time.sleep(0.1)
    bb.set_attr(_ka_to_execute=('ka_br_lvl3', 10.0))
    bb.send_executor()
    time.sleep(1)    

    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1' : {'pareto type' : 'pareto', 'fitness function': 2.19167}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new':{'core_2' : {'valid' : True},
                                                              'core_3' : {'valid' : True}}, 
                                                       'old': {'core_1': {'valid': True}}}

    bb.publish_trigger()
    time.sleep(0.1)
    bb.set_attr(_ka_to_execute=('ka_br_lvl2', 10.0))
    bb.send_executor()
    time.sleep(1) 

    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_2' : {'pareto type' : 'pareto', 'fitness function': 2.06667}}

    assert bb.get_attr('abstract_lvls')['level 2'] == {'new': {'core_3' : {'valid' : True}}, 
                                                       'old': {'core_1' : {'valid': True},
                                                               'core_2' : {'valid' : True}}}
    bb.publish_trigger()
    time.sleep(0.1)
    bb.set_attr(_ka_to_execute=('ka_br_lvl2', 10.0))
    bb.send_executor()
    time.sleep(1) 

    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_2' : {'pareto type' : 'pareto', 'fitness function': 2.06667},
                                                       'core_3' : {'pareto type' : 'weak', 'fitness function': 2.06667}}

    assert bb.get_attr('abstract_lvls')['level 2'] == {'new': {}, 
                                                       'old': {'core_1' : {'valid': True},
                                                               'core_2' : {'valid': True},
                                                               'core_3' : {'valid': True}}}
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_combined_kabr_karp():
    ns = run_nameserver()
    
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.initialize_abstract_level_3()
    model = 'ann'
    with open('test/sm_{}.pkl'.format(model), 'rb') as pickle_file:
        sm_ga = pickle.load(pickle_file)
    bb.set_attr(sm_type=model)
    bb.set_attr(_sm=sm_ga)    
    bb.connect_agent(ka_rp.KaGlobal, 'ka_rp_explore')
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp_exploit')
    bb.connect_agent(ka_br.KaBr_lvl3, 'ka_br_lvl3')
    bb.connect_agent(ka_br.KaBr_lvl2, 'ka_br_lvl2')
    
    rp_explore = ns.proxy('ka_rp_explore')
    bb_lvl2 = ns.proxy('ka_br_lvl2')
    bb_lvl3 = ns.proxy('ka_br_lvl3')
    bb_lvl2.set_attr(_num_allowed_entries=1)
    bb_lvl3.set_attr(_num_allowed_entries=1)

    # Test first trigger publish (ka_rp_explore)
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.25, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0}}
    bb.controller()
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_explore', 0.25)

    # Generate core and test second trigger publish (ka_br_lvl3)
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4, 'cycle length': 375.0, 'reactivity swing': 750.0, 'burnup': 30.0, 'pu mass': 750.0}}, panel='new')
    
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.25, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 0.5, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 4}}
    bb.controller()
    bb.send_executor()
    time.sleep(1.0)
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl3', 4)
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_1': {'valid' : True}}, 'old': {}}
    
    # Test third trigger publish (ka_br_lvl2)
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.25, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 0.5, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 4},
                                    3: {'ka_rp_explore': 0.75, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 5, 'ka_br_lvl3': 0}}
    bb.controller()
    bb.send_executor()
    time.sleep(1.0)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl2', 5)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1': {'pareto type' : 'pareto', 'fitness function' : 2.73889}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old': {'core_1': {'valid' : True}}}
    
    # Test fourth trigger publish (ka_rp_exploit)
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.25, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 0.5, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 4},
                                    3: {'ka_rp_explore': 0.75, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 5, 'ka_br_lvl3': 0},
                                    4: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 5,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0}}
    bb.controller()
    bb.send_executor()
    time.sleep(1.0)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_exploit', 5)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1': {'pareto type' : 'pareto', 'fitness function' : 2.73889}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old': {'core_1': {'valid' : True}}}   
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[61.75, 65.0, 0.4]',
                                                           'core_[68.25, 65.0, 0.4]',
                                                           'core_[65.0, 61.75, 0.4]',
                                                           'core_[65.0, 68.25, 0.4]',
                                                           'core_[65.0, 65.0, 0.38]', 
                                                           'core_[65.0, 65.0, 0.42]',]
    # Test fifth trigger publish (ka_br_lvl3)
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.25, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 0.5, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 4},
                                    3: {'ka_rp_explore': 0.75, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 5, 'ka_br_lvl3': 0},
                                    4: {'ka_rp_explore': 1.0, 'ka_rp_exploit': 5,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    5: {'ka_rp_explore': 1.25, 'ka_rp_exploit': 0,
                                        'ka_br_lvl2': 0, 'ka_br_lvl3': 9}}
    bb.controller()
    bb.send_executor()
    time.sleep(1.0)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl3', 9)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1': {'pareto type' : 'pareto', 'fitness function' : 2.73889}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_[61.75, 65.0, 0.4]': {'valid' : True}}, 'old': {'core_1': {'valid' : True}}}   
    
    ns.shutdown()
    time.sleep(0.1)   