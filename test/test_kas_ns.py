from osbrain import run_nameserver
from osbrain import run_agent
import src.ka.ka_s.neighborhood_search as nhs
import src.bb.blackboard_optimization as bb_opt
from src.utils.problem import BenchmarkProblem
import time
import pickle
import src.utils.moo_benchmarks as moo

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
                                                          'objective functions': {'f1': 365.0, 'f2': 500.0, 'f3' : 600.0}}, panel='old')
    
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
    assert bb.get_blackboard()['level 3']['new'] == {'core_[1,1,2,3]': {'design variables': {'x0': '1', 'x1': '1', 'x2': '2', 'x3': '3'}, 'objective functions': {'f1': 95.0}, 'constraints': {}}, 'core_[0,0,2,3]': {'design variables': {'x0': '0', 'x1': '0', 'x2': '2', 'x3': '3'}, 'objective functions': {'f1': 65.0}, 'constraints': {}}, 'core_[0,1,1,3]': {'design variables': {'x0': '0', 'x1': '1', 'x2': '1', 'x3': '3'}, 'objective functions': {'f1': 55.0}, 'constraints': {}}, 'core_[0,1,2,1]': {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '1'}, 'objective functions': {'f1': 90.0}, 'constraints': {}}}
    ns.shutdown()
    time.sleep(0.1)