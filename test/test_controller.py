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
    obj = {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    dv = {'height':     {'ll': 60.0, 'ul': 80.0, 'variable type': float},
          'smear':      {'ll': 70.0, 'ul': 70.0, 'variable type': float},
          'pu_content': {'ll': 0.5,  'ul': 1.0,  'variable type': float}}
    const = {'eol keff':    {'ll': 1.1, 'ul': 2.5, 'variable type': float}}
    conv_model = {'type': 'dci hvi', 'convergence rate': 1E-6, 'div': {'reactivity swing': 100, 'burnup': 100}}
    bb_controller = controller.Controller(bb_name='sfr_opt', 
                                          bb_type=bb_opt.BbOpt, 
                                          ka=kas, 
                                          design_variables=dv,
                                          objectives=obj,
                                          constraints=const,
                                          archive='sfr_opt', 
                                          agent_wait_time=10,
                                          plot_progress = True,
                                          progress_rate = 50,
                                          convergence_model = conv_model,
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'})
    with open('./sm_gpr.pkl', 'rb') as pickle_file:
        sm_gpr = pickle.load(pickle_file)
    
    assert bb_controller.bb_name == 'sfr_opt'
    assert bb_controller.bb_type == bb_opt.BbOpt
    assert bb_controller.agent_wait_time == 10
    assert bb_controller.plot_progress == True
    assert bb_controller.progress_rate == 50   

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
    bb_controller = controller.Controller(bb_name='sfr_opt', 
                                          bb_type=bb_opt.BbOpt, 
                                          ka=kas, 
                                          archive='sfr_opt', 
                                          agent_wait_time=5,
                                          progress_rate=1,
                                          surrogate_model={'sm_type'     : 'gpr', 
                                                           'pickle file' : './sm_gpr.pkl'})

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
