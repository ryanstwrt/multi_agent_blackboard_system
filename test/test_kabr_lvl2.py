from src.ka.ka_brs.level2 import KaBrLevel2
import src.bb.blackboard as blackboard
import src.bb.blackboard_optimization as bb_opt
import time
from osbrain import run_nameserver
from osbrain import run_agent
import pickle
import src.utils.utilities as utils

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)
    
def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br2', base=KaBrLevel2)
    assert ka_br2.get_attr('bb_lvl_write') == 1
    assert ka_br2.get_attr('bb_lvl_read') == 2
    assert ka_br2.get_attr('_num_allowed_entries') == 10
    assert ka_br2.get_attr('_trigger_val_base') == 4.00000000002
    assert ka_br2.get_attr('_fitness') == 0.0
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_convert_fitness_to_minimzation():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br2', base=KaBrLevel2)
    ka_br2.set_attr(_objectives = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
                                   'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float},
                                   'keff':              {'ll':1.0, 'ul':2.0,  'target': 1.5, 'goal':'et', 'variable type': float}})
    
    assert ka_br2.convert_fitness_to_minimzation('burnup', 0.75) == 0.75
    assert ka_br2.convert_fitness_to_minimzation('reactivity swing', 0.6) == 0.4
    assert round(ka_br2.convert_fitness_to_minimzation('keff', 0.45),2) == 0.9                    
    assert round(ka_br2.convert_fitness_to_minimzation('keff', 0.55),2) == 0.9
    assert round(ka_br2.convert_fitness_to_minimzation('keff', 0.15),2) == 0.3                  
    assert round(ka_br2.convert_fitness_to_minimzation('keff', 0.95),2) == 0.1
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_update_abstract_levels():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv)     
    
    bb.connect_agent(KaBrLevel2, 'ka_br_lvl2')
    br = ns.proxy('ka_br_lvl2')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.45]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11,'burnup' : 61.12}}, panel='new')
    bb.update_abstract_lvl(2, 'core_[65.0, 65.0, 0.45]', {'valid': True}, panel='old')
    
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11,'burnup' : 61.12}}, panel='old')
    bb.update_abstract_lvl(2, 'core_[65.0, 65.0, 0.42]', {'valid': True}, panel='new')
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})

    br.update_abstract_levels()
    assert [x for x in br.get_attr('lvl_read').keys()]  == ['core_[65.0, 65.0, 0.42]']
    assert [x for x in br.get_attr('lvl_write').keys()] == ['core_[65.0, 65.0, 0.42]']
    assert [x for x in br.get_attr('_lvl_data').keys()] == ['core_[65.0, 65.0, 0.45]', 'core_[65.0, 65.0, 0.42]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_add_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br', base=KaBrLevel2) 
    ka_br2.set_attr(_fitness=1.5)
    ka_br2.add_entry(('core_1', 'pareto'))
    
    assert ka_br2.get_attr('_entry') == {'pareto type': 'pareto', 'fitness function': 1.5}
    assert ka_br2.get_attr('_entry_name') == 'core_1'
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_determine_validity():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    ka_br2 = run_agent(name='ka_br', base=KaBrLevel2)
    ka_br2.add_blackboard(bb)
    ka_br2.connect_writer()
    ka_br2.connect_trigger()
    ka_br2.connect_executor()
    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(3, {'design variables': {'height': float, 'smear': float, 'pu_content': float}, 'objective functions': {'keff': float, 'void_coeff': float}})
    bb.add_panel(3, ['new','old'])
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 'objective functions': {'keff': 1.05, 'void_coeff': -150.0,}}, panel='old')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 'objective functions': {'keff': 1.05, 'void_coeff': -160.0}}, panel='old')
    bb.update_abstract_lvl(3, 'core_3', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 'objective functions': {'keff': 1.06, 'void_coeff': -100.0}}, panel='old')
    bb.update_abstract_lvl(3, 'core_4', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 'objective functions': {'keff': 1.00, 'void_coeff': -100.0}}, panel='old')

    bb.update_abstract_lvl(2, 'core_1', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_2', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_3', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_4', {'valid': True}, panel='new')
    
    bb.publish_trigger()
    time.sleep(0.05)
    
    bol, p_type = ka_br2.determine_validity('core_1')
    assert p_type == 'pareto'
    assert bol == True

    bb.update_abstract_lvl(1, 'core_1', {'pareto type': 'pareto', 'fitness function': 1.0})
    bb.publish_trigger()
    time.sleep(0.05)
    bol, p_type = ka_br2.determine_validity('core_2')
    assert p_type == 'pareto'
    assert bol == True

    bb.update_abstract_lvl(1, 'core_2', {'pareto type': 'pareto', 'fitness function': 1.0})
    bb.publish_trigger()
    time.sleep(0.05)
    bol, p_type = ka_br2.determine_validity('core_3')
    assert p_type == 'weak'
    assert bol == True

    bb.update_abstract_lvl(1, 'core_3', {'pareto type': 'weak', 'fitness function': 1.0})
    bb.publish_trigger()
    time.sleep(0.05)
    bol, p_type = ka_br2.determine_validity('core_4')
    assert p_type == None
    assert bol == False
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_move_current_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    ka_br2 = run_agent(name='ka_br', base=KaBrLevel2)
    ka_br2.add_blackboard(bb)
    ka_br2.connect_writer()

    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}, 
                                 'pu_content':  {'ll': 0,    'ul': 0.6, 'goal':'lt', 'variable type': float}})
    
    bb.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
    bb.add_panel(1, ['new', 'old'])
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])

    bb.update_abstract_lvl(2, 'core_1', {'valid': True}, panel='new')
    
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {'core_1' : {'valid' : True}}, 'old' : {}}
    ka_br2.move_entry(ka_br2.get_attr('bb_lvl_read'), 'core_1', {'valid': True}, ka_br2.get_attr('old_panel'), ka_br2.get_attr('new_panel'))
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new' : {}, 'old' : {'core_1' : {'valid' : True}}}
    
    ns.shutdown()
    time.sleep(0.05)

def test_determine_optimal_type():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br', base=KaBrLevel2)
    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}, 
                                 'pu_content':  {'ll': 0,    'ul': 0.6, 'goal':'lt', 'variable type': float}})    
    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.10, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.3}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == 'pareto'

    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.10, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.3}, 
        {'keff': 1.10, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.3})
    assert bool_ == None
    
    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.02, 'void_coeff': -150, 'doppler_coeff': -0.75, 'pu_content': 0.3}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == 'weak'
    
    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.00, 'void_coeff': -100, 'doppler_coeff': -0.55, 'pu_content': 0.3}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.6})
    assert bool_ == 'weak'

    
    bool_ = ka_br2.determine_optimal_type(
        {'keff': 1.02, 'void_coeff': -110, 'doppler_coeff': -0.55, 'pu_content': 0.6}, 
        {'keff': 1.05, 'void_coeff': -120, 'doppler_coeff': -0.65, 'pu_content': 0.5})
    assert bool_ == None
    
    ns.shutdown()
    time.sleep(0.05)

def test_determine_fitness_function():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br', base=KaBrLevel2)
    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -100, 'goal':'lt', 'variable type': float}, 
                                 'pu_content':  {'ll': 0.0, 'ul': 0.6, 'goal':'lt', 'variable type': float},
                                 'power avg':   {'ll': 0.0, 'ul': 1.0, 'goal': 'lt', 'variable type': list, 'goal type': 'avg'},
                                 'power min':   {'ll': 0.0, 'ul': 1.0, 'goal': 'lt', 'goal type': 'min', 'variable type': list},
                                 'power max':   {'ll': 0.0, 'ul': 1.0, 'goal': 'lt', 'goal type': 'max', 'variable type': list}})
    
    fitness = ka_br2.determine_fitness_function('core_1', {'keff': 1.2, 'void_coeff': -200.0, 'pu_content': 0.0, 'power avg': [0.25, 0.5, 0.75], 'power max': [0.25, 0.5, 0.75], 'power min': [0.25, 0.5, 0.75]})
    assert fitness == 4.5
    fitness = ka_br2.determine_fitness_function('core_2', {'keff': 1.0, 'void_coeff': -100.0, 'pu_content': 0.6, 'power avg': [0.25, 0.5, 0.75], 'power max': [0.25, 0.5, 0.75], 'power min': [0.25, 0.5, 0.75]})
    assert fitness == 1.5
    fitness = ka_br2.determine_fitness_function('core_2', {'keff': 1.1, 'void_coeff': -150.0, 'pu_content': 0.3, 'power avg': [0.25, 0.5, 0.75], 'power max': [0.25, 0.5, 0.75], 'power min': [0.25, 0.5, 0.75]})
    assert round(fitness,5) == 3.0
    
    ns.shutdown()
    time.sleep(0.05)   
    
def test_handler_trigger_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
        'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
        'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}}     
    objs = {'cycle length':     {'ll':300, 'ul':400,  'goal':'gt', 'variable type': float},
            'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'pu mass':          {'ll':500, 'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':25,  'ul':75,   'goal':'gt', 'variable type': float}}    
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv)    
    bb.connect_agent(KaBrLevel2, 'ka_br2')
    br = ns.proxy('ka_br2')
    br.set_attr(_num_allowed_entries=1)
    bb.update_abstract_lvl(3, 'core 1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')    
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br2': 0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    bb.update_abstract_lvl(2, 'core 1', {'valid' : True}, panel='new')
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_br2': 0}, 2: {'ka_br2': 4.00000000002}}   
    assert bb.get_attr('_ka_to_execute') == ('ka_br2', 4.00000000002)
        
    ns.shutdown()
    time.sleep(0.05)

def test_handler_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.connect_agent(KaBrLevel2, 'ka_br')
    bb.initialize_metadata_level()
    
    ka_br2 = ns.proxy('ka_br')

    ka_br2.set_attr(_objectives={'keff':        {'ll': 1.0,  'ul': 1.2, 'goal':'gt', 'variable type': float}, 
                                 'void_coeff':  {'ll': -200, 'ul': -75, 'goal':'lt', 'variable type': float}, 
                                 'pu_content':  {'ll': 0,    'ul': 0.6, 'goal':'lt', 'variable type': float}})
    
    ka_br2.set_attr(_constraints={'powers':    {'ll': 0.0,  'ul': 0.1, 'goal type': 'max', 'variable type': list}})
    
    bb.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
    bb.add_abstract_lvl(2, {'valid': bool})
    bb.add_panel(2, ['new', 'old'])
    bb.add_abstract_lvl(3, {'design variables': {'height': float, 'smear': float, 'pu_content': float}, 
                            'objective functions': {'keff': float, 'void_coeff': float, 'pu_content': float},
                            'constraints': {'powers': list}})
    bb.add_panel(3, ['new','old'])
    
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.3}, 
                                         'objective functions': {'keff': 1.05, 'void_coeff': -150.0, 'pu_content': 0.3},
                                         'constraints': {'powers': [0.05, 0.06]}}, panel='old')
    bb.update_abstract_lvl(3, 'core_2', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.3},
                                         'objective functions': {'keff': 1.05, 'void_coeff': -160.0, 'pu_content': 0.3},
                                         'constraints': {'powers': [0.05, 0.06]}}, panel='old')
    bb.update_abstract_lvl(3, 'core_3', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.5},
                                         'objective functions': {'keff': 1.00, 'void_coeff': -100.0, 'pu_content': 0.5},
                                         'constraints': {'powers': [0.05, 0.06]}}, panel='old')
    bb.update_abstract_lvl(3, 'core_4', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.2},
                                         'objective functions': {'keff': 1.00, 'void_coeff': -100.0, 'pu_content': 0.2},
                                         'constraints': {'powers': [0.05, 0.06]}}, panel='old')  
    
    bb.update_abstract_lvl(2, 'core_1', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_2', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_3', {'valid': True}, panel='new')
    bb.update_abstract_lvl(2, 'core_4', {'valid': True}, panel='new')
    
    bb.set_attr(_ka_to_execute=('ka_br', 10.0))
    bb.publish_trigger()
    time.sleep(0.05)
    bb.send_executor()
    time.sleep(0.05)    

    ff = [1.35, 1.43, 0.36667, 0.86667]
    for num, attr in enumerate(bb.get_attr('abstract_lvls')['level 1'].values()):
        assert round(attr['fitness function'],5) == ff[num]

    assert bb.get_attr('abstract_lvls')['level 2'] == {'new': {}, 
                                                       'old': {'core_1' : {'valid' : True}, 
                                                               'core_2' : {'valid' : True},
                                                               'core_3' : {'valid' : True},
                                                               'core_4' : {'valid' : True}}}
    bb.set_attr(_ka_to_execute=('ka_br', 10.0))
    bb.publish_trigger()
    time.sleep(0.05)
    bb.send_executor()
    time.sleep(0.05) 
    assert bb.get_attr('abstract_lvls')['level 2'] == {'new': {}, 
                                                       'old': {'core_1' : {'valid' : True}, 
                                                               'core_2' : {'valid' : True},
                                                               'core_3' : {'valid' : True},
                                                               'core_4' : {'valid' : True}}} 
   
    ns.shutdown()
    time.sleep(0.05)     