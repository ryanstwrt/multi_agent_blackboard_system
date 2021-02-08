from osbrain import run_nameserver
from osbrain import run_agent
import src.ka.ka_s.genetic_algorithm as ga
import src.bb.blackboard_optimization as bb_opt
import time
import pickle

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)

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
    
def test_KaLocalGA():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_trigger_number=2)
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.1]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.1]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0,60.0,0.25]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.25}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0,60.0,0.25]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')

    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[65.0,65.0,0.25]','core_[70.0,60.0,0.1]']
    
    bb.update_abstract_lvl(3, 'core_[90.0,80.0,0.5]', {'design variables': {'height': 90.0, 'smear': 80.0, 'pu_content': 0.50},
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[90.0,80.0,0.5]', {'pareto type' : 'pareto', 'fitness function' : 1.0})    
    bb.update_abstract_lvl(3, 'core_[75.0,65.0,0.9]', {'design variables': {'height': 75.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                         'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[75.0,65.0,0.9]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp.set_attr(offterstspring_per_generation=2)
    rp.set_attr(lvl_read=bb.get_blackboard()['level 1'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[65.0,65.0,0.25]','core_[70.0,60.0,0.1]', 'core_[65.0,60.0,0.25]', 'core_[70.0,65.0,0.1]']
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_KaGa_lvl_2():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_trigger_number=2)
    rp.set_attr(bb_lvl_read=2)
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.1]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(2, 'core_[65.0,65.0,0.1]', {'valid' : True}, panel='new')
    bb.update_abstract_lvl(3, 'core_[70.0,60.0,0.25]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.25}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(2, 'core_[70.0,60.0,0.25]', {'valid' : True}, panel='new')
    rp.set_attr(lvl_read=bb.get_blackboard()['level 2'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')

    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[65.0,65.0,0.25]','core_[70.0,60.0,0.1]']
    
    bb.update_abstract_lvl(3, 'core_[80.0,70.0,0.5]', {'design variables': {'height': 80.0, 'smear': 70.0, 'pu_content': 0.50},
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12}}, panel='old')
    
    bb.update_abstract_lvl(2, 'core_[80.0,70.0,0.5]', {'valid' : True}, panel='new')    
    bb.update_abstract_lvl(3, 'core_[75.0,65.0,0.9]', {'design variables': {'height': 75.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                         'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(2, 'core_[75.0,65.0,0.9]', {'valid' : True}, panel='new')
    
    rp.set_attr(offspring_per_generation=2)
    rp.set_attr(lvl_read=bb.get_blackboard()['level 2'])
    rp.set_attr(_lvl_data=bb.get_blackboard()['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[65.0,65.0,0.25]','core_[70.0,60.0,0.1]', 'core_[80.0,65.0,0.9]', 'core_[75.0,70.0,0.5]']
    
    ns.shutdown()
    time.sleep(0.1)
def test_KaGa_handler_publish():
    pass
    
def test_KaLocalGA_linear_crossover():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)

    bb.initialize_abstract_level_3()

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_trigger_number=2)
    rp.set_attr(crossover_type='linear crossover')
    bb.update_abstract_lvl(3, 'core_[50.0,60.0,0.1]', {'design variables': {'height': 50.0, 'smear': 60.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[50.0,60.0,0.1]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0,70.0,0.2]', {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0,70.0,0.2]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    print
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[60.0,65.0,0.15]','core_[50.0,55.0,0.05]','core_[80.0,70.0,0.25]']
    solutions = ['core_[60.0,65.0,0.15]','core_[50.0,55.0,0.05]','core_[80.0,70.0,0.25]']
    for solution in solutions:
        assert solution in [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()]
    
    bb.update_abstract_lvl(3, 'core_[90.0,80.0,0.5]', {'design variables': {'height': 90.0, 'smear': 80.0, 'pu_content': 0.50},
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[90.0,80.0,0.5]', {'pareto type' : 'pareto', 'fitness function' : 1.0})    
    bb.update_abstract_lvl(3, 'core_[75.0,65.0,0.9]', {'design variables': {'height': 55.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                         'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[75.0,65.0,0.9]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp.set_attr(offspring_per_generation=4)
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[60.0,65.0,0.15]','core_[50.0,55.0,0.05]','core_[80.0,70.0,0.25]','core_[80.0,70.0,0.65]','core_[60.0,65.0,0.05]']
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_KaLocalGA_full():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_size=2)
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.42]', {'design variables': {'height': 65.0, 'smear': 65.0,  'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0,60.0,0.50]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0,60.0,0.50]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    assert rp.get_attr('analyzed_design') == {}
    bb.publish_trigger()
    time.sleep(0.075)
    bb.controller()
    bb.send_executor()
    time.sleep(0.075)
    assert rp.get_attr('analyzed_design') == {'core_[65.0,65.0,0.42]': {'Analyzed': True}, 'core_[70.0,60.0,0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[65.0,65.0,0.5]', 'core_[70.0,60.0,0.42]']

    # Make sure we don't recombine already examined results
    bb.publish_trigger()
    time.sleep(0.075)
    bb.controller()
    bb.send_executor()  
    time.sleep(0.075)
    assert rp.get_attr('analyzed_design') == {'core_[65.0,65.0,0.42]': {'Analyzed': True}, 'core_[70.0,60.0,0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[65.0,65.0,0.5]','core_[70.0,60.0,0.42]']

    # Reduce the PF size and ensure we don't execute the GA_KA
    rp.set_attr(pf_size=1)    
    bb.remove_bb_entry(1, 'core_[65.0,65.0,0.42]')
    bb.publish_trigger()
    time.sleep(0.075)
    bb.controller()
    bb.send_executor()  
    time.sleep(0.075)
    assert rp.get_attr('analyzed_design') == {'core_[65.0,65.0,0.42]': {'Analyzed': True}, 'core_[70.0,60.0,0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[65.0,65.0,0.5]','core_[70.0,60.0,0.42]']
    
    ns.shutdown()
    time.sleep(0.1)

def test_kaga_single_point_crossover():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_attr(_design_variables={'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                  'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                  'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float},
                                  'exp': {'options': ['exp1', 'expb', 'exp4'], 'default': 'exp1', 'variable type': str}})
    rp.set_random_seed(seed=1073)
    genotype1 = {'design variables': {'height':70.0,'smear':65.0,'pu_content':0.50, 'exp': 'exp1'},
                 'objectives': {},
                 'constraints': {}}
    genotype2 = {'design variables': {'height':80.0,'smear':55.0,'pu_content':0.75, 'exp': 'expb'},}
    new_genotype = rp.single_point_crossover(genotype1, genotype2, 2)
    assert new_genotype == [{'height': 70.0, 'smear': 65.0, 'pu_content': 0.75, 'exp': 'expb'},
                            {'height': 80.0, 'smear': 55.0, 'pu_content': 0.5, 'exp': 'exp1'}]   
 

    ns.shutdown()
    time.sleep(0.1)
    
def test_kaga_random_mutation():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_attr(_design_variables={'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float},
                                  'exp': {'options': ['exp1', 'expb', 'exp4'], 'default': 'exp1', 'variable type': str}})
    rp.set_random_seed(seed=1073)
    genotype = {'height':70.0,'smear':65.0,'pu_content':0.5, 'exp': 'exp1'}
    new_genotype = rp.random_mutation(genotype)
    assert new_genotype == {'height': 70.0, 'smear': 65.0, 'pu_content': 0.50213, 'exp': 'exp1'}    
    rp.set_random_seed(seed=10994)
    new_genotype = rp.random_mutation(genotype)
    assert new_genotype == {'height': 70.0, 'smear': 65.0, 'pu_content': 0.5, 'exp': 'exp4'}    

    ns.shutdown()
    time.sleep(0.1)
    
def test_kaga_non_uniform_mutation():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    genotype = {'height':55.0,'smear':65.0,'pu_content':0.5}
    new_genotype = rp.non_uniform_mutation(genotype)
    assert new_genotype == {'height': 55.0, 'smear': 65.0, 'pu_content': 0.83409}

    ns.shutdown()
    time.sleep(0.1)
    
def test_KaLocalGA_crossover_mutate():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ga.GeneticAlgorithm, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=1.0)
    rp.set_attr(pf_trigger_number=2)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='random')
    bb.update_abstract_lvl(3, 'core_[50.0,60.0,0.1]', {'design variables': {'height': 50.0, 'smear': 60.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[50.0,60.0,0.1]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0,70.0,0.2]', {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0,70.0,0.2]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[50.0,60.0,0.19013]','core_[70.0,70.0,0.1]']
    rp.set_random_seed(seed=1073)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='non-uniform')    
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[50.0,60.0,0.19013]','core_[70.0,70.0,0.1]','core_[50.0,60.0,0.32809]','core_[70.0,50.0,0.1]']
    rp.set_random_seed(seed=1073)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='nonsense')    
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[50.0,60.0,0.19013]','core_[70.0,70.0,0.1]','core_[50.0,60.0,0.32809]','core_[70.0,50.0,0.1]']
    
    ns.shutdown()
    time.sleep(0.1)
    