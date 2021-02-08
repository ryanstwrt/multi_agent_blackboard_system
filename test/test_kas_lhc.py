from osbrain import run_nameserver
from osbrain import run_agent
import src.ka_s.latin_hypercube as lhc
import src.bb.blackboard_optimization as bb_opt
import time
import pickle

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)
    
def test_kalhc_init():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=lhc.LatinHypercube)
    
    assert rp.get_attr('lhc_criterion') == 'corr'
    assert rp.get_attr('samples') == 50
    assert rp.get_attr('_class') == 'global search lhc'
    assert rp.get_attr('lhd') == []

    ns.shutdown()
    time.sleep(0.1)    

def test_generate_lhc():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=lhc.LatinHypercube)
    rp.set_random_seed(seed=10997)
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'experiment': {'length': 2,
                                                 'positions': {0: {'options': ['exp_a', 'exp_b', 'exp_c'], 'default': 'no_exp'},
                                                               1: {'options': ['exp_a', 'exp_b', 'exp_c'], 'default': 'no_exp'}},
                                                 'variable type': dict}})    
    rp.generate_lhc()
    lhd = rp.get_attr('lhd')
    assert lhd == [[0.6809999209057951, 0.9615554120232527, 0.49656136684737456, 0.9753243724316766, 0.5019089304961952], [0.9711929013977654, 0.014420205584720094, 0.5192722373572922, 0.1279353428242664, 0.6880940980900646], [0.9029453327709236, 0.41564054492670804, 0.12524195183344775, 0.5008270962873299, 0.9213089340448322], [0.760106621381224, 0.8256601839562258, 0.19696646617949254, 0.36327990785753816, 0.5728934947684282], [0.25191957728746656, 0.2742073822654635, 0.3946508203790589, 0.34071434932779604, 0.2808863163171574], [0.3261081220838052, 0.11713486597548692, 0.11755167713123542, 0.7281942873539828, 0.08015303316928864], [0.546817645943099, 0.335024003267946, 0.03538110932968111, 0.817185175179983, 0.11288643322276645], [0.7216321185551147, 0.5277928209501944, 0.007117453248059203, 0.01627725899672589, 0.8305757707564757], [0.45717629129198484, 0.7369527003874893, 0.29736254914813715, 0.8890264667775205, 0.5273197030191737], [0.14947031043076825, 0.7862241883170962, 0.8252870834868686, 0.7917246248809088, 0.14691500824973178], [0.12317508868319735, 0.2191120619863837, 0.9287142106733572, 0.6210427488692436, 0.005368002026281429], [0.5131509950761277, 0.8163990356740751, 0.41720078439043257, 0.520062418618913, 0.340404341145027], [0.046578252639894534, 0.3553341545186359, 0.745036660374928, 0.8640850551933599, 0.13156175088378053], [0.8084281193323344, 0.7435619420595818, 0.43421318678357185, 0.0811100149287789, 0.04149123952860425], [0.7026783876604088, 0.6363854631864223, 0.6276370396582142, 0.4859182656526318, 0.4873622749699796], [0.8648402574588648, 0.9596412744910673, 0.8850391354662579, 0.7656966623003391, 0.20160884068451657], [0.3608651836255723, 0.22904607159071289, 0.8548427553131095, 0.1997527791473003, 0.31333988805820184], [0.035135916536563644, 0.48305051199883114, 0.21220474768951486, 0.6508556400847968, 0.4772493310208327], [0.7414297136229501, 0.19345349055487027, 0.5503784508924382, 0.4543827578521749, 0.6450563364348826], [0.7908737154105588, 0.06864094060375973, 0.985124913621794, 0.9410224992094903, 0.7902700495183921], [0.9492116849063968, 0.6449525675093549, 0.7719233080580197, 0.4269053129712221, 0.06673178481708908], [0.9307529967857859, 0.3772945171244503, 0.8105473979934937, 0.547401920648945, 0.8925392553294992], [0.6677777643127027, 0.4381329874395766, 0.0684876343235781, 0.22654640913905189, 0.6372388246374948], [0.491618949547566, 0.5491499089737797, 0.27237237494926053, 0.417540613116595, 0.22814905319371256], [0.22091329921406713, 0.45072850934023484, 0.4638130634843712, 0.2819716913781361, 0.9481217460913061], [0.99779977413383, 0.25830966174416664, 0.9731122694424358, 0.14194402970902453, 0.16650959207467889], [0.478080446563879, 0.7041705023685793, 0.3196544619615771, 0.4617971946069063, 0.43526681115267846], [0.831488020645436, 0.8753990715851918, 0.44070629299111136, 0.742511342904494, 0.3798067891622577], [0.6012738296754573, 0.5983770210388333, 0.9423414987673968, 0.9160420733687628, 0.26461339438279013], [0.16264029047647297, 0.6686633024806984, 0.042930939124140886, 0.07459846214462147, 0.6600877929602722], [0.5253487772571346, 0.850095314024168, 0.6579216542711231, 0.21466993519783992, 0.8420227408917628], [0.3979516905073986, 0.31179868546846085, 0.377960825049331, 0.8420293474325576, 0.6032477382805003], [0.26021766247161243, 0.7639263124555183, 0.8777204081265246, 0.9207013625661176, 0.4099399217184587], [0.29770939710990124, 0.5793502235996228, 0.597318807579994, 0.5727809229329885, 0.7061648960005137], [0.08613657060288658, 0.9080195854625139, 0.6065147317498194, 0.670137215134317, 0.3966205055203018], [0.8862787714220052, 0.08008040990853478, 0.7972304601991467, 0.7070451399813448, 0.5501568930700536], [0.8433708795606224, 0.15629543786736394, 0.34938241131245845, 0.03498301948134661, 0.33114318350116123], [0.1910539019560776, 0.034441644482956335, 0.16058532022672214, 0.04510607776428564, 0.7329670436480403], [0.2028658666024252, 0.04746251608346475, 0.2387781290495534, 0.24978188991977981, 0.9805489856413713], [0.07377918369538064, 0.6021721089165694, 0.7076248947578693, 0.26896180561747934, 0.7610403461750422], [0.5781196840788726, 0.38134000100694976, 0.1486963171704705, 0.39996255378632856, 0.034366984476487214], [0.62396860340395, 0.1795797709205764, 0.5210639624508315, 0.5802255748137496, 0.9173951284942847], [0.4094682744418657, 0.8887104440125481, 0.6737779098269228, 0.33122639406899196, 0.2531109919730137], [0.10857473536160422, 0.29225313605260744, 0.08914398961265789, 0.3029338927387737, 0.5889524616403902], [0.34655438603384503, 0.1370457475966135, 0.5672450368345973, 0.16438779181610827, 0.8653204591914218], [0.31931546420513685, 0.9864682607401479, 0.9096376173424926, 0.10006347004578053, 0.19870131205635844], [0.6468767680986667, 0.6865027854710395, 0.2557193933680521, 0.999586480066712, 0.9742715060131517], [0.584821380475579, 0.5080215387083696, 0.33302306191347, 0.8353079763371324, 0.7491875753985664], [0.017826451336479466, 0.9209988009572339, 0.7294827107430164, 0.6162221912944784, 0.8075493284522128], [0.4299487147814416, 0.46415791852288174, 0.6846919208130772, 0.6814056510957717, 0.4499607667592258]]
    
    ns.shutdown()
    time.sleep(0.1) 
    
def test_search_method_continuous():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=lhc.LatinHypercube)
    rp.set_random_seed(seed=10997)
    
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' : {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                  'experiments': {'length':         2, 
                                                  'dict':      {'0': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                                                'random variable': {'ll': 0,  'ul': 2,  'variable type': float}},
                                                  'variable type': dict}})   
    rp.set_attr(samples=2)
    rp.generate_lhc()
    lhd = rp.get_attr('lhd')[0]
    rp.set_attr(_lvl_data={'core_[75.83123,57.2101,0.87458,exp_c,exp_b,0.7568]': {},
                           'core_[63.36984,67.69055,0.17794,no_exp,exp_a,1.37313]': {}})
    rp.search_method()
    design = rp.get_attr('current_design_variables')

    assert lhd == [0.8610411120739083, 0.36050513961800235, 0.8745754870336653, 0.40693147491814724, 0.6644563159973633, 0.378397913414091]
    assert design == {'height': 63.36984, 'smear': 67.69055, 'pu_content': 0.17794, 'position': 'no_exp', 'experiments': {'0': 'exp_a', 'random variable': 1.37313}}
        
    ns.shutdown()
    time.sleep(0.1) 
    
def test_search_method_discrete():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=lhc.LatinHypercube)
    rp.set_random_seed(seed=10997)
    
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' : {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                   })   

    ns.shutdown()
    time.sleep(0.1)     

def test_handler_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(lhc.LatinHypercube, 'ka_rp_lhc')
    
    rp = ns.proxy('ka_rp_lhc')
    rp.set_attr(_trigger_val=2)
    rp.set_random_seed(seed=10997)
    rp.set_attr(samples=2)
    rp.generate_lhc()
    bb.set_attr(_ka_to_execute=('ka_rp_lhc', 2))
    bb.send_executor()
    time.sleep(0.5)

    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core_[57.99991,50.89339,0.6786]': {'design variables': {'height': 57.99991, 'smear': 50.89339, 'pu_content': 0.6786}, 'objective functions': {'cycle length': 120.0, 'reactivity swing': 1074.32906, 'burnup': 101.35059, 'pu mass': 670.08062}, 'constraints': {'eol keff': 0.92403}}, 'core_[78.82683,60.40718,0.10726]': {'design variables': {'height': 78.82683, 'smear': 60.40718, 'pu_content': 0.10726}, 'objective functions': {'cycle length': 120.0, 'reactivity swing': 569.0823, 'burnup': 63.53671, 'pu mass': 168.10431}, 'constraints': {'eol keff': 0.98864}}}
    assert rp.get_attr('_trigger_val') == 0    

    ns.shutdown() 
    time.sleep(0.1)

def test_handler_trigger_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(lhc.LatinHypercube, 'ka_rp_lhc')
    
    bb.publish_trigger()
    time.sleep(0.075)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp_lhc': 50.000006}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_lhc', 50.000006)
    
    rp = ns.proxy('ka_rp_lhc')
    rp.set_attr(lhd=[])

    bb.publish_trigger()
    time.sleep(0.075)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp_lhc': 50.000006}, 2: {'ka_rp_lhc': 0.0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    ns.shutdown()
    time.sleep(0.1)