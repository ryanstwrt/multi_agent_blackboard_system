from osbrain import run_nameserver
from osbrain import run_agent
import src.ka.ka_s.genetic_algorithm as ga
import src.bb.blackboard_optimization as bb_opt
from src.utils.problem import BenchmarkProblem
from src.utils.problem import SFRProblem
import time
from src.utils.problem import BenchmarkProblem

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
    rp = run_agent(name='ka_rp', base=ga.GeneticAlgorithm)

    assert rp.get_attr('_base_trigger_val') == 5.00001
    assert rp.get_attr('previous_populations') == {}
    assert rp.get_attr('crossover_rate') == 0.8
    assert rp.get_attr('offspring_per_generation') == 20
    assert rp.get_attr('mutation_rate') == 0.1
    assert rp.get_attr('perturbation_size') == 0.05
    assert rp.get_attr('crossover_type') == 'single point'
    assert rp.get_attr('num_cross_over_points') == 1
    assert rp.get_attr('mutation_type') == 'random'
    assert rp.get_attr('pf_size') == 40  
    assert rp.get_attr('b') == 2    
    assert rp.get_attr('k') == 5    
    assert rp.get_attr('T') == 100        
    assert rp.get_attr('_class') == 'local search genetic algorithm'

    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.set_attr(problem=problem)

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[0.650,0.750,0.24]', {'design variables': {'x0': 0.650, 'x1': 0.750, 'x2': 0.24},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.750,0.24]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')

    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.65,0.24]', 'core_[0.65,0.75,0.4]']
    
    bb.update_abstract_lvl(3, 'core_[0.950,0.50,0.84]', {'design variables': {'x0': 0.950, 'x1': 0.50, 'x2': 0.84},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.950,0.50,0.84]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[0.250,0.70,0.2]', {'design variables': {'x0': 0.950, 'x1': 0.50, 'x2': 0.84},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.250,0.70,0.2]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.65,0.24]', 'core_[0.65,0.75,0.4]', 'core_[0.95,0.5,0.84]', 'core_[0.65,0.75,0.24]', 'core_[0.65,0.65,0.4]']
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method_lvl_2():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)        
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(bb_lvl_read=2)
    
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(2, 'core_[0.650,0.650,0.4]', {'valid' : True}, panel='new')
    bb.update_abstract_lvl(3, 'core_[0.650,0.750,0.24]', {'design variables': {'x0': 0.650, 'x1': 0.750, 'x2': 0.24},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(2, 'core_[0.650,0.750,0.24]', {'valid' : True}, panel='new')
    rp.set_attr(lvl_read=bb.get_blackboard()['level 2'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')        
        
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.65,0.24]', 'core_[0.65,0.75,0.4]']
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_handler_publish():
    pass
    
def test_linear_crossover():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)        
    rp.set_attr(crossover_type='linear crossover')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[0.650,0.750,0.24]', {'design variables': {'x0': 0.650, 'x1': 0.750, 'x2': 0.24},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.750,0.24]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
        
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'].keys()) == ['core_[0.65,0.7,0.32]', 'core_[0.65,0.6,0.48]', 'core_[0.65,0.8,0.16]']
    
    bb.update_abstract_lvl(3, 'core_[0.950,0.50,0.84]', {'design variables': {'x0': 0.950, 'x1': 0.50, 'x2': 0.84},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.950,0.50,0.84]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[0.250,0.70,0.2]', {'design variables': {'x0': 0.950, 'x1': 0.50, 'x2': 0.84},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.250,0.70,0.2]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.7,0.32]', 'core_[0.65,0.6,0.48]', 'core_[0.65,0.8,0.16]', 'core_[0.8,0.625,0.54]', 'core_[1.0,0.375,1.0]', 'core_[0.5,0.875,0.0]', 'core_[0.8,0.575,0.62]', 'core_[0.5,0.725,0.18]', 'core_[1.0,0.425,1.0]']
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_publish_execute():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
        
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)        
    rp.set_attr(crossover_type='linear crossover')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_size=2)
    
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[0.650,0.750,0.24]', {'design variables': {'x0': 0.650, 'x1': 0.750, 'x2': 0.24},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.750,0.24]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.get_attr('_class')
    
    assert rp.get_attr('analyzed_design') == {}
    bb.publish_trigger()
    time.sleep(0.075)
    bb.controller()
    bb.send_executor()
    time.sleep(0.075)
    assert rp.get_attr('analyzed_design') == {'core_[0.650,0.750,0.24]': {'Analyzed': True}, 'core_[0.650,0.650,0.4]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[0.65,0.7,0.32]', 'core_[0.65,0.6,0.48]', 'core_[0.65,0.8,0.16]']

    # Make sure we don't recombine already examined results
    bb.publish_trigger()
    time.sleep(0.075)
    bb.controller()
    bb.send_executor()  
    time.sleep(0.075)
    assert rp.get_attr('analyzed_design') == {'core_[0.650,0.750,0.24]': {'Analyzed': True}, 'core_[0.650,0.650,0.4]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[0.65,0.7,0.32]', 'core_[0.65,0.6,0.48]', 'core_[0.65,0.8,0.16]']

    # Reduce the PF size and ensure we don't execute the GA_KA
    rp.set_attr(pf_size=1)    
    bb.remove_bb_entry(1, 'core_[0.650,0.750,0.24]')
    bb.publish_trigger()
    time.sleep(0.075)
    bb.controller()
    bb.send_executor()  
    time.sleep(0.075)  
    assert rp.get_attr('analyzed_design') == {'core_[0.650,0.650,0.4]': {'Analyzed': True}, 'core_[0.650,0.750,0.24]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[0.65,0.7,0.32]', 'core_[0.65,0.6,0.48]', 'core_[0.65,0.8,0.16]']
    
    ns.shutdown()
    time.sleep(0.1)

def test_single_point_crossover():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    genotype1 = {'design variables': {'x0':0.700,'x1':0.650,'x2':0.50}}
    genotype2 = {'design variables': {'x0':0.800,'x1':0.550,'x2':0.75}}
    new_genotype = rp.single_point_crossover(genotype1, genotype2, 2)
    assert new_genotype == [{'x0': 0.700, 'x1': 0.650, 'x2': 0.75}, {'x0': 0.800, 'x1': 0.550, 'x2': 0.5}]   
 
    ns.shutdown()
    time.sleep(0.1)
    
def test_random_mutation():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    genotype =  {'x0':0.700,'x1':0.650,'x2':0.50}
    new_genotype = rp.random_mutation(genotype)
    assert new_genotype == {'x0': 0.700, 'x1': 0.650, 'x2': 0.50213}    
    rp.set_random_seed(seed=10994)
    new_genotype = rp.random_mutation(genotype)
    assert new_genotype == {'x0': 0.700, 'x1': 0.650, 'x2': 0.47688}    

    ns.shutdown()
    time.sleep(0.1)
    
def test_non_uniform_mutation():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    genotype =  {'x0':0.700,'x1':0.650,'x2':0.50}
    new_genotype = rp.non_uniform_mutation(genotype)
    assert new_genotype == {'x0': 0.700, 'x1': 0.650, 'x2': 0.83409}

    ns.shutdown()
    time.sleep(0.1)
    
def test_crossover_mutate():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)        
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=1.0)
    rp.set_attr(pf_trigger_number=2)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='random')    
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[0.650,0.750,0.24]', {'design variables': {'x0': 0.650, 'x1': 0.750, 'x2': 0.24},
                                                          'objective functions': {'f0': 36.0, 'f1': 50.0, 'f2' : 60.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[0.650,0.750,0.24]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
        
    assert list(bb.get_attr('abstract_lvls')['level 3']['new']) == ['core_[0.65,0.65,0.22815]', 'core_[0.65,0.75155,0.4]']
    rp.set_random_seed(seed=1073)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='non-uniform')    
    rp.search_method()
    rp.get_attr('_class')
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'])  == ['core_[0.65,0.65,0.22815]', 'core_[0.65,0.75155,0.4]', 'core_[0.65,0.65,0.39371]', 'core_[0.65,0.0039,0.4]']
    rp.set_random_seed(seed=1073)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='nonsense')    
    rp.search_method()
    rp.get_attr('_class')
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'])  == ['core_[0.65,0.65,0.22815]', 'core_[0.65,0.75155,0.4]', 'core_[0.65,0.65,0.39371]', 'core_[0.65,0.0039,0.4]']
    
    ns.shutdown()
    time.sleep(0.1)
    