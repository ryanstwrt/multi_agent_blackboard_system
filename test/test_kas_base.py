import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import src.ka.ka_s.base as base
import time
from src.utils.problem import BenchmarkProblem
from src.utils.problem import SFRProblem
import pickle
    
def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=base.KaS)
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
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('_design_variables') == {}    
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('_class') == 'search'
    assert rp.get_attr('_lvl_data') == {}
    assert rp.get_attr('learning_factor') == 0.5
    assert rp.get_attr('execute_once') == False
   
    ns.shutdown()
    time.sleep(0.1)
    
def test_get_design_name():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=base.KaS)
    rp.set_random_seed(seed=1)
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' : {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                  'experiments': {'length':         2, 
                                                  'dict':      {'0': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                                                'random variable': {'ll': 0,  'ul': 2,  'variable type': float}},
                                                  'variable type': dict}})
    
    current_design_variables={'height': 62.51066, 'smear': 64.40649, 'pu_content': 0.00011, 'position': 'exp_d', 'experiments': {'0':'exp_a', 'random variable': 0.18468}}
    name = rp.get_design_name(current_design_variables)
    assert name == 'core_[62.51066,64.40649,0.00011,exp_d,exp_a,0.18468]'
    
    
    ns.shutdown()
    time.sleep(0.1)   
    
def test_clear_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=base.KaS)
    rp.set_attr(_entry_name='entry_1')         
    rp.set_attr(_entry={'one': 0})     
    assert rp.get_attr('_entry_name') == 'entry_1'
    assert rp.get_attr('_entry') == {'one': 0}
    rp.clear_entry()
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_entry') ==    {}
    
    ns.shutdown()
    time.sleep(0.1)          
    
#----------------------------------------------------------
# Tests for KA-Local
#----------------------------------------------------------

def test_karp_exploit_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=base.KaLocal)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl_data') == 3
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
    
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('bb_lvl_read') == 1
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_design_variables') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('_lvl_data') == {}
    assert rp.get_attr('lvl_read') == None
    assert rp.get_attr('analyzed_design') == {}
    assert rp.get_attr('new_designs') == []
    assert rp.get_attr('_class') == 'local search'   
    assert rp.get_attr('reanalyze_designs') == False
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_read_bb_lvl():    
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='local', base=base.KaLocal)        
    lvl_read = {'core_[65.0,65.0,0.42]':  {'pareto type' : 'pareto', 'fitness function' : 1.0}}

    rp.set_attr(analyzed_design={'core_[65.0,65.0,0.42]': {'Analyzed': True}})
    rp.read_bb_lvl(lvl_read)
    assert rp.get_attr('new_designs') == []
    rp.set_attr(reanalyze_designs=True)
    rp.read_bb_lvl(lvl_read)
    assert rp.get_attr('new_designs') == ['core_[65.0,65.0,0.42]']

 
    ns.shutdown()
    time.sleep(0.1)
    
    
def test_select_core():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=base.KaLocal)
    lvl_read = {'core_[65.0,65.0,0.1]':  {'pareto type' : 'pareto', 'fitness function' : 1.0}, 
                'core_[70.0,60.0,0.25]': {'pareto type' : 'pareto', 'fitness function' : 1.25}, 
                'core_[90.0,80.0,0.5]':  {'pareto type' : 'pareto', 'fitness function' : 1.5},
                'core_[75.0,65.0,0.9]':  {'pareto type' : 'pareto', 'fitness function' : 2.5}}
    
    rp.set_attr(lvl_read=lvl_read)
    rp.set_attr(new_designs=[x for x in lvl_read.keys()])
    rp.set_random_seed(seed=109976)
    rp.set_attr(learning_factor=1.0)
    assert rp.select_core() == 'core_[90.0,80.0,0.5]'
    rp.set_random_seed(seed=109977)
    rp.set_attr(learning_factor=0.0)
    assert rp.select_core() == 'core_[75.0,65.0,0.9]'
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_check_new_designs():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=base.KaLocal)
    lvl_read = {'core_[65.0,65.0,0.1]':  {'pareto type' : 'pareto', 'fitness function' : 1.0}, 
                'core_[70.0,60.0,0.25]': {'pareto type' : 'pareto', 'fitness function' : 1.2}, 
                'core_[90.0,80.0,0.5]':  {'pareto type' : 'pareto', 'fitness function' : 1.5},
                'core_[75.0,65.0,0.9]':  {'pareto type' : 'pareto', 'fitness function' : 2.5}}
    
    rp.set_attr(lvl_read=lvl_read)
    rp.set_attr(new_designs=['core_[75.0,75.0,0.75]', 'core_[65.0,65.0,0.1]'])
    rp.check_new_designs()

    assert rp.get_attr('new_designs') == ['core_[65.0,65.0,0.1]']
    ns.shutdown()
    time.sleep(0.1) 
    
def test_calc_objective():
    
    with open('./sm_gpr.pkl', 'rb') as pickle_file:
        sm_ga = pickle.load(pickle_file)
        
    dvs={'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
         'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
         'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    objs={'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
          'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    cons={'eol keff':    {'ll': 1.0, 'ul': 2.5, 'variable type': float}}    
    problem = SFRProblem(design_variables=dvs,
                         objectives=objs,
                         constraints=cons,
                         sm = sm_ga,
                         sm_type='gpr')
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=base.KaLocal)
    rp.set_attr(problem=problem)
    rp.set_attr(current_design_variables={'height': 65.0, 'smear': 65.0, 'pu_content': 0.4})
    rp.calc_objectives()
    
    assert rp.get_attr('current_objectives') == {'reactivity swing': 677.1446654822049, 'burnup': 71.10762739696487}
    assert rp.get_attr('current_constraints') == {'eol keff': 1.0365716174664996}

    ns.shutdown()
    time.sleep(0.1)     
    
def test_calc_objective_benchmark():
    
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()    
        
    dvs = {}
    objs = {}
    for x in range(3):
        dvs['x{}'.format(x)] = {'ll':0.0, 'ul':1.0, 'variable type': float}

    for x in range(3):
        objs['f{}'.format(x)] = {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float}        
        
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')

    rp = run_agent(name='ka_rp', base=base.KaLocal)
    rp.set_attr(problem=problem)
    rp.set_attr(current_design_variables={'x0': 0.25, 'x1':0.75, 'x2':0.13})
    rp.calc_objectives()
    
    assert rp.get_attr('current_objectives') == {'f0': 13.649221822265138, 'f1': 4.549740607421713, 'f2': 54.596887289060554}
    assert rp.get_attr('current_constraints') == {}

    ns.shutdown()
    time.sleep(0.1)         
    