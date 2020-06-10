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
    os.remove('sfr_opt.h5')
    time.sleep(0.1)
    
def test_run_single_agent_bb():
    kas = {'ka_rp_explore': ka_rp.KaRpExplore, 
           'ka_rp_exploit': ka_rp.KaRpExploit,
           'ka_br_lvl3': ka_br.KaBr_lvl3,
           'ka_br_lvl2': ka_br.KaBr_lvl2}
    bb_controller = controller.Controller(bb_name='sfr_opt', bb_type=bb_sfr.BbSfrOpt, ka=kas, archive='sfr_opt', agent_wait_time=10)
    bb_controller.bb.set_attr(total_solutions=1)
    
    bb_controller.run_single_agent_bb()
    time.sleep(10)
    assert bb_controller.bb.get_attr('_complete') == True
    bb_controller.ns.shutdown()
    os.remove('sfr_opt.h5')
    time.sleep(0.1)
