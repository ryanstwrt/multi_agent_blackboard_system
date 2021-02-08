from osbrain import run_nameserver
from osbrain import run_agent
import src.ka_s.hill_climb as hc
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
    rp = run_agent(name='ka_rp', base=hc.HillClimb)
    
    assert rp.get_attr('_base_trigger_val') == 5.00001
    assert rp.get_attr('avg_diff_limit') == 5
    assert rp.get_attr('step_size') == 0.1
    assert rp.get_attr('step_rate') == 0.1
    assert rp.get_attr('step_limit') == 100
    assert rp.get_attr('convergence_criteria') == 0.001
    assert rp.get_attr('hc_type') == 'simple'
    assert rp.get_attr('_class') == 'local search hc'


    ns.shutdown()
    time.sleep(0.1)
    
def test_determine_step_steepest_ascent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float},
            'eol keff':         {'ll':1.0, 'ul':2.0,   'goal':'et', 'target': 1.5, 'variable type': float},
            'power':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'max'}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(hc.HillClimb, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(hc_type='steepest ascent')
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.1, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    # Test an increase in burnup (greater than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.1, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12, 'eol keff': 1.1, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12, 'eol keff': 1.1, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff,3) == 0.09
    assert pert == '+ height'
    
    # Test an increase in reactivity swing (less than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.1, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 680.11, 'burnup' : 61.12, 'eol keff': 1.1, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 61.12, 'eol keff': 1.1, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.053
    assert pert == '+ pu_content'
    
    # Test an increase in keff (equal to test - below value)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.1, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.4, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.3, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 20.0
    assert pert == '+ pu_content'

    # Test an increase in keff (equal to test - above vaalue)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.9, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.7, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 20.0
    assert pert == '+ pu_content'
    
    # Test an increase in keff (equal to test - cross the value)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.45, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.57, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 3.333
    assert pert == '+ pu_content'
    
    # Test an increase in power ()
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.45, 'power': [1.0,2.0,2.5]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.57, 'power': [1.0,2.0,2.75]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 5.0
    assert pert == '+ pu_content'
    
    # Test a postive a change in two objectives
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 60.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 680.11, 'burnup' : 67.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.138
    assert pert == '+ height'

    # Test a postive a change in both objectives (both have of ~0.078, but + pu_content is slightly greater})
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 661.51, 'burnup' : 60.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 67.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.078
    assert pert == '+ pu_content'
    
    # Test a case with no change in design variables
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 661.51, 'burnup' : 60.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 67.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert diff  == None
    assert pert == None
    
    # Test a postive a change in both objectives (both have of ~0.078, but + pu_content is slightly greater})
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 661.51, 'burnup' : 60.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 0.9}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 67.12, 'eol keff': 1.6, 'power': [1.0,2.0,3.0]},
                                                          'constraints': {'eol keff': 2.8}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert diff  == None
    assert pert == None
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_determine_step_simple():
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

    bb.connect_agent(hc.HillClimb, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12},
                                                          'constraints': {'eol keff': 1.1}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    # Test an increase in burnup (greater than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert pert == '+ height'
    
    # Test multiple increases 
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12},
                                                          'constraints': {'eol keff': 1.1}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12},
                                                          'constraints': {'eol keff': 1.1}},
                   '- height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 650.11, 'burnup' : 62.12},
                                                          'constraints': {'eol keff': 1.1}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert pert == '+ height' or '- height'

    ns.shutdown()
    time.sleep(0.1)
    
    
def test_determine_step_simple_discrete_dv():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BenchmarkBbOpt)
    dv = {'x0' : {'options': ['0', '1', '2', '3'], 'default': '0', 'variable type': str},
          'x1' : {'options': ['0', '1', '2', '3'], 'default': '1', 'variable type': str},
          'x2' : {'options': ['0', '1', '2', '3'], 'default': '2', 'variable type': str},
          'x3' : {'options': ['0', '1', '2', '3'], 'default': '3', 'variable type': str}}
    obj = {'f1': {'ll': 80, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dv,objectives=obj)
    bb.set_attr(sm_type='tsp_benchmark')
    bb.set_attr(_sm=moo.optimization_test_functions('tsp'))
    bb.connect_agent(hc.HillClimb, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_random_seed(seed=1)
    rp.set_attr(hc_type='steepest ascent')
    
    rp.set_attr(new_designs=['core_1'])
    rp.set_attr(_lvl_data={'core_1': {'design variables': {'x0': '0', 
                                                          'x1': '1',
                                                          'x2': '2',
                                                          'x3': '3'}}})
    

    base = {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '3'}
    base_design =  {'f1': 100}
    design_dict = {'+ x0' : {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '3'}, 
                           'objective functions': {'f1': 95},
                                                          'constraints': {}},
                   '+ x1' : {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '3'}, 
                           'objective functions': {'f1': 81},
                                                          'constraints': {}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    assert pert == '+ x1'
    assert round(diff, 5) == 0.15833
    ns.shutdown()
    time.sleep(0.1)
    
    
def test_search_method_steepest_ascent():
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

    bb.connect_agent(hc.HillClimb, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(step_size=0.2)
    rp.set_attr(step_rate=0.5)
    rp.set_attr(step_limit=1)
    rp.set_attr(convergence_criteria=0.001)
    rp.set_attr(hc_type='steepest ascent')
    rp.set_random_seed(seed=1099)
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    bb.update_abstract_lvl(3, 'core_[78.65,65.0,0.42]', {'design variables': {'height': 78.65, 'smear': 65.0, 'pu_content': 0.42}, 
                                                           'objective functions': {'reactivity swing' : 447.30449, 'burnup' : 490.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0,65.0,0.42]'])

    rp.search_method()  
    time.sleep(0.075)
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[65.0,65.0,0.336]', 'core_[65.0,65.0,0.504]', 'core_[65.0,52.0,0.42]', 'core_[52.0,65.0,0.42]', 'core_[78.0,65.0,0.42]', 'core_[65.0,65.0,0.2688]', 'core_[65.0,65.0,0.4032]', 'core_[65.0,52.0,0.336]', 'core_[52.0,65.0,0.336]', 'core_[78.0,65.0,0.336]', ]

    rp.set_attr(step_limit=5000)
    rp.set_random_seed(seed=1099)
    rp.search_method()
    time.sleep(0.075)
        
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[65.0,65.0,0.336]', 'core_[65.0,65.0,0.504]', 'core_[65.0,52.0,0.42]', 'core_[52.0,65.0,0.42]', 'core_[78.0,65.0,0.42]', 'core_[65.0,65.0,0.2688]', 'core_[65.0,65.0,0.4032]', 'core_[65.0,52.0,0.336]', 'core_[52.0,65.0,0.336]', 'core_[78.0,65.0,0.336]', 'core_[65.0,65.0,0.21504]', 'core_[65.0,65.0,0.32256]', 'core_[65.0,52.0,0.2688]', 'core_[52.0,65.0,0.2688]', 'core_[78.0,65.0,0.2688]', 'core_[65.0,65.0,0.17203]', 'core_[65.0,65.0,0.25805]', 'core_[65.0,52.0,0.21504]', 'core_[52.0,65.0,0.21504]', 'core_[78.0,65.0,0.21504]', 'core_[65.0,65.0,0.13762]', 'core_[65.0,65.0,0.20644]', 'core_[65.0,52.0,0.17203]', 'core_[52.0,65.0,0.17203]', 'core_[78.0,65.0,0.17203]', 'core_[65.0,65.0,0.1101]', 'core_[65.0,65.0,0.16514]', 'core_[65.0,52.0,0.13762]', 'core_[52.0,65.0,0.13762]', 'core_[78.0,65.0,0.13762]', 'core_[78.0,65.0,0.1101]', 'core_[78.0,65.0,0.16514]', 'core_[78.0,52.0,0.13762]', 'core_[62.4,65.0,0.13762]', 'core_[78.0,65.0,0.12386]', 'core_[78.0,65.0,0.15138]', 'core_[78.0,58.5,0.13762]', 'core_[70.2,65.0,0.13762]', 'core_[78.0,65.0,0.11147]', 'core_[78.0,65.0,0.13625]', 'core_[78.0,58.5,0.12386]', 'core_[70.2,65.0,0.12386]', 'core_[78.0,65.0,0.10032]', 'core_[78.0,65.0,0.12262]', 'core_[78.0,58.5,0.11147]', 'core_[70.2,65.0,0.11147]', 'core_[78.0,65.0,0.1059]', 'core_[78.0,65.0,0.11704]', 'core_[78.0,61.75,0.11147]', 'core_[78.0,68.25,0.11147]', 'core_[74.1,65.0,0.11147]', 'core_[78.0,68.25,0.1059]', 'core_[78.0,68.25,0.11704]', 'core_[78.0,64.8375,0.11147]', 'core_[74.1,68.25,0.11147]', 'core_[78.0,68.25,0.10868]', 'core_[78.0,68.25,0.11426]', 'core_[78.0,66.54375,0.11147]', 'core_[78.0,69.95625,0.11147]', 'core_[76.05,68.25,0.11147]', 'core_[79.95,68.25,0.11147]', 'core_[79.95,68.25,0.10868]', 'core_[79.95,68.25,0.11426]', 'core_[79.95,66.54375,0.11147]', 'core_[79.95,69.95625,0.11147]', 'core_[77.95125,68.25,0.11147]', 'core_[79.95,69.95625,0.10868]', 'core_[79.95,69.95625,0.11426]', 'core_[79.95,68.20734,0.11147]', 'core_[77.95125,69.95625,0.11147]', 'core_[79.95,69.95625,0.11008]', 'core_[79.95,69.95625,0.11286]', 'core_[79.95,69.0818,0.11147]', 'core_[78.95063,69.95625,0.11147]', 'core_[79.95,69.95625,0.11145]', 'core_[79.95,69.95625,0.11427]', 'core_[79.95,69.0818,0.11286]', 'core_[78.95063,69.95625,0.11286]', 'core_[79.95,69.95625,0.11215]', 'core_[79.95,69.95625,0.11357]', 'core_[79.95,69.51902,0.11286]', 'core_[79.45031,69.95625,0.11286]', 'core_[79.95,69.95625,0.11285]', 'core_[79.95,69.51902,0.11215]', 'core_[79.45031,69.95625,0.11215]', 'core_[79.95,69.95625,0.11214]', 'core_[79.95,69.95625,0.11356]', 'core_[79.95,69.51902,0.11285]', 'core_[79.45031,69.95625,0.11285]', 'core_[79.95,69.95625,0.1125]', 'core_[79.95,69.95625,0.1132]', 'core_[79.95,69.73764,0.11285]', 'core_[79.70016,69.95625,0.11285]', 'core_[79.95,69.73764,0.1125]', 'core_[79.70016,69.95625,0.1125]', 'core_[79.95,69.95625,0.11232]', 'core_[79.95,69.95625,0.11268]', 'core_[79.95,69.84694,0.1125]', 'core_[79.82508,69.95625,0.1125]']

    ns.shutdown()
    time.sleep(0.1)

    
def test_search_method_simple():
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

    bb.connect_agent(hc.HillClimb, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(step_size=0.20)
    rp.set_attr(step_rate=0.2)
    rp.set_attr(step_limit=1)
    rp.set_attr(convergence_criteria=0.01)
    rp.set_random_seed(seed=1073)
    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0,65.0,0.42]'])
    rp.search_method()
    time.sleep(0.075)
    rp.set_attr(step_limit=100)
    assert list(bb.get_blackboard()['level 3']['new'].keys()) ==     ['core_[65.0,65.0,0.336]', 'core_[52.0,65.0,0.336]', 'core_[65.0,65.0,0.2688]']
    rp.search_method()
    time.sleep(0.075)   

    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[65.0,65.0,0.336]', 'core_[52.0,65.0,0.336]', 'core_[65.0,65.0,0.2688]', 'core_[65.0,52.0,0.336]', 'core_[65.0,65.0,0.4032]', 'core_[65.0,65.0,0.32256]', 'core_[52.0,65.0,0.2688]', 'core_[78.0,65.0,0.2688]', 'core_[78.0,65.0,0.21504]', 'core_[78.0,65.0,0.17203]', 'core_[78.0,65.0,0.13762]', 'core_[78.0,65.0,0.1101]', 'core_[62.4,65.0,0.1101]', 'core_[78.0,65.0,0.13212]', 'core_[78.0,65.0,0.08808]', 'core_[78.0,52.0,0.1101]', 'core_[78.0,65.0,0.09248]', 'core_[78.0,65.0,0.12772]', 'core_[65.52,65.0,0.1101]', 'core_[78.0,54.6,0.1101]', 'core_[68.016,65.0,0.1101]', 'core_[78.0,56.68,0.1101]', 'core_[78.0,65.0,0.09601]', 'core_[78.0,65.0,0.12419]', 'core_[70.0128,65.0,0.1101]', 'core_[78.0,58.344,0.1101]', 'core_[78.0,65.0,0.09883]', 'core_[78.0,65.0,0.12137]', 'core_[78.0,65.0,0.10108]', 'core_[78.0,65.0,0.11912]', 'core_[71.61024,65.0,0.1101]', 'core_[78.0,59.6752,0.1101]', 'core_[72.88819,65.0,0.1101]', 'core_[78.0,65.0,0.11732]', 'core_[78.0,69.25984,0.1101]', 'core_[78.0,69.25984,0.10288]', 'core_[78.0,64.72083,0.1101]', 'core_[78.0,69.25984,0.11732]', 'core_[72.88819,69.25984,0.1101]', 'core_[78.0,69.25984,0.10433]', 'core_[73.91055,69.25984,0.1101]', 'core_[78.0,65.62863,0.1101]', 'core_[78.0,69.25984,0.11587]', 'core_[78.0,69.25984,0.10548]', 'core_[78.0,69.25984,0.11472]', 'core_[74.72844,69.25984,0.1101]', 'core_[78.0,66.35487,0.1101]', 'core_[78.0,66.93587,0.1101]', 'core_[75.38275,69.25984,0.1101]', 'core_[78.0,69.25984,0.10641]', 'core_[78.0,69.25984,0.11379]', 'core_[78.0,69.25984,0.11306]', 'core_[78.0,67.40066,0.1101]', 'core_[75.9062,69.25984,0.1101]', 'core_[78.0,69.25984,0.10714]', 'core_[78.0,67.7725,0.1101]', 'core_[78.0,69.25984,0.11246]', 'core_[79.67504,69.25984,0.1101]', 'core_[77.96403,69.25984,0.1101]', 'core_[79.67504,69.25984,0.10774]', 'core_[79.67504,67.7725,0.1101]', 'core_[79.67504,69.25984,0.11246]', 'core_[79.67504,67.7725,0.11246]', 'core_[79.67504,69.25984,0.11488]', 'core_[77.96403,69.25984,0.11246]', 'core_[79.67504,69.25984,0.11004]', 'core_[79.67504,69.25984,0.11053]', 'core_[79.67504,69.25984,0.11439]', 'core_[78.30623,69.25984,0.11246]', 'core_[79.67504,68.06997,0.11246]', 'core_[79.67504,69.25984,0.11401]', 'core_[79.67504,69.25984,0.11558]', 'core_[79.67504,68.30794,0.11401]', 'core_[78.57999,69.25984,0.11401]', 'core_[79.67504,69.25984,0.11244]', 'core_[79.67504,68.49832,0.11401]', 'core_[79.67504,69.25984,0.11276]', 'core_[79.67504,69.25984,0.11152]', 'core_[78.799,69.25984,0.11276]', 'core_[79.67504,69.25984,0.114]', 'core_[79.67504,68.49832,0.11276]']
    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method_discrete_dv():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BenchmarkBbOpt)
    dv = {'x0' : {'options': ['0', '1', '2', '3'], 'default': '0', 'variable type': str},
          'x1' : {'options': ['0', '1', '2', '3'], 'default': '1', 'variable type': str},
          'x2' : {'options': ['0', '1', '2', '3'], 'default': '2', 'variable type': str},
          'x3' : {'options': ['0', '1', '2', '3'], 'default': '3', 'variable type': str}}
    obj = {'f1': {'ll': 10, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dv,objectives=obj)
    bb.set_attr(sm_type='tsp_benchmark')
    bb.set_attr(_sm=moo.optimization_test_functions('tsp'))
    bb.connect_agent(hc.HillClimb, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_attr(step_limit=10)
    rp.set_random_seed(seed=109875)
    rp.set_attr(hc_type='steepest ascent')
    
    bb.update_abstract_lvl(3, 'core_[3,1,2,0]', {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '3'},
                                                   'objective functions': {'f1': 95.0},
                                                   'constraints': {}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[3,1,2,0]', {'pareto type' : 'pareto', 'fitness function' : 1.0})

    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    rp.set_attr(new_designs=['core_[3,1,2,0]'])
   
    rp.search_method()
    time.sleep(0.5)

    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0,1,2,0]', 'core_[0,1,3,3]', 'core_[0,2,2,3]', 'core_[3,1,2,3]', 'core_[0,1,3,2]', 'core_[0,1,2,3]', 'core_[0,0,3,3]', 'core_[1,1,3,3]', 'core_[0,0,3,0]', 'core_[0,0,1,3]', 'core_[0,3,3,3]', 'core_[1,0,3,3]', 'core_[0,0,3,2]', 'core_[0,0,2,3]', 'core_[3,0,3,3]', 'core_[0,0,3,1]', 'core_[0,2,3,3]', 'core_[0,0,0,3]', 'core_[2,0,3,3]']
    
    ns.shutdown()
    time.sleep(0.1)    