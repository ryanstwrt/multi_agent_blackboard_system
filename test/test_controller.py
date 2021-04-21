import src.controller as controller
import src.bb.blackboard as blackboard
import src.bb.blackboard_optimization as bb_opt
from osbrain import run_agent
from osbrain import run_nameserver    
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
        bb_controller = controller.Controller()
        bb_controller.initialize_blackboard(blackboard=bb,
                                  ka=kas, 
                                  agent_wait_time=10,
                                  plot_progress=False,
                                  random_seed=10983,
                                  problem=problem) 

    except OSError:
        time.sleep(0.5)
        bb_controller = controller.Controller()
        bb_controller.initialize_blackboard(blackboard=bb,
                                  ka=kas, 
                                  agent_wait_time=10,
                                  plot_progress=False,
                                  random_seed=10983,
                                  problem=problem) 
    
    assert bb_controller.bb_attr == {'bb_opt': {'plot': False, 'name': 'bb_opt', 'agent_wait_time': 10, 'progress_rate': 15, 'complete': False}}

    bb = bb_controller.bb_opt
    agents =  bb.get_attr('agent_addrs')
    assert [x for x in agents.keys()] == ['ka_rp_explore', 'ka_rp_exploit', 'ka_br_lvl3', 'ka_br_lvl2']
    assert bb.get_attr('archive_name') == 'bb_opt.h5'
    assert bb.get_attr('objectives') == objs
    assert bb.get_attr('design_variables') == dvs
    assert bb.get_attr('constraints') == {}
    assert bb.get_attr('random_seed') == 10983    
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
        bb_controller = controller.Controller()
        bb_controller.initialize_blackboard(blackboard=bb,
                                  ka=kas, 
                                  agent_wait_time=10,
                                  plot_progress=False,
                                  random_seed=10983,
                                  problem=problem) 

    except OSError:
        time.sleep(0.5)
        bb_controller = controller.Controller()
        bb_controller.initialize_blackboard(blackboard=bb,
                                  ka=kas, 
                                  agent_wait_time=10,
                                  plot_progress=False,
                                  random_seed=10983,
                                  problem=problem) 
    
    bb_controller.run_single_agent_bb('bb_opt') 
    
    bb = bb_controller.bb_opt    
    assert list(bb.get_blackboard()['level 1'].keys()) == ['core_[0.90351,0.72307,0.29587]', 'core_[0.85833,0.72307,0.29587]', 'core_[0.94869,0.72307,0.29587]', 'core_[0.90351,0.68692,0.29587]', 'core_[0.90351,0.75922,0.29587]', 'core_[0.81541,0.72307,0.29587]', 'core_[0.90125,0.72307,0.29587]', 'core_[0.85833,0.68692,0.29587]', 'core_[0.85833,0.75922,0.29587]', 'core_[0.94869,0.68692,0.29587]', 'core_[0.90351,0.65257,0.29587]', 'core_[0.90351,0.72127,0.29587]', 'core_[0.94869,0.75922,0.29587]', 'core_[0.90351,0.72126,0.29587]', 'core_[0.90351,0.79718,0.29587]', 'core_[0.90126,0.72307,0.29587]', 'core_[0.99612,0.72307,0.29587]']

    assert bb.get_kaar() == {1: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 2: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 3: {'ka_br_lvl3': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl2': 4.00000000002}, 4: {'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 5: {'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 5.00001}, 6: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 7: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 8: {'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 9: {'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001}, 10: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 11: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 12: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.750011, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 13: {'ka_br_lvl1': 0, 'ka_rp_explore': 3.0000120000000003, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 14: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 15: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 8.400000000042, 'ka_br_lvl1': 0}}
    
    assert bb.get_attr('_complete') == True
   
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
        bb_controller = controller.Controller()
        bb_controller.initialize_blackboard(blackboard=bb,
                                  ka=kas, 
                                  agent_wait_time=10,
                                  plot_progress=False,
                                  random_seed=10983,
                                  problem=problem) 

    except OSError:
        time.sleep(0.5)        
        bb_controller = controller.Controller()
        bb_controller.initialize_blackboard(blackboard=bb,
                                  ka=kas, 
                                  agent_wait_time=10,
                                  plot_progress=False,
                                  random_seed=10983,
                                  problem=problem) 
   
    bb_controller.run_multi_agent_bb('bb_opt')
    time.sleep(0.05)

    bb = bb_controller.bb_opt
    assert list(bb.get_blackboard()['level 1'].keys()) == ['core_[0.90351,0.72307,0.29587]', 'core_[0.85833,0.72307,0.29587]', 'core_[0.94869,0.72307,0.29587]', 'core_[0.90351,0.68692,0.29587]', 'core_[0.90351,0.75922,0.29587]', 'core_[0.81541,0.72307,0.29587]', 'core_[0.90125,0.72307,0.29587]', 'core_[0.85833,0.68692,0.29587]', 'core_[0.85833,0.75922,0.29587]', 'core_[0.94869,0.68692,0.29587]', 'core_[0.90351,0.65257,0.29587]', 'core_[0.90351,0.72127,0.29587]', 'core_[0.94869,0.75922,0.29587]', 'core_[0.90351,0.72126,0.29587]', 'core_[0.90351,0.79718,0.29587]', 'core_[0.90126,0.72307,0.29587]', 'core_[0.99612,0.72307,0.29587]']
    
    assert bb.get_kaar() == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 2: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 3: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 4: {'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 5: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 6: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 7: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 8: {'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 9: {'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 10: {'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 11: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 12: {'ka_rp_explore': 2.750011, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 13: {'ka_rp_explore': 3.0000120000000003, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 14: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001}, 15: {'ka_br_lvl3': 0, 'ka_br_lvl2': 8.400000000042, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0}}
    
    bb_controller.shutdown()    
    os.remove('bb_opt.h5')
    time.sleep(0.05)        

def test_multi_tiered_init():
    kas_tier_1 = {'ka_rp_t1': {'type': Stochastic},
           'ka_rp_ns_t1': {'type': NeighborhoodSearch},
           'ka_br_lvl3t1': {'type': KaBrLevel3},
           'ka_br_lvl2t1': {'type': KaBrLevel2},
           'ka_br_lvl1t1': {'type': KaBrLevel1}}

    bb_tier1 = {'name': 'bb_opt_1', 'type': bb_opt.BbOpt, 'tier': 1, 'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 100, 'convergence_interval': 15,
                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-3,
                                                           'convergence_interval':5, 'pf_size':5}}

    
    kas_tier_2 = {'ka_rp_exploret2': {'type': Stochastic},
           'ka_rp_exploitt2': {'type': NeighborhoodSearch},
           'ka_br_inter':  {'type': InterBB, 'attr':{'bb': 'bb_opt_1'}},
           'ka_br_lvl3t2': {'type': KaBrLevel3},
           'ka_br_lvl2t2': {'type': KaBrLevel2},
           'ka_br_lvl1t2': {'type': KaBrLevel1}}            
    bb_tier2 = {'name': 'bb_opt_2', 'type': bb_opt.BbOpt, 'tier': 2,  'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 100, 'convergence_interval': 15,
                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-3,
                                                           'convergence_interval':5, 'pf_size':5}} 
    
    try:
        mtc = controller.Controller()
    except OSError:
        time.sleep(0.5)
        mtc = controller.Controller()        
        
    mtc.initialize_blackboard(blackboard=bb_tier1,
                                  ka=kas_tier_1, 
                                  agent_wait_time=10,
                                  plot_progress=False,
                                  random_seed=1,
                                  problem=problem)
    bb1 = mtc.bb_opt_1
    assert list(bb1.get_attr('agent_addrs').keys()) == list(kas_tier_1.keys())
              
    mtc.initialize_blackboard(blackboard=bb_tier2,
                                  ka=kas_tier_2, 
                                  agent_wait_time=10,
                                  plot_progress=False,
                                  random_seed=1,
                                  problem=problem)  
    bb2 = mtc.bb_opt_2
    assert list(bb2.get_attr('agent_addrs').keys()) == list(kas_tier_2.keys())
    kas_tier_1_list = list(kas_tier_1.keys())
    kas_tier_1_list.append('ka_br_inter')
    assert list(bb1.get_attr('agent_addrs').keys()) == kas_tier_1_list
    
    mtc.shutdown()    
    time.sleep(0.05)         
    
#def test_multi_tiered_run():
#    kas_tier_1 = {'ka_rp_t1': {'type': Stochastic},
#           'ka_rp_ns_t1': {'type': NeighborhoodSearch},
#           'ka_br_lvl3t1': {'type': KaBrLevel3},
#           'ka_br_lvl2t1': {'type': KaBrLevel2},
#           'ka_br_lvl1t1': {'type': KaBrLevel1}}
#
#    bb_tier1 = {'name': 'bb_opt_1', 'type': bb_opt.BbOpt, 'tier': 1, 'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 4, 'convergence_interval': 2,
#                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-2,
#                                                           'pf_size':1}}
#
#    
#    kas_tier_2 = {'ka_rp_exploret2': {'type': Stochastic},
#           'ka_rp_exploitt2': {'type': NeighborhoodSearch},
#           'ka_br_inter':  {'type': InterBB, 'attr':{'bb': 'bb_opt_1'}},
#           'ka_br_lvl3t2': {'type': KaBrLevel3},
#           'ka_br_lvl2t2': {'type': KaBrLevel2},
#           'ka_br_lvl1t2': {'type': KaBrLevel1}}            
#    bb_tier2 = {'name': 'bb_opt_2', 'type': bb_opt.BbOpt, 'tier': 2,  'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 4, 'convergence_interval': 2,
#                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-2,
#                                                           'pf_size':1}} 
#    
#    kas_tier_3 = {'ka_rp_exploret3': {'type': Stochastic},
#           'ka_rp_exploitt3': {'type': NeighborhoodSearch},
#           'ka_br_inter3':  {'type': InterBB, 'attr':{'bb': 'bb_opt_2'}},
#           'ka_br_inter32':  {'type': InterBB, 'attr':{'bb': 'bb_opt_1'}},
#           'ka_br_lvl3t3': {'type': KaBrLevel3},
#           'ka_br_lvl2t3': {'type': KaBrLevel2},
#           'ka_br_lvl1t3': {'type': KaBrLevel1}}      
#    bb_tier3 = {'name': 'bb_opt_3', 'type': bb_opt.BbOpt, 'tier': 3,  'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 4, 'convergence_interval': 2,
#                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-2,
#                                                           'pf_size':1}}     
#    
#    mtc = controller.Controller()
#        
#    mtc.initialize_blackboard(blackboard=bb_tier1,
#                                  ka=kas_tier_1, 
#                                  agent_wait_time=10,
#                                  plot_progress=False,
#                                  random_seed=1097,
#                                  problem=problem)             
#    mtc.initialize_blackboard(blackboard=bb_tier2,
#                                  ka=kas_tier_2, 
#                                  agent_wait_time=10,
#                                  plot_progress=False,
#                                  random_seed=2097337,
#                                  problem=problem)  
#    mtc.initialize_blackboard(blackboard=bb_tier3,
#                                  ka=kas_tier_3, 
#                                  agent_wait_time=10,
#                                  plot_progress=False,
#                                  random_seed=3093373,
#                                  problem=problem)  
#
#    mtc.run_multi_agent_bb('bb_opt_3')    
#    mtc.run_multi_agent_bb('bb_opt_2')
#    mtc.run_multi_agent_bb('bb_opt_1')
#    
#    bb3 = mtc.bb_opt_3
#    assert list(bb3.get_blackboard()['level 1']) == ['core_[0.99131,0.71506,0.43058]']
#
#    bb2 = mtc.bb_opt_2
#    assert list(bb2.get_blackboard()['level 1']) == ['core_[0.75342,0.31156,0.6875]']
#    
#    bb1 = mtc.bb_opt_1
#    assert list(bb1.get_blackboard()['level 1']) == ['core_[0.99131,0.71506,0.43058]', 'core_[0.75342,0.31156,0.6875]', 'core_[0.71575,0.31156,0.6875]', 'core_[0.79109,0.31156,0.6875]', 'core_[0.75342,0.29598,0.6875]', 'core_[0.75342,0.32714,0.6875]']
#    
#    mtc.shutdown()    
#    os.remove('bb_opt.h5')    
#    time.sleep(0.05)     
    
def test_ControllerAgent_init():  
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ca = run_agent(name='ca', base=controller.ControllerAgent)  
    
    assert ca.get_attr('bb_attr') == {}
    assert ca.get_attr('_run_bb_alias') == None
    assert ca.get_attr('_run_bb_addr') == None
    ns.shutdown()
    time.sleep(0.05)          
    
#def test_serial_multi_tiered_run():
#    kas_tier_1 = {'ka_rp_t1': {'type': Stochastic},
#           'ka_rp_ns_t1': {'type': NeighborhoodSearch},
#           'ka_br_lvl3t1': {'type': KaBrLevel3},
#           'ka_br_lvl2t1': {'type': KaBrLevel2},
#           'ka_br_lvl1t1': {'type': KaBrLevel1}}
#
#    bb_tier1 = {'name': 'bb_opt_1', 'type': bb_opt.BbOpt, 'tier': 1, 'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 8, 'convergence_interval': 2,
#                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-2,
#                                                           'pf_size':1}}
#    
#    kas_tier_2 = {'ka_rp_exploret2': {'type': Stochastic},
#           'ka_rp_exploitt2': {'type': NeighborhoodSearch},
#           'ka_br_inter':  {'type': InterBB, 'attr':{'bb': 'bb_opt_1'}},
#           'ka_br_lvl3t2': {'type': KaBrLevel3},
#           'ka_br_lvl2t2': {'type': KaBrLevel2},
#           'ka_br_lvl1t2': {'type': KaBrLevel1}}            
#    bb_tier2 = {'name': 'bb_opt_2', 'type': bb_opt.BbOpt, 'tier': 2,  'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 8, 'convergence_interval': 2,
#                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-2,
#                                                           'pf_size':1}} 
#    try:
#        mtc = controller.Controller()
#    except OSError:
#        time.sleep(0.5)
#        mtc = controller.Controller()      
#        
#    mtc.initialize_blackboard(blackboard=bb_tier1,
#                                  ka=kas_tier_1, 
#                                  agent_wait_time=10,
#                                  plot_progress=False,
#                                  random_seed=1097,
#                                  problem=problem,)             
#    mtc.initialize_blackboard(blackboard=bb_tier2,
#                                  ka=kas_tier_2, 
#                                  agent_wait_time=10,
#                                  plot_progress=False,
#                                  random_seed=2097337,
#                                  problem=problem)   
#
#    mtc.run_multi_tiered()
#    bb2 = mtc.bb_opt_2
#    bb1 = mtc.bb_opt_1
#    
#    assert set(list(bb2.get_blackboard()['level 1'].keys())).issubset(list(bb1.get_blackboard()['level 3']['old'].keys())) == True
#    assert list(bb2.get_blackboard()['level 1']) == ['core_[0.75342,0.31156,0.6875]', 'core_[0.71575,0.31156,0.6875]', 'core_[0.79109,0.31156,0.6875]', 'core_[0.75342,0.29598,0.6875]', 'core_[0.75342,0.32714,0.6875]']
#    assert list(bb1.get_blackboard()['level 1']) == ['core_[0.75342,0.31156,0.6875]', 'core_[0.71575,0.31156,0.6875]', 'core_[0.79109,0.31156,0.6875]', 'core_[0.75342,0.29598,0.6875]', 'core_[0.75342,0.32714,0.6875]']
#    
#    mtc.shutdown()    
#    os.remove('bb_opt.h5')    
#    time.sleep(0.05)   
    
def test_controlleragent_init_master():

    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ca = run_agent(name='ca', base=controller.ControllerAgent)  
    mca = run_agent(name='mca', base=controller.MasterControllerAgent)  
    
    assert ca.get_attr('_run_bb_alias') == None
    assert ca.get_attr('_run_bb_addr') == None
    assert mca.get_attr('bb_addrs') == {}
    assert ca.get_attr('controller_agent_attr') == {}
    
    ca.set_attr(master_ca=mca)
    ca.connect_run_bb()
    assert ca.get_attr('_run_bb_alias') == 'run_bb_ca'
    assert list(mca.get_attr('bb_addrs').keys()) == ['ca']
    
    ns.shutdown()
    time.sleep(0.05)      
    
def test_controlleragent_handler_run_bb():
   
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ca = run_agent(name='ca', base=controller.ControllerAgent)  
    mca = run_agent(name='mca', base=controller.MasterControllerAgent)   
    ca.set_attr(master_ca=mca)
    ca.connect_run_bb()
    kas_tier_1 = {'ka_rp_t1': {'type': Stochastic},
           'ka_rp_ns_t1': {'type': NeighborhoodSearch},
           'ka_br_lvl3t1': {'type': KaBrLevel3},
           'ka_br_lvl2t1': {'type': KaBrLevel2},
           'ka_br_lvl1t1': {'type': KaBrLevel1}}

    bb_tier1 = {'name': 'bb_opt_1', 'type': bb_opt.BbOpt, 'tier': 1, 'attr': {'archive_name': 'bb_opt.h5', 'total_tvs': 8, 'convergence_interval': 2,
                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-2,
                                                           'pf_size':1}}    
    ca.initialize_blackboard(blackboard=bb_tier1,
                             ka=kas_tier_1, 
                             agent_wait_time=10,
                             plot_progress=False,
                             random_seed=1097,
                             problem=problem)      
    ca.set_attr(bb_name='bb_opt_1')
    bb_attr = ca.get_attr('bb_attr')
    ca.handler_run_bb(bb_attr)
    
    ns.shutdown()
    time.sleep(0.05)          
    
#def test_multi_tiered_run():
#    kas_tier_1 = {'mc_t1': {'type': Stochastic},
#           'ns_t1': {'type': NeighborhoodSearch},
#           'lvl3_t1': {'type': KaBrLevel3},
#           'lvl2_t1': {'type': KaBrLevel2},
#           'lvl1_t1': {'type': KaBrLevel1}}
#
#    bb_tier1 = {'name': 'bb_opt_1', 'type': bb_opt.BbOpt, 'tier': 1, 'attr': {'archive_name': 'bb_opt_1.h5', 'total_tvs': 8, 'convergence_interval': 2,
#                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-2,
#                                                           'pf_size':1}}
#    
#    kas_tier_2 = {'mc_t2': {'type': Stochastic},
#           'ns_t2': {'type': NeighborhoodSearch},
#           'inter':  {'type': InterBB, 'attr':{'bb': 'bb_opt_1'}},
#           'lvl3_t2': {'type': KaBrLevel3},
#           'lvl2_t2': {'type': KaBrLevel2},
#           'lvl1_t2': {'type': KaBrLevel1}}            
#    bb_tier2 = {'name': 'bb_opt_2', 'type': bb_opt.BbOpt, 'tier': 2,  'attr': {'archive_name': 'bb_opt_2.h5', 'total_tvs': 8, 'convergence_interval': 2,
#                                                           'skipped_tvs': 0, 'convergence_type': 'hvi', 'convergence_rate':1E-2,
#                                                           'pf_size':1}} 
#    try:
#        ns = run_nameserver()
#    except OSError:
#        time.sleep(0.5)
#        ns = run_nameserver()
#    mtc = run_agent(name='mca', base=controller.MasterControllerAgent)       
#        
#    mtc.initialize_blackboard(blackboard=bb_tier1,
#                                  ka=kas_tier_1, 
#                                  agent_wait_time=10,
#                                  plot_progress=False,
#                                  random_seed=1097,
#                                  problem=problem)             
#    mtc.initialize_blackboard(blackboard=bb_tier2,
#                                  ka=kas_tier_2, 
#                                  agent_wait_time=10,
#                                  plot_progress=False,
#                                  random_seed=2097337,
#                                  problem=problem)   
#
#    mtc.run_multi_tiered()
#    complete = False
#    time.sleep(5)
#    while not complete:
#        mtc.check_multi_tiered()
#        complete = False if False in [x['complete'] for x in mtc.get_attr('bb_attr').values()] else True
#
#    ca_attr = mtc.get_attr('controller_agent_attr')
#    bb2 = getattr(ca_attr['ca_bb_opt_2']['controller agent'], ca_attr['ca_bb_opt_2']['blackboard'])
#    bb1 = getattr(ca_attr['ca_bb_opt_1']['controller agent'], ca_attr['ca_bb_opt_1']['blackboard']) 
#    
#    assert sorted(list(bb2.get_blackboard()['level 1'])) == sorted(['core_[0.75342,0.31156,0.6875]', 'core_[0.71575,0.31156,0.6875]', 'core_[0.79109,0.31156,0.6875]', 'core_[0.75342,0.29598,0.6875]', 'core_[0.75342,0.32714,0.6875]'])
#    assert sorted(list(bb1.get_blackboard()['level 1'])) == sorted(['core_[0.75342,0.31156,0.6875]', 'core_[0.98618,0.88344,0.20599]', 'core_[0.93922,0.88344,0.19569]', 'core_[0.93922,0.92761,0.20599]'])    
#                  
#    mtc.shutdown()    
#    os.remove('bb_opt_1.h5')    
#    os.remove('bb_opt_2.h5')    
#    ns.shutdown()    
#    time.sleep(0.05)