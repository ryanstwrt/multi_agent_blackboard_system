import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import ka
import time
import ka_rp
from collections import OrderedDict
import bb_sfr_opt as bb_sfr

def test_karp_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRp)
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 0
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
    assert rp.get_attr('_trigger_val') == 1.0
    
    ns.shutdown()
    time.sleep(0.1)
    
#----------------------------------------------------------
# Tests fopr KA-RP-verify
#----------------------------------------------------------
    
def test_karp_verify_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRp_verify)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 2
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
    assert rp.get_attr('_trigger_val') == 1.0
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('interp_path') == None
    assert rp.get_attr('interpolator_dict') == {}
    assert rp.get_attr('objectives') == ['keff', 'void', 'doppler']
    assert rp.get_attr('independent_variable_ranges') == OrderedDict({'height': (50,80),
                                                                     'smear': (50,70),
                                                                     'pu_content':(0,1)})
    ns.shutdown()
    time.sleep(0.1)

def test_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRp_verify)
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    assert rp.get_attr('_entry_name') == 'core_{}'.format([x for x in rp.get_attr('design_variables').values()])
    
    ns.shutdown()
    time.sleep(0.1)
    
#----------------------------------------------------------
# Tests fopr KA-RP-Explore
#----------------------------------------------------------

def test_karp_scout_init():
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
    assert rp.get_attr('_trigger_val') == 1.0
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('objectives') == []
    assert rp.get_attr('independent_variable_ranges') == OrderedDict({'height': (50,80),
                                                                     'smear': (50,70),
                                                                     'pu_content':(0,1)})
    ns.shutdown()
    time.sleep(0.1)
    
def test_handler_executor_explore():
    pass
    
def test_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_create_sm_interpolate():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    rp.set_attr(objectives=['keff','void','doppler'])
    rp.create_sm()
    sm = rp.get_attr('_sm')
    keff = sm['keff']((61.37,51.58,0.7340))
    assert keff == 0.9992587833657331
    
    ns.shutdown()
    time.sleep(0.1)

def test_create_sm_regression():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExplore)
    
    rp.set_attr(sm_type='lr')
    rp.set_attr(objectives=['keff','void','doppler'])
    rp.create_sm()
    sm = rp.get_attr('_sm')
    objs = sm.predict('lr', [[61.37,51.58,0.7340]])
    assert round(objs[0][0], 8) == 0.99992182
    assert sm.models['lr']['score'] == 0.93162733339492
    assert sm.models['lr']['mse_score'] == 0.06837266660508003
    
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
    assert rp.get_attr('_trigger_val') == 1.0
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('bb_lvl_read') == 1
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('objectives') == []
    assert rp.get_attr('independent_variable_ranges') == OrderedDict({'height': (50,80),
                                                                     'smear': (50,70),
                                                                     'pu_content':(0,1)})
    assert rp.get_attr('perturbations') == [0.99, 1.01]
    assert rp.get_attr('perturbed_cores') == {}
    assert rp.get_attr('lvl') == {}
    assert rp.get_attr('new_panel') == 'new'
    assert rp.get_attr('old_panel') == 'old'
    ns.shutdown()
    time.sleep(0.1)

def test_handler_executor_exploit():
    pass
    
def test_exploit_mc_design_variables():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRpExploit)
    
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.mc_design_variables()
    assert rp.get_attr('design_variables') != {}
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_perturb_design():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    #bb.connect_agent(ka_rp.KaRpExploit, 'ka_rp_exploit')

    ns.shutdown()
    time.sleep(0.1)    

def test_write_to_bb():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    ka = run_agent(name='ka_rp_exploit', base=ka_rp.KaRpExploit)
    ka.add_blackboard(bb)
    ka.connect_writer()
    
    ka.set_attr(_entry_name='core1')
    core_attrs = {'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                         'cycle length': 100.0, 'reactivity swing': 110.0, 
                                         'burnup': 32.0, 'pu mass': 1000.0}}
    ka.set_attr(_entry=core_attrs)
    ka.write_to_bb(True)
    assert bb.get_attr('abstract_lvls')['level 3'] == {'core1': {'reactor parameters': 
                                                                 {'height': 60.0, 'smear': 70.0, 
                                                                  'pu_content': 0.2, 'cycle length': 100.0, 
                                                                  'reactivity swing': 110.0, 'burnup': 32.0, 
                                                                  'pu mass': 1000.0}}}
    assert bb.get_attr('_new_entry') == True
    assert bb.get_attr('_agent_writing') == False
    
    ka.set_attr(_entry_name='core2')
    core_attrs = {'reactor parameters': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2, 
                                         'cycle length': 100.0, 'reactivity swing': 110.0, 
                                         'burnup': 32.0, 'pu mass': 1000.0}}
    ka.set_attr(_entry=core_attrs)
    ka.write_to_bb(False)
    assert bb.get_attr('abstract_lvls')['level 3'] == {'core1': {'reactor parameters': 
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