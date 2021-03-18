from osbrain import run_nameserver
from osbrain import run_agent
import src.ka.ka_s.hill_climb as hc
import src.bb.blackboard_optimization as bb_opt
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

    dvs = {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
          'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
          'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float},
            'eol keff':         {'ll':1.0, 'ul':2.0,   'goal':'et', 'target': 1.5, 'variable type': float},
            'power':        {'ll':0,   'ul':10,   'goal':'lt', 'variable type': list, 'goal type':'max'}}
    cons = {'eol keff':         {'ll':1.0, 'ul':2.5, 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints=cons)

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
    
    # Test a constraint violation
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

    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    dvs = {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
          'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
          'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    cons = {'eol keff':         {'ll':1.0, 'ul':2.5, 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints=cons)

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
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv = {'x0' : {'options': ['0', '1', '2', '3'], 'default': '0', 'variable type': str},
          'x1' : {'options': ['0', '1', '2', '3'], 'default': '1', 'variable type': str},
          'x2' : {'options': ['0', '1', '2', '3'], 'default': '2', 'variable type': str},
          'x3' : {'options': ['0', '1', '2', '3'], 'default': '3', 'variable type': str}}
    obj = {'f1': {'ll': 80, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dv,objectives=obj)
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
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(hc.HillClimb, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)        
    rp.set_attr(step_size=0.2)
    rp.set_attr(step_rate=0.5)
    rp.set_attr(step_limit=1)
    rp.set_attr(convergence_criteria=0.001)
    rp.set_attr(hc_type='steepest ascent')
    rp.set_random_seed(seed=1099)
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[0.650,0.650,0.4]'])

    rp.search_method()  
    time.sleep(0.075)
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.65,0.32]', 'core_[0.65,0.65,0.48]', 'core_[0.65,0.52,0.4]', 'core_[0.65,0.78,0.4]', 'core_[0.52,0.65,0.4]', 'core_[0.78,0.65,0.4]', 'core_[0.65,0.65,0.384]', 'core_[0.65,0.65,0.576]', 'core_[0.65,0.52,0.48]', 'core_[0.65,0.78,0.48]', 'core_[0.52,0.65,0.48]', 'core_[0.78,0.65,0.48]']

    rp.set_attr(step_limit=25)
    rp.set_random_seed(seed=1099)
    rp.search_method()
    time.sleep(0.075)
        
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.65,0.32]', 'core_[0.65,0.65,0.48]', 'core_[0.65,0.52,0.4]', 'core_[0.65,0.78,0.4]', 'core_[0.52,0.65,0.4]', 'core_[0.78,0.65,0.4]', 'core_[0.65,0.65,0.384]', 'core_[0.65,0.65,0.576]', 'core_[0.65,0.52,0.48]', 'core_[0.65,0.78,0.48]', 'core_[0.52,0.65,0.48]', 'core_[0.78,0.65,0.48]', 'core_[0.65,0.65,0.3072]', 'core_[0.65,0.65,0.4608]', 'core_[0.65,0.52,0.384]', 'core_[0.65,0.78,0.384]', 'core_[0.52,0.65,0.384]', 'core_[0.78,0.65,0.384]', 'core_[0.65,0.65,0.24576]', 'core_[0.65,0.65,0.36864]', 'core_[0.65,0.52,0.3072]', 'core_[0.65,0.78,0.3072]', 'core_[0.52,0.65,0.3072]', 'core_[0.78,0.65,0.3072]', 'core_[0.65,0.65,0.27648]', 'core_[0.65,0.65,0.33792]', 'core_[0.65,0.585,0.3072]', 'core_[0.65,0.715,0.3072]', 'core_[0.585,0.65,0.3072]', 'core_[0.715,0.65,0.3072]', 'core_[0.65,0.65,0.29184]', 'core_[0.65,0.65,0.32256]', 'core_[0.65,0.6175,0.3072]', 'core_[0.65,0.6825,0.3072]', 'core_[0.6175,0.65,0.3072]', 'core_[0.6825,0.65,0.3072]', 'core_[0.65,0.65,0.29952]', 'core_[0.65,0.65,0.31488]', 'core_[0.65,0.63375,0.3072]', 'core_[0.65,0.66625,0.3072]', 'core_[0.63375,0.65,0.3072]', 'core_[0.66625,0.65,0.3072]', 'core_[0.65,0.65,0.29203]', 'core_[0.65,0.65,0.30701]', 'core_[0.65,0.63375,0.29952]', 'core_[0.65,0.66625,0.29952]', 'core_[0.63375,0.65,0.29952]', 'core_[0.66625,0.65,0.29952]', 'core_[0.65,0.65,0.29578]', 'core_[0.65,0.65,0.30326]', 'core_[0.65,0.64187,0.29952]', 'core_[0.65,0.65813,0.29952]', 'core_[0.64187,0.65,0.29952]', 'core_[0.65813,0.65,0.29952]', 'core_[0.65,0.65,0.29765]', 'core_[0.65,0.65,0.30139]', 'core_[0.65,0.64594,0.29952]', 'core_[0.65,0.65406,0.29952]', 'core_[0.64594,0.65,0.29952]', 'core_[0.65406,0.65,0.29952]', 'core_[0.65,0.65,0.29858]', 'core_[0.65,0.65,0.30046]', 'core_[0.65,0.64797,0.29952]', 'core_[0.65,0.65203,0.29952]', 'core_[0.64797,0.65,0.29952]', 'core_[0.65203,0.65,0.29952]', 'core_[0.65,0.65,0.3014]', 'core_[0.65,0.64797,0.30046]', 'core_[0.65,0.65203,0.30046]', 'core_[0.64797,0.65,0.30046]', 'core_[0.65203,0.65,0.30046]', 'core_[0.64797,0.65,0.3014]', 'core_[0.64797,0.64797,0.30046]', 'core_[0.64797,0.65203,0.30046]', 'core_[0.64595,0.65,0.30046]', 'core_[0.64999,0.65,0.30046]', 'core_[0.64595,0.65,0.29952]', 'core_[0.64595,0.65,0.3014]', 'core_[0.64595,0.64797,0.30046]', 'core_[0.64595,0.65203,0.30046]', 'core_[0.64393,0.65,0.30046]', 'core_[0.64393,0.65,0.29952]', 'core_[0.64393,0.65,0.3014]', 'core_[0.64393,0.64797,0.30046]', 'core_[0.64393,0.65203,0.30046]', 'core_[0.64192,0.65,0.30046]', 'core_[0.64594,0.65,0.30046]', 'core_[0.64192,0.65,0.29952]', 'core_[0.64192,0.65,0.3014]', 'core_[0.64192,0.64797,0.30046]', 'core_[0.64192,0.65203,0.30046]', 'core_[0.63991,0.65,0.30046]', 'core_[0.63991,0.65,0.29952]', 'core_[0.63991,0.65,0.3014]', 'core_[0.63991,0.64797,0.30046]', 'core_[0.63991,0.65203,0.30046]', 'core_[0.63791,0.65,0.30046]', 'core_[0.64191,0.65,0.30046]', 'core_[0.63791,0.65,0.29952]', 'core_[0.63791,0.65,0.3014]', 'core_[0.63791,0.64797,0.30046]', 'core_[0.63791,0.65203,0.30046]', 'core_[0.63592,0.65,0.30046]', 'core_[0.6399,0.65,0.30046]', 'core_[0.63592,0.65,0.29952]', 'core_[0.63592,0.65,0.3014]', 'core_[0.63592,0.64797,0.30046]', 'core_[0.63592,0.65203,0.30046]', 'core_[0.63393,0.65,0.30046]', 'core_[0.63393,0.65,0.29952]', 'core_[0.63393,0.65,0.3014]', 'core_[0.63393,0.64797,0.30046]', 'core_[0.63393,0.65203,0.30046]', 'core_[0.63195,0.65,0.30046]', 'core_[0.63591,0.65,0.30046]', 'core_[0.63195,0.65,0.29952]', 'core_[0.63195,0.65,0.3014]', 'core_[0.63195,0.64797,0.30046]', 'core_[0.63195,0.65203,0.30046]', 'core_[0.62998,0.65,0.30046]', 'core_[0.63392,0.65,0.30046]', 'core_[0.62998,0.65,0.29952]', 'core_[0.62998,0.65,0.3014]', 'core_[0.62998,0.64797,0.30046]', 'core_[0.62998,0.65203,0.30046]', 'core_[0.62801,0.65,0.30046]', 'core_[0.62801,0.65,0.29952]', 'core_[0.62801,0.65,0.3014]', 'core_[0.62801,0.64797,0.30046]', 'core_[0.62801,0.65203,0.30046]', 'core_[0.62605,0.65,0.30046]', 'core_[0.62997,0.65,0.30046]', 'core_[0.62605,0.65,0.29952]', 'core_[0.62605,0.65,0.3014]', 'core_[0.62605,0.64797,0.30046]', 'core_[0.62605,0.65203,0.30046]', 'core_[0.62409,0.65,0.30046]', 'core_[0.62409,0.65,0.29952]', 'core_[0.62409,0.65,0.3014]', 'core_[0.62409,0.64797,0.30046]', 'core_[0.62409,0.65203,0.30046]', 'core_[0.62214,0.65,0.30046]', 'core_[0.62604,0.65,0.30046]', 'core_[0.62214,0.65,0.29952]', 'core_[0.62214,0.65,0.3014]', 'core_[0.62214,0.64797,0.30046]', 'core_[0.62214,0.65203,0.30046]', 'core_[0.6202,0.65,0.30046]', 'core_[0.62408,0.65,0.30046]']

    ns.shutdown()
    time.sleep(0.1)

    
def test_search_method_simple():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.connect_agent(hc.HillClimb, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(problem=problem)        
    rp.set_attr(step_size=0.2)
    rp.set_attr(step_rate=0.2)
    rp.set_attr(step_limit=1)
    rp.set_attr(convergence_criteria=0.001)
    rp.set_random_seed(seed=103)
    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                          'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[0.650,0.650,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[0.650,0.650,0.4]'])
    
    rp.search_method()
    time.sleep(0.075)
    rp.set_attr(step_limit=100)
    
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.52,0.4]', 'core_[0.65,0.52,0.48]', 'core_[0.65,0.52,0.32]', 'core_[0.65,0.416,0.4]', 'core_[0.78,0.52,0.4]', 'core_[0.52,0.52,0.4]', 'core_[0.65,0.624,0.4]']
    rp.search_method()
    time.sleep(0.075)   

    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.65,0.52,0.4]', 'core_[0.65,0.52,0.48]', 'core_[0.65,0.52,0.32]', 'core_[0.65,0.416,0.4]', 'core_[0.78,0.52,0.4]', 'core_[0.52,0.52,0.4]', 'core_[0.65,0.624,0.4]', 'core_[0.65,0.78,0.4]', 'core_[0.65,0.78,0.32]', 'core_[0.52,0.78,0.4]', 'core_[0.78,0.78,0.4]', 'core_[0.65,0.936,0.4]', 'core_[0.65,0.78,0.48]', 'core_[0.65,0.78,0.336]', 'core_[0.754,0.78,0.4]', 'core_[0.546,0.78,0.4]', 'core_[0.65,0.9048,0.4]', 'core_[0.65,0.78,0.464]', 'core_[0.65,0.6552,0.4]', 'core_[0.65,0.87984,0.4]', 'core_[0.65,0.68016,0.4]', 'core_[0.5668,0.78,0.4]', 'core_[0.7332,0.78,0.4]', 'core_[0.65,0.78,0.4512]', 'core_[0.65,0.78,0.3488]', 'core_[0.65,0.78,0.35904]', 'core_[0.65,0.70013,0.4]', 'core_[0.65,0.85987,0.4]', 'core_[0.65,0.78,0.44096]', 'core_[0.58344,0.78,0.4]', 'core_[0.71656,0.78,0.4]', 'core_[0.59675,0.78,0.4]', 'core_[0.70325,0.78,0.4]', 'core_[0.65,0.7161,0.4]', 'core_[0.65,0.78,0.36723]', 'core_[0.65,0.8439,0.4]', 'core_[0.65,0.78,0.43277]', 'core_[0.6926,0.78,0.4]', 'core_[0.65,0.78,0.37379]', 'core_[0.65,0.83112,0.4]', 'core_[0.6074,0.78,0.4]', 'core_[0.65,0.72888,0.4]', 'core_[0.65,0.78,0.42621]', 'core_[0.65,0.78,0.42097]', 'core_[0.65,0.78,0.37903]', 'core_[0.68408,0.78,0.4]', 'core_[0.61592,0.78,0.4]', 'core_[0.65,0.73911,0.4]', 'core_[0.65,0.82089,0.4]', 'core_[0.65,0.78,0.38322]', 'core_[0.65,0.78,0.41678]', 'core_[0.67726,0.78,0.4]', 'core_[0.62274,0.78,0.4]', 'core_[0.65,0.81272,0.4]', 'core_[0.65,0.74728,0.4]', 'core_[0.65,0.78,0.38658]', 'core_[0.67181,0.78,0.4]', 'core_[0.65,0.80617,0.4]', 'core_[0.65,0.75383,0.4]', 'core_[0.65,0.78,0.41342]', 'core_[0.62819,0.78,0.4]', 'core_[0.65,0.78,0.38926]', 'core_[0.63255,0.78,0.4]', 'core_[0.65,0.80094,0.4]', 'core_[0.66745,0.78,0.4]', 'core_[0.65,0.75906,0.4]', 'core_[0.65,0.78,0.41074]', 'core_[0.65,0.79675,0.4]', 'core_[0.65,0.76325,0.4]', 'core_[0.66396,0.78,0.4]', 'core_[0.65,0.78,0.39141]', 'core_[0.65,0.78,0.40859]', 'core_[0.63604,0.78,0.4]', 'core_[0.65,0.7934,0.4]', 'core_[0.65,0.78,0.39313]', 'core_[0.66117,0.78,0.4]', 'core_[0.65,0.7666,0.4]', 'core_[0.65,0.78,0.40687]', 'core_[0.63883,0.78,0.4]', 'core_[0.64107,0.78,0.4]', 'core_[0.65,0.78,0.3945]', 'core_[0.65,0.79072,0.4]', 'core_[0.65893,0.78,0.4]', 'core_[0.65,0.78,0.4055]', 'core_[0.65,0.76928,0.4]', 'core_[0.65,0.78858,0.4]', 'core_[0.65715,0.78,0.4]', 'core_[0.65,0.77142,0.4]', 'core_[0.65,0.78,0.3956]', 'core_[0.64285,0.78,0.4]', 'core_[0.65,0.78,0.4044]', 'core_[0.65,0.78,0.39648]', 'core_[0.65,0.78,0.40352]', 'core_[0.65572,0.78,0.4]', 'core_[0.64428,0.78,0.4]', 'core_[0.65,0.77314,0.4]', 'core_[0.65,0.78686,0.4]', 'core_[0.64543,0.78,0.4]', 'core_[0.65457,0.78,0.4]', 'core_[0.65,0.77451,0.4]', 'core_[0.65,0.78,0.40281]', 'core_[0.65,0.78,0.39719]', 'core_[0.65,0.78549,0.4]', 'core_[0.64634,0.78,0.4]', 'core_[0.65366,0.78,0.4]', 'core_[0.65,0.77561,0.4]', 'core_[0.65,0.78439,0.4]', 'core_[0.65,0.78,0.40225]', 'core_[0.65,0.78,0.39775]', 'core_[0.65,0.78,0.3982]', 'core_[0.65,0.78351,0.4]', 'core_[0.65293,0.78,0.4]', 'core_[0.65,0.77649,0.4]', 'core_[0.64707,0.78,0.4]', 'core_[0.65,0.78,0.4018]', 'core_[0.65,0.78281,0.4]', 'core_[0.65,0.77719,0.4]', 'core_[0.65,0.78,0.39856]', 'core_[0.65234,0.78,0.4]', 'core_[0.64766,0.78,0.4]', 'core_[0.65,0.78,0.40144]', 'core_[0.65,0.77775,0.4]', 'core_[0.65,0.78225,0.4]', 'core_[0.65,0.78,0.39885]', 'core_[0.65,0.78,0.40115]', 'core_[0.65187,0.78,0.4]', 'core_[0.64813,0.78,0.4]', 'core_[0.65,0.78,0.40092]', 'core_[0.65,0.78,0.39908]', 'core_[0.65,0.7782,0.4]', 'core_[0.6515,0.78,0.4]', 'core_[0.6485,0.78,0.4]', 'core_[0.65,0.7818,0.4]', 'core_[0.6512,0.78,0.4]', 'core_[0.65,0.78,0.39926]', 'core_[0.65,0.78144,0.4]', 'core_[0.65,0.78,0.40074]', 'core_[0.65,0.77856,0.4]', 'core_[0.6488,0.78,0.4]', 'core_[0.64904,0.78,0.4]', 'core_[0.65,0.78,0.39941]', 'core_[0.65,0.78115,0.4]', 'core_[0.65,0.78,0.40059]', 'core_[0.65,0.77885,0.4]', 'core_[0.65096,0.78,0.4]', 'core_[0.65,0.78,0.39953]', 'core_[0.65,0.78,0.40047]', 'core_[0.65,0.78092,0.4]', 'core_[0.64923,0.78,0.4]', 'core_[0.65077,0.78,0.4]', 'core_[0.65,0.77908,0.4]']
    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method_discrete_dv():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv = {'x0' : {'options': ['0', '1', '2', '3'], 'default': '0', 'variable type': str},
          'x1' : {'options': ['0', '1', '2', '3'], 'default': '1', 'variable type': str},
          'x2' : {'options': ['0', '1', '2', '3'], 'default': '2', 'variable type': str},
          'x3' : {'options': ['0', '1', '2', '3'], 'default': '3', 'variable type': str}}
    obj = {'f1': {'ll': 10, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dv,objectives=obj,constraints={})
    problem = BenchmarkProblem(design_variables=dv,
                         objectives=obj,
                         constraints={},
                         benchmark_name = 'tsp')      
    
    bb.connect_agent(hc.HillClimb, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_attr(step_limit=10)
    rp.set_random_seed(seed=109875)
    rp.set_attr(hc_type='steepest ascent')
    rp.set_attr(problem=problem)        
    
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