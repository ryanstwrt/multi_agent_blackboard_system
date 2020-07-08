import platypus as plat
import performance_measure as pm
import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import ka_rp
import bb_sfr_opt as bb_sfr
import pickle
import time
import copy

def test_hypervolume_indicator_base():    
    lower_ref = [0,0]
    upper_ref = [2,2]
    pf =[[1,1]]
    hv = pm.hypervolume_indicator(pf, lower_ref, upper_ref)
    assert hv == 0.25

def test_hypervolume_indicator_sfr():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_sfr.BbSfrOpt)

    model = 'lr'
    with open('/Users/ryanstewart/projects/Dakota_Interface/GA_BB/sm_{}.pkl'.format(model), 'rb') as pickle_file:
        sm_ga = pickle.load(pickle_file)
    bb.set_attr(sm_type=model)
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':1500, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':200,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaRpExploit, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(local_search='hill climbing')
    rp.set_attr(step_rate=0.5)
    rp.set_attr(step_limit = 150)
    lower_ref = [0,    -200]
    upper_ref = [1500, 0]
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'reactor parameters': {'height': 65.0, 'smear': 65.0, 
                                                                'pu_content': 0.42, 'reactivity swing' : 750.0,
                                                                'burnup' : 200.0}}, panel='old')
    pf = []
    for core in bb.get_attr('abstract_lvls')['level 3']['old'].values():
        rx_params = [core['reactor parameters']['reactivity swing'], -core['reactor parameters']['burnup']]
        pf.append(rx_params)
    hv1 = pm.hypervolume_indicator(pf, lower_ref, upper_ref)
    assert round(hv1,3) == 0.5
    bb.update_abstract_lvl(3, 'core_[70.0, 65.0, 0.65]', {'reactor parameters': {'height': 70.0, 'smear': 65.0, 
                                                                'pu_content': 0.65, 'reactivity swing' : 750.0,
                                                                'burnup' : 100.0}}, panel='old')
    pf = []
    for core in bb.get_attr('abstract_lvls')['level 3']['old'].values():
        rx_params = [core['reactor parameters']['reactivity swing'], -core['reactor parameters']['burnup']]
        pf.append(rx_params)
    hv2 = pm.hypervolume_indicator(pf, lower_ref, upper_ref)
    assert hv2 == hv1
    bb.update_abstract_lvl(3, 'core_[71.0, 65.0, 0.65]', {'reactor parameters': {'height': 70.0, 'smear': 65.0, 
                                                                'pu_content': 0.65, 'reactivity swing' : 740.0,
                                                                'burnup' : 200.0}}, panel='old')
    pf = []
    for core in bb.get_attr('abstract_lvls')['level 3']['old'].values():
        rx_params = [core['reactor parameters']['reactivity swing'], -core['reactor parameters']['burnup']]
        pf.append(rx_params)
    hv3 = pm.hypervolume_indicator(pf, lower_ref, upper_ref)
#    assert hv3 == 0.75
    
    ## Keep this in mind for determining the importance of an objective
    for num, var in enumerate(pf):   
        pf_test = copy.copy(pf)
        pf_test.pop(num)
        hv = pm.hypervolume_indicator(pf_test, lower_ref, upper_ref)
        print('New Volume: {}, Contribution: {}'.format(hv, hv3-hv))
    ns.shutdown()
    time.sleep(0.05)
    assert 1 > 2