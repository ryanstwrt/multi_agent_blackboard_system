import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import time
import src.ka.ka_s.pymoo_plugin as pm
import src.bb.blackboard_optimization as bb_opt
import numpy as np
import pickle

def test_init():
    
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_s = run_agent(name='ka_pymoo', base=pm.PyMooAlgorithm)

    assert ka_s.get_attr('pymoo_algorithm_name') == 'nsga2'
    assert ka_s.get_attr('_class') == 'local search pymoo nsga2'    
    assert ka_s.get_attr('termination_type') == 'n_eval'
    assert ka_s.get_attr('termination_criteria') == 250   
    assert ka_s.get_attr('termination') == None
    assert ka_s.get_attr('pop_size') == 25       
    assert ka_s.get_attr('n_offspring') == 10    
    assert ka_s.get_attr('initial_pop') == None  
    assert ka_s.get_attr('n_partitions') == 12
    assert ka_s.get_attr('ref_dir_type') == 'das-dennis'
    assert ka_s.get_attr('ref_dirs') == None
    
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
    from pymoo.factory import get_algorithm, get_termination
    
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
    problem = ka_s.get_attr('problem')
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

    with open('./sm_gpr.pkl', 'rb') as pickle_file:
        sm_ga = pickle.load(pickle_file)        
        
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(pm.PyMooAlgorithm, 'ka_nsga2')
    ka = bb.get_attr('_proxy_server')
    ka_s = ka.proxy('ka_nsga2')
    ka_s.set_random_seed(seed=10893)    
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.75]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.75}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.75]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0,60.0,0.25]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.25}, 
                                                         'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0,60.0,0.25]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    ka_s.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    ka_s.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    ka_s.set_attr(pop_size=2)
    ka_s.set_attr(n_pop=1)
    ka_s.set_attr(termination_criteria=6)

    ka_s.search_method()
    ka_s.get_attr('_class')
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[65.0,65.0,0.75]', 'core_[70.0,60.0,0.25]', 'core_[65.0,65.11826218482396,0.75]', 'core_[63.23921054183972,65.0,0.75]', 'core_[60.627285073278316,65.11826218482396,0.75]', 'core_[65.0,63.98405154463569,0.7593013064317452]']
    ns.shutdown()
    time.sleep(0.1)       