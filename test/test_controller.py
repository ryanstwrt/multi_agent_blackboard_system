import src.controller as controller
import src.blackboard as blackboard
import src.bb_opt as bb_opt
import src.ka_rp as ka_rp
import src.ka_br as ka_br
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
    kas = {'ka_rp_explore': ka_rp.KaGlobal, 
           'ka_rp_exploit': ka_rp.KaLocal,
           'ka_br_lvl3': ka_br.KaBr_lvl3,
           'ka_br_lvl2': ka_br.KaBr_lvl2}
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
    kas = {'ka_rp_explore': ka_rp.KaGlobal, 
           'ka_rp_exploit': ka_rp.KaLocal,
           'ka_br_lvl3': ka_br.KaBr_lvl3,
           'ka_br_lvl2': ka_br.KaBr_lvl2,
           'ka_br_lvl1': ka_br.KaBr_lvl1,}
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
    
