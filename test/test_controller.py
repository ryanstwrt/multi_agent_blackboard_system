import controller
import blackboard
import bb_opt
import ka_rp
import ka_br
import time
import os
import pickle

def test_controller_init():
    bb_controller = controller.Controller()
    assert bb_controller.bb_name == 'bb'
    assert bb_controller.bb_type == blackboard.Blackboard
    assert bb_controller.agent_wait_time == 30
    bb_controller._ns.shutdown()
    time.sleep(0.05)
    
def test_controller_init_sfr_opt():
    kas = {'ka_rp_explore': ka_rp.KaGlobal, 
           'ka_rp_exploit': ka_rp.KaLocal,
           'ka_br_lvl3': ka_br.KaBr_lvl3,
           'ka_br_lvl2': ka_br.KaBr_lvl2}
    bb_controller = controller.Controller(bb_name='sfr_opt', 
                                          bb_type=bb_opt.BbOpt, 
                                          ka=kas, 
                                          archive='sfr_opt', 
                                          agent_wait_time=10,
                                          plot_progress = True,
                                          progress_rate = 50,
                                          surrogate_model={'sm_type'     : 'lr', 
                                                           'pickle file' : 'test/sm_lr_2obj.pkl'})
    with open('test/sm_lr_2obj.pkl', 'rb') as pickle_file:
        sm_lr = pickle.load(pickle_file)
    
    assert bb_controller.bb_name == 'sfr_opt'
    assert bb_controller.bb_type == bb_opt.BbOpt
    assert bb_controller.agent_wait_time == 10
    assert bb_controller.plot_progress == True
    assert bb_controller.progress_rate == 50   

    agents =  bb_controller.bb.get_attr('agent_addrs')
    assert [x for x in agents.keys()] == ['ka_rp_explore', 'ka_rp_exploit', 'ka_br_lvl3', 'ka_br_lvl2']
    assert bb_controller.bb.get_attr('sm_type') == 'lr'
    assert type(bb_controller.bb.get_attr('_sm')) == type(sm_lr)
    assert bb_controller.bb.get_attr('archive_name') == 'sfr_opt.h5'
    
    bb_controller._ns.shutdown()
    time.sleep(0.05)
    
def test_run_single_agent_bb():
    kas = {'ka_rp_explore': ka_rp.KaGlobal, 
           'ka_rp_exploit': ka_rp.KaLocal,
           'ka_br_lvl3': ka_br.KaBr_lvl3,
           'ka_br_lvl2': ka_br.KaBr_lvl2,
           'ka_br_lvl1': ka_br.KaBr_lvl1,}
    bb_controller = controller.Controller(bb_name='sfr_opt', 
                                          bb_type=bb_opt.BbOpt, 
                                          ka=kas, 
                                          archive='sfr_opt', 
                                          agent_wait_time=5,
                                          progress_rate=1,
                                          surrogate_model={'sm_type'     : 'lr', 
                                                           'pickle file' : 'test/sm_lr_4obj.pkl'})

    bb_controller.bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                                       'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    bb_controller.bb.update_abstract_lvl(1, 'core_1', {'pareto type' : 'pareto', 'fitness function': 1.0})    
    bb_controller.bb.set_attr(hv_convergence=1)
    bb_controller.bb.set_attr(num_calls=1)
    bb_controller.bb.set_attr(total_solutions=1)
    bb_controller.bb.set_attr(hv_list=[0.6,0.6])
    bb_controller.run_single_agent_bb()
    assert bb_controller.bb.get_attr('_complete') == True
    bb_controller.shutdown()
    os.remove('sfr_opt.h5')
    time.sleep(0.05)
