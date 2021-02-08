from osbrain import run_nameserver
from osbrain import run_agent
import src.ka_s.random_walk as rw
import src.bb.blackboard_optimization as bb_opt
import pickle
import time

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)

def test_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=rw.RandomWalk)
    
    assert rp.get_attr('_base_trigger_val') == 5.00001 
    assert rp.get_attr('_class') == 'local search random walk'
    assert rp.get_attr('step_size') == 0.01
    assert rp.get_attr('walk_length') == 10
        
    ns.shutdown()
    time.sleep(0.1)
    
def test_search_method():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(rw.RandomWalk, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=10893)

    bb.update_abstract_lvl(3, 'core_[65.0,65.0,0.4]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4},
                                                          'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0,'burnup' : 50.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0,65.0,0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0,65.0,0.4]'])
    rp.search_method()
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0,65.0,0.4]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    
    
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'].keys()) == ['core_[65.0,64.99541,0.4]','core_[65.00093,64.99541,0.4]','core_[65.00093,64.99541,0.39677]','core_[65.01003,64.99541,0.39677]','core_[65.01003,64.99541,0.39262]','core_[65.01003,64.9917,0.39262]','core_[65.01003,64.9831,0.39262]','core_[65.01003,64.9831,0.38717]','core_[65.0023,64.9831,0.38717]','core_[65.0023,64.98111,0.38717]']
    ns.shutdown()
    time.sleep(0.1)