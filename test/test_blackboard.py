import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard

def test_blackboard_init():
    bb = blackboard.Blackboard()
    assert bb.agents == []
    assert bb.trained_models == None
    assert bb.lvl_1 == {}
    assert bb.lvl_2 == {}
    assert bb.lvl_3 == {}
    assert bb.lvl_4 == {}
    
def test_blackboard_agent_init():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=blackboard.Blackboard)
    assert bb.get_agents() == []
    assert bb.get_trained_models() == None
    for lvl_val, x in zip([{},{},{},{},None],[1,2,3,4,5]):
        assert bb.get_abstract_lvl(x) == lvl_val
    ns.shutdown()