import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import bb_basic
import time
import os

def test_BbTraditional_init():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_basic.BbTraditional)
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
    bb = run_agent(name='blackboard', base=bb_basic.BbTraditional)
    bb.connect_agent('rp', 'ka_rp')
    bb.connect_agent('br', 'ka_br')
    
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
    bb = run_agent(name='blackboard', base=bb_basic.BbTraditional)
    bb.connect_agent('rp', 'ka_rp')
    bb.connect_agent('rp', 'ka_rp1')
    bb.connect_agent('rp', 'ka_br')
    
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
    bb = run_agent(name='blackboard', base=bb_basic.BbTraditional)

    bb.add_abstract_lvl(1, {'entry 1': str, 'entry 2': bool, 'entry 3': int})
    bb.update_abstract_lvl(1, 'core_1', {'entry 1': 'test', 'entry 2': False, 'entry 3': 2})
    bb.determine_complete()
    
    assert bb.get_attr('_complete') == True
    ns.shutdown()
    time.sleep(0.1)