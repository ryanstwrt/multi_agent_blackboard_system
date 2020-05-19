import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import ka
import time
import ka_rp
import bb_sfr_opt as bb_sfr

def test_karp_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRp)
    assert rp.get_attr('bb') == None
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    
    assert rp.get_attr('_trigger_val') == 0
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    
    ns.shutdown()
    time.sleep(0.1)
    
#----------------------------------------------------------
# Tests fopr KA-RP-Explore
#----------------------------------------------------------

def test_karp_explore_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 0
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('objectives') == []
    assert rp.get_attr('design_variable_ranges') == {}
    ns.shutdown()
    time.sleep(0.1)
    
def test_explore_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.generate_sm()
    bb.connect_agent(ka_rp.KaRpExplore, 'ka_rp_explore')
    
    rp = ns.proxy('ka_rp_explore')
    rp.set_attr(_trigger_val=1)
    bb.set_attr(_ka_to_execute=('ka_rp_explore', 2))
    bb.send_executor()
    time.sleep(2.0)
    
    entry = rp.get_attr('_entry')
    core_name = rp.get_attr('_entry_name')
    bb_entry = {core_name: entry}
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == bb_entry
    assert rp.get_attr('_trigger_val') == 0

    ns.shutdown()
    time.sleep(0.1)

def test_explore_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.connect_agent(ka_rp.KaRpExplore, 'ka_rp')
    
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0.25}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 0.25)
    
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0.25}, 2: {'ka_rp': 0.50}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 0.50)
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_explore_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    rp.set_attr(design_variable_ranges={'height': (50, 80), 'smear': (50,70), 'pu_content': (0,1)})
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_create_sm_interpolate():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.set_attr(objectives=['keff','void','doppler'])
    bb.generate_sm()
    
    sm = bb.get_attr('_sm')
    keff = sm['keff']((61.37,51.58,0.7340))
    assert keff == 0.9992587833657331
    
    ns.shutdown()
    time.sleep(0.1)

def test_create_sm_regression():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.set_attr(objectives=['keff','void','doppler'])
    bb.set_attr(sm_type='lr')
    bb.generate_sm()
    
    sm = bb.get_attr('_sm')
    objs = sm.predict('lr', [[61.37,51.58,0.7340]])
    assert round(objs[0][0], 8) == 1.00290541
    assert sm.models['lr']['score'] == 0.8690755311077457
    assert sm.models['lr']['mse_score'] == 0.13092446889225426
    
    ns.shutdown()
    time.sleep(0.1)

#----------------------------------------------------------
# Tests fopr KA-RP-Exploit
#----------------------------------------------------------

def test_karp_exploit_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExploit)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 0.0
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('bb_lvl_read') == 1
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('objectives') == []
    assert rp.get_attr('design_variable_ranges') == {}
    assert rp.get_attr('perturbations') == [0.99, 1.01]
    assert rp.get_attr('new_panel') == 'new'
    assert rp.get_attr('old_panel') == 'old'
    ns.shutdown()
    time.sleep(0.1)

def test_exploit_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.generate_sm()
    bb.connect_agent(ka_rp.KaRpExploit, 'ka_rp_exploit')
    
    rp = ns.proxy('ka_rp_exploit')
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    
    assert bb.get_attr('abstract_lvls')['level 3'] == {'new':{},'old':{}}
    
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 
                                                                'pu_content': 0.4, 'cycle length': 365.0, 
                                                                'pu mass': 500.0, 'reactivity swing' : 600.0,
                                                                'burnup' : 50.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_1', {'pareto type' : 'pareto', 'fitness function': 1.0}, panel='new')
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    bb.send_executor()      
    time.sleep(5)
    
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[64.35, 65.0, 0.4]',
                                                           'core_[65.65, 65.0, 0.4]',
                                                           'core_[65.0, 64.35, 0.4]',
                                                           'core_[65.0, 65.65, 0.4]',
                                                           'core_[65.0, 65.0, 0.396]', 
                                                           'core_[65.0, 65.0, 0.404]',]
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new': {}, 'old': {'core_1' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}}
    
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    bb.send_executor()  
    time.sleep(1.0)
    
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[64.35, 65.0, 0.4]',
                                                           'core_[65.65, 65.0, 0.4]',
                                                           'core_[65.0, 64.35, 0.4]',
                                                           'core_[65.0, 65.65, 0.4]',
                                                           'core_[65.0, 65.0, 0.396]', 
                                                           'core_[65.0, 65.0, 0.404]',]
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new': {}, 'old': {'core_1' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}}

    
    ns.shutdown()
    time.sleep(0.1)
    
def test_exploit_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExploit)
    rp.set_attr(design_variable_ranges={'height': (50, 80), 'smear': (50,70), 'pu_content': (0,1)})
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_exploit_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.generate_sm()
    bb.connect_agent(ka_rp.KaRpExploit, 'ka_rp')
    
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    bb.update_abstract_lvl(1, 'core 1', {'pareto type' : 'pareto', 'fitness function' : 1.0}, panel='new')
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0}, 2: {'ka_rp':5}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 5)
    
    ns.shutdown()
    time.sleep(0.1)
    
    
def test_exploit_perturb_design():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.generate_sm()
    bb.connect_agent(ka_rp.KaRpExploit, 'ka_rp_exploit')

    rp = ns.proxy('ka_rp_exploit')
    
    bb.update_abstract_lvl(3, 'core_1', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 
                                                                'pu_content': 0.4, 'cycle length': 365.0, 
                                                                'pu mass': 500.0, 'reactivity swing' : 600.0,
                                                                'burnup' : 50.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_1', {'pareto type' : 'pareto', 'fitness function' : 1.0}, panel='new')
 
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new': {'core_1' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}, 'old': {}}
    rp.perturb_design()
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[64.35, 65.0, 0.4]',
                                                           'core_[65.65, 65.0, 0.4]',
                                                           'core_[65.0, 64.35, 0.4]',
                                                           'core_[65.0, 65.65, 0.4]',
                                                           'core_[65.0, 65.0, 0.396]', 
                                                           'core_[65.0, 65.0, 0.404]',]
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new': {}, 'old': {'core_1' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}}

    ns.shutdown()
    time.sleep(0.1)
    
def test_exploit_move_entry():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExploit)
    rp.add_blackboard(bb)
    rp.connect_writer()
    
    bb.add_abstract_lvl(1, {'pareto type' : str, 'fitness function' : float})
    bb.add_panel(1, ['new', 'old'])
    
    bb.update_abstract_lvl(1, 'core 1', {'pareto type' : 'weak', 'fitness function' : 1.0}, panel='new')
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new' : {'core 1' : {'pareto type' : 'weak', 'fitness function' : 1.0}}, 'old' : {}}    
    rp.move_entry(rp.get_attr('bb_lvl_read'), 'core 1', {'pareto type' : 'weak', 'fitness function' : 1.0}, rp.get_attr('old_panel'), rp.get_attr('new_panel'))
    assert bb.get_attr('abstract_lvls')['level 1'] == {'new' : {}, 'old' : {'core 1' : {'pareto type' : 'weak', 'fitness function' : 1.0}}}    

    ns.shutdown()
    time.sleep(0.1)
    
def test_exploit_write_to_bb():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    ka = run_agent(name='ka_rp_exploit', base=ka_rp.KaRpExploit)
    ka.add_blackboard(bb)
    ka.connect_writer()
    
    core_attrs = {'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                         'cycle length': 100.0, 'reactivity swing': 110.0, 
                                         'burnup': 32.0, 'pu mass': 1000.0}}
    ka.write_to_bb(ka.get_attr('bb_lvl'), 'core1', core_attrs, complete=True, panel='new')
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core1': {'reactor parameters': 
                                                                 {'height': 60.0, 'smear': 70.0, 
                                                                  'pu_content': 0.2, 'cycle length': 100.0, 
                                                                  'reactivity swing': 110.0, 'burnup': 32.0, 
                                                                  'pu mass': 1000.0}}}
    assert bb.get_attr('_new_entry') == True
    assert bb.get_attr('_agent_writing') == False
    
    core_attrs = {'reactor parameters': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2, 
                                         'cycle length': 100.0, 'reactivity swing': 110.0, 
                                         'burnup': 32.0, 'pu mass': 1000.0}}
    ka.write_to_bb(ka.get_attr('bb_lvl'), 'core2', core_attrs, complete=False, panel='new')
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core1': {'reactor parameters': 
                                                                 {'height': 60.0, 'smear': 70.0, 
                                                                  'pu_content': 0.2, 'cycle length': 100.0, 
                                                                  'reactivity swing': 110.0, 'burnup': 32.0, 
                                                                  'pu mass': 1000.0}},
                                                               'core2': {'reactor parameters': 
                                                                 {'height': 70.0, 'smear': 70.0, 
                                                                  'pu_content': 0.2, 'cycle length': 100.0, 
                                                                  'reactivity swing': 110.0, 'burnup': 32.0, 
                                                                  'pu mass': 1000.0}}}
    assert bb.get_attr('_new_entry') == False
    assert bb.get_attr('_agent_writing') == False


    ns.shutdown()
    time.sleep(0.1)