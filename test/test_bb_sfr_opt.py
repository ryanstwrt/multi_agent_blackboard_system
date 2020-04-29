import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import bb_sfr_opt as bb_sfr
import time
import os
import ka_rp as karp
import ka_br as kabr

def test_BbTraditional_init():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbTraditional)
    assert bb.get_attr('agent_addrs') == {}
    assert bb.get_attr('_agent_writing') == False
    assert bb.get_attr('_new_entry') == False
    assert bb.get_attr('archive_name') == 'blackboard_archive.h5'
    assert bb.get_attr('_sleep_limit') == 10

    assert bb.get_attr('abstract_lvls') == {}
    assert bb.get_attr('abstract_lvls_format') == {}
    
    assert bb.get_attr('_ka_to_execute') == (None, 0) 
    assert bb.get_attr('_trigger_event') == 0
    assert bb.get_attr('_kaar') == {}
    assert bb.get_attr('_pub_trigger_alias') == 'trigger'
    
    assert bb.get_attr('_complete') == False
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_connect_agent():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbTraditional)
    bb.connect_agent(karp.KaRp_verify, 'ka_rp')
    bb.connect_agent(kabr.KaBr_verify, 'ka_br')
    
    agents = bb.get_attr('agent_addrs')
    
    assert [x for x in agents.keys()] == ['ka_rp', 'ka_br']
    assert ns.agents() == ['blackboard', 'ka_rp', 'ka_br']

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
    time.sleep(0.1)
    
def test_determine_complete():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbTraditional)
    bb.connect_agent(karp.KaRp_verify, 'ka_rp')
    bb.connect_agent(karp.KaRp_verify, 'ka_rp1')
    bb.connect_agent(kabr.KaBr_verify, 'ka_br')
    
    assert ns.agents() == ['blackboard', 'ka_rp', 'ka_rp1', 'ka_br']

    
    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    bb.determine_complete()
    
    time.sleep(0.5)
    assert bb.get_attr('_complete') == True
    assert ns.agents() == ['blackboard']

    ns.shutdown()
    time.sleep(0.1)
    
def test_wait_for_ka():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbTraditional)

    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    bb.determine_complete()
    
    assert bb.get_attr('_complete') == True
    ns.shutdown()
    time.sleep(0.1)
    
#----------------------------------------------------------
# Tests fopr BbSfrOpt
#----------------------------------------------------------

def test_BbSfrOpt_init():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    assert bb.get_attr('agent_addrs') == {}
    assert bb.get_attr('_agent_writing') == False
    assert bb.get_attr('_new_entry') == False
    assert bb.get_attr('archive_name') == 'blackboard_archive.h5'
    assert bb.get_attr('_sleep_limit') == 10

    assert bb.get_attr('abstract_lvls_format') == {'level 1': {'new':{'pareto type': str}, 'old':{'pareto type': str}},
                                            'level 2': {'new': {'valid': bool}, 'old': {'valid': bool}},
                                            'level 3': {'reactor parameters': {'height': float, 'smear': float, 'pu_content': float, 'cycle length': float, 'reactivity swing': float, 'burnup': float, 'pu mass': float}}}

    assert bb.get_attr('abstract_lvls') == {'level 1': {'new':{}, 'old':{}}, 'level 2': {'new':{}, 'old':{}}, 'level 3': {}}
    
    assert bb.get_attr('_ka_to_execute') == (None, 0) 
    assert bb.get_attr('_trigger_event') == 0
    assert bb.get_attr('_kaar') == {}
    assert bb.get_attr('_pub_trigger_alias') == 'trigger'
    
    assert bb.get_attr('_complete') == False
    
    ns.shutdown()
    time.sleep(0.1)
    
def test_add_ka_specific():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.connect_agent(karp.KaRpExplore, 'ka_rp_explore')
    bb.connect_agent(karp.KaRpExploit, 'ka_rp_exploit')
    bb.connect_agent(kabr.KaBr_lvl2, 'ka_br_lvl2')
    bb.connect_agent(kabr.KaBr_lvl3, 'ka_br_lvl3')

    for alias in ns.agents():
        agent = ns.proxy(alias)
        if 'rp' in alias:
            assert agent.get_attr('objectives') == ['cycle length', 'reactivity swing', 'burnup', 'pu mass']
            assert agent.get_attr('sm_type') == 'interpolate'
        elif 'lvl3' in alias:
            assert agent.get_attr('desired_results') == {'cycle length': (0, 1000), 
                                                         'reactivity swing': (0, 7500), 'burnup': (0,200), 'pu mass': (0, 1000)}
        elif 'lvl2' in alias:
            assert agent.get_attr('desired_results') == {'cycle length': 'gt', 
                                                         'reactivity swing': 'lt', 'burnup': 'gt', 'pu mass': 'lt'}
            
    ns.shutdown()
    time.sleep(0.1)  

def test_determine_complete():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    bb.connect_agent(kabr.KaBr_lvl2, 'ka_br_lvl2')

    for x in range(11):
        name = 'core{}'.format(x)
        entry = {'pareto type': 'pareto'}
        bb.update_abstract_lvl(1, name, entry, panel='new')
    assert bb.get_attr('_complete') == False
    bb.determine_complete()
    time.sleep(0.1)
    assert bb.get_attr('_complete') == True
    assert ns.agents() == ['blackboard']

    ns.shutdown()
    time.sleep(0.1)
    
def test_handler_writer():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)
    rp = run_agent(name='explore', base=karp.KaRpExplore)
    rp1 = run_agent(name='exploit', base=karp.KaRpExploit)
    rp.add_blackboard(bb)
    rp1.add_blackboard(bb)
    rp.connect_writer()
    rp1.connect_writer()
    
    rp.set_attr(_entry={'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                               'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}})
    rp.set_attr(_entry_name='core1')
    rp.write_to_bb()
    assert bb.get_attr('abstract_lvls')['level 3'] == {'core1': {'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                                                                        'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}}

    rp1.set_attr(_entry={'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                                'cycle length': 100.0, 'reactivity swing': 10000.0, 'burnup': 32.0, 'pu mass': 1000.0}})
    rp1.set_attr(_entry_name='core2')
    rp1.write_to_bb(True)
    
    assert bb.get_attr('abstract_lvls')['level 3'] == {'core1': {'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                                                                        'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}},
                                                       'core2': {'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 'cycle length': 100.0, 'reactivity swing': 10000.0, 'burnup': 32.0, 'pu mass': 1000.0}}}

    rp1.set_attr(_entry={'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                                'cycle length': 100.0, 'reactivity swing': 10000.0, 'burnup': 32.0, 'pu mass': 1000.0}})
    rp1.set_attr(_entry_name='core3')

    assert bb.get_attr('_new_entry') == True
    bb.set_attr(_new_entry=False)
    rp1.write_to_bb(False)
    assert bb.get_attr('_new_entry') == False

    
    assert bb.get_attr('abstract_lvls')['level 3'] == {'core1': {'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                                                                        'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}},
                                                       'core2': {'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                                                                        'cycle length': 100.0, 'reactivity swing': 10000.0, 'burnup': 32.0, 'pu mass': 1000.0}},
                                                       'core3': {'reactor parameters': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2, 
                                                                                        'cycle length': 100.0, 'reactivity swing': 10000.0, 'burnup': 32.0, 'pu mass': 1000.0}}}
    
    
    ns.shutdown()
    time.sleep(0.1)          

def test_BbSfrOpt_add_panel():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_sfr.BbSfrOpt)

    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.add_panel(1, ['new', 'old'])
    print(bb.get_attr('abstract_lvls'))

    ns.shutdown()
    time.sleep(0.1)
