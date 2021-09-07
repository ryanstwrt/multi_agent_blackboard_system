from osbrain import run_nameserver
from osbrain import run_agent
import mabs.ka.ka_s.neighborhood_search as nhs
import mabs.bb.blackboard_optimization as bb_opt
from mabs.utils.problem import BenchmarkProblem
import time
import pickle
import mabs.utils.moo_benchmarks as moo

dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}    
        
problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')  

def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=nhs.NeighborhoodSearch)

    assert rp.get_attr('_base_trigger_val') == 5.00001
    assert rp.get_attr('perturbation_size') == 0.05
    assert rp.get_attr('neighboorhod_search') == 'fixed'
    assert rp.get_attr('_class') == 'local search neighborhood search'

    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method_continuous():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp_exploit')
    
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)    
    rp.set_random_seed(seed=10893)

    rp = ns.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
 
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[0.650,0.650,0.4]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[0.650,0.650,0.4]'])
    rp.search_method()
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'].keys()) == ['core_[0.6175,0.65,0.4]', 'core_[0.6825,0.65,0.4]', 'core_[0.65,0.6175,0.4]', 'core_[0.65,0.6825,0.4]', 'core_[0.65,0.65,0.38]', 'core_[0.65,0.65,0.42]']
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['old'].keys()] == ['core_[0.650,0.650,0.4]']
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[0.650,0.650,0.4]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}

    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method_discrete():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dvs = {'x0' : {'options': ['0','1','2','3'],'default': '0','variable type': str},
           'x1' : {'options': ['0','1','2','3'],'default': '1','variable type': str},
           'x2' : {'options': ['0','1','2','3'],'default': '2','variable type': str},
           'x3' : {'options': ['0','1','2','3'],'default': '3','variable type': str}}
    objs = {'f1': {'ll': 80, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dvs,objectives=objs,constraints={})
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'tsp')      
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_random_seed(seed=1)
    rp.set_attr(problem=problem)    
    
    rp.set_attr(new_designs=['core_1'])
    rp.set_attr(lvl_read={'core_1':  {'pareto type' : 'pareto', 'fitness': 1.0}})
    rp.set_attr(_lvl_data={'core_1': {'design variables': {'x0': '0', 
                                                          'x1': '1',
                                                          'x2': '2',
                                                          'x3': '3'}}})
    rp.search_method()
    assert bb.get_blackboard()['level 3']['new'] == {'core_[1,1,2,3]': {'design variables': {'x0': '1', 'x1': '1', 'x2': '2', 'x3': '3'}, 'objective functions': {'f1': 95.0}, 'constraints': {}}, 'core_[0,2,2,3]': {'design variables': {'x0': '0', 'x1': '2', 'x2': '2', 'x3': '3'}, 'objective functions': {'f1': 65.0}, 'constraints': {}}, 'core_[0,1,0,3]': {'design variables': {'x0': '0', 'x1': '1', 'x2': '0', 'x3': '3'}, 'objective functions': {'f1': 60.0}, 'constraints': {}}, 'core_[0,1,2,1]': {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '1'}, 'objective functions': {'f1': 90.0}, 'constraints': {}}, 'core_[0,1,2,0]': {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '0'}, 'objective functions': {'f1': 60.0}, 'constraints': {}}}
    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method_permutation():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dvs = {'x0' : {'permutation': ['0','1','2','3'], 'variable type': str},}
    objs = {'f1': {'ll': 80, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dvs,objectives=objs,constraints={})
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'tsp_perm')      
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_random_seed(seed=1)
    rp.set_attr(problem=problem)    
    
    rp.set_attr(new_designs=['core_1'])
    rp.set_attr(lvl_read={'core_1':  {'pareto type' : 'pareto', 'fitness': 1.0}})
    rp.set_attr(_lvl_data={'core_1': {'design variables': {'x0': ['0','1','2','3']}}})
    rp.search_method()
    assert bb.get_blackboard()['level 3']['new'] == {'core_[[0,2,1,3]]': {'design variables': {'x0': ['0','2','1','3']}, 'objective functions': {'f1': 95.0}, 'constraints': {}},
                                                     'core_[[1,2,0,3]]': {'design variables': {'x0': ['1','2','0','3']}, 'objective functions': {'f1': 100.0}, 'constraints': {}}}
    ns.shutdown()
    time.sleep(0.1)   
    
def test_get_perturbed_design_permutation():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dvs = {'x0' : {'permutation': ['0','1','2','3'], 'variable type': str}}
    objs = {'f1': {'ll': 80, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dvs,objectives=objs,constraints={})
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'tsp')      
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_random_seed(seed=1)
    rp.set_attr(problem=problem)    
    
    rp.set_attr(new_designs=['core_1'])
    rp.set_attr(lvl_read={'core_1':  {'pareto type' : 'pareto', 'fitness': 1.0}})
    design =  {'x0': ['0','1','2','3']}
    assert rp.get_perturbed_design('x0', design, 0.15) == {'x0': ['0','1','3','2']}
    
    ns.shutdown()
    time.sleep(0.1)    
    
def test_search_method_mixed():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    model = 're22'
    objs = {'f0': {'ll':0.0,    'ul':500.0, 'goal':'lt', 'variable type': float},
            'f1': {'ll':0.0,    'ul':50.0, 'goal':'lt', 'variable type': float},}
    dvs =  {'x0':  {'options' : [0.20, 0.31, 0.40, 0.44, 0.60, 0.62, 0.79, 0.80, 0.88, 0.93, 1.0, 1.20, 1.24, 1.32, 1.40, 1.55, 1.58, 1.60, 1.76, 1.80, 1.86, 2.0, 2.17, 2.20, 2.37, 2.40, 2.48, 2.60, 2.64, 2.79, 2.80, 3.0, 3.08, 3,10, 3.16, 3.41, 3.52, 3.60, 3.72, 3.95, 3.96, 4.0, 4.03, 4.20, 4.34, 4.40, 4.65, 4.74, 4.80, 4.84, 5.0, 5.28, 5.40, 5.53, 5.72, 6.0, 6.16, 6.32, 6.60, 7.11, 7.20, 7.80, 7.90, 8.0, 8.40, 8.69, 9.0, 9.48, 10.27, 11.0, 11.06, 11.85, 12.0, 13.0, 14.0, 15.0], 'variable type': float},
            'x1':  {'ll': 0.0,  'ul':20.0, 'variable type': float},
            'x2':  {'ll': 0.0,  'ul':40.0, 'variable type': float},}  
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = model)      
    
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp_exploit')
    
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)    
    rp.set_random_seed(seed=10893)

    rp = ns.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[13.0,250.0,25.0]', {'design variables': {'x0': 13.0, 'x1': 10.0, 'x2': 20.0},
                                                         'objective functions': {'f0': 365.0, 'f1': 500.0,},
                                                         'constraints': {}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[13.0,250.0,25.0]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
 
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[13.0,250.0,25.0]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[13.0,250.0,25.0]'])
    rp.search_method()
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'].keys()) == ['core_[1.86,10.0,20.0]', 'core_[1.4,10.0,20.0]', 'core_[13.0,9.5,20.0]', 'core_[13.0,10.5,20.0]', 'core_[13.0,10.0,19.0]', 'core_[13.0,10.0,21.0]']
    assert list(bb.get_attr('abstract_lvls')['level 3']['old'].keys()) == ['core_[13.0,250.0,25.0]']

    ns.shutdown()
    time.sleep(0.1)
    
def test_multiple_perturbations():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    model = 're22'
    objs = {'f0': {'ll':0.0,    'ul':500.0, 'goal':'lt', 'variable type': float},
            'f1': {'ll':0.0,    'ul':50.0, 'goal':'lt', 'variable type': float},}
    dvs =  {'x0':  {'options' : [0.20, 0.31, 0.40, 0.44, 0.60, 0.62, 0.79, 0.80, 0.88, 0.93, 1.0, 1.20, 1.24, 1.32, 1.40, 1.55, 1.58, 1.60, 1.76, 1.80, 1.86, 2.0, 2.17, 2.20, 2.37, 2.40, 2.48, 2.60, 2.64, 2.79, 2.80, 3.0, 3.08, 3,10, 3.16, 3.41, 3.52, 3.60, 3.72, 3.95, 3.96, 4.0, 4.03, 4.20, 4.34, 4.40, 4.65, 4.74, 4.80, 4.84, 5.0, 5.28, 5.40, 5.53, 5.72, 6.0, 6.16, 6.32, 6.60, 7.11, 7.20, 7.80, 7.90, 8.0, 8.40, 8.69, 9.0, 9.48, 10.27, 11.0, 11.06, 11.85, 12.0, 13.0, 14.0, 15.0], 'variable type': float},
            'x1':  {'ll': 0.0,  'ul':20.0, 'variable type': float},
            'x2':  {'ll': 0.0,  'ul':40.0, 'variable type': float},}  
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = model)      
    
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp_exploit')
    
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)    
    rp.set_random_seed(seed=10893)
    rp.set_attr(additional_perturbations=3)

    rp = ns.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[13.0,250.0,25.0]', {'design variables': {'x0': 13.0, 'x1': 10.0, 'x2': 20.0},
                                                         'objective functions': {'f0': 365.0, 'f1': 500.0,},
                                                         'constraints': {}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[13.0,250.0,25.0]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
 
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[13.0,250.0,25.0]'])
    rp.search_method()
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'].keys()) == ['core_[1.86,9.5,19.0]', 'core_[5.0,10.5,21.0]', 'core_[8.69,9.5,19.0]', 'core_[4.34,10.5,21.0]', 'core_[11.06,9.5,19.0]', 'core_[1.6,10.5,19.0]']
    assert list(bb.get_attr('abstract_lvls')['level 3']['old'].keys()) == ['core_[13.0,250.0,25.0]']

    ns.shutdown() 
    time.sleep(0.1)
    
    
def test_force_shutdown():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.initialize_metadata_level()
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp_ns')
    bb.set_attr(final_trigger=0)
    
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp = ns.proxy('ka_rp_ns')
    rp.set_attr(problem=problem, debug_wait=True, debug_wait_time=0.05)    
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'], _lvl_data=bb.get_blackboard()['level 3']['old'], new_designs=['core_[0.650,0.650,0.4]'])
    bb.set_attr(_kaar = {0: {}, 1: {'ka_rp_ns': 2}}, _ka_to_execute=('ka_rp_ns', 2))
    bb.send_executor()
    bb.send_shutdown()
    time.sleep(0.1)
    assert ns.agents() == ['blackboard']
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.6175,0.65,0.4]']

    ns.shutdown() 
    time.sleep(0.1)      