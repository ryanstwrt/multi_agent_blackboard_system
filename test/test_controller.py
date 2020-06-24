import controller
import blackboard
import bb_sfr_opt as bb_sfr
import ka_rp
import ka_br
import time
import os

def test_controller_init():
    bb_controller = controller.Controller()
    assert bb_controller.bb_name == 'bb'
    assert bb_controller.bb_type == blackboard.Blackboard
    assert bb_controller.agent_wait_time == 30
    bb_controller.ns.shutdown()
    time.sleep(0.1)
    
def test_controller_init_sfr_opt():
    kas = {'ka_rp_explore': ka_rp.KaRpExplore, 
           'ka_rp_exploit': ka_rp.KaRpExploit,
           'ka_br_lvl3': ka_br.KaBr_lvl3,
           'ka_br_lvl2': ka_br.KaBr_lvl2}
    bb_controller = controller.Controller(bb_name='sfr_opt', bb_type=bb_sfr.BbSfrOpt, ka=kas, archive='sfr_opt', agent_wait_time=10)
    assert bb_controller.bb_name == 'sfr_opt'
    assert bb_controller.bb_type == bb_sfr.BbSfrOpt
    assert bb_controller.agent_wait_time == 10

    assert bb_controller.bb.get_attr('archive_name') == 'sfr_opt.h5'
    agents =  bb_controller.bb.get_attr('agent_addrs')
    assert [x for x in agents.keys()] == ['ka_rp_explore', 'ka_rp_exploit', 'ka_br_lvl3', 'ka_br_lvl2']
    
    bb_controller.ns.shutdown()
    time.sleep(0.1)
    
def test_run_single_agent_bb():
    kas = {'ka_rp_explore': ka_rp.KaRpExplore, 
           'ka_rp_exploit': ka_rp.KaRpExploit,
           'ka_br_lvl3': ka_br.KaBr_lvl3,
           'ka_br_lvl2': ka_br.KaBr_lvl2}
    bb_controller = controller.Controller(bb_name='sfr_opt', bb_type=bb_sfr.BbSfrOpt, ka=kas, archive='sfr_opt', agent_wait_time=10)

    bb_controller.bb.set_attr(total_solutions=0)
    bb_controller.bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 
                                                                'pu_content': 0.4, 'cycle length': 365.0, 
                                                                'pu mass': 500.0, 'reactivity swing' : 600.0,
                                                                'burnup' : 50.0}}, panel='old')
    bb_controller.bb.update_abstract_lvl(1, 'core_1', {'pareto type' : 'pareto', 'fitness function': 1.0}, panel='new')    
    bb_controller.run_single_agent_bb()
    time.sleep(10)
    assert bb_controller.bb.get_attr('_complete') == True
    bb_controller.ns.shutdown()
    os.remove('sfr_opt.h5')
    time.sleep(0.1)
