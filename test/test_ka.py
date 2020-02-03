import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import pandas as pd
import blackboard
import knowledge_agent as ka
import time

def test_ka_init():
    ka_b = ka.KaBase()
    assert ka_b.bb == None
    assert ka_b.entry == None
    
def test_ka_reactor_physics_init():
    ka_rp = ka.KaReactorPhysics()
    assert ka_rp.bb == None
    assert ka_rp.core_name == None
    assert ka_rp.xs_set == None
    assert ka_rp.rx_parameters == None
    assert ka_rp.surrogate_models == None
    
def test_ka_add_blackboard():
    bb = blackboard.Blackboard()
    ka_b = ka.KaBase()
    ka_b.add_blackboard(bb)
    assert ka_b.bb == bb
    ka_rp = ka.KaReactorPhysics()
    ka_rp.add_blackboard(bb)
    assert ka_rp.bb == bb    
    
def test_ka_base_write_to_blackboard():
    bb = blackboard.Blackboard()
    ka_b = ka.KaBase()
    ka_b.add_blackboard(bb)
    try:
        ka_b.write_to_blackboard()
    except NotImplementedError:
        pass
    ka_rp = ka.KaReactorPhysics()
    ka_rp.add_blackboard(bb)
    ka_rp.write_to_blackboard()
