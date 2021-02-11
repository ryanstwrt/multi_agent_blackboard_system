import src.controller as controller
import src.bb.blackboard as blackboard
import src.bb.blackboard_optimization as bb_opt
import time
import os
import pickle
from src.ka.ka_s.stochastic import Stochastic
from src.ka.ka_s.latin_hypercube import LatinHypercube
from src.ka.ka_s.neighborhood_search import NeighborhoodSearch
from src.ka.ka_s.hill_climb import HillClimb
from src.ka.ka_s.genetic_algorithm import GeneticAlgorithm
from src.ka.ka_brs.level3 import KaBrLevel3
from src.ka.ka_brs.level2 import KaBrLevel2
from src.ka.ka_brs.level1 import KaBrLevel1
from src.ka.ka_brs.inter_bb import InterBB
from src.utils.problem import SFRProblem    
from src.utils.problem import BenchmarkProblem

dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}  
        
problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')  
    
def test_init():
    kas = {'ka_rp_explore': {'type': Stochastic, 'attr' : {}},
           'ka_rp_exploit': {'type': NeighborhoodSearch, 'attr' : {'perturbation_size' : 0.25}},
           'ka_br_lvl3': {'type': KaBrLevel3, 'attr' : {}},
           'ka_br_lvl2': {'type': KaBrLevel2, 'attr' : {}}}

    bb = {'name': 'bb_opt', 'type': bb_opt.BbOpt, 'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 100, 'convergence_interval': 15}}
    
    try:
        bb_controller = controller.Controller(blackboard=bb,
                                              ka=kas, 
                                              agent_wait_time=10,
                                              plot_progress=True,
                                              random_seed=1,
                                              problem=problem)

    except OSError:
        time.sleep(0.5)
        bb_controller = controller.Controller(blackboard=bb,
                                              ka=kas, 
                                              agent_wait_time=10,
                                              plot_progress=True,
                                              random_seed=1,
                                              problem=problem)
    
    assert bb_controller.bb_name == 'bb_opt'
    assert bb_controller.bb_type == bb_opt.BbOpt
    assert bb_controller.agent_wait_time == 10
    assert bb_controller.plot_progress == True
    assert bb_controller.progress_rate == 15  

    agents =  bb_controller.bb.get_attr('agent_addrs')
    bb = bb_controller.bb
    assert [x for x in agents.keys()] == ['ka_rp_explore', 'ka_rp_exploit', 'ka_br_lvl3', 'ka_br_lvl2']
    assert bb_controller.bb.get_attr('archive_name') == 'bb_opt.h5'
    assert bb.get_attr('objectives') == objs
    assert bb.get_attr('design_variables') == dvs
    assert bb.get_attr('constraints') == {}
    assert bb.get_attr('random_seed') == 1    
    ps = bb.get_attr('_proxy_server')
    ka = ps.proxy('ka_rp_exploit')
    assert ka.get_attr('perturbation_size') == 0.25
    
    bb_controller._ns.shutdown()
    time.sleep(0.05)
    
def test_run_single_agent_bb():
    kas = {'ka_rp_explore': {'type': Stochastic},
           'ka_rp_exploit': {'type': NeighborhoodSearch},
           'ka_br_lvl3': {'type': KaBrLevel3},
           'ka_br_lvl2': {'type': KaBrLevel2},
           'ka_br_lvl1': {'type': KaBrLevel1}}
    bb = {'name': 'bb_opt', 'type': bb_opt.BbOpt, 'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 100, 'convergence_interval': 15,
                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-3,
                                                           'convergence_interval':5, 'pf_size':5}}
    
    try:
        bb_controller = controller.Controller(blackboard=bb,
                                              ka=kas, 
                                              agent_wait_time=10,
                                              plot_progress=False,
                                              random_seed=10983,
                                              problem=problem)

    except OSError:
        time.sleep(0.5)
        bb_controller = controller.Controller(blackboard=bb,
                                              ka=kas, 
                                              agent_wait_time=10,
                                              plot_progress=False,
                                              random_seed=1,
                                              problem=problem)
    
    bb_controller.run_single_agent_bb()
    
    assert list(bb_controller.bb.get_blackboard()['level 1'].keys()) == ['core_[0.90351,0.72307,0.29587]', 'core_[0.85833,0.72307,0.29587]', 'core_[0.94869,0.72307,0.29587]', 'core_[0.90351,0.68692,0.29587]', 'core_[0.90351,0.75922,0.29587]', 'core_[0.81541,0.72307,0.29587]', 'core_[0.90125,0.72307,0.29587]', 'core_[0.85833,0.68692,0.29587]', 'core_[0.85833,0.75922,0.29587]', 'core_[0.94869,0.68692,0.29587]', 'core_[0.90351,0.65257,0.29587]', 'core_[0.90351,0.72127,0.29587]', 'core_[0.94869,0.75922,0.29587]', 'core_[0.90351,0.72126,0.29587]', 'core_[0.90351,0.79718,0.29587]', 'core_[0.90126,0.72307,0.29587]', 'core_[0.99612,0.72307,0.29587]', 'core_[0.90126,0.68692,0.29587]', 'core_[0.99612,0.68692,0.29587]', 'core_[0.94869,0.65257,0.29587]', 'core_[0.94869,0.72127,0.29587]']

    assert bb_controller.bb.get_hv_list() == [0.0, 0.0, 0.0, 0.0, 0.0, 0.995747042, 0.995747042, 0.995747042, 0.995747042, 0.995747042, 0.9962161123, 0.9962161123, 0.9962161123, 0.9962161123, 0.9962161123, 0.9966947564]
    

    assert bb_controller.bb.get_kaar() == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 2: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 3: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 4: {'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 5: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 6: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 7: {'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 8: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.7500069999999996}, 9: {'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 10: {'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 11: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 12: {'ka_rp_explore': 2.750011, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 13: {'ka_rp_explore': 3.0000120000000003, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 8.00000000004, 'ka_br_lvl1': 0}, 14: {'ka_rp_explore': 3.2500130000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 15: {'ka_rp_explore': 3.5000140000000006, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}}
    
    assert bb_controller.bb.get_attr('_complete') == True
    bb_controller.shutdown()
    os.remove('bb_opt.h5')
    time.sleep(0.05)

def test_run_multi_agent_bb():
    kas = {'ka_rp_explore': {'type': Stochastic},
           'ka_rp_exploit': {'type': NeighborhoodSearch},
           'ka_br_lvl3': {'type': KaBrLevel3},
           'ka_br_lvl2': {'type': KaBrLevel2},
           'ka_br_lvl1': {'type': KaBrLevel1}}
    bb = {'name': 'bb_opt', 'type': bb_opt.BbOpt, 'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 100, 'convergence_interval': 15,
                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-3,
                                                           'convergence_interval':5, 'pf_size':5}}
    
    try:
        bb_controller = controller.Controller(blackboard=bb,
                                              ka=kas, 
                                              agent_wait_time=10,
                                              plot_progress=False,
                                              random_seed=10983,
                                              problem=problem)

    except OSError:
        time.sleep(0.5)
        bb_controller = controller.Controller(blackboard=bb,
                                              ka=kas, 
                                              agent_wait_time=10,
                                              plot_progress=False,
                                              random_seed=1,
                                              problem=problem)
   
    bb_controller.run_multi_agent_bb()
    time.sleep(0.05)

    assert list(bb_controller.bb.get_blackboard()['level 1'].keys()) == ['core_[0.90351,0.72307,0.29587]', 'core_[0.85833,0.72307,0.29587]', 'core_[0.94869,0.72307,0.29587]', 'core_[0.90351,0.68692,0.29587]', 'core_[0.90351,0.75922,0.29587]', 'core_[0.81541,0.72307,0.29587]', 'core_[0.90125,0.72307,0.29587]', 'core_[0.85833,0.68692,0.29587]', 'core_[0.85833,0.75922,0.29587]', 'core_[0.94869,0.68692,0.29587]', 'core_[0.90351,0.65257,0.29587]', 'core_[0.90351,0.72127,0.29587]', 'core_[0.94869,0.75922,0.29587]', 'core_[0.90351,0.72126,0.29587]', 'core_[0.90351,0.79718,0.29587]', 'core_[0.90126,0.72307,0.29587]', 'core_[0.99612,0.72307,0.29587]', 'core_[0.90126,0.68692,0.29587]', 'core_[0.99612,0.68692,0.29587]', 'core_[0.94869,0.65257,0.29587]', 'core_[0.94869,0.72127,0.29587]']
    
    assert bb_controller.bb.get_kaar() == {1: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 2: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 3: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 4: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 5: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 6: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 7: {'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 8: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 9: {'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 10: {'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 11: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 12: {'ka_rp_explore': 2.750011, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 13: {'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 8.00000000004, 'ka_br_lvl1': 0, 'ka_rp_explore': 3.0000120000000003}, 14: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 3.2500130000000005}, 15: {'ka_rp_explore': 3.5000140000000006, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}}

    bb_controller.shutdown()    
    os.remove('bb_opt.h5')
    time.sleep(0.05)        
