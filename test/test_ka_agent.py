import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pandas as pd
import blackboard
import knowledge_agent as ka
import time

def test_ka_init_agent():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    assert ka_b.get_attr('entry') == None
    assert ka_b.get_attr('bb') == None
    assert ka_b.get_attr('rep_addr') == None
    assert ka_b.get_attr('rep_alias') == None
    ns.shutdown()
    time.sleep(0.01)
    
def test_ka_reactor_physics_init():
    ns = run_nameserver()
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    assert ka_rp.get_attr('entry') == None
    assert ka_rp.get_attr('bb') == None
    assert ka_rp.get_attr('rep_addr') == None
    assert ka_rp.get_attr('rep_alias') == None
    assert ka_rp.get_attr('core_name') == None
    assert ka_rp.get_attr('xs_set') == None
    assert ka_rp.get_attr('rx_parameters') == None
    assert ka_rp.get_attr('surrogate_models') == None
    ns.shutdown()
    time.sleep(0.01)

def test_add_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_b.add_blackboard(bb)
    ka_rp.add_blackboard(bb)
    
    ka_b_bb = ka_b.get_attr('bb')
    ka_b_rp = ka_rp.get_attr('bb')
    assert ka_b.get_attr('bb') == bb
    assert ka_b_bb.get_attr('trained_models') == None
    assert ka_rp.get_attr('bb') == bb
    assert ka_b_rp.get_attr('trained_models') == None
    bb.set_attr(trained_models=10)
    assert ka_b_bb.get_attr('trained_models') == 10
    assert ka_b_rp.get_attr('trained_models') == 10
    ns.shutdown()
    time.sleep(0.01)

def test_connect_REP_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_b = run_agent(name='ka_base', base=ka.KaBase)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)

    ka_b.add_blackboard(bb)
    ka_b.connect_REP_blackboard()
    ka_rp.connect_REP_blackboard()
    assert ka_b.get_attr('rep_alias') == 'write_0'
    assert ka_rp.get_attr('rep_alias') == 'write_1'
    assert bb.get_attr('agent_addrs')['ka_base']['addr'] == ka_b.get_attr('rep_addr')
    assert bb.get_attr('agent_addrs')['ka_rp']['addr'] == ka_rp.get_attr('rep_addr')
    assert bb.get_attr('agent_addrs')['ka_base']['alias'] == ka_b.get_attr('rep_alias')
    assert bb.get_attr('agent_addrs')['ka_rp']['alias'] == ka_rp.get_attr('rep_alias')
    ns.shutdown()
    time.sleep(0.01)

def test_write_to_blackboard():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    ka_rp = run_agent(name='ka_rp', base=ka.KaReactorPhysics)
    ka_rp.add_blackboard(bb)
    ka_rp.connect_REP_blackboard()
    
    assert bb.get_attr('agent_writing') == False
    ka_rp.set_attr(core_name='core_1')
    ka_rp.write_to_blackboard()
    lvl_3 = bb.get_attr('lvl_3')
    assert bb.get_attr('agent_writing') == False
    assert lvl_3 == {'core_1': {'reactor_parameters': None, 'xs_set': None}}

    ns.shutdown()
    time.sleep(0.01)