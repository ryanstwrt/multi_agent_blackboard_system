from osbrain import run_nameserver
from osbrain import run_agent
import src.ka_s.neighborhood_search as nhs
import src.bb.blackboard_optimization as bb_opt
import time
import pickle
import src.moo_benchmarks as moo

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)

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
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp_exploit')

    rp = ns.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                              'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
 
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0,65.0,0.42]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0,65.0,0.42]'])
    rp.search_method()
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[61.75,65.0,0.4]',
                                                           'core_[68.25,65.0,0.4]',
                                                           'core_[65.0,61.75,0.4]',
                                                           'core_[65.0,68.25,0.4]',
                                                           'core_[65.0,65.0,0.38]',]
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['old'].keys()] == ['core_[65.0,65.0,0.42]']
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0,65.0,0.42]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}

    ns.shutdown()
    time.sleep(0.1)
    
    
def test_search_method_discrete():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BenchmarkBbOpt)
    dv = {'x0' : {'options': ['0','1','2','3'],'default': '0','variable type': str},
          'x1' : {'options': ['0','1','2','3'],'default': '1','variable type': str},
          'x2' : {'options': ['0','1','2','3'],'default': '2','variable type': str},
          'x3' : {'options': ['0','1','2','3'],'default': '3','variable type': str}}
    obj = {'f1': {'ll': 80, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dv,objectives=obj)
    bb.set_attr(sm_type='tsp_benchmark')
    bb.set_attr(_sm=moo.optimization_test_functions('tsp'))
    bb.connect_agent(nhs.NeighborhoodSearch, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_random_seed(seed=1)
    
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