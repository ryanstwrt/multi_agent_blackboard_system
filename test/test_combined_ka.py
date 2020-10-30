import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pickle
import src.ka as ka
import time
import os
import src.ka_br as ka_br
import src.bb_opt as bb_opt
import src.ka_rp as ka_rp

    
def test_combined_kabr_karp():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    with open('./sm_gpr.pkl', 'rb') as pickle_file:
        sm_ga = pickle.load(pickle_file)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    obj = {'reactivity swing': {'ll':0,   'ul':1000,  'goal':'lt', 'variable type': float},
           'burnup':           {'ll':0,   'ul':200,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=obj)
    bb.connect_agent(ka_rp.KaGlobal, 'ka_rp_explore')
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp_exploit')
    bb.connect_agent(ka_br.KaBr_lvl3, 'ka_br_lvl3')
    bb.connect_agent(ka_br.KaBr_lvl2, 'ka_br_lvl2')
    bb.connect_agent(ka_br.KaBr_lvl1, 'ka_br_lvl1')
    
    rp_explore = ns.proxy('ka_rp_explore')
    bb_lvl1 = ns.proxy('ka_br_lvl1')
    bb_lvl2 = ns.proxy('ka_br_lvl2')
    bb_lvl3 = ns.proxy('ka_br_lvl3')
    bb_lvl1.set_attr(_lower_objective_reference_point=[0,0])
    bb_lvl1.set_attr(_upper_objective_reference_point=[1,1])
    bb_lvl2.set_attr(_num_allowed_entries=1)
    bb_lvl3.set_attr(_num_allowed_entries=1)

    # Test first trigger publish (ka_rp_explore), but don't execute it, then update the bb with a new core design
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 0}}
    bb.controller()
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_explore', 0.250001)

    # Generate core and test second trigger publish (ka_br_lvl3)
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'reactivity swing': 800.0, 'burnup': 30.0},
                                         'constraints': {'eol keff': 1.1}}, panel='new')
    
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 3.00000000001}}
    bb.controller()
    bb.send_executor()
    time.sleep(0.5)
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl3', 3.00000000001)
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_1': {'valid' : True}}, 'old': {}}
    
    # Test third trigger publish (ka_br_lvl2)
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 3.00000000001},
                                    3: {'ka_rp_explore': 0.750003, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl3': 0}}
    bb.controller()
    bb.send_executor()
    time.sleep(0.5)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl2', 4.00000000002)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1': {'pareto type' : 'pareto', 'fitness function' : 0.35}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old': {'core_1': {'valid' : True}}}

    
    # Test fifth trigger publish (ka_rp_exploit)
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 3.00000000001},
                                    3: {'ka_rp_explore': 0.750003, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl3': 0},
                                    4: {'ka_rp_explore': 1.000004, 'ka_rp_exploit': 5.00001,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 0},}
    bb.controller()
    bb.send_executor()
    time.sleep(0.5)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_exploit', 5.00001)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1': {'pareto type' : 'pareto', 'fitness function' : 0.35}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old': {'core_1': {'valid' : True}}}   
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[61.75, 65.0, 0.4]',
                                                           'core_[68.25, 65.0, 0.4]',
                                                           'core_[65.0, 61.75, 0.4]',
                                                           'core_[65.0, 68.25, 0.4]',
                                                           'core_[65.0, 65.0, 0.38]', 
                                                           'core_[65.0, 65.0, 0.42]',]
    # Test sixth trigger publish (ka_br_lvl3)
    print(bb.get_attr('abstract_lvls')['level 3'])
    bb.publish_trigger()
    time.sleep(0.1)
    assert bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    2: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 3.00000000001},
                                    3: {'ka_rp_explore': 0.750003, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl3': 0},
                                    4: {'ka_rp_explore': 1.000004, 'ka_rp_exploit': 5.00001,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 0},
                                    5: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0,
                                        'ka_br_lvl1': 0, 'ka_br_lvl2': 0, 'ka_br_lvl3': 3.00000000001},}
    bb.controller()
    bb.send_executor()
    time.sleep(0.5)
    
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl3', 3.00000000001)    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1': {'pareto type' : 'pareto', 'fitness function' : 0.35}}
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_[61.75, 65.0, 0.4]': {'valid' : True},
                                                                'core_[68.25, 65.0, 0.4]': {'valid' : True},
                                                                'core_[65.0, 61.75, 0.4]': {'valid' : True},
                                                                'core_[65.0, 68.25, 0.4]': {'valid' : True},
                                                                'core_[65.0, 65.0, 0.38]': {'valid' : True},
                                                                'core_[65.0, 65.0, 0.42]': {'valid' : True}}, 
                                                       'old' : {'core_1': {'valid' : True}}}   
    
    bb_lvl3.set_attr(_num_allowed_entries=10)

    #Test the workings of ka_br_lvl1 
    for i in range(2):
        bb.publish_trigger()
        time.sleep(0.1)
        bb.controller()
        bb.send_executor()
        time.sleep(0.5)

    a = bb.get_attr('abstract_lvls')['level 3']['old']
    assert bb.get_attr('_ka_to_execute') == ('ka_br_lvl1', 6.00000000003)
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[61.75, 65.0, 0.4]': {'pareto type' : 'pareto', 'fitness function' : 0.59328},
                                                       'core_[68.25, 65.0, 0.4]': {'pareto type' : 'pareto', 'fitness function' : 0.64323},
                                                       'core_[65.0, 65.0, 0.38]': {'pareto type' : 'pareto', 'fitness function' : 0.62255}}

    ns.shutdown()
    time.sleep(0.1)   