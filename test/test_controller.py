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
    kas = {'ka_rp_explore': {'type': karp.KaGlobal, 'attr' : {}},
           'ka_rp_exploit': {'type': karp.KaLocal, 'attr' : {'perturbation_size' : 0.25}},
           'ka_br_lvl3': {'type': kabr.KaBr_lvl3, 'attr' : {}},
           'ka_br_lvl2': {'type': kabr.KaBr_lvl2, 'attr' : {}}}
    obj = {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    dv = {'height':     {'ll': 60.0, 'ul': 80.0, 'variable type': float},
          'smear':      {'ll': 70.0, 'ul': 70.0, 'variable type': float},
          'pu_content': {'ll': 0.5,  'ul': 1.0,  'variable type': float}}
    const = {'eol keff':    {'ll': 1.1, 'ul': 2.5, 'variable type': float}}

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
                                          total_tvs=100,
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
                                          total_tvs=100,
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'})
    with open('./sm_gpr.pkl', 'rb') as pickle_file:
        sm_gpr = pickle.load(pickle_file)
    
    assert bb_controller.bb_name == 'sfr_opt'
    assert bb_controller.bb_type == bb_opt.BbOpt
    assert bb_controller.agent_wait_time == 10
    assert bb_controller.plot_progress == True
    assert bb_controller.progress_rate == 25  

    agents =  bb_controller.bb.get_attr('agent_addrs')
    bb = bb_controller.bb
    assert [x for x in agents.keys()] == ['ka_rp_explore', 'ka_rp_exploit', 'ka_br_lvl3', 'ka_br_lvl2']
    assert bb_controller.bb.get_attr('sm_type') == 'gpr'
    assert type(bb_controller.bb.get_attr('_sm')) == type(sm_gpr)
    assert bb_controller.bb.get_attr('archive_name') == 'sfr_opt.h5'
    assert bb.get_attr('objectives') == obj
    assert bb.get_attr('design_variables') == dv
    assert bb.get_attr('constraints') == const
    ps = bb.get_attr('_proxy_server')
    ka = ps.proxy('ka_rp_exploit')
    assert ka.get_attr('perturbation_size') == 0.25
    
    bb_controller._ns.shutdown()
    time.sleep(0.05)
    
def test_run_single_agent_bb():
    kas = {'ka_rp_explore': {'type': karp.KaGlobal},
           'ka_rp_exploit': {'type': karp.KaLocal},
           'ka_br_lvl3': {'type': kabr.KaBr_lvl3},
           'ka_br_lvl2': {'type': kabr.KaBr_lvl2},
           'ka_br_lvl1': {'type': kabr.KaBr_lvl1}}
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
                                          total_tvs=100,
                                          skipped_tvs=0,
                                          convergence_type='hvi',
                                          convergence_rate=1E-3,
                                          convergence_interval=5,
                                          pf_size=5,
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
                                          total_tvs=100,
                                          skipped_tvs=0,
                                          convergence_type='hvi',
                                          convergence_rate=1E-3,
                                          convergence_interval=5,
                                          pf_size=5,
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'},
                                          random_seed=10983)
   
    bb_controller.run_single_agent_bb()
    
    assert list(bb_controller.bb.get_blackboard()['level 1'].keys()) == ['core_[73.25004,64.46135,0.26703]', 'core_[77.10531,67.68442,0.26703]', 'core_[77.10531,64.46135,0.25368]', 'core_[73.25004,67.68442,0.28108]', 'core_[69.58754,64.46135,0.28108]', 'core_[76.91254,64.46135,0.28108]', 'core_[73.06691,64.46135,0.29587]', 'core_[76.91254,67.68442,0.29587]', 'core_[69.58754,67.68442,0.29587]', 'core_[66.10816,64.46135,0.29587]', 'core_[73.06692,64.46135,0.29587]']

    assert bb_controller.bb.get_hv_list() == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0544373155, 0.0544373155, 0.0544373155, 0.0544373155, 0.0544373155, 0.0659891097, 0.0659891097, 0.0659891097, 0.0659891097, 0.0659891097, 0.0701328254, 0.0701328254, 0.0701328254, 0.0701328254, 0.0701328254, 0.0701328254, 0.0701328254, 0.0701328254, 0.0701328254, 0.0701328254, 0.0738202257]

    assert bb_controller.bb.get_kaar() == {1: {'ka_rp_exploit': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_br_lvl3': 0}, 2: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0}, 3: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 4: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.750003}, 5: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 6: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 7: {'ka_br_lvl2': 0, 'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl1': 6.00000000003}, 8: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 9: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001}, 10: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 11: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 12: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.750011, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.800000000024}, 13: {'ka_rp_explore': 3.0000120000000003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 14: {'ka_br_lvl1': 0, 'ka_rp_explore': 3.2500130000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 15: {'ka_rp_explore': 3.5000140000000006, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 16: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 3.7500150000000008}, 17: {'ka_rp_explore': 4.0000160000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 18: {'ka_rp_explore': 4.250017000000001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 19: {'ka_rp_explore': 4.500018000000001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 20: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.750019000000001}, 21: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0}, 22: {'ka_rp_exploit': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_br_lvl3': 0, 'ka_br_lvl2': 9.200000000046}, 23: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 0.750003}, 24: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004}, 25: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}}
    
    assert bb_controller.bb.get_attr('_complete') == True
    bb_controller.shutdown()
    os.remove('sfr_opt.h5')
    time.sleep(0.05)

def test_run_multi_agent_bb():
    kas = {'ka_rp_explore': {'type': karp.KaGlobal},
           'ka_rp_exploit': {'type': karp.KaLocal},
           'ka_br_lvl3': {'type': kabr.KaBr_lvl3},
           'ka_br_lvl2': {'type': kabr.KaBr_lvl2},
           'ka_br_lvl1': {'type': kabr.KaBr_lvl1}}
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
                                          total_tvs=100,
                                          skipped_tvs=0,
                                          convergence_type='hvi',
                                          convergence_rate=1E-3,
                                          convergence_interval=5,
                                          pf_size=5,
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
                                          total_tvs=100,
                                          skipped_tvs=0,
                                          convergence_type='hvi',
                                          convergence_rate=1E-3,
                                          convergence_interval=5,
                                          pf_size=5,
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'},
                                          random_seed=10983)
   
    bb_controller.run_multi_agent_bb()
    time.sleep(0.05)

    assert list(bb_controller.bb.get_blackboard()['level 1'].keys()) == ['core_[73.25004,64.46135,0.26703]', 'core_[77.10531,67.68442,0.26703]', 'core_[77.10531,64.46135,0.25368]', 'core_[73.25004,67.68442,0.28108]', 'core_[69.58754,64.46135,0.28108]', 'core_[76.91254,64.46135,0.28108]', 'core_[73.06691,64.46135,0.29587]', 'core_[76.91254,67.68442,0.29587]', 'core_[69.58754,67.68442,0.29587]', 'core_[66.10816,64.46135,0.29587]', 'core_[73.06692,64.46135,0.29587]']
    
    assert bb_controller.bb.get_kaar() == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_br_lvl3': 0}, 2: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 3: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 4: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 5: {'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 6: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0}, 7: {'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 8: {'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 9: {'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 10: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 11: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.50001}, 12: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.750011, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.800000000024}, 13: {'ka_rp_explore': 3.0000120000000003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 14: {'ka_rp_explore': 3.2500130000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 15: {'ka_rp_explore': 3.5000140000000006, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 16: {'ka_rp_explore': 3.7500150000000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 17: {'ka_rp_explore': 4.0000160000000005, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 18: {'ka_rp_exploit': 5.00001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.250017000000001, 'ka_br_lvl3': 3.00000000001}, 19: {'ka_rp_explore': 4.500018000000001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 20: {'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 4.750019000000001}, 21: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 22: {'ka_br_lvl3': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl2': 9.200000000046}, 23: {'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 24: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004}, 25: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 5.00001}}

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
    kas = {'ka_rp_explore': {'type': karp.KaGlobal},
           'ka_rp_pert': {'type': karp.KaLocal},
           'ka_rp_hc':      {'type': karp.KaLocalHC, 'attr' : {'step_limit':15}},
           'ka_br_lvl3':    {'type': kabr.KaBr_lvl3},
           'ka_br_lvl2':    {'type': kabr.KaBr_lvl2},
           'ka_br_lvl1':    {'type': kabr.KaBr_lvl1, 'attr' : {'total_pf_size' : 100, 'pareto_sorter': 'dci', 'dci_div' : {'f1': 80, 'f2': 80}}}}

    try:
        bb_controller = controller.BenchmarkController(bb_name=model, 
                                      bb_type=bb_opt.BenchmarkBbOpt, 
                                      ka=kas, 
                                      archive='{}_benchmark'.format(model),
                                      objectives=objs, 
                                      design_variables=dvs,
                                      benchmark=model, 
                                      total_tvs=10,
                                      skipped_tvs=1,
                                      convergence_type='hvi',
                                      convergence_rate=1E-5,
                                      convergence_interval=5,
                                      pf_size=10,                                                   
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
                                      total_tvs=10,
                                      skipped_tvs=1,
                                      convergence_type='hvi',
                                      convergence_rate=1E-5,
                                      convergence_interval=5,
                                      pf_size=10,
                                      random_seed=10987)
    bb = bb_controller.bb

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
    kas = {'mka_rp_hc': {'type': karp.KaLocalHC},
           'mka_rp_pert': {'type': karp.KaLocal},
           'mka_rp_ga': {'type': karp.KaLocalGA},
           'mka_br_lvl3': {'type': kabr.KaBr_lvl3},
           'mka_br_lvl2': {'type': kabr.KaBr_lvl2},
           'mka_br_lvl1': {'type': kabr.KaBr_lvl1}}
    
    mtc.initialize_blackboard('master_bb', bb_name='bb_master', 
                              bb_type=bb_opt.MasterBbOpt, 
                              ka=kas, 
                              archive='bb_master')
    
    master_bb = mtc.master_bb
    assert master_bb.get_attr('name') == 'bb_master'
    assert master_bb.get_attr('archive_name') == 'bb_master.h5'

    assert master_bb.get_attr('sm_type') == 'gpr'
    assert master_bb.get_attr('objectives') == {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'goal':'gt', 'variable type': float},
                                                'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
    assert master_bb.get_attr('design_variables') == {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    assert master_bb.get_attr('constraints') == {
                            'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                            'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    
    kas = {'ska_rp_mc': {'type': karp.KaGlobal}, 
           'ska_rp_hc': {'type': karp.KaLocalHC},
           'ska_rp_lhc': {'type': karp.KaLHC},
           'ska_rp_pert': {'type': karp.KaLocal},
           'ska_rp_ga': {'type': karp.KaLocalGA},
           'ska_br_lvl3': {'type': kabr.KaBr_lvl3},
           'ska_br_lvl2': {'type': kabr.KaBr_lvl2},
           'ska_br_lvl1': {'type': kabr.KaBr_lvl1},
           'ska_br_inter': {'type': kabr.KaBr_interBB, 'attr':{'bb': master_bb}}}
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', 
                              bb_type=bb_opt.SubBbOpt, 
                              ka=kas,  
                              archive='bb_sub')
    
    sub_bb = mtc.sub_bb
    assert sub_bb.get_attr('name') == 'bb_sub'
    assert sub_bb.get_attr('archive_name') == 'bb_sub.h5'

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
    kas = {'mka_rp_hc': {'type': karp.KaLocalHC},
           'mka_rp_pert': {'type': karp.KaLocal},
           'mka_rp_ga': {'type': karp.KaLocalGA},
           'mka_br_lvl3': {'type': kabr.KaBr_lvl3},
           'mka_br_lvl2': {'type': kabr.KaBr_lvl2},
           'mka_br_lvl1': {'type': kabr.KaBr_lvl1}}
    
    mtc.initialize_blackboard('master_bb', bb_name='bb_master', 
                                           bb_type=bb_opt.MasterBbOpt, 
                                           ka=kas, 
                                           archive='bb_master', 
                                           total_tvs=10,
                                           skipped_tvs=0,
                                           convergence_type='hvi',
                                           convergence_rate=0.04,
                                           convergence_interval=5,
                                           pf_size=5,
                                           random_seed=1)
    
    master_bb = mtc.master_bb
    kas = {'ska_rp_mc': {'type': karp.KaGlobal}, 
           'ska_rp_hc': {'type': karp.KaLocalHC},
           'ska_rp_pert': {'type': karp.KaLocal},
           'ska_br_lvl3': {'type': kabr.KaBr_lvl3},
           'ska_br_lvl2': {'type': kabr.KaBr_lvl2},
           'ska_br_lvl1': {'type': kabr.KaBr_lvl1},
           'ska_br_inter': {'type': kabr.KaBr_interBB, 'attr':{'bb': master_bb}}}
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', 
                              bb_type=bb_opt.SubBbOpt, 
                              ka=kas,  
                              archive='bb_sub', 
                              total_tvs=50,
                              skipped_tvs=0,
                              convergence_type='hvi',
                              convergence_rate=0.04,
                              convergence_interval=8,
                              pf_size=5,                              
                              random_seed=1)
    
    sub_bb = mtc.sub_bb
    mtc.run_sub_bb(sub_bb)

    assert list(sub_bb.get_blackboard()['level 1']) == ['core_[73.61973,58.3461,0.55869]', 'core_[70.11403,61.26341,0.55869]', 'core_[70.11403,58.3461,0.53076]', 'core_[69.41289,58.3461,0.55869]', 'core_[69.41289,64.18071,0.17533]', 'core_[77.12543,64.18071,0.11504]', 'core_[77.12543,64.18071,0.10354]', 'core_[77.12543,64.18071,0.10469]', 'core_[70.18414,69.95697,0.10469]', 'core_[77.12543,64.29046,0.11317]', 'core_[71.50299,69.95697,0.11317]', 'core_[77.12543,64.85711,0.11317]', 'core_[77.12543,65.36709,0.10574]', 'core_[72.06523,69.95697,0.10574]', 'core_[77.12543,65.82608,0.10574]', 'core_[77.12543,65.82608,0.11198]', 'core_[77.12543,66.23917,0.11198]', 'core_[73.02667,69.95697,0.11198]', 'core_[77.12543,66.61095,0.10662]', 'core_[77.12543,66.94555,0.11121]', 'core_[77.12543,67.24669,0.11121]', 'core_[77.12543,67.51772,0.10733]', 'core_[79.81463,69.95697,0.10733]', 'core_[79.81463,69.95697,0.10359]', 'core_[79.81463,67.51772,0.10733]', 'core_[79.81463,69.95697,0.11107]', 'core_[79.81463,69.95697,0.1072]', 'core_[79.81463,67.51772,0.11107]', 'core_[79.81463,69.95697,0.11494]', 'core_[79.81463,69.95697,0.11093]', 'core_[79.81463,67.51772,0.11494]', 'core_[79.81463,69.95697,0.11133]', 'core_[79.81463,67.76165,0.11494]', 'core_[79.81463,67.98118,0.11494]', 'core_[79.81463,69.95697,0.11819]', 'core_[79.81463,69.95697,0.11169]', 'core_[79.81463,69.95697,0.11786]', 'core_[79.81463,68.17876,0.11494]', 'core_[79.81463,69.95697,0.11202]', 'core_[79.81463,69.95697,0.11757]', 'core_[79.81463,68.35658,0.11494]', 'core_[79.81463,69.95697,0.11231]', 'core_[79.81463,69.95697,0.11257]', 'core_[79.81463,68.51662,0.11494]', 'core_[79.81463,69.95697,0.11731]', 'core_[79.81463,69.95697,0.11707]', 'core_[79.81463,69.95697,0.11281]', 'core_[79.81463,68.66065,0.11494]', 'core_[79.81463,69.95697,0.11302]', 'core_[79.81463,68.79028,0.11494]', 'core_[79.81463,69.95697,0.11686]', 'core_[79.81463,69.95697,0.11667]', 'core_[79.81463,68.90695,0.11494]', 'core_[79.81463,69.95697,0.11321]', 'core_[79.81463,69.95697,0.11649]', 'core_[79.81463,69.01196,0.11494]', 'core_[79.81463,69.95697,0.11339]', 'core_[79.81463,69.10646,0.11494]', 'core_[79.81463,69.95697,0.11634]', 'core_[79.81463,69.95697,0.11354]', 'core_[79.81463,69.95697,0.1162]', 'core_[79.81463,69.95697,0.11368]', 'core_[79.81463,69.19151,0.11494]', 'core_[79.81463,69.95697,0.11607]', 'core_[79.81463,69.26805,0.11494]', 'core_[79.81463,69.95697,0.11381]', 'core_[79.81463,69.95697,0.11596]', 'core_[79.81463,69.95697,0.11392]', 'core_[79.81463,69.33695,0.11494]', 'core_[79.81463,69.95697,0.11586]', 'core_[79.81463,69.95697,0.11402]', 'core_[79.81463,69.39895,0.11494]', 'core_[79.81463,69.95697,0.11411]', 'core_[79.81463,69.45475,0.11494]', 'core_[79.81463,69.95697,0.11577]', 'core_[79.81463,69.95697,0.11568]', 'core_[79.81463,69.95697,0.1142]', 'core_[79.81463,69.50497,0.11494]', 'core_[79.81463,69.95697,0.11561]', 'core_[79.81463,69.55017,0.11494]', 'core_[79.81463,69.95697,0.11427]', 'core_[79.81463,69.59085,0.11494]', 'core_[79.81463,69.95697,0.11434]', 'core_[79.81463,69.95697,0.11554]', 'core_[79.81463,69.62746,0.11494]', 'core_[79.81463,69.95697,0.1144]', 'core_[79.81463,69.95697,0.11548]', 'core_[79.81463,69.95697,0.11543]', 'core_[79.81463,69.66041,0.11543]', 'core_[79.47629,69.95697,0.11543]', 'core_[79.81463,69.95697,0.11592]', 'core_[79.81463,69.69007,0.11543]', 'core_[79.51012,69.95697,0.11543]', 'core_[79.81463,69.95697,0.11499]', 'core_[79.81463,69.95697,0.11587]', 'core_[79.81463,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11542]', 'core_[79.81463,69.71676,0.11503]', 'core_[79.54057,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11464]', 'core_[79.56798,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11539]', 'core_[79.56798,69.95697,0.11539]', 'core_[79.81463,69.95697,0.11575]', 'core_[79.81463,69.95697,0.11571]', 'core_[79.81463,69.95697,0.11507]', 'core_[79.81463,69.7624,0.11507]', 'core_[79.81463,69.95697,0.11475]', 'core_[79.59264,69.95697,0.11507]', 'core_[79.81463,69.78186,0.11507]', 'core_[79.61484,69.95697,0.11507]', 'core_[79.81463,69.95697,0.11478]', 'core_[79.81463,69.95697,0.11536]', 'core_[79.61484,69.95697,0.11536]', 'core_[79.81463,69.95697,0.11565]', 'core_[79.63482,69.95697,0.11536]', 'core_[79.81463,69.95697,0.1151]', 'core_[79.81463,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11536]', 'core_[79.99444,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11588]', 'core_[79.99444,69.81513,0.11562]', 'core_[79.83225,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11585]', 'core_[79.99444,69.95697,0.11539]', 'core_[79.99444,69.95697,0.11583]', 'core_[79.99444,69.95697,0.11541]', 'core_[79.99444,69.82931,0.11541]', 'core_[79.99444,69.95697,0.1152]', 'core_[79.84847,69.95697,0.11541]', 'core_[79.99444,69.84208,0.11541]', 'core_[79.99444,69.95697,0.1156]', 'core_[79.86306,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11522]', 'core_[79.99444,69.95697,0.11524]', 'core_[79.8762,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11558]', 'core_[79.99444,69.85357,0.11541]', 'core_[79.88803,69.95697,0.11541]', 'core_[79.99444,69.86391,0.11541]', 'core_[79.99444,69.95697,0.11526]', 'core_[79.99444,69.95697,0.11556]', 'core_[79.99444,69.95697,0.11527]', 'core_[79.99444,69.95697,0.11555]', 'core_[79.99444,69.87321,0.11541]', 'core_[79.89867,69.95697,0.11541]', 'core_[79.90824,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11553]', 'core_[79.99444,69.95697,0.11529]', 'core_[79.99444,69.88159,0.11541]']
    
    assert sub_bb.get_blackboard()['level 100']['final']['hvi'] == 0.1221981715
    
    assert sub_bb.get_kaar() == {1: {'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0}, 2: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0}, 3: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0}, 4: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0}, 5: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0}, 6: {'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0}, 7: {'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.250001, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl3': 3.00000000001}, 8: {'ska_br_lvl3': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 0.500002, 'ska_rp_hc': 0, 'ska_rp_pert': 0, 'ska_br_lvl2': 4.00000000002}, 9: {'ska_br_inter': 6.00000000001, 'ska_rp_mc': 0.750003, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0}, 10: {'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.000004, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 5.00001}, 11: {'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.2500049999999998, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 0, 'ska_br_lvl3': 3.00000000001, 'ska_br_lvl2': 0}, 12: {'ska_rp_mc': 1.5000059999999997, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_br_lvl3': 30.600000000101996, 'ska_br_lvl2': 0}, 13: {'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.7500069999999996, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 0, 'ska_br_lvl3': 0, 'ska_br_lvl2': 97.200000000486}, 14: {'ska_rp_mc': 2.000008, 'ska_rp_hc': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 6.00000000003, 'ska_br_inter': 6.00000000001, 'ska_rp_pert': 5.00001}, 15: {'ska_br_inter': 6.00000000001, 'ska_rp_mc': 2.250009, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0}, 16: {'ska_rp_mc': 2.50001, 'ska_rp_hc': 5.00001, 'ska_rp_pert': 5.00001, 'ska_br_lvl3': 0, 'ska_br_lvl2': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0}}
    
    assert list(master_bb.get_blackboard()['level 3']['new'].keys()) == ['core_[70.11403,58.3461,0.55869]', 'core_[73.61973,58.3461,0.55869]', 'core_[70.11403,61.26341,0.55869]', 'core_[70.11403,58.3461,0.53076]', 'core_[69.41289,58.3461,0.55869]', 'core_[69.41289,64.18071,0.17533]', 'core_[77.12543,64.18071,0.11504]', 'core_[77.12543,64.18071,0.10354]', 'core_[77.12543,64.18071,0.10469]', 'core_[70.18414,69.95697,0.10469]', 'core_[77.12543,64.29046,0.11317]', 'core_[71.50299,69.95697,0.11317]', 'core_[77.12543,64.85711,0.11317]', 'core_[77.12543,65.36709,0.10574]', 'core_[72.06523,69.95697,0.10574]', 'core_[77.12543,65.82608,0.10574]', 'core_[77.12543,65.82608,0.11198]', 'core_[77.12543,66.23917,0.11198]', 'core_[73.02667,69.95697,0.11198]', 'core_[77.12543,66.61095,0.10662]', 'core_[77.12543,66.94555,0.11121]', 'core_[77.12543,67.24669,0.11121]', 'core_[77.12543,67.51772,0.10733]', 'core_[79.81463,69.95697,0.10733]', 'core_[79.81463,69.95697,0.10359]', 'core_[79.81463,67.51772,0.10733]', 'core_[79.81463,69.95697,0.11107]', 'core_[79.81463,69.95697,0.1072]', 'core_[79.81463,67.51772,0.11107]', 'core_[79.81463,69.95697,0.11494]', 'core_[79.81463,69.95697,0.11093]', 'core_[79.81463,67.51772,0.11494]', 'core_[79.81463,69.95697,0.11133]', 'core_[79.81463,67.76165,0.11494]', 'core_[79.81463,67.98118,0.11494]', 'core_[79.81463,69.95697,0.11819]', 'core_[79.81463,69.95697,0.11169]', 'core_[79.81463,69.95697,0.11786]', 'core_[79.81463,68.17876,0.11494]', 'core_[79.81463,69.95697,0.11202]', 'core_[79.81463,69.95697,0.11757]', 'core_[79.81463,68.35658,0.11494]', 'core_[79.81463,69.95697,0.11231]', 'core_[79.81463,69.95697,0.11257]', 'core_[79.81463,68.51662,0.11494]', 'core_[79.81463,69.95697,0.11731]', 'core_[79.81463,69.95697,0.11707]', 'core_[79.81463,69.95697,0.11281]', 'core_[79.81463,68.66065,0.11494]', 'core_[79.81463,69.95697,0.11302]', 'core_[79.81463,68.79028,0.11494]', 'core_[79.81463,69.95697,0.11686]', 'core_[79.81463,69.95697,0.11667]', 'core_[79.81463,68.90695,0.11494]', 'core_[79.81463,69.95697,0.11321]', 'core_[79.81463,69.95697,0.11649]', 'core_[79.81463,69.01196,0.11494]', 'core_[79.81463,69.95697,0.11339]', 'core_[79.81463,69.10646,0.11494]', 'core_[79.81463,69.95697,0.11634]', 'core_[79.81463,69.95697,0.11354]', 'core_[79.81463,69.95697,0.1162]', 'core_[79.81463,69.95697,0.11368]', 'core_[79.81463,69.19151,0.11494]', 'core_[79.81463,69.95697,0.11607]', 'core_[79.81463,69.26805,0.11494]', 'core_[79.81463,69.95697,0.11381]', 'core_[79.81463,69.95697,0.11596]', 'core_[79.81463,69.95697,0.11392]', 'core_[79.81463,69.33695,0.11494]', 'core_[79.81463,69.95697,0.11586]', 'core_[79.81463,69.95697,0.11402]', 'core_[79.81463,69.39895,0.11494]', 'core_[79.81463,69.95697,0.11411]', 'core_[79.81463,69.45475,0.11494]', 'core_[79.81463,69.95697,0.11577]', 'core_[79.81463,69.95697,0.11568]', 'core_[79.81463,69.95697,0.1142]', 'core_[79.81463,69.50497,0.11494]', 'core_[79.81463,69.95697,0.11561]', 'core_[79.81463,69.55017,0.11494]', 'core_[79.81463,69.95697,0.11427]', 'core_[79.81463,69.59085,0.11494]', 'core_[79.81463,69.95697,0.11434]', 'core_[79.81463,69.95697,0.11554]', 'core_[79.81463,69.62746,0.11494]', 'core_[79.81463,69.95697,0.1144]', 'core_[79.81463,69.95697,0.11548]', 'core_[79.81463,69.95697,0.11543]', 'core_[79.81463,69.66041,0.11543]', 'core_[79.47629,69.95697,0.11543]', 'core_[79.81463,69.95697,0.11592]', 'core_[79.81463,69.69007,0.11543]', 'core_[79.51012,69.95697,0.11543]', 'core_[79.81463,69.95697,0.11499]', 'core_[79.81463,69.95697,0.11587]', 'core_[79.81463,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11542]', 'core_[79.81463,69.71676,0.11503]', 'core_[79.54057,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11464]', 'core_[79.56798,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11539]', 'core_[79.56798,69.95697,0.11539]', 'core_[79.81463,69.95697,0.11575]', 'core_[79.81463,69.95697,0.11571]', 'core_[79.81463,69.95697,0.11507]', 'core_[79.81463,69.7624,0.11507]', 'core_[79.81463,69.95697,0.11475]', 'core_[79.59264,69.95697,0.11507]', 'core_[79.81463,69.78186,0.11507]', 'core_[79.61484,69.95697,0.11507]', 'core_[79.81463,69.95697,0.11478]', 'core_[79.81463,69.95697,0.11536]', 'core_[79.61484,69.95697,0.11536]', 'core_[79.81463,69.95697,0.11565]', 'core_[79.63482,69.95697,0.11536]', 'core_[79.81463,69.95697,0.1151]', 'core_[79.81463,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11536]', 'core_[79.99444,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11588]', 'core_[79.99444,69.81513,0.11562]', 'core_[79.83225,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11585]', 'core_[79.99444,69.95697,0.11539]', 'core_[79.99444,69.95697,0.11583]', 'core_[79.99444,69.95697,0.11541]', 'core_[79.99444,69.82931,0.11541]', 'core_[79.99444,69.95697,0.1152]', 'core_[79.84847,69.95697,0.11541]', 'core_[79.99444,69.84208,0.11541]', 'core_[79.99444,69.95697,0.1156]', 'core_[79.86306,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11522]', 'core_[79.99444,69.95697,0.11524]', 'core_[79.8762,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11558]', 'core_[79.99444,69.85357,0.11541]', 'core_[79.88803,69.95697,0.11541]', 'core_[79.99444,69.86391,0.11541]', 'core_[79.99444,69.95697,0.11526]', 'core_[79.99444,69.95697,0.11556]', 'core_[79.99444,69.95697,0.11527]', 'core_[79.99444,69.95697,0.11555]', 'core_[79.99444,69.87321,0.11541]', 'core_[79.89867,69.95697,0.11541]', 'core_[79.90824,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11553]', 'core_[79.99444,69.95697,0.11529]', 'core_[79.99444,69.88159,0.11541]']
    
    os.remove('bb_sub.h5')
    mtc.shutdown()
    time.sleep(0.05)    

def test_MTC_run_master_bb():    
    try:
        mtc = controller.Multi_Tiered_Controller()
    except OSError:
        mtc = controller.Multi_Tiered_Controller()

    kas = {'mka_rp_mc': {'type': karp.KaGlobal},
          'mka_rp_hc': {'type': karp.KaLocalHC},
          'mka_rp_pert': {'type': karp.KaLocal},
          'mka_br_lvl3': {'type': kabr.KaBr_lvl3},
          'mka_br_lvl2': {'type': kabr.KaBr_lvl2},
          'mka_br_lvl1': {'type': kabr.KaBr_lvl1}}
    
    mtc.initialize_blackboard('master_bb', bb_name='bb_master', 
                              bb_type=bb_opt.MasterBbOpt, 
                              ka=kas, 
                              archive='bb_master', 
                              total_tvs=50,
                              skipped_tvs=1,
                              convergence_type='hvi',
                              convergence_rate=0.5,
                              convergence_interval=5,
                              pf_size=5, 
                              random_seed=1)
    
    master_bb = mtc.master_bb
    master_bb.set_attr(skipped_tvs=0)
    kas = {'ska_rp_mc': {'type': karp.KaGlobal}, 
           'ska_rp_hc': {'type': karp.KaLocalHC},
           'ska_rp_pert': {'type': karp.KaLocal},
           'ska_br_lvl3': {'type': kabr.KaBr_lvl3},
           'ska_br_lvl2': {'type': kabr.KaBr_lvl2},
           'ska_br_lvl1': {'type': kabr.KaBr_lvl1},
           'ska_br_inter': {'type': kabr.KaBr_interBB, 'attr':{'bb': master_bb}}}
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', 
                              bb_type=bb_opt.SubBbOpt, 
                              ka=kas,  
                              archive='bb_sub', 
                              total_tvs=50,
                              skipped_tvs=1,
                              convergence_type='hvi',
                              convergence_rate=0.04,
                              convergence_interval=8,
                              pf_size=5, 
                              random_seed=1)
    
    sub_bb = mtc.sub_bb
    sub_bb.set_attr(skipped_tvs=0)
        
    mtc.run_sub_bb(sub_bb)
    
    assert list(master_bb.get_blackboard()['level 3']['new'].keys()) == ['core_[70.11403,58.3461,0.55869]', 'core_[73.61973,58.3461,0.55869]', 'core_[70.11403,61.26341,0.55869]', 'core_[70.11403,58.3461,0.53076]', 'core_[69.41289,58.3461,0.55869]', 'core_[69.41289,64.18071,0.17533]', 'core_[77.12543,64.18071,0.11504]', 'core_[77.12543,64.18071,0.10354]', 'core_[77.12543,64.18071,0.10469]', 'core_[70.18414,69.95697,0.10469]', 'core_[77.12543,64.29046,0.11317]', 'core_[71.50299,69.95697,0.11317]', 'core_[77.12543,64.85711,0.11317]', 'core_[77.12543,65.36709,0.10574]', 'core_[72.06523,69.95697,0.10574]', 'core_[77.12543,65.82608,0.10574]', 'core_[77.12543,65.82608,0.11198]', 'core_[77.12543,66.23917,0.11198]', 'core_[73.02667,69.95697,0.11198]', 'core_[77.12543,66.61095,0.10662]', 'core_[77.12543,66.94555,0.11121]', 'core_[77.12543,67.24669,0.11121]', 'core_[77.12543,67.51772,0.10733]', 'core_[79.81463,69.95697,0.10733]', 'core_[79.81463,69.95697,0.10359]', 'core_[79.81463,67.51772,0.10733]', 'core_[79.81463,69.95697,0.11107]', 'core_[79.81463,69.95697,0.1072]', 'core_[79.81463,67.51772,0.11107]', 'core_[79.81463,69.95697,0.11494]', 'core_[79.81463,69.95697,0.11093]', 'core_[79.81463,67.51772,0.11494]', 'core_[79.81463,69.95697,0.11133]', 'core_[79.81463,67.76165,0.11494]', 'core_[79.81463,67.98118,0.11494]', 'core_[79.81463,69.95697,0.11819]', 'core_[79.81463,69.95697,0.11169]', 'core_[79.81463,69.95697,0.11786]', 'core_[79.81463,68.17876,0.11494]', 'core_[79.81463,69.95697,0.11202]', 'core_[79.81463,69.95697,0.11757]', 'core_[79.81463,68.35658,0.11494]', 'core_[79.81463,69.95697,0.11231]', 'core_[79.81463,69.95697,0.11257]', 'core_[79.81463,68.51662,0.11494]', 'core_[79.81463,69.95697,0.11731]', 'core_[79.81463,69.95697,0.11707]', 'core_[79.81463,69.95697,0.11281]', 'core_[79.81463,68.66065,0.11494]', 'core_[79.81463,69.95697,0.11302]', 'core_[79.81463,68.79028,0.11494]', 'core_[79.81463,69.95697,0.11686]', 'core_[79.81463,69.95697,0.11667]', 'core_[79.81463,68.90695,0.11494]', 'core_[79.81463,69.95697,0.11321]', 'core_[79.81463,69.95697,0.11649]', 'core_[79.81463,69.01196,0.11494]', 'core_[79.81463,69.95697,0.11339]', 'core_[79.81463,69.10646,0.11494]', 'core_[79.81463,69.95697,0.11634]', 'core_[79.81463,69.95697,0.11354]', 'core_[79.81463,69.95697,0.1162]', 'core_[79.81463,69.95697,0.11368]', 'core_[79.81463,69.19151,0.11494]', 'core_[79.81463,69.95697,0.11607]', 'core_[79.81463,69.26805,0.11494]', 'core_[79.81463,69.95697,0.11381]', 'core_[79.81463,69.95697,0.11596]', 'core_[79.81463,69.95697,0.11392]', 'core_[79.81463,69.33695,0.11494]', 'core_[79.81463,69.95697,0.11586]', 'core_[79.81463,69.95697,0.11402]', 'core_[79.81463,69.39895,0.11494]', 'core_[79.81463,69.95697,0.11411]', 'core_[79.81463,69.45475,0.11494]', 'core_[79.81463,69.95697,0.11577]', 'core_[79.81463,69.95697,0.11568]', 'core_[79.81463,69.95697,0.1142]', 'core_[79.81463,69.50497,0.11494]', 'core_[79.81463,69.95697,0.11561]', 'core_[79.81463,69.55017,0.11494]', 'core_[79.81463,69.95697,0.11427]', 'core_[79.81463,69.59085,0.11494]', 'core_[79.81463,69.95697,0.11434]', 'core_[79.81463,69.95697,0.11554]', 'core_[79.81463,69.62746,0.11494]', 'core_[79.81463,69.95697,0.1144]', 'core_[79.81463,69.95697,0.11548]', 'core_[79.81463,69.95697,0.11543]', 'core_[79.81463,69.66041,0.11543]', 'core_[79.47629,69.95697,0.11543]', 'core_[79.81463,69.95697,0.11592]', 'core_[79.81463,69.69007,0.11543]', 'core_[79.51012,69.95697,0.11543]', 'core_[79.81463,69.95697,0.11499]', 'core_[79.81463,69.95697,0.11587]', 'core_[79.81463,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11542]', 'core_[79.81463,69.71676,0.11503]', 'core_[79.54057,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11464]', 'core_[79.56798,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11539]', 'core_[79.56798,69.95697,0.11539]', 'core_[79.81463,69.95697,0.11575]', 'core_[79.81463,69.95697,0.11571]', 'core_[79.81463,69.95697,0.11507]', 'core_[79.81463,69.7624,0.11507]', 'core_[79.81463,69.95697,0.11475]', 'core_[79.59264,69.95697,0.11507]', 'core_[79.81463,69.78186,0.11507]', 'core_[79.61484,69.95697,0.11507]', 'core_[79.81463,69.95697,0.11478]', 'core_[79.81463,69.95697,0.11536]', 'core_[79.61484,69.95697,0.11536]', 'core_[79.81463,69.95697,0.11565]', 'core_[79.63482,69.95697,0.11536]', 'core_[79.81463,69.95697,0.1151]', 'core_[79.81463,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11536]', 'core_[79.99444,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11588]', 'core_[79.99444,69.81513,0.11562]', 'core_[79.83225,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11585]', 'core_[79.99444,69.95697,0.11539]', 'core_[79.99444,69.95697,0.11583]', 'core_[79.99444,69.95697,0.11541]', 'core_[79.99444,69.82931,0.11541]', 'core_[79.99444,69.95697,0.1152]', 'core_[79.84847,69.95697,0.11541]', 'core_[79.99444,69.84208,0.11541]', 'core_[79.99444,69.95697,0.1156]', 'core_[79.86306,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11522]', 'core_[79.99444,69.95697,0.11524]', 'core_[79.8762,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11558]', 'core_[79.99444,69.85357,0.11541]', 'core_[79.88803,69.95697,0.11541]', 'core_[79.99444,69.86391,0.11541]', 'core_[79.99444,69.95697,0.11526]', 'core_[79.99444,69.95697,0.11556]', 'core_[79.99444,69.95697,0.11527]', 'core_[79.99444,69.95697,0.11555]', 'core_[79.99444,69.87321,0.11541]', 'core_[79.89867,69.95697,0.11541]', 'core_[79.90824,69.95697,0.11541]', 'core_[79.99444,69.95697,0.11553]', 'core_[79.99444,69.95697,0.11529]', 'core_[79.99444,69.88159,0.11541]']
    
    mtc.run_sub_bb(master_bb)

    assert list(master_bb.get_blackboard()['level 1'].keys()) == ['core_[79.81463,69.95697,0.10733]', 'core_[79.81463,69.95697,0.10359]', 'core_[79.81463,69.95697,0.11107]', 'core_[79.81463,69.95697,0.1072]', 'core_[79.81463,69.95697,0.11494]', 'core_[79.81463,69.95697,0.11093]', 'core_[79.81463,69.95697,0.11133]', 'core_[79.81463,69.95697,0.11819]', 'core_[79.81463,69.95697,0.11169]', 'core_[79.81463,69.95697,0.11786]', 'core_[79.81463,69.95697,0.11202]', 'core_[79.81463,69.95697,0.11757]', 'core_[79.81463,69.95697,0.11231]', 'core_[79.81463,69.95697,0.11257]', 'core_[79.81463,69.95697,0.11731]', 'core_[79.81463,69.95697,0.11281]', 'core_[79.81463,69.95697,0.11302]', 'core_[79.81463,69.95697,0.11321]', 'core_[79.81463,69.95697,0.11339]', 'core_[79.81463,69.95697,0.11354]', 'core_[79.81463,69.95697,0.11368]', 'core_[79.81463,69.95697,0.11381]', 'core_[79.81463,69.95697,0.11392]', 'core_[79.81463,69.95697,0.11402]', 'core_[79.81463,69.95697,0.11411]', 'core_[79.81463,69.95697,0.1142]', 'core_[79.81463,69.95697,0.11427]', 'core_[79.81463,69.95697,0.11434]', 'core_[79.81463,69.95697,0.1144]', 'core_[79.81463,69.95697,0.11543]', 'core_[79.81463,69.95697,0.11499]', 'core_[79.81463,69.95697,0.11503]', 'core_[79.81463,69.95697,0.11542]', 'core_[79.81463,69.95697,0.11464]', 'core_[79.81463,69.95697,0.11539]', 'core_[79.81463,69.95697,0.11507]', 'core_[79.81463,69.95697,0.11475]', 'core_[79.81463,69.95697,0.11478]', 'core_[79.81463,69.95697,0.11536]', 'core_[79.81463,69.95697,0.1151]', 'core_[79.99444,69.95697,0.11536]', 'core_[79.99444,69.95697,0.11562]', 'core_[79.99444,69.95697,0.11588]', 'core_[79.99444,69.95697,0.11585]', 'core_[79.99444,69.95697,0.11539]', 'core_[79.99444,69.95697,0.11583]', 'core_[79.99444,69.95697,0.11541]', 'core_[79.99444,69.95697,0.1152]', 'core_[79.99444,69.95697,0.1156]', 'core_[79.99444,69.95697,0.11522]', 'core_[79.99444,69.95697,0.11524]', 'core_[79.99444,69.95697,0.11558]', 'core_[79.99444,69.95697,0.11526]', 'core_[79.99444,69.95697,0.11555]', 'core_[79.99444,69.95697,0.11553]', 'core_[79.99444,69.95697,0.11529]', 'core_[79.81463,69.95697,0.10576]', 'core_[79.81463,69.95697,0.09841]', 'core_[79.81463,69.95697,0.10877]', 'core_[79.81463,69.95697,0.12246]', 'core_[79.81463,69.95697,0.1002]', 'core_[79.81463,69.95697,0.11022]', 'core_[79.81463,69.95697,0.09018]', 'core_[79.81463,69.95697,0.08116]', 'core_[79.81463,69.95697,0.08928]', 'core_[79.81463,69.95697,0.07304]', 'core_[79.81463,69.95697,0.08034]', 'core_[79.81463,69.95697,0.06574]', 'core_[79.81463,69.95697,0.07231]', 'core_[79.81463,69.95697,0.05917]', 'core_[79.81463,69.95697,0.05325]', 'core_[79.81463,69.95697,0.04792]', 'core_[79.81463,69.95697,0.05271]', 'core_[79.81463,69.95697,0.04313]', 'core_[79.81463,69.95697,0.03882]', 'core_[79.81463,69.95697,0.03494]', 'core_[79.81463,69.95697,0.03843]', 'core_[79.81463,69.95697,0.03145]', 'core_[79.81463,69.95697,0.0283]', 'core_[79.81463,69.95697,0.02547]', 'core_[79.81463,69.95697,0.02292]', 'core_[79.81463,69.95697,0.02521]', 'core_[79.81463,69.95697,0.02063]', 'core_[79.81463,69.95697,0.01857]', 'core_[79.81463,69.95697,0.02043]', 'core_[79.81463,69.95697,0.01671]', 'core_[79.81463,69.95697,0.01654]', 'core_[79.81463,69.95697,0.01639]', 'core_[79.81463,69.95697,0.01626]', 'core_[79.81463,69.95697,0.01614]', 'core_[79.81463,69.95697,0.01603]', 'core_[79.81463,69.95697,0.01593]', 'core_[79.81463,69.95697,0.01584]', 'core_[79.81463,69.95697,0.01576]', 'core_[79.81463,69.95697,0.01569]', 'core_[79.99444,69.95697,0.01434]', 'core_[79.99444,69.95697,0.01431]', 'core_[79.99444,69.95697,0.01428]', 'core_[79.99444,69.95697,0.01425]', 'core_[79.99444,69.95697,0.01422]', 'core_[79.99444,69.95697,0.01419]', 'core_[79.99444,69.95697,0.01416]', 'core_[79.99444,69.95697,0.01413]', 'core_[79.99444,69.95697,0.0141]', 'core_[79.99444,69.95697,0.01407]', 'core_[79.99444,69.95697,0.01404]', 'core_[79.99444,69.95697,0.01401]', 'core_[79.99444,69.95697,0.01398]', 'core_[79.99444,69.95697,0.01395]', 'core_[79.99444,69.95697,0.01392]', 'core_[79.99444,69.95697,0.01389]', 'core_[79.99444,69.95697,0.01386]', 'core_[79.99444,69.95697,0.01383]', 'core_[79.99444,69.95697,0.0138]', 'core_[79.99444,69.95697,0.01377]', 'core_[79.99444,69.95697,0.01374]', 'core_[79.99444,69.95697,0.01371]', 'core_[79.99444,69.95697,0.01368]', 'core_[79.99444,69.95697,0.01365]', 'core_[79.99444,69.95697,0.01362]', 'core_[79.99444,69.95697,0.01359]', 'core_[79.99444,69.95697,0.01356]', 'core_[79.99444,69.95697,0.01361]', 'core_[79.99444,69.95697,0.01358]']

    assert master_bb.get_kaar() == {1: {'mka_rp_hc': 0, 'mka_rp_pert': 0, 'mka_rp_mc': 0.250001, 'mka_br_lvl3': 18.1200000000604, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0}, 2: {'mka_rp_pert': 0, 'mka_br_lvl3': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 0.500002, 'mka_rp_hc': 0, 'mka_br_lvl2': 60.400000000302}, 3: {'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl1': 6.00000000003, 'mka_rp_mc': 0.750003, 'mka_br_lvl2': 0}, 4: {'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 1.000004, 'mka_rp_hc': 5.00001, 'mka_br_lvl2': 0}, 5: {'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 1.2500049999999998, 'mka_br_lvl3': 3.00000000001}, 6: {'mka_br_lvl3': 3.00000000001, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 1.5000059999999997, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001}, 7: {'mka_rp_hc': 5.00001, 'mka_rp_mc': 1.7500069999999996, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 33.7200000001124, 'mka_br_lvl1': 0, 'mka_br_lvl2': 0}, 8: {'mka_rp_mc': 2.000008, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl1': 0, 'mka_br_lvl2': 46.00000000023}, 9: {'mka_br_lvl1': 6.00000000003, 'mka_rp_mc': 2.250009, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 0, 'mka_br_lvl2': 0}, 10: {'mka_br_lvl3': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 2.50001, 'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl2': 0}}
    os.remove('bb_sub.h5')
    os.remove('bb_master.h5')
    
    mtc.shutdown()
    time.sleep(0.05) 

