import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import src.blackboard as blackboard
import pickle
import src.ka as ka
import time
import src.ka_rp as ka_rp
import src.bb_opt as bb_opt

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)


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
    assert rp.get_attr('_base_trigger_val') == 0.250001   
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('design_variables') == {}    
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('_class') == 'search'
    
    ns.shutdown()
    time.sleep(0.05)
    
#----------------------------------------------------------
# Tests fopr KA-RP-Explore
#----------------------------------------------------------

def test_karp_explore_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaGlobal)
    
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
    assert rp.get_attr('_base_trigger_val') == 0.250001
    
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    ns.shutdown()
    time.sleep(0.05)
    
def test_explore_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(ka_rp.KaGlobal, 'ka_rp_explore')
    
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
    time.sleep(0.05)

def test_explore_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(ka_rp.KaGlobal, 'ka_rp')
    
    bb.publish_trigger()
    time.sleep(0.15)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0.250001}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 0.250001)
    
    bb.publish_trigger()
    time.sleep(0.15)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0.250001}, 2: {'ka_rp': 0.500002}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 0.500002)
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_explore_search_method():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaGlobal)
    rp.set_random_seed(seed=1)
    rp.set_attr(design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'experiments': {'length':         2, 
                                                  'positions':      {0: {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d'], 'default': 'no_exp'},
                                                                     1: {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d'], 'default': 'no_exp'}},
                                                  'variable type': list}})
    
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.search_method()
    assert rp.get_attr('current_design_variables') == {'height': 54.03093, 'smear': 66.94867, 'pu_content': 0.76377, 'experiments': ['exp_d', 'no_exp']}
    rp.search_method()
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_explore_set_random_seed():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaGlobal)
    rp.set_attr(design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                 'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                 'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}})    
    rp.set_random_seed(seed=10983)
    rp.search_method()
    assert rp.get_attr('current_design_variables') == {'height': 74.70197, 'pu_content': 0.19624, 'smear': 64.49033}
    rp.set_random_seed()
    rp.search_method()
    assert rp.get_attr('current_design_variables') != {'height': 74.70197, 'pu_content': 0.19624, 'smear': 64.49033}
    
    ns.shutdown()
    time.sleep(0.05)    
    
    
#def test_create_sm_interpolate():
#    ns = run_nameserver()
#    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
#    objs={'bol keff': {'ll':0.95, 'ul': 1.25, 'goal':'gt', 'variable type': float}, 
#                       'void': {'ll':-200, 'ul': 0, 'goal':'lt',  'variable type': float}, 
#                       'doppler': {'ll':-10, 'ul':0, 'goal':'lt',  'variable type': float}}
#    bb.initialize_abstract_level_3(objectives=objs)
#    bb.generate_sm()
#    
#    sm = bb.get_attr('_sm')
#    keff = sm['bol keff']((61.37,51.58,0.7340))
#    assert keff == 0.9992587833657331
#    
#    ns.shutdown()
#    time.sleep(0.05)

#def test_create_sm_regression():
#    ns = run_nameserver()
#    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
 #   objs={'bol keff': {'ll':0.95, 'ul':1.25, 'goal':'gt', 'variable type': float}}
  #  bb.initialize_abstract_level_3(objectives=objs)
   # bb.set_attr(sm_type='lr')
#    bb.generate_sm()
 #   time.sleep(1)
  #  sm = bb.get_attr('_sm')
   # objs = sm.predict('lr', [[61.37,51.58,0.7340]])
#    assert round(objs[0][0], 8) == 1.00720012
 #   assert round(sm.models['lr']['score'], 8)  == round(0.95576537, 8)
  #  assert round(sm.models['lr']['mse_score'], 8) == round(0.04423463, 8)
    
#    ns.shutdown()
#    time.sleep(0.05)

#----------------------------------------------------------
# Tests for KA-LHC
#----------------------------------------------------------

def test_kalhc_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLHC)
    
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
    
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('lhc_criterion') == 'corr'
    assert rp.get_attr('samples') == 50
    assert rp.get_attr('lhd') == []

    ns.shutdown()
    time.sleep(0.05)    

def test_kalhc_generate_lhc():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLHC)
    rp.set_attr(design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}})    
    rp.generate_lhc()
    lhd = rp.get_attr('lhd')
    assert len(lhd) == 50
    assert len(lhd[0]) == 3
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_kalhc_search_method():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLHC)
    
    rp.set_attr(design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}})    
    rp.generate_lhc()
    lhd = rp.get_attr('lhd')[0]
    print(lhd)
    
    rp.search_method()
    design = rp.get_attr('current_design_variables')
    assert round(lhd[2], 5) == design['pu_content']
    
    ns.shutdown()
    time.sleep(0.05) 

def test_kalhc_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(ka_rp.KaLHC, 'ka_rp_lhc')
    
    rp = ns.proxy('ka_rp_lhc')
    rp.set_attr(_trigger_val=2)
    bb.set_attr(_ka_to_execute=('ka_rp_lhc', 2))
    bb.send_executor()
    time.sleep(2.0)
    
    entry = rp.get_attr('_entry')
    core_name = rp.get_attr('_entry_name')
    bb_entry = {core_name: entry}
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == bb_entry
    assert rp.get_attr('_trigger_val') == 0    

    ns.shutdown()
    time.sleep(0.05)

def test_kalhc_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(ka_rp.KaLHC, 'ka_rp_lhc')
    
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp_lhc': 50.000006}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_lhc', 50.000006)
    
    rp = ns.proxy('ka_rp_lhc')
    for i in range(50):
        rp.search_method()
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp_lhc': 50.000006}, 2: {'ka_rp_lhc': 0.0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    ns.shutdown()
    time.sleep(0.05)
    
#----------------------------------------------------------
# Tests for KA-Local
#----------------------------------------------------------

def test_karp_exploit_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLocal)
    
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
    
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('bb_lvl_read') == 1
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('perturbation_size') == 0.05
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('lvl_data') == None
    assert rp.get_attr('lvl_read') == None
    assert rp.get_attr('analyzed_design') == {}
    assert rp.get_attr('new_designs') == []

    ns.shutdown()
    time.sleep(0.05)

#----------------------------------------------------------
# Tests fopr KA-Local-HC
#----------------------------------------------------------

def test_karp_exploit_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLocalHC)
    
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
    
    assert rp.get_attr('lvl_data') == None
    assert rp.get_attr('lvl_read') == None
    assert rp.get_attr('analyzed_design') == {}
    assert rp.get_attr('new_designs') == []
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5  
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('bb_lvl_read') == 1
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('current_design_variables') == {}

    assert rp.get_attr('step_size') == 0.05
    assert rp.get_attr('step_rate') == 0.01
    assert rp.get_attr('step_limit') == 100
    assert rp.get_attr('convergence_criteria') == 0.001

    ns.shutdown()
    time.sleep(0.05)
    
def test_determine_model_applicability():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')

    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    
    rp.set_attr(current_design_variables={'height': 65.0, 'smear': 65.0, 'pu_content': 0.42})
    rp.determine_model_applicability('height')
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {}
    rp.set_attr(current_design_variables={'height': 85.0, 'smear': 65.0, 'pu_content': 0.42})
    rp.determine_model_applicability('height')
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {}
    
    rp.set_attr(current_design_variables={'height': 70.0, 'smear': 65.0, 'pu_content': 0.42})
    rp.determine_model_applicability('height')
    time.sleep(1)
    
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == ['core_[70.0, 65.0, 0.42]']

    ns.shutdown()
    time.sleep(0.05)
    
def test_exploit_handler_executor_pert():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp_exploit')
    
    rp = ns.proxy('ka_rp_exploit')
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    
    assert bb.get_attr('abstract_lvls')['level 3'] == {'new':{},'old':{}}
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_1', {'pareto type' : 'pareto', 'fitness function': 1.0})
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    rp.set_attr(new_designs=['core_1'])
    bb.send_executor()      
    time.sleep(1.0)
    
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[61.75, 65.0, 0.4]',
                                                           'core_[68.25, 65.0, 0.4]',
                                                           'core_[65.0, 61.75, 0.4]',
                                                           'core_[65.0, 68.25, 0.4]',
                                                           'core_[65.0, 65.0, 0.38]', 
                                                           'core_[65.0, 65.0, 0.42]']
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    
    ns.shutdown()
    time.sleep(0.05)

def test_exploit_handler_executor_rw():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(ka_rp.KaLocalRW, 'ka_rp_exploit')
    
    rp = ns.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=10893)
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
        
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_1', {'pareto type' : 'pareto', 'fitness function': 1.0})

    rp.set_attr(local_search='random walk')
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    rp.set_attr(new_designs=['core_1'])

    bb.send_executor()  
    time.sleep(1.0)
    assert [k for k in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == ['core_[65.0, 64.99646, 0.4]', 'core_[65.0, 64.99646, 0.40435]', 'core_[65.0, 64.98988, 0.40435]', 'core_[65.00639, 64.98988, 0.40435]', 'core_[65.00639, 64.98988, 0.40313]', 'core_[65.00639, 64.98988, 0.39711]', 'core_[65.01204, 64.98988, 0.39711]', 'core_[65.01484, 64.98988, 0.39711]', 'core_[65.0235, 64.98988, 0.39711]', 'core_[65.01739, 64.98988, 0.39711]']
  
    ns.shutdown()
    time.sleep(0.05)  
    
def test_exploit_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp')
    
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    bb.update_abstract_lvl(1, 'core 1', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.publish_trigger()
    time.sleep(0.25)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0}, 2: {'ka_rp':5.00001}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 5.00001)
    
    ns.shutdown()
    time.sleep(0.05)
    
    
def test_exploit_perturb_design():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp_exploit')

    rp = ns.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
 
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0, 65.0, 0.42]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0, 65.0, 0.42]'])
    rp.search_method()
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[61.75, 65.0, 0.4]', 
                                                           'core_[68.25, 65.0, 0.4]',
                                                           'core_[65.0, 61.75, 0.4]',
                                                           'core_[65.0, 68.25, 0.4]',
                                                           'core_[65.0, 65.0, 0.38]',]
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['old'].keys()] == ['core_[65.0, 65.0, 0.42]']
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0, 65.0, 0.42]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}

    ns.shutdown()
    time.sleep(0.05)
    
def test_exploit_write_to_bb():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    ka = run_agent(name='ka_rp_exploit', base=ka_rp.KaLocal)
    bb.initialize_abstract_level_3()
    ka.add_blackboard(bb)
    ka.connect_writer()
    
    core_attrs = {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}
    ka.write_to_bb(ka.get_attr('bb_lvl'), 'core1', core_attrs, panel='new')
    time.sleep(1)
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core1': {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}}
    assert bb.get_attr('_agent_writing') == False
    
    core_attrs = {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}
    ka.write_to_bb(ka.get_attr('bb_lvl'), 'core2', core_attrs, panel='new')
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core1': {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}},
                                                              'core2': {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}}
    assert bb.get_attr('_agent_writing') == False
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kalocalrw():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(ka_rp.KaLocalRW, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=10893)

    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.4]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4},
                                                          'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0,'burnup' : 50.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0, 65.0, 0.4]'])
    rp.search_method()
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0, 65.0, 0.4]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == ['core_[65.0, 64.99646, 0.4]', 'core_[65.0, 64.99646, 0.40435]', 'core_[65.0, 64.98988, 0.40435]', 'core_[65.00639, 64.98988, 0.40435]', 'core_[65.00639, 64.98988, 0.40313]', 'core_[65.00639, 64.98988, 0.39711]', 'core_[65.01204, 64.98988, 0.39711]', 'core_[65.01484, 64.98988, 0.39711]', 'core_[65.0235, 64.98988, 0.39711]', 'core_[65.01739, 64.98988, 0.39711]']
    ns.shutdown()
    time.sleep(0.05)
    
def test_determine_step_steepest_ascent():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(hc_type='steepest ascent')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    # Test an increase in burnup (greater than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert diff == 0.09
    assert pert == '+ height'
    
    # Test an increase in reactivity swing (less than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 680.11, 'burnup' : 61.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 61.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.053
    assert pert == '+ pu_content'
    
    # Test a postive a change in both objectives
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 680.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.138
    assert pert == '+ height'

    # Test a postive a change in both objectives (both have of ~0.078, but + pu_content is slightly greater})
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 661.51, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.078
    assert pert == '+ pu_content'
    
    # Test a case with no change in design variables
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 661.51, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert diff  == None
    assert pert == None
    
    ns.shutdown()
    time.sleep(0.05)

    
def test_determine_step_simple():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    # Test an increase in burnup (greater than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert pert == '+ height'
    
    # Test multiple increases 
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12}},
                   '- height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 650.11, 'burnup' : 62.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert pert == '+ height' or '- height'

    ns.shutdown()
    time.sleep(0.05)
    
    
def test_kalocalhc():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)

    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(step_size=0.1)
    rp.set_attr(step_rate=0.5)
    rp.set_attr(step_limit=5000)
    rp.set_attr(convergence_criteria=0.005)
    rp.set_attr(hc_type='steepest ascent')
    rp.set_random_seed(seed=1099)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    bb.update_abstract_lvl(3, 'core_[78.65, 65.0, 0.42]', {'design variables': {'height': 78.65, 'smear': 65.0, 'pu_content': 0.42}, 
                                                           'objective functions': {'reactivity swing' : 447.30449, 'burnup' : 490.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0, 65.0, 0.42]'])
    rp.search_method()
    time.sleep(3)
    
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] ==  ['core_[65.0, 65.0, 0.378]', 'core_[65.0, 65.0, 0.3402]', 'core_[65.0, 65.0, 0.30618]', 'core_[65.0, 65.0, 0.27556]', 'core_[65.0, 65.0, 0.248]', 'core_[65.0, 65.0, 0.2232]', 'core_[65.0, 65.0, 0.20088]', 'core_[65.0, 65.0, 0.18079]', 'core_[65.0, 65.0, 0.16271]', 'core_[71.5, 65.0, 0.16271]', 'core_[78.65, 65.0, 0.16271]', 'core_[78.65, 65.0, 0.14644]', 'core_[78.65, 65.0, 0.1318]', 'core_[78.65, 65.0, 0.11862]', 'core_[78.65, 68.25, 0.11862]', 'core_[78.65, 68.25, 0.12455]', 'core_[78.65, 69.95625, 0.12455]', 'core_[78.65, 69.95625, 0.12144]', 'core_[79.63313, 69.95625, 0.12144]', 'core_[79.63313, 69.95625, 0.12296]', 'core_[79.63313, 69.95625, 0.1245]', 'core_[79.63313, 69.95625, 0.12606]', 'core_[79.63313, 69.95625, 0.12527]']
   
    ns.shutdown()
    time.sleep(0.05)

def test_kalocalhc_simple():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(step_size=0.75)
    rp.set_attr(step_rate=0.01)
    rp.set_attr(convergence_criteria=0.001)
    rp.set_random_seed(seed=1073)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0, 65.0, 0.42]'])
    rp.search_method()
    time.sleep(2)
    assert([x for x in bb.get_attr('abstract_lvls')['level 3']['new']]) == ['core_[65.0, 65.0, 0.105]', 'core_[65.0, 65.0, 0.02625]', 'core_[65.0, 65.0, 0.00656]', 'core_[65.0, 65.0, 0.00164]', 'core_[65.0, 65.0, 0.00287]', 'core_[65.0, 65.0, 0.00502]', 'core_[65.0, 65.0, 0.00126]', 'core_[65.0, 65.0, 0.00031]', 'core_[65.0, 65.0, 8e-05]', 'core_[65.0, 65.0, 2e-05]', 'core_[65.0, 65.0, 4e-05]', 'core_[65.0, 65.0, 1e-05]', 'core_[65.0, 65.0, 0.0]']
   
    ns.shutdown()
    time.sleep(0.05)
    
#----------------------------------------------------------
# Tests fopr KA-GA
#----------------------------------------------------------
    
def test_KaLocalGA():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_trigger_number=2)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.1]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.1]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.25]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.25}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 60.0, 0.25]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    time.sleep(2)

    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[70.0, 65.0, 0.1]', 'core_[65.0, 60.0, 0.25]']
    bb.update_abstract_lvl(3, 'core_[90.0, 80.0, 0.5]', {'design variables': {'height': 90.0, 'smear': 80.0, 'pu_content': 0.50},
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[90.0, 80.0, 0.5]', {'pareto type' : 'pareto', 'fitness function' : 1.0})    
    bb.update_abstract_lvl(3, 'core_[75.0, 65.0, 0.9]', {'design variables': {'height': 75.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                         'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[75.0, 65.0, 0.9]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp.set_attr(offspring_per_generation=2)
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    time.sleep(2)
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == ['core_[70.0, 65.0, 0.1]', 'core_[65.0, 60.0, 0.25]', 'core_[65.0, 80.0, 0.5]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_KaLocalGA_linear_crossover():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_trigger_number=2)
    rp.set_attr(crossover_type='linear crossover')
    bb.update_abstract_lvl(3, 'core_[50.0, 60.0, 0.1]', {'design variables': {'height': 50.0, 'smear': 60.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[50.0, 60.0, 0.1]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 70.0, 0.2]', {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 70.0, 0.2]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    time.sleep(2)
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[60.0, 65.0, 0.15]', 'core_[80.0, 70.0, 0.25]', 'core_[50.0, 55.0, 0.05]']
    solutions = ['core_[60.0, 65.0, 0.15]', 'core_[50.0, 55.0, 0.05]', 'core_[80.0, 70.0, 0.25]']
    for solution in solutions:
        assert solution in [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()]
    
    bb.update_abstract_lvl(3, 'core_[90.0, 80.0, 0.5]', {'design variables': {'height': 90.0, 'smear': 80.0, 'pu_content': 0.50},
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[90.0, 80.0, 0.5]', {'pareto type' : 'pareto', 'fitness function' : 1.0})    
    bb.update_abstract_lvl(3, 'core_[75.0, 65.0, 0.9]', {'design variables': {'height': 55.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                         'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[75.0, 65.0, 0.9]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp.set_attr(offspring_per_generation=4)
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    time.sleep(2)
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[60.0, 65.0, 0.15]', 'core_[80.0, 70.0, 0.25]', 'core_[50.0, 55.0, 0.05]', 'core_[70.0, 70.0, 0.3]', 'core_[50.0, 50.0, 0.0]', 'core_[80.0, 70.0, 0.7]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_KaLocalGA_full():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_size=2)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0,  'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.50]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 60.0, 0.50]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    assert rp.get_attr('analyzed_design') == {}
    bb.publish_trigger()
    time.sleep(0.5)
    bb.controller()
    bb.send_executor()
    time.sleep(0.5)
    assert rp.get_attr('analyzed_design') == {'core_[65.0, 65.0, 0.42]': {'Analyzed': True}, 'core_[70.0, 60.0, 0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[70.0, 65.0, 0.42]', 'core_[65.0, 60.0, 0.5]']

    # Make sure we don't recombine already examined results
    bb.publish_trigger()
    time.sleep(0.5)
    bb.controller()
    bb.send_executor()  
    time.sleep(0.5)
    assert rp.get_attr('analyzed_design') == {'core_[65.0, 65.0, 0.42]': {'Analyzed': True}, 'core_[70.0, 60.0, 0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[70.0, 65.0, 0.42]', 'core_[65.0, 60.0, 0.5]']

    # Reduce the PF size and ensure we don't execute the GA_KA
    rp.set_attr(pf_size=1)    
    bb.remove_bb_entry(1, 'core_[65.0, 65.0, 0.42]')
    bb.publish_trigger()
    time.sleep(0.5)
    bb.controller()
    bb.send_executor()  
    time.sleep(0.5)
    assert rp.get_attr('analyzed_design') == {'core_[65.0, 65.0, 0.42]': {'Analyzed': True}, 'core_[70.0, 60.0, 0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[70.0, 65.0, 0.42]', 'core_[65.0, 60.0, 0.5]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kaga_random_mutation():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    genotype = {'height':70.0,'smear':65.0,'pu_content':0.5}
    new_genotype = rp.random_mutation(genotype)
    assert new_genotype == {'height': 70.0, 'smear': 66.2978, 'pu_content': 0.5}    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kaga_non_uniform_mutation():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    genotype = {'height':55.0,'smear':65.0,'pu_content':0.5}
    new_genotype = rp.non_uniform_mutation(genotype)
    assert new_genotype == {'height': 55.0, 'smear': 70.0, 'pu_content': 0.5}

    ns.shutdown()
    time.sleep(0.05)

#----------------------------------------------------------
# Tests fopr KA-SM
#----------------------------------------------------------

def test_KaSm_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_sm', base=ka_rp.KaLocalSm)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_sm'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 0.0
    
    assert rp.get_attr('lvl_data') == None
    assert rp.get_attr('lvl_read') == None
    assert rp.get_attr('analyzed_design') == {}
    assert rp.get_attr('new_designs') == []
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5  
    assert rp.get_attr('objective_functions') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('design_variables') == {}
    assert rp.get_attr('bb_lvl_read') == 3
    assert rp.get_attr('current_design_variables') == {}

    assert rp.get_attr('sm_type') == 'gpr'
    assert rp.get_attr('_sm') == None

    ns.shutdown()
    time.sleep(0.05)
    
def test_KaSm_generate_sm():
    ns = run_nameserver()
    rp = run_agent(name='ka_sm', base=ka_rp.KaLocalSm)
    rp.set_attr(design_variables={'a': {}, 'b': {}})
    rp.set_attr(_objectives={'c': {}, 'd': {}})
    rp.set_attr(sm_type='gpr')
    
    data = {}
    for i in range(25):
        data[i] = {'a': i, 'b': 10*i, 'c': i ** 2, 'd': (i + i) ** 2}

    rp.generate_sm(data)
    sm = rp.get_attr('_sm')
    obj = sm.predict('gpr', {'c': 4, 'd': 16}, output='dict')
    assert round(obj['a'], 5) == 2
    assert round(obj['b'], 5) == 20
    
    ns.shutdown()
    time.sleep(0.05)