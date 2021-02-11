from osbrain import run_nameserver
from osbrain import run_agent
import src.ka.ka_s.random_walk as rw
import src.bb.blackboard_optimization as bb_opt
from src.utils.problem import BenchmarkProblem
import time

def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=rw.RandomWalk)
    
    assert rp.get_attr('_base_trigger_val') == 5.00001 
    assert rp.get_attr('_class') == 'local search random walk'
    assert rp.get_attr('step_size') == 0.01
    assert rp.get_attr('walk_length') == 10
        
    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
    objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}    
        
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')   
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.connect_agent(rw.RandomWalk, 'ka_rp_exploit') 
    
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)    
    rp.set_random_seed(seed=10893)

    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f1': 365.0, 'f2': 500.0, 'f3' : 600.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[0.650,0.650,0.4]'])
    rp.search_method()
    
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[0.650,0.650,0.4]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}  
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'].keys()) == ['core_[0.65,0.64541,0.4]', 'core_[0.65093,0.64541,0.4]', 'core_[0.65093,0.64541,0.39677]', 'core_[0.66003,0.64541,0.39677]', 'core_[0.66003,0.64541,0.39262]', 'core_[0.66003,0.6417,0.39262]', 'core_[0.66003,0.6331,0.39262]', 'core_[0.66003,0.6331,0.38717]', 'core_[0.6523,0.6331,0.38717]', 'core_[0.6523,0.63111,0.38717]']
    ns.shutdown()
    time.sleep(0.1)