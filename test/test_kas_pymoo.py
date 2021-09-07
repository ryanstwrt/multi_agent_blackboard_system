from osbrain import run_nameserver
from osbrain import run_agent
import time
import mabs.ka.ka_s.pymoo_plugin as pm
import mabs.bb.blackboard_optimization as bb_opt
from pymoo.factory import get_algorithm, get_termination
from mabs.utils.problem import BenchmarkProblem
import numpy as np

def test_init():
    
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_s = run_agent(name='ka_pymoo', base=pm.PyMooAlgorithm)

    assert ka_s.get_attr('pymoo_algorithm_name') == 'nsga2'
    assert ka_s.get_attr('crossover') == 'real_sbx'
    assert ka_s.get_attr('mutation') == 'real_pm'
    assert ka_s.get_attr('_class') == 'local search pymoo nsga2'    
    assert ka_s.get_attr('termination_type') == 'n_eval'
    assert ka_s.get_attr('termination_criteria') == 250   
    assert ka_s.get_attr('termination') == None
    assert ka_s.get_attr('pop_size') == 25       
    assert ka_s.get_attr('n_offspring') == 10    
    assert ka_s.get_attr('initial_pop') == None  
    
    ns.shutdown()
    time.sleep(0.1)    
    
def test_setup_mixed():
    
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_s = run_agent(name='ka_pymoo', base=pm.PyMooAlgorithm)
    objs = {'f0': {'ll':0.0,    'ul':500.0, 'goal':'lt', 'variable type': float},
            'f1': {'ll':0.0,    'ul':50.0, 'goal':'lt', 'variable type': float},}
    dvs =  {'x0':  {'options' : [0.20, 0.31, 0.40, 0.44, 0.60, 0.62, 0.79, 0.80, 0.88, 0.93, 1.0, 1.20, 1.24, 1.32, 1.40, 1.55, 1.58, 1.60, 1.76, 1.80, 1.86, 2.0, 2.17, 2.20, 2.37, 2.40, 2.48, 2.60, 2.64, 2.79, 2.80, 3.0, 3.08, 3,10, 3.16, 3.41, 3.52, 3.60, 3.72, 3.95, 3.96, 4.0, 4.03, 4.20, 4.34, 4.40, 4.65, 4.74, 4.80, 4.84, 5.0, 5.28, 5.40, 5.53, 5.72, 6.0, 6.16, 6.32, 6.60, 7.11, 7.20, 7.80, 7.90, 8.0, 8.40, 8.69, 9.0, 9.48, 10.27, 11.0, 11.06, 11.85, 12.0, 13.0, 14.0, 15.0], 'variable type': float},
            'x1':  {'ll': 0.0,  'ul':20.0, 'variable type': float},
            'x2':  {'ll': 0.0,  'ul':40.0, 'variable type': float},}
    ka_s.set_attr(_design_variables=dvs)
    ka_s.set_attr(_objectives=objs)
    
    ka_s.set_attr(lvl_read = {'core_[1,10.0,10.5]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                              'core_[1,10.0,20.0]': {'pareto type' : 'pareto', 'fitness function' : 1.0}})
    ka_s.set_attr(_lvl_data = {'core_[1,10.0,10.5]': {'design variables': {'x0': 1, 'x1': 10.0, 'x2': 10.50},
                                                      'objective functions': {'f0' : 450.11, 'f1' : 35.12},
                                                      'constraints': {}},
                               'core_[1,10.0,20.0]': {'design variables': {'x0': 1, 'x1': 10.0, 'x2': 20.0}, 
                                                      'objective functions': {'f0' : 310.11,'f1' : 25.12},
                                                      'constraints': {}}})   
    assert ka_s.get_attr('crossover') == 'real_sbx'
    assert ka_s.get_attr('mutation') == 'real_pm'
    assert ka_s.get_attr('_class') == 'local search pymoo nsga2'    
    assert ka_s.get_attr('termination_type') == 'n_eval'
    assert ka_s.get_attr('termination_criteria') == 250   
    assert ka_s.get_attr('termination') == None
    assert ka_s.get_attr('pop_size') == 25       
    assert ka_s.get_attr('n_offspring') == 10    
    assert ka_s.get_attr('initial_pop') == None  
    
    ka_s.setup_problem()

    
    assert np.array([[90.0,80.0,0.5], [75.0,65.0,0.9]]).all() == ka_s.get_attr('initial_pop').all()
    assert type(get_termination('n_eval', 250)) ==  type(ka_s.get_attr('termination'))
    problem = ka_s.get_attr('_problem')
    assert problem.n_var == 3
    assert problem.n_obj == 2
    assert problem.n_constr == 0
    assert problem.xl.all() == np.array([0, 0.0, 0.0]).all()
    assert problem.xu.all() == np.array([77, 20.0, 40.0]).all()    
    assert type(get_algorithm('nsga2', sampling=np.array([[1,10.0,10.5], [1,10.0,20.]]), pop_size=25, n_offpsring=10)) == type(ka_s.get_attr('algorithm'))
    
    ns.shutdown()
    time.sleep(0.1)     
    
def test_get_pf():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_s = run_agent(name='ka_pymoo', base=pm.PyMooAlgorithm)
    ka_s.set_attr(_design_variables={'height':     {'ll': 50.0, 'ul': 100.0, 'variable type': float},
                                     'smear':      {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                     'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}  )
    ka_s.set_attr(lvl_read= {'core_[90.0,80.0,0.5]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                                 'core_[75.0,65.0,0.9]': {'pareto type' : 'pareto', 'fitness function' : 1.0}})
    ka_s.set_attr(_lvl_data= {'core_[90.0,80.0,0.5]': {'design variables': {'height': 90.0, 'smear': 80.0, 'pu_content': 0.50},
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12}},
                                 'core_[75.0,65.0,0.9]': {'design variables': {'height': 75.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                         'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12}}})

    X = ka_s.get_pf()
    
    assert np.array([[90.0,80.0,0.5], [75.0,65.0,0.9]]).all() == X.all()
    
    ns.shutdown()
    time.sleep(0.1)        
    
def test_setup_problem():
    
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_s = run_agent(name='ka_pymoo', base=pm.PyMooAlgorithm)
    ka_s.set_attr(_design_variables={'height':     {'ll': 50.0, 'ul': 100.0, 'variable type': float},
                                     'smear':      {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                     'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}})
    ka_s.set_attr(_objectives={'reactivity swing': {'ll':0,  'ul':1500, 'goal':'lt', 'variable type': float},
                               'burnup':           {'ll':0,   'ul':150,  'goal':'gt', 'variable type': float}})
    ka_s.set_attr(_constraints={'excess reactivity':        {'ll': 0, 'ul': 30000, 'variable type': float}}) 
    
    ka_s.set_attr(lvl_read= {'core_[90.0,80.0,0.5]': {'pareto type' : 'pareto', 'fitness function' : 1.0},
                                 'core_[75.0,65.0,0.9]': {'pareto type' : 'pareto', 'fitness function' : 1.0}})
    ka_s.set_attr(_lvl_data= {'core_[90.0,80.0,0.5]': {'design variables': {'height': 90.0, 'smear': 80.0, 'pu_content': 0.50},
                                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12},
                                                      'constraints': {'excess reactivity': 2500}},
                              'core_[75.0,65.0,0.9]': {'design variables': {'height': 75.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                        'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12},
                                                        'constraints': {'excess reactivity': 5000}}})
    ka_s.set_attr(pop_size=2)
    ka_s.set_attr(n_pop=1)
    ka_s.setup_problem()
    
    assert np.array([[90.0,80.0,0.5], [75.0,65.0,0.9]]).all() == ka_s.get_attr('initial_pop').all()
    assert type(get_termination('n_eval', 250)) ==  type(ka_s.get_attr('termination'))
    problem = ka_s.get_attr('_problem')
    assert problem.n_var == 3
    assert problem.n_obj == 2
    assert problem.n_constr == 1
    assert problem.xl.all() == np.array([50.0, 50.0, 0.0]).all()
    assert problem.xu.all() == np.array([100.0, 80.0, 1.0]).all()
    assert problem.base.get_attr('_design_variables') == {'height':     {'ll': 50.0, 'ul': 100.0, 'variable type': float},
                                     'smear':      {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                     'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}    
    assert type(get_algorithm('nsga2', sampling=np.array([[90.0,80.0,0.5], [75.0,65.0,0.9]]), pop_size=31, n_offpsring=10)) == type(ka_s.get_attr('algorithm'))
    ns.shutdown()
    time.sleep(0.1)      

def test_search_method():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
    objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}
        
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')        
        
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(constraints={})
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints={})

    bb.connect_agent(pm.PyMooAlgorithm, 'ka_nsga2')
    ka = bb.get_attr('_proxy_server')
    ka_s = ka.proxy('ka_nsga2')
    ka_s.set_attr(problem=problem)            
    ka_s.set_random_seed(seed=10893) 
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[0.650,0.750,0.24]', {'design variables': {'x0': 0.650, 'x1': 0.750, 'x2': 0.24},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.750,0.24]', {'pareto type' : 'pareto', 'fitness function' : 1.0})   
    ka_s.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    ka_s.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    ka_s.set_attr(pop_size=2)
    ka_s.set_attr(n_pop=1)
    ka_s.set_attr(termination_criteria=6)

    ka_s.search_method()
    ka_s.get_attr('_class')
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.65,0.4]', 'core_[0.65,0.75,0.24]', 'core_[0.65,0.6559273381756285,0.4]', 'core_[0.5913069633410922,0.65,0.4]', 'core_[0.4455492956093361,0.65,0.4]', 'core_[0.5913069633410922,0.5932894680193752,0.4093256985734208]']
    ns.shutdown()
    time.sleep(0.1)       
    
def test_search_method_mixed():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    objs = {'f0': {'ll':0.0,    'ul':500.0, 'goal':'lt', 'variable type': float},
            'f1': {'ll':0.0,    'ul':50.0, 'goal':'lt', 'variable type': float},}
    dvs =  {'x0':  {'options' : [0.20, 0.31, 0.40, 0.44, 0.60, 0.62, 0.79, 0.80, 0.88, 0.93, 1.0, 1.20, 1.24, 1.32, 1.40, 1.55, 1.58, 1.60, 1.76, 1.80, 1.86, 2.0, 2.17, 2.20, 2.37, 2.40, 2.48, 2.60, 2.64, 2.79, 2.80, 3.0, 3.08, 3,10, 3.16, 3.41, 3.52, 3.60, 3.72, 3.95, 3.96, 4.0, 4.03, 4.20, 4.34, 4.40, 4.65, 4.74, 4.80, 4.84, 5.0, 5.28, 5.40, 5.53, 5.72, 6.0, 6.16, 6.32, 6.60, 7.11, 7.20, 7.80, 7.90, 8.0, 8.40, 8.69, 9.0, 9.48, 10.27, 11.0, 11.06, 11.85, 12.0, 13.0, 14.0, 15.0], 'variable type': float},
            'x1':  {'ll': 0.0,  'ul':20.0, 'variable type': float},
            'x2':  {'ll': 0.0,  'ul':40.0, 'variable type': float},}
        
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 're22')        
        
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(constraints={})
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints={})

    bb.connect_agent(pm.PyMooAlgorithm, 'ka_nsga2')
    ka = bb.get_attr('_proxy_server')
    ka_s = ka.proxy('ka_nsga2')
    ka_s.set_attr(problem=problem)            
    ka_s.set_random_seed(seed=10893) 
    bb.update_abstract_lvl(3, 'core_[1.0,10.0,10.5]', {'design variables': {'x0': 1.0, 'x1': 10.0, 'x2': 10.50},
                                                     'objective functions': {'f0' : 450.11, 'f1' : 35.12},
                                                     'constraints': {}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[1.0,10.0,10.5]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[1.0,10.0,20.0]', {'design variables': {'x0': 1.0, 'x1': 10.0, 'x2': 20.0}, 
                                                     'objective functions': {'f0' : 310.11,'f1' : 25.12},
                                                     'constraints': {}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[1.0,10.0,20.0]', {'pareto type' : 'pareto', 'fitness function' : 1.0})   
    ka_s.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    ka_s.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    ka_s.set_attr(pop_size=2)
    ka_s.set_attr(n_pop=1)
    ka_s.set_attr(termination_criteria=6)

    ka_s.search_method()
    ka_s.get_attr('_class')
    cores = ['core_[1.0,10.0,10.5]', 'core_[0.0,10.0,18.218799041622493]', 'core_[0.0,13.747225989026843,10.5]', 'core_[3.0,18.179701390487754,7.564838427000653]', 'core_[1.0,10.0,20.0]', 'core_[5.0,10.0,10.5]']
    assert set(list(bb.get_blackboard()['level 3']['new'].keys())) == set(cores)

    ns.shutdown()
    time.sleep(0.1)           
    
def test_force_shutdown():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
    objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}
        
    problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')        
        
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(constraints={})
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints={})
    bb.initialize_metadata_level()


    bb.connect_agent(pm.PyMooAlgorithm, 'ka_nsga2')
    ka = bb.get_attr('_proxy_server')
    ka_s = ka.proxy('ka_nsga2')
    ka_s.set_random_seed(seed=10893) 
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[0.650,0.750,0.24]', {'design variables': {'x0': 0.650, 'x1': 0.750, 'x2': 0.24},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.750,0.24]', {'pareto type' : 'pareto', 'fitness function' : 1.0})   
    ka_s.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    ka_s.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    ka_s.set_attr(pop_size=2)
    ka_s.set_attr(n_pop=1)
    ka_s.set_attr(termination_criteria=15)

    ka_s.set_attr(problem=problem, debug_wait=True, debug_wait_time=0.05)    
    bb.set_attr(final_trigger=0, _kaar = {0: {}, 1: {'ka_nsga2': 2}}, _ka_to_execute=('ka_nsga2', 2))    
    bb.send_executor()
    time.sleep(0.1)
    bb.send_shutdown()
    time.sleep(0.1)   
   
    assert ns.agents() == ['blackboard', 'ka_nsga2']
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.65,0.4]', 'core_[0.65,0.75,0.24]']

    ns.shutdown() 
    time.sleep(0.1)       