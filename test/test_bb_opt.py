import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import src.bb.blackboard as blackboard
import src.bb.blackboard_optimization as bb_opt
import time
import os
from src.ka.ka_s.stochastic import Stochastic
from src.ka.ka_s.latin_hypercube import LatinHypercube
from src.ka.ka_s.neighborhood_search import NeighborhoodSearch
from src.utils.problem import BenchmarkProblem
from src.ka.ka_brs.level3 import KaBrLevel3
from src.ka.ka_brs.level2 import KaBrLevel2
from src.ka.ka_brs.level1 import KaBrLevel1
import src.ka.base as ka

dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}    
        
problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')    

def test_BbOpt_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    assert bb.get_attr('agent_addrs') == {}
    assert bb.get_attr('_agent_writing') == False
    assert bb.get_attr('_new_entry') == False
    assert bb.get_attr('archive_name') == 'blackboard_archive.h5'
    assert bb.get_attr('_sleep_limit') == 10
    assert bb.get_attr('_ka_to_execute') == (None, 0) 
    assert bb.get_attr('_trigger_event') == 0
    assert bb.get_attr('_kaar') == {}
    assert bb.get_attr('_pub_trigger_alias') == 'trigger'
    
    assert bb.get_attr('objectives') == {}
    assert bb.get_attr('design_variables') == {}
    assert bb.get_attr('constraints') == {}
    assert bb.get_attr('_complete') == False
    assert bb.get_attr('_nadir_point') == {}
    assert bb.get_attr('_ideal_point') == {}
    assert bb.get_attr('objectives_ll') == []
    assert bb.get_attr('objectives_ul') == []
    assert bb.get_attr('abstract_lvls') == {'level 1': {},
                                            'level 2': {'new': {}, 'old': {}}}
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_create_lvl_format():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'experiments': {'length':         2, 
                                                  'dict':      {'0': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                                                '1': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str}},
                                                  'variable type': dict}}
    lvl_format = bb.create_level_format(dv)
    assert lvl_format == {'height': float, 'smear': float, 'pu_content': float, 'experiments': {'0': str, '1': str}}
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_initalize_abstract_level_3_basic():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.set_attr(problem=problem)
    assert bb.get_attr('abstract_lvls_format') == {'level 1': {'pareto type': str, 'fitness function': float},
                                                   'level 2': {'new': {'valid': bool}, 
                                                               'old': {'valid': bool}},
                                                   'level 3': {'new': {'design variables': {'x0': float, 'x1': float, 'x2': float},
                                                                       'objective functions': {'f0': float, 'f1': float, 'f2': float},
                                                                       'constraints': {}},
                                                               'old': {'design variables': {'x0': float, 'x1': float, 'x2': float},
                                                                       'objective functions': {'f0': float, 'f1': float, 'f2': float},
                                                                       'constraints': {}}}}

    
    assert bb.get_attr('abstract_lvls') == {'level 1': {}, 
                                            'level 2': {'new':{}, 'old':{}}, 
                                            'level 3': {'new': {}, 'old': {}}}
    ns.shutdown()
    time.sleep(0.05)

def test_initalize_abstract_level_3():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    o_ = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    d_ =   {'height':           {'ll': 50, 'ul': 80, 'variable type': float},
            'experiments': {'length':         2, 
                            'dict':      {'0': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d'], 'default': 'no_exp', 'variable type': str},
                                          '1': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d'], 'default': 'no_exp', 'variable type': str}},
                            'variable type': dict}}
    c_ = {'constraint_1': {'ll': 0.0, 'ul':1.0, 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=o_, design_variables=d_, constraints=c_)
    assert bb.get_attr('abstract_lvls_format') == {'level 1': {'pareto type': str, 'fitness function': float},
                                                   'level 2': {'new': {'valid': bool}, 
                                                               'old': {'valid': bool}},
                                                   'level 3': {'new': {'design variables': {'height': float, 'experiments': {'0': str, '1': str}},
                                                                       'objective functions':  {'reactivity swing': float, 'burnup': float},
                                                                       'constraints': {'constraint_1': float}},
                                                               'old': {'design variables': {'height': float, 'experiments': {'0': str, '1': str}},
                                                                       'objective functions':  {'reactivity swing': float, 'burnup': float},
                                                                       'constraints': {'constraint_1': float}}}}

    assert bb.get_attr('abstract_lvls') == {'level 1': {}, 
                                            'level 2': {'new':{}, 'old':{}}, 
                                            'level 3': {'new': {}, 'old': {}}}
    ns.shutdown()
    time.sleep(0.05)
    
def test_connect_agent():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.connect_agent(Stochastic, 'ka_rp')
    bb.connect_agent(KaBrLevel3, 'ka_br')
    bb.connect_agent(ka.KaBase, 'ka')
    
    agents = bb.get_attr('agent_addrs')
    
    assert [x for x in agents.keys()] == ['ka_rp', 'ka_br', 'ka']
    assert ns.agents() == ['blackboard', 'ka_rp', 'ka_br', 'ka']

    rp = ns.proxy('ka_rp')
    br = ns.proxy('ka_br')
    
    assert bb.get_attr('agent_addrs')['ka_rp']['executor'] == (rp.get_attr('_executor_alias'), rp.get_attr('_executor_addr'))
    assert bb.get_attr('agent_addrs')['ka_br']['executor'] == (br.get_attr('_executor_alias'), br.get_attr('_executor_addr'))
    assert bb.get_attr('agent_addrs')['ka_rp']['trigger_response'] == (rp.get_attr('_trigger_response_alias'), rp.get_attr('_trigger_response_addr'))
    assert bb.get_attr('agent_addrs')['ka_br']['trigger_response'] == (br.get_attr('_trigger_response_alias'), br.get_attr('_trigger_response_addr'))
    assert bb.get_attr('agent_addrs')['ka_rp']['shutdown'] == (rp.get_attr('_shutdown_alias'), rp.get_attr('_shutdown_addr'))
    assert bb.get_attr('agent_addrs')['ka_br']['shutdown'] == (br.get_attr('_shutdown_alias'), br.get_attr('_shutdown_addr'))
    assert bb.get_attr('agent_addrs')['ka_rp']['writer'] == (rp.get_attr('_writer_alias'), rp.get_attr('_writer_addr'))
    assert bb.get_attr('agent_addrs')['ka_br']['writer'] == (br.get_attr('_writer_alias'), br.get_attr('_writer_addr'))
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_add_ka_specific():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)    
    bb.connect_agent(Stochastic, 'ka_rp_explore')
    bb.connect_agent(LatinHypercube, 'ka_rp_lhc')
    bb.connect_agent(NeighborhoodSearch, 'ka_rp_exploit')
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    bb.connect_agent(KaBrLevel2, 'ka_br_lvl2')
    bb.connect_agent(KaBrLevel3, 'ka_br_lvl3')

    for alias in ns.agents():
        agent = ns.proxy(alias)
        if 'rp' in alias:
            assert agent.get_attr('_objectives') == {'f0':      {'ll':0,   'ul':1000,  'goal':'lt', 'variable type': float},
                                                     'f1':      {'ll':0,   'ul':1000,  'goal':'lt', 'variable type': float},
                                                     'f2':      {'ll':0,   'ul':1000,  'goal':'lt', 'variable type': float},}
            assert agent.get_attr('_design_variables') == {'x0': {'ll': 0.0, 'ul': 1.0, 'variable type': float},
                                                           'x1': {'ll': 0.0, 'ul': 1.0, 'variable type': float},
                                                           'x2': {'ll': 0.0, 'ul': 1.0,  'variable type': float}}
            if 'lhc' in alias:
                assert len(agent.get_attr('lhd')) == 50
                assert len(agent.get_attr('lhd')[0]) == 3
        elif 'lvl' in alias:
            assert agent.get_attr('_objectives') == {'f0':      {'ll':0,   'ul':1000,  'goal':'lt', 'variable type': float},
                                                     'f1':      {'ll':0,   'ul':1000,  'goal':'lt', 'variable type': float},
                                                     'f2':      {'ll':0,   'ul':1000,  'goal':'lt', 'variable type': float},}
            
    ns.shutdown()
    time.sleep(0.05)  

def test_get_hv_list():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)   
    bb.set_attr(hv_list=[0.0,0.5,0.6])
    
    assert bb.get_hv_list() == [0, 0.5, 0.6]
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_get_complete_status():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)  
    assert bb.get_complete_status() == False
    bb.set_attr(_complete=True)
    
    assert bb.get_complete_status() == True
    
    ns.shutdown()
    time.sleep(0.05) 
    
def test_hv_indicator():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':50,  'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)

    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 100.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    
    assert bb.hv_indicator() == 0.5
    
    ns.shutdown()
    time.sleep(0.05)  

def test_handler_writer():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    rp = run_agent(name='explore', base=Stochastic)
    rp1 = run_agent(name='exploit', base=NeighborhoodSearch)
    bb.initialize_abstract_level_3()
    rp.add_blackboard(bb)
    rp1.add_blackboard(bb)
    rp.connect_writer()
    rp1.connect_writer()
    
    dv = {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2}
    obj = {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}
    
    entry={'design variables': dv, 'objective functions': obj}
    rp.write_to_bb(rp.get_attr('bb_lvl_data'), 'core1', entry, panel='new')
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core1': {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                                                                        'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}}
    dv = {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2}
    obj = {'cycle length': 100.0, 'reactivity swing': 10000.0, 'burnup': 32.0, 'pu mass': 1000.0}
    entry={'design variables': dv, 'objective functions': obj}
                                  
    rp1.write_to_bb(rp1.get_attr('bb_lvl_data'), 'core2', entry, panel='new')
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core1': {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                                                                        'objective functions' :{'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}},
                                                               'core2': {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                                                                         'objective functions': {'cycle length': 100.0, 'reactivity swing': 10000.0, 'burnup': 32.0, 'pu mass': 1000.0}}}
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_determine_complete_tvs():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':50,  'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)

    bb.set_attr(convergence_rate=1E-3)
    bb.set_attr(convergence_interval=2)
    bb.set_attr(pf_size=9)
    bb.set_attr(total_tvs=11)
    
    _kaar = {}
    for i in range(60,70):
        _kaar[i-60] = {'ka_rp': 1}
        bb.update_abstract_lvl(1, 'core_[{}.0, 66.0, 0.42]'.format(i), {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.set_attr(_kaar=_kaar)
    bb.set_attr(hv_list=[0,0.25,0.32,0.35,0.5,0.56,0.66,0.76,0.86,0.96])
    bb.determine_complete()    
    assert bb.get_attr('_complete') == False    
    _kaar[10] = {'ka_rp':1}
    bb.set_attr(_kaar=_kaar)    
    bb.determine_complete()
    assert bb.get_attr('_complete') == True    

    ns.shutdown()
    time.sleep(0.05)    
    

def test_determine_complete_hv():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':50,  'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)

    bb.set_attr(skipped_tvs=1)
    bb.set_attr(convergence_rate=1E-3)
    bb.set_attr(convergence_interval=2)
    bb.set_attr(pf_size=9)
    
    for i in range(60,70):
        bb.update_abstract_lvl(1, 'core_[{}.0, 66.0, 0.42]'.format(i), {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    bb.set_attr(hv_list=[0,0.25,0.32,0.35,0.5,0.6,0.6,0.6,0.6,0.6])
    bb.set_attr(_kaar={'a':{'a':1},'b':{'b':2}})
    assert bb.get_attr('_complete') == False
    bb.determine_complete_hv()
    assert bb.get_attr('_complete') == True    

    ns.shutdown()
    time.sleep(0.05)

def test_meta_data_entry():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_metadata_level()
    bb.set_attr(meta_data={'hvi': [0.1,0.2,0.3,0.4,0.5]})
    bb.meta_data_entry('agent_x', 1.5, 4)
    assert bb.get_attr('abstract_lvls')['level 100'] == {'4': {'agent': 'agent_x', 'time': 1.5, 'hvi': 0.4}}
    
    ns.shutdown()
    time.sleep(0.05)    

def test_convergence_update():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_metadata_level()

    bb.set_attr(_trigger_event=3)
    bb.set_attr(_ka_to_execute=('agent_x', 2.4))
    bb.set_attr(hv_list=[0.1,0.2,0.3,0.4,0.5])
    bb.convergence_update()
    assert bb.get_attr('hv_list') == [0.1,0.2,0.3,0.4,0.5,0.5]
    
    ns.shutdown()
    time.sleep(0.05)  
    
def test_dc_indicator():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':100,  'goal':'gt', 'variable type': float},
            'power':             {'ll':0,   'ul':10,   'goal':'lt', 'goal type': 'max', 'variable type': list}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_metadata_level()

    bb.set_attr(convergence_type='dci hvi')
    bb.set_attr(dci_div={'reactivity swing': 100, 'burnup': 100, 'power': 10})
    
    cores = {'core_[70.0, 65.0, 0.42]': {'reactivity swing' : 500.0, 'burnup' : 70.0, 'power': 7.5}}

    bb.update_abstract_lvl(1, 'core_[70.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 70.0, 'power': [2.5,5.0,7.5]}}, panel='old')
    
    bb.dc_indicator()
    assert bb.get_attr('previous_pf') == cores
    assert bb.get_attr('dci_convergence_list') == [0.0]

    for i in range(60,70):
        bb.update_abstract_lvl(1, 'core_[{}.0, 65.0, 0.42]'.format(i), {'pareto type' : 'pareto', 'fitness function' : 1.0})
        bb.update_abstract_lvl(3, 'core_[{}.0, 65.0, 0.42]'.format(i), {'design variables': {'height': float(i), 'smear': 65.0, 'pu_content': 0.42}, 
                                                                        'objective functions': {'reactivity swing' : 500.0, 'burnup' : float(i), 'power': [2.5,5.0,7.5]}}, panel='old')
        cores.update({'core_[{}.0, 65.0, 0.42]'.format(i): {'reactivity swing' : 500.0, 'burnup' : float(i), 'power': 7.5 }})

    bb.dc_indicator()
    assert bb.get_attr('dci_convergence_list') == [0.0,  0.8409090909090909]
    assert bb.get_attr('previous_pf') == cores

    for i in range(71,100):
        bb.update_abstract_lvl(1, 'core_[{}.0, 65.0, 0.42]'.format(i), {'pareto type' : 'pareto', 'fitness function' : 1.0})
        bb.update_abstract_lvl(3, 'core_[{}.0, 65.0, 0.42]'.format(i), {'design variables': {'height': float(i), 'smear': 65.0, 'pu_content': 0.42}, 
                                                                        'objective functions': {'reactivity swing' : 500.0, 'burnup' : float(i), 'power': [2.5,5.0,7.5]}}, panel='old')
        cores.update({'core_[{}.0, 65.0, 0.42]'.format(i): {'reactivity swing' : 500.0, 'burnup' : float(i), 'power': 7.5}})
    
    bb.dc_indicator()
    assert bb.get_attr('dci_convergence_list') == [0.0,  0.8409090909090909, 0.70625]
    assert bb.get_attr('previous_pf') == cores

    bb.update_abstract_lvl(1, 'core_[71.1, 65.0, 0.42]'.format(i), {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[71.1, 65.0, 0.42]'.format(i), {'design variables': {'height': 71.1, 'smear': 65.0, 'pu_content': 0.42}, 
                                                                    'objective functions': {'reactivity swing' : 500.0, 'burnup' : 71.1, 'power': [2.5,5.0,7.5]}}, panel='old')
    cores.update({'core_[71.1, 65.0, 0.42]':  {'reactivity swing' : 500.0, 'burnup' : 71.1, 'power': 7.5}})
    bb.dc_indicator()
    assert bb.get_attr('dci_convergence_list') == [0.0,  0.8409090909090909, 0.70625, 0.0]
    assert bb.get_attr('previous_pf') == cores
    
    ns.shutdown()
    time.sleep(0.05)  
    
def test_determine_complete_dci_hvi():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,  'ul':100,  'goal':'gt', 'variable type': float},
            'power':             {'ll':0,   'ul':10,   'goal':'lt', 'goal type': 'avg', 'variable type': list}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_metadata_level()
    bb.set_attr(convergence_interval=1)
    bb.set_attr(skipped_tvs=0)
    bb.set_attr(pf_size=1)
    
    bb.set_attr(convergence_type='dci hvi')
    bb.set_attr(dci_div={'reactivity swing': 100, 'burnup': 100, 'power': 10})    
    
    bb.update_abstract_lvl(1, 'core_[70.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 1000.0, 'burnup' : 0.0, 'power': [2.5,5.0,7.5]}}, panel='old')
    bb.publish_trigger()
    bb.convergence_indicator()
    assert bb.get_attr('dci_convergence_list') == [0.0]
    assert bb.get_attr('hv_list') == [0.0, 0.0]
    bb.update_abstract_lvl(1, 'core_[71.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[71.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0, 'power': [2.5,5.0,7.5]}}, panel='old')
    bb.publish_trigger()       
    bb.convergence_indicator()
    bb.update_abstract_lvl(1, 'core_[71.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[71.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0, 'power': [2.5,5.0,7.5]}}, panel='old')
    bb.publish_trigger()        
    bb.convergence_indicator()
    
    bb.determine_complete_dci_hvi()
    assert bb.get_attr('dci_convergence_list') == [0.0,  0.5,  0.0]
    assert bb.get_attr('hv_list') == [0.0, 0.0, 0.0, 0.125]
    bb.update_abstract_lvl(1, 'core_[72.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[72.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 100.0, 'power': [2.5,5.0,7.5]}}, panel='old')
    bb.publish_trigger()                
    bb.convergence_indicator()
    bb.update_abstract_lvl(1, 'core_[72.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[72.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 100.0, 'power': [2.5,5.0,7.5]}}, panel='old')
    bb.publish_trigger()                
    bb.convergence_indicator()
    bb.determine_complete_dci_hvi()
    assert bb.get_attr('dci_convergence_list') == [0.0,  0.5,  0.0, 0.33333333333333337, 0.0]
    assert bb.get_attr('hv_list') == [0.0, 0.0, 0.0, 0.125, 0.125, 0.25]
    assert bb.get_complete_status() == False
    
    bb.update_abstract_lvl(1, 'core_[72.0, 65.0, 0.43]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[72.0, 65.0, 0.43]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.43}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 100.0, 'power': [2.5,5.0,7.5]}}, panel='old')
    bb.publish_trigger()                
    bb.convergence_indicator()
    bb.determine_complete_dci_hvi()
    assert bb.get_attr('dci_convergence_list') == [0.0,  0.5,  0.0, 0.33333333333333337, 0.0, 0.0]
    assert bb.get_attr('hv_list') == [0.0, 0.0, 0.0, 0.125, 0.125, 0.25, 0.25]
    assert bb.get_complete_status() == True

    ns.shutdown()
    time.sleep(0.05)

def test_add_meta_data_level():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(meta_data_to_log=['hvi'])
    bb.initialize_metadata_level()

    assert bb.get_attr('abstract_lvls_format') == {'level 1': {'pareto type': str, 'fitness function': float},
                                                   'level 2': {'new': {'valid': bool}, 
                                                               'old': {'valid': bool}},
                                                   'level 100': {'agent': str, 'hvi': float, 'time': float}}
    ns.shutdown()
    time.sleep(0.05)      
    
def test_log_metadata():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(meta_data_to_log=['hvi'])
    bb.initialize_metadata_level()

    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':50,  'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)

    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 100.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})    
    bb.log_metadata()
    bb.update_abstract_lvl(3, 'core_[64.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 250.0, 'burnup' : 75.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[64.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})    
    bb.log_metadata()    
    
    assert bb.get_attr('meta_data') == {'hvi': [0.0, 0.5, 0.625]}
    ns.shutdown()
    time.sleep(0.05)
    
def test_log_metadata2():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.set_attr(meta_data_to_log=['hvi', 'gd', 'igd'])
    bb.set_attr(problem=problem)    
    bb.initialize_metadata_level()
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)

    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.42}, 
                                                          'objective functions': {'f0' : 0.0, 'f1' : 0.0001, 'f2':0.5}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0}) 
    bb.update_abstract_lvl(3, 'core_[65.1, 65.0, 0.42]', {'design variables': {'x0': 0.651, 'x1': 0.651, 'x2': 0.43}, 
                                                          'objective functions': {'f0' : 0.5, 'f1' : 0.0, 'f2':0.0001}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.1, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})     
    bb.log_metadata()
    
    assert bb.get_attr('meta_data') == {'hvi': [0.0, 0.999999650000025], 'gd': [0.0, 0.0001], 'igd': [0.0, 0.31842014860754597]}
    ns.shutdown()
    time.sleep(0.05)       
    
def test_convergence_indicator_dci_hvi():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,  'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_metadata_level()

    bb.set_attr(convergence_type='dci hvi')
    bb.set_attr(dci_div={'reactivity swing': 100, 'burnup': 100})    
    bb.update_abstract_lvl(1, 'core_[70.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 1000.0, 'burnup' : 0.0}}, panel='old')
    
    bb.convergence_indicator()
    assert bb.get_attr('dci_convergence_list') == [0.0]
    bb.update_abstract_lvl(1, 'core_[71.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[71.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 500.0, 'burnup' : 50.0}}, panel='old')
        
    bb.convergence_indicator()
    assert bb.get_attr('dci_convergence_list') == [0.0,  1.0]

    ns.shutdown()
    time.sleep(0.05) 
    
def test_convergence_indicator_hvi():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,  'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_metadata_level()

    bb.update_abstract_lvl(1, 'core_[70.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 1000.0, 'burnup' : 0.0}}, panel='old')
    assert bb.get_attr('hv_list') == [0.0]

    bb.convergence_indicator()
    assert bb.get_attr('hv_list') == [0.0, 0.0]

    ns.shutdown()
    time.sleep(0.05) 

def test_convergence_indicator_random():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    objs = {'reactivity swing': {'ll':0,   'ul':1000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,  'ul':100,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)

    bb.update_abstract_lvl(1, 'core_[70.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 65.0, 0.42]', {'design variables': {'height': 70.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 1000.0, 'burnup' : 0.0}}, panel='old')
    assert bb.get_attr('hv_list') == [0.0]

    bb.convergence_indicator()
    assert bb.get_attr('hv_list') == [0.0, 0.0]

    ns.shutdown()
    time.sleep(0.05) 
    
def test_read_from_h5():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb_h5 = run_agent(name='blackboard1', base=bb_opt.BbOpt)
    bb_h5.set_attr(archive_name='blackboard_archive.h5')
    dv={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'experiments': {'length':         2, 
                                                  'dict':  {'0': {'options': ['exp_a', 'exp_b', 'exp_c'], 'default': 'no_exp', 'variable type': str},
                                                            '1': {'options': ['exp_a', 'exp_b', 'exp_c'], 'default': 'no_exp', 'variable type': str}},
                                                  'variable type': dict},}
    objs = {'reactivity swing': {'ll':0.0,  'ul':1000.0, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0.0,  'ul':100.0,  'goal':'gt', 'variable type': float},
            'powers':           {'ll': -10,  'ul':10.0,  'goal':'et', 'goal_type': 'max', 'variable type': list},
            'list_powers':      {'ll': -10,  'ul':10.0,  'goal':'et', 'goal_type': 'max', 'variable type': list},}
    cons = {'eol': {'ll': 1.0, 'ul': 2.0, 'variable type': float}}

    bb_h5.initialize_abstract_level_3(objectives=objs, design_variables=dv, constraints=cons)    
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dv, constraints=cons)
    bb.initialize_metadata_level()
    bb_h5.initialize_metadata_level()

    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 54.0, 'smear': 66.9, 'pu_content': 0.76, 'experiments': {'0': 'exp_a', '1':'no_exp'}},
                                         'objective functions': {'reactivity swing': 50.0, 'burnup': 10.0, 'powers': [0.1,0.2,0.3], 'list_powers': [[0.5,0.8,0.7],[0.2,0.9,0.4]]},
                                         'constraints': {'eol keff': 1.02}}, panel='old')    
    bb.write_to_h5()
    bb_bb = bb.get_attr('abstract_lvls')

    bb_h5.load_h5(panels={2: ['new','old'], 3: ['new','old']})    
    bb_h5_bb = bb_h5.get_attr('abstract_lvls')

    assert bb_bb == {'level 1': {}, 'level 2': {'new': {}, 'old': {}}, 'level 100': {}, 'level 3': {'new': {}, 'old': {'core_1': {'design variables': {'height': 54.0, 'smear': 66.9, 'pu_content': 0.76, 'experiments': {'0': 'exp_a', '1': 'no_exp'}}, 'objective functions': {'reactivity swing': 50.0, 'burnup': 10.0, 'powers': [0.1,0.2,0.3], 'list_powers': [[0.5,0.8,0.7],[0.2,0.9,0.4]]}, 'constraints': {'eol keff': 1.02}}}}}
    
    assert bb_h5_bb == {'level 1': {}, 'level 2': {'new': {}, 'old': {}}, 'level 100': {}, 'level 3': {'new': {}, 'old': {'core_1': {'design variables': {'height': 54.0, 'smear': 66.9, 'pu_content': 0.76, 'experiments': {'0': 'exp_a', '1': 'no_exp'}}, 'objective functions': {'reactivity swing': 50.0, 'burnup': 10.0, 'powers': [0.1,0.2,0.3], 'list_powers': [[0.5,0.8,0.7],[0.2,0.9,0.4]]}, 'constraints': {'eol keff': 1.02}}}}}
    
    os.remove('blackboard_archive.h5')
    ns.shutdown()
    time.sleep(0.05)    
    
def test_connect_sub_bb():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    
    bb.connect_sub_blackboard('sub_bb', bb_opt.SubBbOpt)
    sub_bb = bb.get_attr('_sub_bbs')
    assert [x for x in sub_bb.keys()] == ['sub_bb']
    sub_bb = sub_bb['sub_bb']
    assert sub_bb.get_attr('name') == 'sub_bb'
    assert sub_bb.get_attr('archive_name') == 'sub_bb.h5'
    assert sub_bb.get_attr('design_variables') == {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                                   'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                                   'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    assert sub_bb.get_attr('objectives') == {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                                             'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    assert sub_bb.get_attr('constraints') == {'eol keff': {'ll': 1.0, 'ul': 2.5, 'variable type': float},
                                              'pu mass':  {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
    
    assert sub_bb.get_attr('convergence_interval') == 25
    assert sub_bb.get_attr('convergence_rate') == 1E-4
    
    ns.shutdown()       
    time.sleep(0.05)    
    
def test_MasterBbOpt_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.MasterBbOpt)   
    
    assert bb.get_attr('objectives') == {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'goal': 'gt', 'variable type': float},
                           'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
    assert bb.get_attr('design_variables') == {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    assert bb.get_attr('constraints') == {
                            'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                            'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float}}
    
    assert bb.get_attr('convergence_interval') == 25
    assert bb.get_attr('convergence_rate') == 1E-4
    ns.shutdown()       
    time.sleep(0.05)    
    
def test_SubBbOpt_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.SubBbOpt)   
    
    assert bb.get_attr('objectives') == {'reactivity swing': {'ll':0,     'ul':750,  'goal':'lt', 'variable type': float},
                           'burnup':           {'ll':0,     'ul':200,  'goal':'gt', 'variable type': float},}
    assert bb.get_attr('design_variables') == {'height':     {'ll': 50.0, 'ul': 80.0, 'variable type': float},
                                 'smear':      {'ll': 50.0, 'ul': 70.0, 'variable type': float},
                                 'pu_content': {'ll': 0.0,  'ul': 1.0,  'variable type': float}}
    assert bb.get_attr('constraints') == {'eol keff':  {'ll': 1.0, 'ul': 2.5, 'variable type': float},
                            'pu mass':   {'ll':0,     'ul':2000, 'goal':'lt', 'variable type': float}}
    
    assert bb.get_attr('convergence_interval') == 25
    assert bb.get_attr('convergence_rate') == 1E-4    
    ns.shutdown()       
    time.sleep(0.05)     
    
def test_agent_performing_action():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.set_attr(problem=problem)
    bb.connect_agent(Stochastic, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_attr(debug_wait=True)
    rp.set_attr(debug_wait_time=0.25)
    bb.set_attr(_ka_to_execute=('ka_rp', 2))
    bb.send_executor()
    assert bb.get_attr('agent_addrs')['ka_rp']['performing action'] == True
    time.sleep(0.75)
    assert bb.get_attr('agent_addrs')['ka_rp']['performing action'] == False
    
    ns.shutdown()       
    time.sleep(0.05)  
    
def test_agent_shutdown():
    # Testing shutdown of agents who have failed (ka_rp2), who are idel (ka_rp3), and are in the middle of an action (ka_rp).
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs, constraints={})
    bb.set_attr(problem=problem)
    bb.connect_agent(Stochastic, 'ka_rp')
    bb.connect_agent(NeighborhoodSearch, 'ka_rp2')
    bb.connect_agent(Stochastic, 'ka_rp3')
    bb.connect_agent(KaBrLevel1, 'ka_br_lvl1')
    bb.connect_agent(KaBrLevel2, 'ka_br_lvl2')
    bb.connect_agent(KaBrLevel3, 'ka_br_lvl3')

    bb.update_abstract_lvl(3, 'core_[0.650,0.650,0.4]', {'design variables': {'x0': 0.650, 'x1': 0.650, 'x2': 0.4},
                                                         'objective functions': {'f0': 365.0, 'f1': 500.0, 'f2' : 600.0},
                                                         'constraints': {}}, panel='new')  

    bb.initialize_metadata_level()
    
    rp2 = ns.proxy('ka_rp2')
    # Force the agent to fail due to passing False
    rp = ns.proxy('ka_rp')
    bb.send('executor_{}'.format('ka_rp2'), False)
    
    rp.set_attr(debug_wait=True)
    rp.set_attr(debug_wait_time=0.1)
    bb.set_attr(_ka_to_execute=('ka_rp', 2))
    rp.set_random_seed(seed=1)
    bb.send_executor()
    assert bb.get_attr('agent_addrs')['ka_rp']['performing action'] == True
    while len(bb.get_attr('agent_addrs')) > 0:
        bb.send_shutdown()
        time.sleep(0.01)
    time.sleep(0.05)
    assert ns.agents() == ['blackboard'] 
    assert bb.get_attr('final_trigger') == 0
    assert list(bb.get_blackboard()['level 3']['old'].keys()) == ['core_[0.650,0.650,0.4]', 'core_[0.41702,0.72032,0.00011]']
    assert list(bb.get_blackboard()['level 2']['old'].keys()) == ['core_[0.650,0.650,0.4]', 'core_[0.41702,0.72032,0.00011]']
    assert list(bb.get_blackboard()['level 1'].keys()) == ['core_[0.41702,0.72032,0.00011]']

    ns.shutdown()       
    time.sleep(0.05)  

    
def test_pass_agent_attr():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.set_attr(problem=problem)
    bb.connect_agent(NeighborhoodSearch, 'ka_rp', attr={'perturbation_size' : 0.25})

    rp = ns.proxy('ka_rp')    
    assert rp.get_attr('perturbation_size') == 0.25

    ns.shutdown()       
    time.sleep(0.05)  