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
    lvls = bb_controller.bb.get_attr('abstract_lvls')

    assert [x for x in lvls['level 1']] == ['core_[70.96687, 64.49033, 0.18643]', 'core_[78.43707, 64.49033, 0.18643]', 'core_[74.70197, 61.26581, 0.18643]', 'core_[74.70197, 67.71485, 0.18643]', 'core_[74.70197, 64.49033, 0.17711]', 'core_[74.51522, 64.49033, 0.19624]', 'core_[78.43707, 61.26581, 0.19624]', 'core_[78.43707, 67.71485, 0.19624]', 'core_[70.96687, 67.71485, 0.19624]', 'core_[74.70197, 64.32911, 0.19624]', 'core_[67.41853, 64.49033, 0.19624]', 'core_[74.51521, 64.49033, 0.19624]', 'core_[74.70197, 64.3291, 0.19624]', 'core_[76.62379, 61.44685, 0.12881]']
    assert len([x for x in lvls['level 2']['new']]) == 0
    assert len([x for x in lvls['level 2']['old']]) == 26
    assert len([x for x in lvls['level 3']['new']]) == 38
    assert len([x for x in lvls['level 3']['old']]) == 28
    
    assert bb_controller.bb.get_attr('hv_list') == [0.0, 0.0, 0.0, 0.0, 0.0, 0.05335896864304055, 0.05335896864304055, 0.05335896864304055, 0.05335896864304055, 0.05335896864304055, 0.06442559991558683, 0.06442559991558683, 0.06442559991558683, 0.06442559991558683, 0.06442559991558683, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789, 0.07758427453681789]
    assert bb_controller.bb.get_attr('_kaar') == {1: {'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_br_lvl3': 0}, 2: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 3: {'ka_br_lvl2': 4.00000000002, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0}, 4: {'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001}, 5: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.000004, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001}, 6: {'ka_br_lvl1': 0, 'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 4.00000000002}, 7: {'ka_br_lvl1': 6.00000000003, 'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0}, 8: {'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0}, 9: {'ka_br_lvl3': 3.00000000001, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.000008, 'ka_rp_exploit': 5.00001, 'ka_br_lvl2': 0}, 10: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.250009, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 11: {'ka_br_lvl1': 0, 'ka_rp_explore': 2.50001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 12: {'ka_rp_explore': 2.750011, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 13: {'ka_rp_explore': 3.0000120000000003, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 14: {'ka_br_lvl1': 0, 'ka_rp_explore': 0.250001, 'ka_rp_exploit': 0, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0}, 15: {'ka_rp_explore': 0.500002, 'ka_rp_exploit': 0, 'ka_br_lvl3': 0, 'ka_br_lvl2': 5.00000000002, 'ka_br_lvl1': 0}, 16: {'ka_rp_explore': 0.750003, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 6.00000000003}, 17: {'ka_rp_explore': 1.000004, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 0, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 18: {'ka_rp_explore': 1.2500049999999998, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 19: {'ka_rp_explore': 1.5000059999999997, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 20: {'ka_rp_explore': 1.7500069999999996, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 21: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 3.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.000008}, 22: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 4.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.250009}, 23: {'ka_rp_explore': 2.50001, 'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 4.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0}, 24: {'ka_br_lvl3': 4.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 2.750011, 'ka_rp_exploit': 5.00001}, 25: {'ka_rp_exploit': 5.00001, 'ka_br_lvl3': 4.00000000001, 'ka_br_lvl2': 0, 'ka_br_lvl1': 0, 'ka_rp_explore': 3.0000120000000003}}
    assert bb_controller.bb.get_attr('_complete') == True
    bb_controller.shutdown()
    os.remove('sfr_opt.h5')
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
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', bb_type=bb_opt.SubBbOpt, ka=kas,  archive='bb_sub', convergence_model={'type': 'hvi', 'convergence rate': 0.5, 'interval': 5, 'pf size': 5, 'total tvs': 50}, random_seed=1)
    
    sub_bb = mtc.sub_bb
    
    mtc.run_sub_bb(sub_bb)
    
    assert list(sub_bb.get_attr('abstract_lvls')['level 1']) == ['core_[66.24237, 65.34383, 0.3812]', 'core_[65.91157, 64.85498, 0.36214]', 'core_[69.20715, 64.85498, 0.36214]', 'core_[72.48584, 64.69284, 0.36214]', 'core_[68.86155, 64.69284, 0.36214]', 'core_[68.86155, 61.4582, 0.36214]', 'core_[72.30463, 61.4582, 0.32683]', 'core_[72.30463, 64.53111, 0.32683]', 'core_[78.92167, 66.91492, 0.16778]', 'core_[78.72437, 66.91492, 0.13666]', 'core_[74.78815, 66.91492, 0.13666]', 'core_[71.04874, 66.91492, 0.13666]', 'core_[71.04874, 63.56917, 0.13666]']
    assert sub_bb.get_attr('abstract_lvls')['level 100']['final']['hvi'] == 0.09250101486016733
    assert sub_bb.get_attr('_kaar')[14] == {'ska_br_lvl3': 0, 'ska_br_lvl1': 0, 'ska_br_inter': 0, 'ska_rp_mc': 1.5000059999999997, 'ska_rp_hc': 0, 'ska_rp_pert': 5.00001, 'ska_br_lvl2': 10.00000000002}

    assert master_bb.get_attr('abstract_lvls')['level 3']['new'] == {'core_[66.24237, 68.78298, 0.3812]': {'design variables': {'height': 66.24237, 'smear': 68.78298, 'pu_content': 0.3812}, 'objective functions': {'eol keff': 1.0693, 'pu mass': 577.24453}, 'constraints': {'reactivity swing': 620.80003, 'burnup': 54.98791}}}
        
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
        
    mtc.initialize_blackboard('sub_bb', bb_name='bb_sub', bb_type=bb_opt.SubBbOpt, ka=kas,  archive='bb_sub', convergence_model={'type': 'hvi', 'convergence rate': 0.5, 'interval': 5, 'pf size': 5, 'total tvs': 50}, random_seed=1)
    
    sub_bb = mtc.sub_bb
    
    mtc.run_sub_bb(sub_bb)
    assert master_bb.get_attr('abstract_lvls')['level 3']['new'] == {'core_[66.24237, 68.78298, 0.3812]': {'design variables': {'height': 66.24237, 'smear': 68.78298, 'pu_content': 0.3812}, 'objective functions': {'eol keff': 1.0693, 'pu mass': 577.24453}, 'constraints': { 'reactivity swing': 620.80003, 'burnup': 54.98791}}}
        
    mtc.run_sub_bb(master_bb)
    assert list(master_bb.get_attr('abstract_lvls')['level 1']) == ['core_[69.55449, 68.78298, 0.3812]', 'core_[66.24237, 68.78298, 0.36214]', 'core_[69.55449, 68.61102, 0.3812]', 'core_[69.55449, 68.61102, 0.36214]', 'core_[69.55449, 68.61102, 0.38025]', 'core_[72.30463, 68.2684, 0.37647]', 'core_[72.30463, 68.2684, 0.39529]', 'core_[72.30463, 68.2684, 0.41505]', 'core_[71.94356, 68.09773, 0.4358]', 'core_[71.94356, 68.09773, 0.41401]', 'core_[71.94356, 68.09773, 0.39331]', 'core_[71.58429, 68.09773, 0.41298]', 'core_[68.00508, 67.75767, 0.37178]', 'core_[71.40533, 64.36979, 0.35231]', 'core_[71.40533, 61.1513, 0.35231]', 'core_[74.9756, 61.1513, 0.35231]', 'core_[74.9756, 60.99842, 0.35231]', 'core_[71.22682, 60.99842, 0.35231]', 'core_[67.66548, 60.99842, 0.35231]', 'core_[67.66548, 60.99842, 0.33469]']

    assert master_bb.get_attr('_kaar')[9] == {'mka_rp_hc': 5.00001, 'mka_rp_pert': 5.00001, 'mka_br_lvl3': 3.00000000001, 'mka_br_lvl2': 0, 'mka_br_lvl1': 0, 'mka_rp_mc': 2.250009}
    
    mtc.shutdown()
    time.sleep(0.05) 