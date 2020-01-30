import blackboard as blackboard

def test_blackboard_init():
    bb = blackboard.Blackboard()
    assert bb.agents == []
    assert bb.trained_models == None
    assert bb.lvl_1 == {}
    assert bb.lvl_2 == {}
    assert bb.lvl_3 == {}
    assert bb.lvl_4 == {}