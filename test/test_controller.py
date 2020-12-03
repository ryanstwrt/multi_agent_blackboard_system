import src.controller as controller
import src.blackboard as blackboard
import src.bb_opt as bb_opt
import src.ka_rp as karp
import src.ka_br as kabr
import time
import os
import pickle

def test_controller_init():
    try:
        bb_controller = controller.Controller()
    except OSError:
        time.sleep(0.5)
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
    conv_model = {'type': 'dci hvi', 'convergence rate': 1E-6, 'div': {'reactivity swing': 100, 'burnup': 100}, 
                  'skipped tvs': 0, 'interval':5, 'pf size': 5, 'total tvs': 100}
    try:
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
    except OSError:
        time.sleep(0.5)
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
    try:
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
                                                             'total tvs': 100,
                                                             'skipped tvs': 0},
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'},
                                          random_seed=10983)
    except:
        time.sleep(0.5)
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
                                                             'total tvs': 100,
                                                             'skipped tvs': 0},
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'},
                                          random_seed=10983)
   
    bb_controller.run_single_agent_bb()
    lvls = bb_controller.bb.get_blackboard()
        
    assert [x for x in lvls['level 1']] == ['core_[73.25004,64.46135,0.26703]', 'core_[77.10531,61.23828,0.26703]', 'core_[77.10531,67.68442,0.26703]', 'core_[77.10531,64.46135,0.25368]', 'core_[73.25004,67.68442,0.28108]', 'core_[69.58754,64.46135,0.28108]', 'core_[76.91254,64.46135,0.28108]', 'core_[73.06691,64.46135,0.29587]', 'core_[76.91254,67.68442,0.29587]', 'core_[69.58754,67.68442,0.29587]', 'core_[66.10816,64.46135,0.29587]', 'core_[73.06692,64.46135,0.29587]']

    assert bb_controller.bb.get_hv_list() == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0458598596, 0.0458598596, 0.0458598596, 0.0458598596, 0.0458598596, 0.0553631786, 0.0553631786, 0.0553631786, 0.0553631786, 0.0553631786, 0.0587847208, 0.0587847208, 0.0587847208, 0.0587847208, 0.0587847208, 0.0587847208, 0.0587847208, 0.0587847208, 0.0587847208, 0.0587847208, 0.0618252533]

    assert bb_controller.bb.get_kaar() == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_br_lvl3': 0}, 2: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 3: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 4: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 5: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 6: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 7: {'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 8: {'ka_br_lvl3': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl2': 0}, 9: {'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 10: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 11: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 12: {'ka_rp_explore': 2.750011, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.800000000024, 'ka_br_lvl1': 0}, 13: {'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 3.0000120000000003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 14: {'ka_rp_explore': 3.2500130000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 15: {'ka_rp_explore': 3.5000140000000006, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 16: {'ka_rp_explore': 3.7500150000000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 17: {'ka_rp_explore': 4.0000160000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 18: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.250017000000001, 'ka_br_lvl2': 0}, 19: {'ka_rp_explore': 4.500018000000001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 20: {'ka_rp_explore': 4.750019000000001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_exploit': 0}, 21: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001}, 22: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 9.200000000046}, 23: {'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 24: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 25: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}}
    
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
    try:
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
                                                             'total tvs': 1000,
                                                             'skipped tvs': 1},
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'},
                                          random_seed=10983)
    except OSError:
        time.sleep(0.5)
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
                                                             'total tvs': 1000,
                                                             'skipped tvs': 1},
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'},
                                          random_seed=10983)
   
    bb_controller.run_multi_agent_bb()
    time.sleep(0.05)
        
    assert list(bb_controller.bb.get_blackboard()['level 1'].keys()) == ['core_[73.25004,64.46135,0.26703]', 'core_[77.10531,61.23828,0.26703]', 'core_[77.10531,67.68442,0.26703]', 'core_[77.10531,64.46135,0.25368]', 'core_[73.25004,67.68442,0.28108]', 'core_[69.58754,64.46135,0.28108]', 'core_[76.91254,64.46135,0.28108]', 'core_[73.06691,64.46135,0.29587]', 'core_[76.91254,67.68442,0.29587]', 'core_[69.58754,67.68442,0.29587]', 'core_[66.10816,64.46135,0.29587]', 'core_[73.06692,64.46135,0.29587]']
    
    assert bb_controller.bb.get_kaar() == {1: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 2: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 3: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 4: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 5: {'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 6: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 7: {'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 8: {'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 9: {'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 10: {'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 11: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.50001}, 12: {'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.800000000024, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.750011}, 13: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 3.0000120000000003}, 14: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 3.2500130000000005}, 15: {'ka_rp_explore': 3.5000140000000006, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl1': 0, 'ka_br_lvl2': 0}, 16: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 3.7500150000000008, 'ka_rp_exploit': 5.00001}, 17: {'ka_rp_explore': 4.0000160000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 18: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.250017000000001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001}, 19: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.500018000000001, 'ka_rp_exploit': 5.00001}, 20: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.750019000000001}, 21: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 22: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 9.200000000046}, 23: {'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001}, 24: {'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 5.00001}, 25: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}}

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
    try:
        bb_controller = controller.BenchmarkController(bb_name=model, 
                                      bb_type=bb_opt.BenchmarkBbOpt, 
                                      ka=kas, 
                                      archive='{}_benchmark'.format(model),
                                      objectives=objs, 
                                      design_variables=dvs,
                                      benchmark=model, 
                                      convergence_model={'type': 'hvi', 'convergence rate': 1E-5, 
                                                         'interval': 5, 'pf size': 10, 'total tvs': 10, 'skipped tvs': 1},
                                      random_seed=10987)
    except OSError:
        time.sleep(0.5)
        bb_controller = controller.BenchmarkController(bb_name=model, 
                                      bb_type=bb_opt.BenchmarkBbOpt, 
                                      ka=kas, 
                                      archive='{}_benchmark'.format(model),
                                      objectives=objs, 
                                      design_variables=dvs,
                                      benchmark=model, 
                                      convergence_model={'type': 'hvi', 'convergence rate': 1E-5, 
                                                         'interval': 5, 'pf size': 10, 'total tvs': 10, 'skipped tvs': 1},
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
    
    assert bb_controller.bb.get_blackboard()['level 100']['final']['hvi'] == 0.655747859
    
    bb_controller.shutdown()
    os.remove('sf2_benchmark.h5')
    time.sleep(0.05)
    
#------------------------------------------------
# Test of Multi_Tiered_Controller
#------------------------------------------------

def test_MTC_init():
    try:
        mtc = controller.Multi_Tiered_Controller()
    except OSError:
        time.sleep(0.5)
        mtc = controller.Multi_Tiered_Controller()
        
    assert mtc.master_bb == None
    assert mtc.sub_bb == None
    assert mtc._ns != None
    assert mtc._proxy_server != None
    mtc.shutdown()
    time.sleep(0.05)    
    
def test_MTC_initialize_bb():  
    try:
        mtc = controller.Multi_Tiered_Controller()
    except OSError:
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
    assert master_bb.get_attr('convergence_model') == {'type': 'hvi', 'convergence rate': 1E-5, 'interval': 25, 'pf size': 200, 'total tvs': 1000000.0, 'skipped tvs': 200}
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
    assert sub_bb.get_attr('convergence_model') == {'type': 'hvi', 'convergence rate': 1E-5, 'interval': 25, 'pf size': 200, 'total tvs': 1000000.0, 'skipped tvs': 200}
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
    try:
        mtc = controller.Multi_Tiered_Controller()
    except OSError:
        mtc = controller.Multi_Tiered_Controller()        
    kas = {'mka_rp_hc': karp.KaLocalHC,
           'mka_rp_pert': karp.KaLocal,
           'mka_rp_ga': karp.KaLocalGA,
           'mka_br_lvl3': kabr.KaBr_lvl3,
           'mka_br_lvl2': kabr.KaBr_lvl2,
           'mka_br_lvl1': kabr.KaBr_lvl1}
    
    mtc.initialize_blackboard('master_bb', bb_name='bb_master', bb_type=bb_opt.MasterBbOpt, ka=kas, archive='bb_master', convergence_model={'type': 'hvi', 'convergence rate': 0.04, 'interval': 5, 'pf size': 5, 'total tvs': 50, 'skipped tvs': 1}, random_seed=1)
    
    master_bb = mtc.master_bb
    master_bb.set_attr(skipped_tvs=0)
    kas = {'ska_rp_mc': karp.KaGlobal, 
           'ska_rp_hc': karp.KaLocalHC,
           'ska_rp_pert': karp.KaLocal,
           'ska_br_lvl3': kabr.KaBr_lvl3,
           'ska_br_lvl2': kabr.KaBr_lvl2,
           'ska_br_lvl1': kabr.KaBr_lvl1,
           'ska_br_inter': kabr.KaBr_interBB}
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', bb_type=bb_opt.SubBbOpt, ka=kas,  archive='bb_sub', convergence_model={'type': 'hvi', 'convergence rate': 0.04, 'interval': 8, 'pf size': 5, 'total tvs': 50, 'skipped tvs': 1}, random_seed=1)
    
    sub_bb = mtc.sub_bb
    sub_bb.set_attr(skipped_tvs=0)
    
    mtc.run_sub_bb(sub_bb)

    assert list(sub_bb.get_blackboard()['level 1']) == ['core_[73.61973,58.3461,0.55869]', 'core_[70.11403,61.26341,0.55869]', 'core_[70.11403,58.3461,0.53076]', 'core_[69.41289,58.3461,0.55869]', 'core_[69.41289,64.18071,0.12782]', 'core_[77.12543,64.18071,0.11504]', 'core_[77.12543,64.18071,0.10354]', 'core_[77.12543,64.18071,0.12654]', 'core_[77.12543,64.18071,0.10469]', 'core_[70.18414,69.95697,0.11504]', 'core_[70.87827,69.95697,0.11504]', 'core_[77.12543,64.85711,0.11504]', 'core_[77.12543,65.36709,0.11504]', 'core_[77.12543,65.82608,0.11504]', 'core_[77.12543,66.23917,0.11504]', 'core_[77.12543,66.61095,0.11504]', 'core_[77.12543,66.94555,0.11504]', 'core_[77.12543,67.24669,0.11504]', 'core_[77.12543,67.51772,0.11504]', 'core_[79.81463,69.95697,0.11504]', 'core_[79.81463,69.95697,0.11103]', 'core_[77.03167,69.95697,0.11504]', 'core_[79.81463,69.95697,0.11905]', 'core_[79.81463,69.95697,0.1232]', 'core_[79.81463,67.51772,0.1232]', 'core_[79.81463,69.95697,0.1275]', 'core_[79.81463,67.51772,0.1275]', 'core_[79.81463,69.95697,0.12305]', 'core_[79.81463,67.76165,0.1275]', 'core_[79.81463,69.95697,0.1235]', 'core_[79.81463,67.98118,0.1275]', 'core_[79.81463,69.95697,0.1239]', 'core_[79.81463,68.17876,0.1275]', 'core_[79.81463,69.95697,0.12426]', 'core_[79.81463,68.35658,0.1275]', 'core_[79.81463,69.95697,0.12458]', 'core_[79.81463,69.95697,0.12487]', 'core_[79.81463,68.51662,0.1275]', 'core_[79.81463,69.95697,0.12745]', 'core_[79.81463,68.51662,0.13013]', 'core_[79.81463,69.95697,0.12772]', 'core_[79.81463,68.66065,0.12772]', 'core_[79.81463,69.95697,0.12535]', 'core_[79.81463,68.79028,0.12985]', 'core_[79.81463,69.95697,0.12768]', 'core_[79.81463,69.95697,0.1279]', 'core_[79.81463,69.95697,0.12598]', 'core_[79.81463,68.90695,0.1279]', 'core_[79.81463,69.95697,0.12617]', 'core_[79.81463,69.01196,0.1279]', 'core_[79.81463,69.01196,0.12963]', 'core_[79.81463,69.95697,0.12788]', 'core_[79.81463,69.10646,0.12963]', 'core_[79.81463,69.95697,0.12805]', 'core_[79.81463,69.10646,0.12805]', 'core_[79.81463,69.95697,0.12803]', 'core_[79.81463,69.10646,0.12961]', 'core_[79.81463,69.19151,0.12961]', 'core_[79.81463,69.95697,0.12819]', 'core_[79.81463,69.95697,0.12679]', 'core_[79.81463,69.19151,0.12819]', 'core_[79.81463,69.95697,0.12818]', 'core_[79.81463,69.26805,0.12945]', 'core_[79.81463,69.95697,0.1283]', 'core_[79.81463,69.33695,0.1283]', 'core_[79.81463,69.95697,0.12716]', 'core_[79.81463,69.39895,0.1283]', 'core_[79.81463,69.95697,0.12728]', 'core_[79.81463,69.39895,0.12932]', 'core_[79.81463,69.95697,0.12829]', 'core_[79.81463,69.45475,0.12932]', 'core_[79.81463,69.95697,0.12839]', 'core_[79.81463,69.45475,0.12839]', 'core_[79.81463,69.95697,0.12747]', 'core_[79.81463,69.50497,0.12839]', 'core_[79.81463,69.95697,0.12756]', 'core_[79.81463,69.50497,0.12922]', 'core_[79.81463,69.55017,0.12922]', 'core_[79.81463,69.95697,0.12847]', 'core_[79.81463,69.55017,0.12847]', 'core_[79.81463,69.95697,0.1278]', 'core_[79.81463,69.59085,0.12847]', 'core_[79.81463,69.59085,0.12914]', 'core_[79.81463,69.95697,0.12846]', 'core_[79.81463,69.62746,0.12914]', 'core_[79.81463,69.95697,0.12853]', 'core_[79.81463,69.62746,0.12853]', 'core_[79.81463,69.95697,0.12792]', 'core_[79.81463,69.66041,0.12853]', 'core_[79.81463,69.66041,0.12907]', 'core_[79.81463,69.95697,0.12852]', 'core_[79.81463,69.69007,0.12907]', 'core_[79.81463,69.95697,0.12858]', 'core_[79.81463,69.71676,0.12907]', 'core_[79.81463,69.95697,0.12863]', 'core_[79.81463,69.74078,0.12907]', 'core_[79.81463,69.95697,0.12867]', 'core_[79.81463,69.7624,0.12871]', 'core_[79.81463,69.95697,0.12835]', 'core_[79.81463,69.78186,0.12871]', 'core_[79.81463,69.79937,0.12871]', 'core_[79.99444,69.95697,0.12871]', 'core_[79.99444,69.95697,0.129]', 'core_[79.99444,69.79937,0.129]', 'core_[79.99444,69.95697,0.12929]', 'core_[79.99444,69.95697,0.12958]', 'core_[79.99444,69.79937,0.12929]', 'core_[79.99444,69.95697,0.12955]', 'core_[79.99444,69.81513,0.12929]', 'core_[79.99444,69.95697,0.12903]', 'core_[79.99444,69.95697,0.12905]', 'core_[79.84847,69.95697,0.12929]', 'core_[79.99444,69.95697,0.12953]', 'core_[79.99444,69.82931,0.12953]', 'core_[79.99444,69.95697,0.12977]', 'core_[79.99444,69.95697,0.12932]', 'core_[79.99444,69.84208,0.12953]', 'core_[79.99444,69.95697,0.12974]', 'core_[79.99444,69.95697,0.12934]', 'core_[79.99444,69.85357,0.12953]', 'core_[79.99444,69.95697,0.12972]', 'core_[79.99444,69.95697,0.1297]', 'core_[79.99444,69.95697,0.12936]', 'core_[79.99444,69.86391,0.12953]', 'core_[79.99444,69.95697,0.12937]', 'core_[79.99444,69.95697,0.12969]', 'core_[79.99444,69.87321,0.12953]', 'core_[79.99444,69.95697,0.12967]', 'core_[79.99444,69.95697,0.12939]', 'core_[79.99444,69.88159,0.12953]']
    
    assert sub_bb.get_blackboard()['level 100']['final']['hvi'] == 0.1012149136
    
    assert sub_bb.get_kaar() == {1: {'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0}, 2: {'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0}, 3: {'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0}, 4: {'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0}, 5: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0}, 6: {'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0}, 7: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 3.00000000001}, 8: {'ska_br_lvl3': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.500002, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl2': 4.00000000002}, 9: {'ska_br_lvl1': 0, 'ska_br_inter': 6.00000000001, 'ska_rp_mc': 0.750003, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0}, 10: {'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.000004, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 5.00001}, 11: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.2500049999999998, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 0, 'ska_br_lvl3': 3.00000000001}, 12: {'ska_rp_mc': 1.5000059999999997, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_br_lvl3': 34.200000000114, 'ska_br_lvl2': 0}, 13: {'ska_rp_mc': 1.7500069999999996, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_br_lvl2': 110.00000000055}, 14: {'ska_rp_hc': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl1': 6.00000000003, 'ska_rp_mc': 2.000008, 'ska_rp_pert': 5.00001, 'ska_br_lvl2': 0, 'ska_br_inter': 6.00000000001}, 15: {'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_inter': 6.00000000001, 'ska_rp_mc': 2.250009, 'ska_rp_hc': 5.00001, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0}, 16: {'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl1': 0, 'ska_rp_mc': 2.50001, 'ska_rp_hc': 5.00001, 'ska_br_lvl2': 0, 'ska_br_inter': 0}}
    
    assert list(master_bb.get_blackboard()['level 3']['new'].keys()) == ['core_[70.11403,58.3461,0.55869]', 'core_[73.61973,58.3461,0.55869]', 'core_[70.11403,61.26341,0.55869]', 'core_[70.11403,58.3461,0.53076]', 'core_[69.41289,58.3461,0.55869]', 'core_[69.41289,64.18071,0.12782]', 'core_[77.12543,64.18071,0.11504]', 'core_[77.12543,64.18071,0.10354]', 'core_[77.12543,64.18071,0.12654]', 'core_[77.12543,64.18071,0.10469]', 'core_[70.18414,69.95697,0.11504]', 'core_[70.87827,69.95697,0.11504]', 'core_[77.12543,64.85711,0.11504]', 'core_[77.12543,65.36709,0.11504]', 'core_[77.12543,65.82608,0.11504]', 'core_[77.12543,66.23917,0.11504]', 'core_[77.12543,66.61095,0.11504]', 'core_[77.12543,66.94555,0.11504]', 'core_[77.12543,67.24669,0.11504]', 'core_[77.12543,67.51772,0.11504]', 'core_[79.81463,69.95697,0.11504]', 'core_[79.81463,69.95697,0.11103]', 'core_[77.03167,69.95697,0.11504]', 'core_[79.81463,69.95697,0.11905]', 'core_[79.81463,69.95697,0.1232]', 'core_[79.81463,67.51772,0.1232]', 'core_[79.81463,69.95697,0.1275]', 'core_[79.81463,67.51772,0.1275]', 'core_[79.81463,69.95697,0.12305]', 'core_[79.81463,67.76165,0.1275]', 'core_[79.81463,69.95697,0.1235]', 'core_[79.81463,67.98118,0.1275]', 'core_[79.81463,69.95697,0.1239]', 'core_[79.81463,68.17876,0.1275]', 'core_[79.81463,69.95697,0.12426]', 'core_[79.81463,68.35658,0.1275]', 'core_[79.81463,69.95697,0.12458]', 'core_[79.81463,69.95697,0.12487]', 'core_[79.81463,68.51662,0.1275]', 'core_[79.81463,69.95697,0.12745]', 'core_[79.81463,68.51662,0.13013]', 'core_[79.81463,69.95697,0.12772]', 'core_[79.81463,68.66065,0.12772]', 'core_[79.81463,69.95697,0.12535]', 'core_[79.81463,68.79028,0.12985]', 'core_[79.81463,69.95697,0.12768]', 'core_[79.81463,69.95697,0.1279]', 'core_[79.81463,69.95697,0.12598]', 'core_[79.81463,68.90695,0.1279]', 'core_[79.81463,69.95697,0.12617]', 'core_[79.81463,69.01196,0.1279]', 'core_[79.81463,69.01196,0.12963]', 'core_[79.81463,69.95697,0.12788]', 'core_[79.81463,69.10646,0.12963]', 'core_[79.81463,69.95697,0.12805]', 'core_[79.81463,69.10646,0.12805]', 'core_[79.81463,69.95697,0.12803]', 'core_[79.81463,69.10646,0.12961]', 'core_[79.81463,69.19151,0.12961]', 'core_[79.81463,69.95697,0.12819]', 'core_[79.81463,69.95697,0.12679]', 'core_[79.81463,69.19151,0.12819]', 'core_[79.81463,69.95697,0.12818]', 'core_[79.81463,69.26805,0.12945]', 'core_[79.81463,69.95697,0.1283]', 'core_[79.81463,69.33695,0.1283]', 'core_[79.81463,69.95697,0.12716]', 'core_[79.81463,69.39895,0.1283]', 'core_[79.81463,69.95697,0.12728]', 'core_[79.81463,69.39895,0.12932]', 'core_[79.81463,69.95697,0.12829]', 'core_[79.81463,69.45475,0.12932]', 'core_[79.81463,69.95697,0.12839]', 'core_[79.81463,69.45475,0.12839]', 'core_[79.81463,69.95697,0.12747]', 'core_[79.81463,69.50497,0.12839]', 'core_[79.81463,69.95697,0.12756]', 'core_[79.81463,69.50497,0.12922]', 'core_[79.81463,69.55017,0.12922]', 'core_[79.81463,69.95697,0.12847]', 'core_[79.81463,69.55017,0.12847]', 'core_[79.81463,69.95697,0.1278]', 'core_[79.81463,69.59085,0.12847]', 'core_[79.81463,69.59085,0.12914]', 'core_[79.81463,69.95697,0.12846]', 'core_[79.81463,69.62746,0.12914]', 'core_[79.81463,69.95697,0.12853]', 'core_[79.81463,69.62746,0.12853]', 'core_[79.81463,69.95697,0.12792]', 'core_[79.81463,69.66041,0.12853]', 'core_[79.81463,69.66041,0.12907]', 'core_[79.81463,69.95697,0.12852]', 'core_[79.81463,69.69007,0.12907]', 'core_[79.81463,69.95697,0.12858]', 'core_[79.81463,69.71676,0.12907]', 'core_[79.81463,69.95697,0.12863]', 'core_[79.81463,69.74078,0.12907]', 'core_[79.81463,69.95697,0.12867]', 'core_[79.81463,69.7624,0.12871]', 'core_[79.81463,69.95697,0.12835]', 'core_[79.81463,69.78186,0.12871]', 'core_[79.81463,69.79937,0.12871]', 'core_[79.99444,69.95697,0.12871]', 'core_[79.99444,69.95697,0.129]', 'core_[79.99444,69.79937,0.129]', 'core_[79.99444,69.95697,0.12929]', 'core_[79.99444,69.95697,0.12958]', 'core_[79.99444,69.79937,0.12929]', 'core_[79.99444,69.95697,0.12955]', 'core_[79.99444,69.81513,0.12929]', 'core_[79.99444,69.95697,0.12903]', 'core_[79.99444,69.95697,0.12905]', 'core_[79.84847,69.95697,0.12929]', 'core_[79.99444,69.95697,0.12953]', 'core_[79.99444,69.82931,0.12953]', 'core_[79.99444,69.95697,0.12977]', 'core_[79.99444,69.95697,0.12932]', 'core_[79.99444,69.84208,0.12953]', 'core_[79.99444,69.95697,0.12974]', 'core_[79.99444,69.95697,0.12934]', 'core_[79.99444,69.85357,0.12953]', 'core_[79.99444,69.95697,0.12972]', 'core_[79.99444,69.95697,0.1297]', 'core_[79.99444,69.95697,0.12936]', 'core_[79.99444,69.86391,0.12953]', 'core_[79.99444,69.95697,0.12937]', 'core_[79.99444,69.95697,0.12969]', 'core_[79.99444,69.87321,0.12953]', 'core_[79.99444,69.95697,0.12967]', 'core_[79.99444,69.95697,0.12939]', 'core_[79.99444,69.88159,0.12953]']
    
    os.remove('bb_sub.h5')
    mtc.shutdown()
    time.sleep(0.05)    

def test_MTC_run_master_bb():    
    try:
        mtc = controller.Multi_Tiered_Controller()
    except OSError:
        mtc = controller.Multi_Tiered_Controller()

    kas = {'mka_rp_mc': karp.KaGlobal,
           'mka_rp_hc': karp.KaLocalHC,
           'mka_rp_pert': karp.KaLocal,
           'mka_br_lvl3': kabr.KaBr_lvl3,
           'mka_br_lvl2': kabr.KaBr_lvl2,
           'mka_br_lvl1': kabr.KaBr_lvl1}
    
    mtc.initialize_blackboard('master_bb', bb_name='bb_master', bb_type=bb_opt.MasterBbOpt, ka=kas, archive='bb_master', convergence_model={'type': 'hvi', 'convergence rate': 0.5, 'interval': 5, 'pf size': 5, 'total tvs': 50, 'skipped tvs': 1}, random_seed=1)
    
    master_bb = mtc.master_bb
    master_bb.set_attr(skipped_tvs=0)
    kas = {'ska_rp_mc': karp.KaGlobal, 
           'ska_rp_hc': karp.KaLocalHC,
           'ska_rp_pert': karp.KaLocal,
           'ska_br_lvl3': kabr.KaBr_lvl3,
           'ska_br_lvl2': kabr.KaBr_lvl2,
           'ska_br_lvl1': kabr.KaBr_lvl1,
           'ska_br_inter': kabr.KaBr_interBB}
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', bb_type=bb_opt.SubBbOpt, ka=kas,  archive='bb_sub', convergence_model={'type': 'hvi', 'convergence rate': 0.04, 'interval': 8, 'pf size': 5, 'total tvs': 50, 'skipped tvs': 1}, random_seed=1)
    
    sub_bb = mtc.sub_bb
    sub_bb.set_attr(skipped_tvs=0)
    
    
    mtc.run_sub_bb(sub_bb)
    assert list(master_bb.get_blackboard()['level 3']['new'].keys()) == ['core_[70.11403,58.3461,0.55869]', 'core_[73.61973,58.3461,0.55869]', 'core_[70.11403,61.26341,0.55869]', 'core_[70.11403,58.3461,0.53076]', 'core_[69.41289,58.3461,0.55869]', 'core_[69.41289,64.18071,0.12782]', 'core_[77.12543,64.18071,0.11504]', 'core_[77.12543,64.18071,0.10354]', 'core_[77.12543,64.18071,0.12654]', 'core_[77.12543,64.18071,0.10469]', 'core_[70.18414,69.95697,0.11504]', 'core_[70.87827,69.95697,0.11504]', 'core_[77.12543,64.85711,0.11504]', 'core_[77.12543,65.36709,0.11504]', 'core_[77.12543,65.82608,0.11504]', 'core_[77.12543,66.23917,0.11504]', 'core_[77.12543,66.61095,0.11504]', 'core_[77.12543,66.94555,0.11504]', 'core_[77.12543,67.24669,0.11504]', 'core_[77.12543,67.51772,0.11504]', 'core_[79.81463,69.95697,0.11504]', 'core_[79.81463,69.95697,0.11103]', 'core_[77.03167,69.95697,0.11504]', 'core_[79.81463,69.95697,0.11905]', 'core_[79.81463,69.95697,0.1232]', 'core_[79.81463,67.51772,0.1232]', 'core_[79.81463,69.95697,0.1275]', 'core_[79.81463,67.51772,0.1275]', 'core_[79.81463,69.95697,0.12305]', 'core_[79.81463,67.76165,0.1275]', 'core_[79.81463,69.95697,0.1235]', 'core_[79.81463,67.98118,0.1275]', 'core_[79.81463,69.95697,0.1239]', 'core_[79.81463,68.17876,0.1275]', 'core_[79.81463,69.95697,0.12426]', 'core_[79.81463,68.35658,0.1275]', 'core_[79.81463,69.95697,0.12458]', 'core_[79.81463,69.95697,0.12487]', 'core_[79.81463,68.51662,0.1275]', 'core_[79.81463,69.95697,0.12745]', 'core_[79.81463,68.51662,0.13013]', 'core_[79.81463,69.95697,0.12772]', 'core_[79.81463,68.66065,0.12772]', 'core_[79.81463,69.95697,0.12535]', 'core_[79.81463,68.79028,0.12985]', 'core_[79.81463,69.95697,0.12768]', 'core_[79.81463,69.95697,0.1279]', 'core_[79.81463,69.95697,0.12598]', 'core_[79.81463,68.90695,0.1279]', 'core_[79.81463,69.95697,0.12617]', 'core_[79.81463,69.01196,0.1279]', 'core_[79.81463,69.01196,0.12963]', 'core_[79.81463,69.95697,0.12788]', 'core_[79.81463,69.10646,0.12963]', 'core_[79.81463,69.95697,0.12805]', 'core_[79.81463,69.10646,0.12805]', 'core_[79.81463,69.95697,0.12803]', 'core_[79.81463,69.10646,0.12961]', 'core_[79.81463,69.19151,0.12961]', 'core_[79.81463,69.95697,0.12819]', 'core_[79.81463,69.95697,0.12679]', 'core_[79.81463,69.19151,0.12819]', 'core_[79.81463,69.95697,0.12818]', 'core_[79.81463,69.26805,0.12945]', 'core_[79.81463,69.95697,0.1283]', 'core_[79.81463,69.33695,0.1283]', 'core_[79.81463,69.95697,0.12716]', 'core_[79.81463,69.39895,0.1283]', 'core_[79.81463,69.95697,0.12728]', 'core_[79.81463,69.39895,0.12932]', 'core_[79.81463,69.95697,0.12829]', 'core_[79.81463,69.45475,0.12932]', 'core_[79.81463,69.95697,0.12839]', 'core_[79.81463,69.45475,0.12839]', 'core_[79.81463,69.95697,0.12747]', 'core_[79.81463,69.50497,0.12839]', 'core_[79.81463,69.95697,0.12756]', 'core_[79.81463,69.50497,0.12922]', 'core_[79.81463,69.55017,0.12922]', 'core_[79.81463,69.95697,0.12847]', 'core_[79.81463,69.55017,0.12847]', 'core_[79.81463,69.95697,0.1278]', 'core_[79.81463,69.59085,0.12847]', 'core_[79.81463,69.59085,0.12914]', 'core_[79.81463,69.95697,0.12846]', 'core_[79.81463,69.62746,0.12914]', 'core_[79.81463,69.95697,0.12853]', 'core_[79.81463,69.62746,0.12853]', 'core_[79.81463,69.95697,0.12792]', 'core_[79.81463,69.66041,0.12853]', 'core_[79.81463,69.66041,0.12907]', 'core_[79.81463,69.95697,0.12852]', 'core_[79.81463,69.69007,0.12907]', 'core_[79.81463,69.95697,0.12858]', 'core_[79.81463,69.71676,0.12907]', 'core_[79.81463,69.95697,0.12863]', 'core_[79.81463,69.74078,0.12907]', 'core_[79.81463,69.95697,0.12867]', 'core_[79.81463,69.7624,0.12871]', 'core_[79.81463,69.95697,0.12835]', 'core_[79.81463,69.78186,0.12871]', 'core_[79.81463,69.79937,0.12871]', 'core_[79.99444,69.95697,0.12871]', 'core_[79.99444,69.95697,0.129]', 'core_[79.99444,69.79937,0.129]', 'core_[79.99444,69.95697,0.12929]', 'core_[79.99444,69.95697,0.12958]', 'core_[79.99444,69.79937,0.12929]', 'core_[79.99444,69.95697,0.12955]', 'core_[79.99444,69.81513,0.12929]', 'core_[79.99444,69.95697,0.12903]', 'core_[79.99444,69.95697,0.12905]', 'core_[79.84847,69.95697,0.12929]', 'core_[79.99444,69.95697,0.12953]', 'core_[79.99444,69.82931,0.12953]', 'core_[79.99444,69.95697,0.12977]', 'core_[79.99444,69.95697,0.12932]', 'core_[79.99444,69.84208,0.12953]', 'core_[79.99444,69.95697,0.12974]', 'core_[79.99444,69.95697,0.12934]', 'core_[79.99444,69.85357,0.12953]', 'core_[79.99444,69.95697,0.12972]', 'core_[79.99444,69.95697,0.1297]', 'core_[79.99444,69.95697,0.12936]', 'core_[79.99444,69.86391,0.12953]', 'core_[79.99444,69.95697,0.12937]', 'core_[79.99444,69.95697,0.12969]', 'core_[79.99444,69.87321,0.12953]', 'core_[79.99444,69.95697,0.12967]', 'core_[79.99444,69.95697,0.12939]', 'core_[79.99444,69.88159,0.12953]']
    
    mtc.run_sub_bb(master_bb)

    assert list(master_bb.get_blackboard()['level 1'].keys()) == ['core_[79.81463,69.95697,0.11504]', 'core_[79.81463,69.95697,0.11103]', 'core_[79.81463,69.95697,0.11905]', 'core_[79.81463,69.95697,0.1232]', 'core_[79.81463,69.95697,0.1275]', 'core_[79.81463,69.95697,0.12305]', 'core_[79.81463,69.95697,0.1235]', 'core_[79.81463,69.95697,0.1239]', 'core_[79.81463,69.95697,0.12426]', 'core_[79.81463,69.95697,0.12458]', 'core_[79.81463,69.95697,0.12487]', 'core_[79.81463,69.95697,0.12745]', 'core_[79.81463,69.95697,0.12772]', 'core_[79.81463,69.95697,0.12535]', 'core_[79.81463,69.95697,0.12768]', 'core_[79.81463,69.95697,0.1279]', 'core_[79.81463,69.95697,0.12598]', 'core_[79.81463,69.95697,0.12617]', 'core_[79.81463,69.95697,0.12788]', 'core_[79.81463,69.95697,0.12803]', 'core_[79.81463,69.95697,0.12679]', 'core_[79.81463,69.95697,0.12818]', 'core_[79.81463,69.95697,0.1283]', 'core_[79.81463,69.95697,0.12716]', 'core_[79.81463,69.95697,0.12728]', 'core_[79.81463,69.95697,0.12829]', 'core_[79.81463,69.95697,0.12839]', 'core_[79.81463,69.95697,0.12756]', 'core_[79.81463,69.95697,0.12847]', 'core_[79.81463,69.95697,0.1278]', 'core_[79.81463,69.95697,0.12846]', 'core_[79.81463,69.95697,0.12792]', 'core_[79.81463,69.95697,0.12852]', 'core_[79.81463,69.95697,0.12858]', 'core_[79.81463,69.95697,0.12863]', 'core_[79.81463,69.95697,0.12867]', 'core_[79.81463,69.95697,0.12835]', 'core_[79.99444,69.95697,0.12871]', 'core_[79.99444,69.95697,0.129]', 'core_[79.99444,69.95697,0.12929]', 'core_[79.99444,69.95697,0.12958]', 'core_[79.99444,69.95697,0.12903]', 'core_[79.99444,69.95697,0.12905]', 'core_[79.99444,69.95697,0.12953]', 'core_[79.99444,69.95697,0.12977]', 'core_[79.99444,69.95697,0.12932]', 'core_[79.99444,69.95697,0.12974]', 'core_[79.99444,69.95697,0.12934]', 'core_[79.99444,69.95697,0.1297]', 'core_[79.99444,69.95697,0.12936]', 'core_[79.99444,69.95697,0.12969]', 'core_[79.99444,69.95697,0.12967]', 'core_[79.99444,69.95697,0.12939]', 'core_[79.81463,69.95697,0.10548]', 'core_[79.81463,69.95697,0.11658]', 'core_[79.81463,69.95697,0.10929]', 'core_[79.81463,69.95697,0.12079]', 'core_[79.81463,69.95697,0.12213]', 'core_[79.81463,69.95697,0.09993]', 'core_[79.81463,69.95697,0.10992]', 'core_[79.81463,69.95697,0.08994]', 'core_[79.81463,69.95697,0.08095]', 'core_[79.81463,69.95697,0.08904]', 'core_[79.81463,69.95697,0.07285]', 'core_[79.81463,69.95697,0.08013]', 'core_[79.81463,69.95697,0.06556]', 'core_[79.81463,69.95697,0.07212]', 'core_[79.81463,69.95697,0.059]', 'core_[79.81463,69.95697,0.0531]', 'core_[79.81463,69.95697,0.04779]', 'core_[79.81463,69.95697,0.05257]', 'core_[79.81463,69.95697,0.04301]', 'core_[79.81463,69.95697,0.03871]', 'core_[79.81463,69.95697,0.03484]', 'core_[79.81463,69.95697,0.03832]', 'core_[79.81463,69.95697,0.03136]', 'core_[79.81463,69.95697,0.02822]', 'core_[79.81463,69.95697,0.0254]', 'core_[79.81463,69.95697,0.02286]', 'core_[79.81463,69.95697,0.02515]', 'core_[79.81463,69.95697,0.02057]', 'core_[79.81463,69.95697,0.01851]', 'core_[79.81463,69.95697,0.02036]', 'core_[79.81463,69.95697,0.01666]', 'core_[79.81463,69.95697,0.01499]', 'core_[79.81463,69.95697,0.01349]', 'core_[79.81463,69.95697,0.01214]', 'core_[79.81463,69.95697,0.01202]', 'core_[79.81463,69.95697,0.01191]', 'core_[79.81463,69.95697,0.01182]', 'core_[79.81463,69.95697,0.01173]', 'core_[79.81463,69.95697,0.01165]', 'core_[79.81463,69.95697,0.01158]', 'core_[79.81463,69.95697,0.01151]', 'core_[79.81463,69.95697,0.01145]', 'core_[79.99444,69.95697,0.01046]', 'core_[79.99444,69.95697,0.01048]', 'core_[79.99444,69.95697,0.01044]', 'core_[79.99444,69.95697,0.01042]', 'core_[79.99444,69.95697,0.0104]', 'core_[79.99444,69.95697,0.01038]', 'core_[79.99444,69.95697,0.01036]', 'core_[79.99444,69.95697,0.01034]', 'core_[79.99444,69.95697,0.01032]', 'core_[79.99444,69.95697,0.0103]', 'core_[79.99444,69.95697,0.01028]', 'core_[79.99444,69.95697,0.01026]', 'core_[79.99444,69.95697,0.01024]', 'core_[79.99444,69.95697,0.01022]', 'core_[79.99444,69.95697,0.0102]', 'core_[79.99444,69.95697,0.01018]', 'core_[79.99444,69.95697,0.01016]', 'core_[79.99444,69.95697,0.01014]', 'core_[79.99444,69.95697,0.01012]', 'core_[79.99444,69.95697,0.0101]', 'core_[79.99444,69.95697,0.01008]', 'core_[79.99444,69.95697,0.01006]', 'core_[79.99444,69.95697,0.01004]', 'core_[79.99444,69.95697,0.01002]', 'core_[79.99444,69.95697,0.01]', 'core_[79.99444,69.95697,0.00998]', 'core_[79.99444,69.95697,0.00996]', 'core_[79.99444,69.95697,0.00994]', 'core_[79.99444,69.95697,0.00992]', 'core_[79.99444,69.95697,0.0099]', 'core_[79.99444,69.95697,0.00988]', 'core_[79.99444,69.95697,0.00986]', 'core_[79.99444,69.95697,0.00984]', 'core_[79.99444,69.95697,0.00982]', 'core_[79.99444,69.95697,0.0098]', 'core_[79.99444,69.95697,0.00978]', 'core_[79.99444,69.95697,0.00976]', 'core_[79.99444,69.95697,0.00974]', 'core_[79.99444,69.95697,0.00972]', 'core_[79.99444,69.95697,0.0097]', 'core_[79.99444,69.95697,0.00968]', 'core_[79.99444,69.95697,0.00966]']

    assert master_bb.get_kaar() == {1: {'mka_rp_hc': 0, 'mka_rp_pert': 0, 'mka_rp_mc': 0.250001, 'mka_br_lvl3': 15.720000000052401, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0}, 2: {'mka_rp_mc': 0.500002, 'mka_rp_hc': 0, 'mka_rp_pert': 0, 'mka_br_lvl3': 0, 'mka_br_lvl2': 52.400000000262, 'mka_br_lvl1': 0}, 3: {'mka_rp_mc': 0.750003, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl2': 0, 'mka_br_lvl1': 6.00000000003, 'mka_rp_hc': 5.00001}, 4: {'mka_br_lvl3': 0, 'mka_rp_mc': 1.000004, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0}, 5: {'mka_rp_mc': 1.2500049999999998, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 3.00000000001, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0}, 6: {'mka_rp_mc': 1.5000059999999997, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 3.00000000001, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0}, 7: {'mka_rp_mc': 1.7500069999999996, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 35.0400000001168, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0}, 8: {'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 2.000008, 'mka_rp_hc': 5.00001, 'mka_br_lvl2': 50.400000000252}, 9: {'mka_rp_hc': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl2': 0, 'mka_br_lvl1': 6.00000000003, 'mka_rp_mc': 2.250009, 'mka_rp_pert': 5.00001}, 10: {'mka_rp_mc': 2.50001, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0}}
    os.remove('bb_sub.h5')
    os.remove('bb_master.h5')
    
    mtc.shutdown()
    time.sleep(0.05) 

