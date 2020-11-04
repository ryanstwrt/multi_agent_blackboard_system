import src.controller as controller
import src.blackboard as blackboard
import src.bb_opt as bb_opt
import src.ka_rp as karp
import src.ka_br as kabr
import time
import os
import pickle

def test_controller_init():
    bb_controller = controller.Controller()
    assert bb_controller.bb_name == 'bb'
    assert bb_controller.bb_type == blackboard.Blackboard
    assert bb_controller.agent_wait_time == 30
    assert bb_controller.agent_time == 0
    assert bb_controller.progress_rate == 25
    assert bb_controller.plot_progress == False
    bb_controller._ns.shutdown()
    time.sleep(0.05)
    
def test_controller_init_sfr_opt():
    kas = {'ka_rp_explore': karp.KaGlobal, 
           'ka_rp_exploit': karp.KaLocal,
           'ka_br_lvl3': kabr.KaBr_lvl3,
           'ka_br_lvl2': kabr.KaBr_lvl2}
    obj = {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    dv = {'height':     {'ll': 60.0, 'ul': 80.0, 'variable type': float},
          'smear':      {'ll': 70.0, 'ul': 70.0, 'variable type': float},
          'pu_content': {'ll': 0.5,  'ul': 1.0,  'variable type': float}}
    const = {'eol keff':    {'ll': 1.1, 'ul': 2.5, 'variable type': float}}
    conv_model = {'type': 'dci hvi', 'convergence rate': 1E-6, 'div': {'reactivity swing': 100, 'burnup': 100}, 'interval':5, 'pf size': 5, 'total tvs': 100}
    bb_controller = controller.Controller(bb_name='sfr_opt', 
                                          bb_type=bb_opt.BbOpt, 
                                          ka=kas, 
                                          design_variables=dv,
                                          objectives=obj,
                                          constraints=const,
                                          archive='sfr_opt', 
                                          agent_wait_time=10,
                                          plot_progress = True,
                                          convergence_model = conv_model,
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'})
    with open('./sm_gpr.pkl', 'rb') as pickle_file:
        sm_gpr = pickle.load(pickle_file)
    
    assert bb_controller.bb_name == 'sfr_opt'
    assert bb_controller.bb_type == bb_opt.BbOpt
    assert bb_controller.agent_wait_time == 10
    assert bb_controller.plot_progress == True
    assert bb_controller.progress_rate == 5  

    agents =  bb_controller.bb.get_attr('agent_addrs')
    bb = bb_controller.bb
    assert [x for x in agents.keys()] == ['ka_rp_explore', 'ka_rp_exploit', 'ka_br_lvl3', 'ka_br_lvl2']
    assert bb_controller.bb.get_attr('sm_type') == 'gpr'
    assert type(bb_controller.bb.get_attr('_sm')) == type(sm_gpr)
    assert bb_controller.bb.get_attr('archive_name') == 'sfr_opt.h5'
    assert bb.get_attr('objectives') == obj
    assert bb.get_attr('design_variables') == dv
    assert bb.get_attr('constraints') == const
    assert bb.get_attr('convergence_model') == conv_model
    
    bb_controller._ns.shutdown()
    time.sleep(0.05)
    
def test_run_single_agent_bb():
    kas = {'ka_rp_explore': karp.KaGlobal, 
           'ka_rp_exploit': karp.KaLocal,
           'ka_br_lvl3': kabr.KaBr_lvl3,
           'ka_br_lvl2': kabr.KaBr_lvl2,
           'ka_br_lvl1': kabr.KaBr_lvl1,}
    objectives = {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float},
                           'pu mass':          {'ll':0,     'ul':1500, 'goal':'lt', 'variable type': float}}    
    bb_controller = controller.Controller(bb_name='sfr_opt', 
                                          bb_type=bb_opt.BbOpt, 
                                          ka=kas,
                                          objectives=objectives,
                                          archive='sfr_opt', 
                                          agent_wait_time=5,
                                          convergence_model={'type': 'hvi', 
                                                             'convergence rate': 1E-3, 
                                                             'interval':5, 
                                                             'pf size': 5, 
                                                             'total tvs': 100},
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'},
                                          random_seed=10983)
   
    bb_controller.run_single_agent_bb()
    lvls = bb_controller.bb.get_blackboard()
    
    assert [x for x in lvls['level 1']] == ['core_[73.25004, 64.46135, 0.26703]', 'core_[77.10531, 61.23828, 0.26703]', 'core_[77.10531, 67.68442, 0.26703]', 'core_[77.10531, 64.46135, 0.25368]', 'core_[69.58754, 67.68442, 0.29587]', 'core_[76.91254, 67.68442, 0.29587]', 'core_[73.25004, 67.68442, 0.28108]', 'core_[73.06691, 64.46135, 0.29587]', 'core_[76.91254, 64.46135, 0.28108]', 'core_[66.10816, 64.46135, 0.29587]', 'core_[73.06692, 64.46135, 0.29587]', 'core_[69.58754, 64.46135, 0.28108]']
        
    assert bb_controller.bb.get_hv_list() == [0.0, 0.0, 0.0, 0.0, 0.0, 0.045859852362675264, 0.045859852362675264, 0.045859852362675264, 0.045859852362675264, 0.045859852362675264, 0.055363176197322575, 0.055363176197322575, 0.055363176197322575, 0.055363176197322575, 0.055363176197322575, 0.05878471112854599, 0.05878471112854599, 0.05878471112854599, 0.05878471112854599, 0.05878471112854599, 0.05878471112854599, 0.05878471112854599, 0.05878471112854599, 0.05878471112854599, 0.05878471112854599, 0.061825241254536124]
    
    assert bb_controller.bb.get_kaar() == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_br_lvl3': 0}, 2: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 3: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 4: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 5: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 6: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 7: {'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 8: {'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 9: {'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 10: {'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 11: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 12: {'ka_rp_explore': 2.750011, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.800000000024, 'ka_br_lvl1': 0}, 13: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 3.0000120000000003}, 14: {'ka_rp_explore': 3.2500130000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 15: {'ka_rp_explore': 3.5000140000000006, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 16: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 3.7500150000000008, 'ka_rp_exploit': 5.00001}, 17: {'ka_rp_explore': 4.0000160000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl1': 0, 'ka_br_lvl2': 0}, 18: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.250017000000001}, 19: {'ka_rp_explore': 4.500018000000001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 20: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.750019000000001}, 21: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0}, 22: {'ka_rp_explore': 0.500002, 'ka_br_lvl3': 0, 'ka_br_lvl2': 9.200000000046, 'ka_br_lvl1': 0, 'ka_rp_exploit': 0}, 23: {'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001}, 24: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004}, 25: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}}
    
    assert bb_controller.bb.get_attr('_complete') == True
    bb_controller.shutdown()
    os.remove('sfr_opt.h5')
    time.sleep(0.05)

def test_multi_agent_Bb():
    kas = {'ka_rp_explore': karp.KaGlobal, 
           'ka_rp_exploit': karp.KaLocal,
           'ka_br_lvl3': kabr.KaBr_lvl3,
           'ka_br_lvl2': kabr.KaBr_lvl2,
           'ka_br_lvl1': kabr.KaBr_lvl1,}
    objectives = {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float},
                           'pu mass':          {'ll':0,     'ul':1500, 'goal':'lt', 'variable type': float}}    
    bb_controller = controller.Controller(bb_name='sfr_opt', 
                                          bb_type=bb_opt.BbOpt, 
                                          ka=kas,
                                          objectives=objectives,
                                          archive='sfr_opt', 
                                          agent_wait_time=5.0,
                                          convergence_model={'type': 'hvi', 
                                                             'convergence rate': 1E-3, 
                                                             'interval':5, 
                                                             'pf size': 5, 
                                                             'total tvs': 1000},
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'},
                                          random_seed=10983)
   
    bb_controller.run_multi_agent_bb()
    time.sleep(0.05)
        
    assert list(bb_controller.bb.get_blackboard()['level 1'].keys()) == ['core_[73.25004, 64.46135, 0.26703]', 'core_[77.10531, 61.23828, 0.26703]', 'core_[77.10531, 67.68442, 0.26703]', 'core_[77.10531, 64.46135, 0.25368]', 'core_[69.58754, 67.68442, 0.29587]', 'core_[76.91254, 67.68442, 0.29587]', 'core_[73.25004, 67.68442, 0.28108]', 'core_[73.06691, 64.46135, 0.29587]', 'core_[76.91254, 64.46135, 0.28108]', 'core_[66.10816, 64.46135, 0.29587]', 'core_[73.06692, 64.46135, 0.29587]', 'core_[69.58754, 64.46135, 0.28108]']
    
    assert bb_controller.bb.get_kaar() =={1: {'ka_rp_exploit': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 2: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 3: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 4: {'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 5: {'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 6: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 7: {'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 8: {'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 9: {'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 10: {'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 11: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 12: {'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.800000000024, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.750011}, 13: {'ka_rp_explore': 3.0000120000000003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 14: {'ka_rp_explore': 3.2500130000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 15: {'ka_rp_explore': 3.5000140000000006, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 16: {'ka_rp_explore': 3.7500150000000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 17: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.0000160000000005}, 18: {'ka_rp_explore': 4.250017000000001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 19: {'ka_rp_explore': 4.500018000000001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_br_lvl3': 3.00000000001}, 20: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.750019000000001}, 21: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0}, 22: {'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 9.200000000046, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002}, 23: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 0.750003}, 24: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004}, 25: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.2500049999999998}}

    bb_controller.shutdown()    
    os.remove('sfr_opt.h5')
    time.sleep(0.05)        
    
#------------------------------------------------
# Test of Benchmark Controller
#------------------------------------------------
    
def test_BenchmarkController():
    model = 'sf2'
    objs = {'f1': {'ll':0, 'ul':4, 'goal':'lt', 'variable type': float},
            'f2': {'ll':0, 'ul':4, 'goal':'lt', 'variable type': float}}
    dvs =  {'x1':  {'ll':-10, 'ul':10, 'variable type': float}}
    const = {}

    kas = {'ka_rp_explore': karp.KaGlobal, 
           'ka_rp_hc': karp.KaLocalHC,
           'ka_rp_pert': karp.KaLocal,
           'ka_br_lvl3': kabr.KaBr_lvl3,
           'ka_br_lvl2': kabr.KaBr_lvl2,
           'ka_br_lvl1': kabr.KaBr_lvl1}

    bb_controller = controller.BenchmarkController(bb_name=model, 
                                      bb_type=bb_opt.BenchmarkBbOpt, 
                                      ka=kas, 
                                      archive='{}_benchmark'.format(model),
                                      objectives=objs, 
                                      design_variables=dvs,
                                      benchmark=model, 
                                      convergence_model={'type': 'hvi', 'convergence rate': 1E-5, 
                                                         'interval': 5, 'pf size': 10, 'total tvs': 10},
                                      random_seed=10987)
    bb = bb_controller.bb
    ka = bb.get_attr('_proxy_server')
    ka2 = ka.proxy('ka_rp_hc')
    ka2.set_attr(step_limit=15)

    br1 = ka.proxy('ka_br_lvl1')
    br1.set_attr(total_pf_size = 100)
    br1.set_attr(pareto_sorter='dci')
    br1.set_attr(dci_div={'f1': 80, 'f2': 80})

    bb_controller.run_single_agent_bb()    
    assert bb_controller.bb.get_attr('_complete') == True
    
    assert bb_controller.bb.get_kaar() == {1: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 2: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0, 'ka_br_lvl3': 0}, 3: {'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0}, 4: {'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0}, 5: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0, 'ka_br_lvl3': 0}, 6: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0, 'ka_br_lvl3': 0}, 7: {'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 8: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 9: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_hc': 0, 'ka_rp_pert': 0}, 10: {'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_hc': 0, 'ka_rp_pert': 0}}
    
    assert bb_controller.bb.get_blackboard()['level 100']['final']['hvi'] == 0.6557478589750001
    
    bb_controller.shutdown()
    os.remove('sf2_benchmark.h5')
    time.sleep(0.05)
    
#------------------------------------------------
# Test of Multi_Tiered_Controller
#------------------------------------------------

def test_MTC_init():
    mtc = controller.Multi_Tiered_Controller()
    assert mtc.master_bb == None
    assert mtc.sub_bb == None
    assert mtc._ns != None
    assert mtc._proxy_server != None
    mtc.shutdown()
    time.sleep(0.05)    
    
def test_MTC_initialize_bb():    
    mtc = controller.Multi_Tiered_Controller()
    kas = {'mka_rp_hc': karp.KaLocalHC,
           'mka_rp_pert': karp.KaLocal,
           'mka_rp_ga': karp.KaLocalGA,
           'mka_br_lvl3': kabr.KaBr_lvl3,
           'mka_br_lvl2': kabr.KaBr_lvl2,
           'mka_br_lvl1': kabr.KaBr_lvl1}
    
    mtc.initialize_blackboard('master_bb', bb_name='bb_master', bb_type=bb_opt.MasterBbOpt, ka=kas, archive='bb_master')
    
    master_bb = mtc.master_bb
    assert master_bb.get_attr('name') == 'bb_master'
    assert master_bb.get_attr('archive_name') == 'bb_master.h5'
    assert master_bb.get_attr('convergence_model') == {'type': 'hvi', 'convergence rate': 1E-5, 'interval': 25, 'pf size': 200, 'total tvs': 1000000.0}
    assert master_bb.get_attr('sm_type') == 'gpr'
    assert master_bb.get_attr('objectives') == {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'goal':'gt', 'variable type': float},
                                                'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
    assert master_bb.get_attr('design_variables') == {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    assert master_bb.get_attr('constraints') == {
                            'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                            'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    
    kas = {'ska_rp_mc': karp.KaGlobal, 
           'ska_rp_hc': karp.KaLocalHC,
           'ska_rp_lhc': karp.KaLHC,
           'ska_rp_pert': karp.KaLocal,
           'ska_rp_ga': karp.KaLocalGA,
           'ska_br_lvl3': kabr.KaBr_lvl3,
           'ska_br_lvl2': kabr.KaBr_lvl2,
           'ska_br_lvl1': kabr.KaBr_lvl1,
           'ska_br_inter': kabr.KaBr_interBB}
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', bb_type=bb_opt.SubBbOpt, ka=kas,  archive='bb_sub')
    
    sub_bb = mtc.sub_bb
    assert sub_bb.get_attr('name') == 'bb_sub'
    assert sub_bb.get_attr('archive_name') == 'bb_sub.h5'
    assert sub_bb.get_attr('convergence_model') == {'type': 'hvi', 'convergence rate': 1E-5, 'interval': 25, 'pf size': 200, 'total tvs': 1000000.0}
    assert sub_bb.get_attr('sm_type') == 'gpr'
    assert sub_bb.get_attr('objectives') == {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float},}
    assert sub_bb.get_attr('design_variables') == {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    assert sub_bb.get_attr('constraints') == {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'variable type': float},
                            'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
    assert mtc.bb_attr == {'bb_master': {'plot': False, 'name': 'bb_master', 'wait time': 30},
                          'bb_sub': {'plot': False, 'name': 'bb_sub', 'wait time': 30}}
    mtc.shutdown()
    time.sleep(0.05)
    
def test_MTC_run_sub_bb():    
    mtc = controller.Multi_Tiered_Controller()
    kas = {'mka_rp_hc': karp.KaLocalHC,
           'mka_rp_pert': karp.KaLocal,
           'mka_rp_ga': karp.KaLocalGA,
           'mka_br_lvl3': kabr.KaBr_lvl3,
           'mka_br_lvl2': kabr.KaBr_lvl2,
           'mka_br_lvl1': kabr.KaBr_lvl1}
    
    mtc.initialize_blackboard('master_bb', bb_name='bb_master', bb_type=bb_opt.MasterBbOpt, ka=kas, archive='bb_master', random_seed=1)
    
    master_bb = mtc.master_bb
    kas = {'ska_rp_mc': karp.KaGlobal, 
           'ska_rp_hc': karp.KaLocalHC,
           'ska_rp_pert': karp.KaLocal,
           'ska_br_lvl3': kabr.KaBr_lvl3,
           'ska_br_lvl2': kabr.KaBr_lvl2,
           'ska_br_lvl1': kabr.KaBr_lvl1,
           'ska_br_inter': kabr.KaBr_interBB}
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', bb_type=bb_opt.SubBbOpt, ka=kas,  archive='bb_sub', convergence_model={'type': 'hvi', 'convergence rate': 0.04, 'interval': 5, 'pf size': 5, 'total tvs': 50}, random_seed=1)
    
    sub_bb = mtc.sub_bb
    
    mtc.run_sub_bb(sub_bb)
    
    assert list(sub_bb.get_blackboard()['level 1']) == ['core_[70.11403, 61.2634, 0.53076]', 'core_[70.11403, 64.32657, 0.53076]', 'core_[66.60833, 61.11024, 0.53076]', 'core_[63.27791, 63.84532, 0.50422]', 'core_[66.44181, 63.84532, 0.47901]', 'core_[66.27571, 60.65305, 0.45506]', 'core_[66.27571, 63.6857, 0.45506]', 'core_[66.27571, 66.86998, 0.45506]', 'core_[73.06897, 66.7028, 0.41069]', 'core_[73.06897, 63.36766, 0.41069]', 'core_[69.41552, 63.36766, 0.41069]', 'core_[69.41552, 60.19928, 0.39016]']
    
    assert sub_bb.get_blackboard()['level 100']['final']['hvi'] == 0.06706342806620001
    
    assert sub_bb.get_kaar() == {1: {'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0}, 2: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0}, 3: {'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0}, 4: {'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0}, 5: {'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0}, 6: {'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0}, 7: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 3.00000000001}, 8: {'ska_br_lvl3': 0, 'ska_br_lvl2': 4.00000000002, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.500002, 'ska_rp_hc': 0, 'ska_rp_pert': 0}, 9: {'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 6.00000000001, 'ska_rp_mc': 0.750003, 'ska_rp_hc': 5.00001}, 10: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.000004, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0}, 11: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.2500049999999998, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 0, 'ska_br_lvl3': 3.00000000001}, 12: {'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.5000059999999997, 'ska_br_lvl3': 7.0800000000236, 'ska_br_lvl2': 0}, 13: {'ska_rp_mc': 1.7500069999999996, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 13.200000000066, 'ska_br_lvl1': 0, 'ska_br_inter': 0}, 14: {'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 6.00000000003, 'ska_br_inter': 6.00000000001, 'ska_rp_mc': 2.000008, 'ska_rp_hc': 5.00001}, 15: {'ska_rp_mc': 2.250009, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 6.00000000001}}
    
    assert list(master_bb.get_blackboard()['level 3']['new'].keys()) == ['core_[70.11403, 58.3461, 0.55869]', 'core_[70.11403, 61.2634, 0.53076]', 'core_[70.11403, 64.32657, 0.53076]', 'core_[66.60833, 61.11024, 0.53076]', 'core_[63.27791, 63.84532, 0.50422]', 'core_[66.44181, 63.84532, 0.47901]', 'core_[66.27571, 60.65305, 0.45506]', 'core_[66.27571, 63.6857, 0.45506]', 'core_[66.27571, 66.86998, 0.45506]', 'core_[73.06897, 66.7028, 0.41069]', 'core_[73.06897, 63.36766, 0.41069]', 'core_[69.41552, 63.36766, 0.41069]', 'core_[69.41552, 60.19928, 0.39016]']
    
    os.remove('bb_sub.h5')
        
    mtc.shutdown()
    time.sleep(0.05)    

def test_MTC_run_master_bb():    
    mtc = controller.Multi_Tiered_Controller()
    kas = {'mka_rp_mc': karp.KaGlobal,
           'mka_rp_hc': karp.KaLocalHC,
           'mka_rp_pert': karp.KaLocal,
           'mka_br_lvl3': kabr.KaBr_lvl3,
           'mka_br_lvl2': kabr.KaBr_lvl2,
           'mka_br_lvl1': kabr.KaBr_lvl1}
    
    mtc.initialize_blackboard('master_bb', bb_name='bb_master', bb_type=bb_opt.MasterBbOpt, ka=kas, archive='bb_master', convergence_model={'type': 'hvi', 'convergence rate': 0.5, 'interval': 5, 'pf size': 5, 'total tvs': 50}, random_seed=1)
    
    master_bb = mtc.master_bb
    kas = {'ska_rp_mc': karp.KaGlobal, 
           'ska_rp_hc': karp.KaLocalHC,
           'ska_rp_pert': karp.KaLocal,
           'ska_br_lvl3': kabr.KaBr_lvl3,
           'ska_br_lvl2': kabr.KaBr_lvl2,
           'ska_br_lvl1': kabr.KaBr_lvl1,
           'ska_br_inter': kabr.KaBr_interBB}
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', bb_type=bb_opt.SubBbOpt, ka=kas,  archive='bb_sub', convergence_model={'type': 'hvi', 'convergence rate': 0.04, 'interval': 5, 'pf size': 5, 'total tvs': 50}, random_seed=1)
    
    sub_bb = mtc.sub_bb
    
    
    mtc.run_sub_bb(sub_bb)
    
    assert list(master_bb.get_blackboard()['level 3']['new'].keys()) == ['core_[70.11403, 58.3461, 0.55869]', 'core_[70.11403, 61.2634, 0.53076]', 'core_[70.11403, 64.32657, 0.53076]', 'core_[66.60833, 61.11024, 0.53076]', 'core_[63.27791, 63.84532, 0.50422]', 'core_[66.44181, 63.84532, 0.47901]', 'core_[66.27571, 60.65305, 0.45506]', 'core_[66.27571, 63.6857, 0.45506]', 'core_[66.27571, 66.86998, 0.45506]', 'core_[73.06897, 66.7028, 0.41069]', 'core_[73.06897, 63.36766, 0.41069]', 'core_[69.41552, 63.36766, 0.41069]', 'core_[69.41552, 60.19928, 0.39016]']
    
    mtc.run_sub_bb(master_bb)

    assert master_bb.get_blackboard()['level 1'] == {'core_[73.06897, 66.7028, 0.41069]': {'pareto type': 'pareto', 'fitness function': 0.72724}, 'core_[76.72242, 66.7028, 0.41069]': {'pareto type': 'weak', 'fitness function': 0.7195}, 'core_[69.45206, 69.45471, 0.3894]': {'pareto type': 'weak', 'fitness function': 0.74729}, 'core_[66.01418, 69.45471, 0.3894]': {'pareto type': 'weak', 'fitness function': 0.75286}, 'core_[66.01418, 66.0167, 0.3894]': {'pareto type': 'weak', 'fitness function': 0.75248}, 'core_[66.01418, 66.0167, 0.37012]': {'pareto type': 'pareto', 'fitness function': 0.76418}, 'core_[65.85243, 62.74887, 0.3518]': {'pareto type': 'pareto', 'fitness function': 0.76983}, 'core_[65.85243, 65.85494, 0.36921]': {'pareto type': 'pareto', 'fitness function': 0.76478}, 'core_[65.85243, 65.69358, 0.36921]': {'pareto type': 'pareto', 'fitness function': 0.76466}, 'core_[62.59273, 65.69358, 0.36921]': {'pareto type': 'pareto', 'fitness function': 0.76733}, 'core_[62.59273, 62.44175, 0.36921]': {'pareto type': 'weak', 'fitness function': 0.76111}, 'core_[62.59273, 65.53262, 0.38749]': {'pareto type': 'pareto', 'fitness function': 0.75672}}
       
    assert master_bb.get_kaar() == {1: {'mka_rp_mc': 0.250001, 'mka_rp_hc': 0, 'mka_rp_pert': 0, 'mka_br_lvl1': 0, 'mka_br_lvl3': 3.00000000001, 'mka_br_lvl2': 0}, 2: {'mka_rp_mc': 0.500002, 'mka_rp_hc': 0, 'mka_rp_pert': 0, 'mka_br_lvl3': 0, 'mka_br_lvl2': 5.200000000026, 'mka_br_lvl1': 0}, 3: {'mka_rp_mc': 0.750003, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl2': 0, 'mka_br_lvl1': 6.00000000003}, 4: {'mka_br_lvl2': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 1.000004, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0}, 5: {'mka_br_lvl3': 3.00000000001, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 1.2500049999999998, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001}, 6: {'mka_br_lvl1': 0, 'mka_rp_mc': 1.5000059999999997, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 3.00000000001, 'mka_br_lvl2': 0}, 7: {'mka_rp_mc': 1.7500069999999996, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 13.0800000000436, 'mka_br_lvl1': 0, 'mka_br_lvl2': 0}, 8: {'mka_br_lvl3': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 2.000008, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl2': 14.00000000007}, 9: {'mka_rp_mc': 2.250009, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl2': 0, 'mka_br_lvl1': 6.00000000003}, 10: {'mka_rp_pert': 5.00001, 'mka_rp_mc': 2.50001, 'mka_rp_hc': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0}}
    os.remove('bb_sub.h5')
    os.remove('bb_master.h5')
    
    mtc.shutdown()
    time.sleep(0.05) 

