import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import src.blackboard as blackboard
import pickle
import src.ka as ka
import time
import src.ka_rp as ka_rp
import src.bb_opt as bb_opt
import src.moo_benchmarks as moo

with open('./sm_gpr.pkl', 'rb') as pickle_file:
    sm_ga = pickle.load(pickle_file)


def test_karp_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaRp)
    assert rp.get_attr('bb') == None
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    
    assert rp.get_attr('_trigger_val') == 0
    assert rp.get_attr('_base_trigger_val') == 0.250001   
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('_design_variables') == {}    
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('_class') == 'search'
    assert rp.get_attr('_lvl_data') == {}
    
    ns.shutdown()
    time.sleep(0.05)
    
#----------------------------------------------------------
# Tests fopr KA-RP-Explore
#----------------------------------------------------------

def test_karp_explore_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaGlobal)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl_data') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 0
    assert rp.get_attr('_base_trigger_val') == 0.250001
    
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_design_variables') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    ns.shutdown()
    time.sleep(0.05)
    
def test_explore_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(ka_rp.KaGlobal, 'ka_rp_explore')
    
    rp = ns.proxy('ka_rp_explore')
    rp.set_attr(_trigger_val=1)
    bb.set_attr(_ka_to_execute=('ka_rp_explore', 2))
    bb.send_executor()
    time.sleep(0.05)
    
    entry = rp.get_attr('_entry')
    core_name = rp.get_attr('_entry_name')
    bb_entry = {core_name: entry}
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == bb_entry
    assert rp.get_attr('_trigger_val') == 0    

    ns.shutdown()
    time.sleep(0.05)

def test_explore_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(ka_rp.KaGlobal, 'ka_rp')
    
    bb.publish_trigger()
    time.sleep(0.15)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0.250001}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 0.250001)
    
    bb.publish_trigger()
    time.sleep(0.15)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0.250001}, 2: {'ka_rp': 0.500002}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 0.500002)
    
    ns.shutdown()
    time.sleep(0.05)

def test_get_design_name():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaGlobal)
    rp.set_random_seed(seed=1)
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' : {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                  'experiments': {'length':         2, 
                                                  'dict':      {'0': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                                                'random variable': {'ll': 0,  'ul': 2,  'variable type': float}},
                                                  'variable type': dict}})
    
    current_design_variables={'height': 62.51066, 'smear': 64.40649, 'pu_content': 0.00011, 'position': 'exp_d', 'experiments': {'0':'exp_a', 'random variable': 0.18468}}
    name = rp.get_design_name(current_design_variables)
    assert name == 'core_[62.51066, 64.40649, 0.00011, exp_d, exp_a, 0.18468]'
    
    
    ns.shutdown()
    time.sleep(0.05)    
    

def test_explore_search_method():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaGlobal)
    rp.set_random_seed(seed=1)
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' : {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                  'experiments': {'length':         2, 
                                                  'dict':      {'0': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                                                'random variable': {'ll': 0,  'ul': 2,  'variable type': float}},
                                                  'variable type': dict}})
    
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('_entry_name') == None
    rp.search_method()
    assert rp.get_attr('current_design_variables') == {'height': 62.51066, 'smear': 64.40649, 'pu_content': 0.00011, 'position': 'exp_d', 'experiments': {'0':'exp_a', 'random variable': 0.18468}}
    rp.search_method()
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_explore_set_random_seed():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaGlobal)
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                 'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                 'pu_content': {'ll': 0,  'ul': 1,  'variable type': float}})    
    rp.set_random_seed(seed=10983)
    rp.search_method()
    assert rp.get_attr('current_design_variables') == {'height': 77.10531, 'pu_content': 0.29587, 'smear': 64.46135}
    rp.set_random_seed()
    rp.search_method()
    assert rp.get_attr('current_design_variables') != {'height': 77.10531, 'pu_content': 0.29587, 'smear': 64.46135}
    
    ns.shutdown()
    time.sleep(0.05)    
    
    
#def test_create_sm_interpolate():
#    ns = run_nameserver()
#    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
#    objs={'bol keff': {'ll':0.95, 'ul': 1.25, 'goal':'gt', 'variable type': float}, 
#                       'void': {'ll':-200, 'ul': 0, 'goal':'lt',  'variable type': float}, 
#                       'doppler': {'ll':-10, 'ul':0, 'goal':'lt',  'variable type': float}}
#    bb.initialize_abstract_level_3(objectives=objs)
#    bb.generate_sm()
#    
#    sm = bb.get_attr('_sm')
#    keff = sm['bol keff']((61.37,51.58,0.7340))
#    assert keff == 0.9992587833657331
#    
#    ns.shutdown()
#    time.sleep(0.05)

#def test_create_sm_regression():
#    ns = run_nameserver()
#    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
 #   objs={'bol keff': {'ll':0.95, 'ul':1.25, 'goal':'gt', 'variable type': float}}
  #  bb.initialize_abstract_level_3(objectives=objs)
   # bb.set_attr(sm_type='lr')
#    bb.generate_sm()
 #   time.sleep(0.05)
  #  sm = bb.get_attr('_sm')
   # objs = sm.predict('lr', [[61.37,51.58,0.7340]])
#    assert round(objs[0][0], 8) == 1.00720012
 #   assert round(sm.models['lr']['score'], 8)  == round(0.95576537, 8)
  #  assert round(sm.models['lr']['mse_score'], 8) == round(0.04423463, 8)
    
#    ns.shutdown()
#    time.sleep(0.05)

#----------------------------------------------------------
# Tests for KA-LHC
#----------------------------------------------------------

def test_kalhc_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLHC)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl_data') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 0
    
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_design_variables') == {}
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('lhc_criterion') == 'corr'
    assert rp.get_attr('samples') == 50
    assert rp.get_attr('lhd') == []

    ns.shutdown()
    time.sleep(0.05)    

def test_kalhc_generate_lhc():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLHC)
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
    time.sleep(0.05) 
    
def test_kalhc_search_method():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLHC)
    rp.set_random_seed(seed=10997)
    
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' : {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                  'experiments': {'length':         2, 
                                                  'dict':      {'0': {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                                                'random variable': {'ll': 0,  'ul': 2,  'variable type': float}},
                                                  'variable type': dict}})   
    rp.generate_lhc()
    lhd = rp.get_attr('lhd')[0]
    
    rp.search_method()
    design = rp.get_attr('current_design_variables')
    assert lhd == [0.49289349476842825, 0.27333988805820186, 0.6094827107430164, 0.28938241131245845, 0.7480195854625139, 0.1395797709205764]
    assert design == {'height': 64.7868, 'smear': 55.4668, 'pu_content': 0.60948, 'position': 'exp_b', 'experiments': {'0': 'exp_b', 'random variable': 0.27916}}
    ns.shutdown()
    time.sleep(0.05) 

    
def test_kalocal_search_method_discrete():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLHC)
    rp.set_random_seed(seed=10997)
    
    rp.set_attr(_design_variables={'height':     {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' : {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},
                                   })   

    ns.shutdown()
    time.sleep(0.05)     

def test_kalhc_handler_executor():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(ka_rp.KaLHC, 'ka_rp_lhc')
    
    rp = ns.proxy('ka_rp_lhc')
    rp.set_attr(_trigger_val=2)
    bb.set_attr(_ka_to_execute=('ka_rp_lhc', 2))
    bb.send_executor()
    time.sleep(0.05)
    
    entry = rp.get_attr('_entry')
    core_name = rp.get_attr('_entry_name')
    bb_entry = {core_name: entry}
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == bb_entry
    assert rp.get_attr('_trigger_val') == 0    

    ns.shutdown()
    time.sleep(0.05)

def test_kalhc_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.connect_agent(ka_rp.KaLHC, 'ka_rp_lhc')
    
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp_lhc': 50.000006}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp_lhc', 50.000006)
    
    rp = ns.proxy('ka_rp_lhc')
    for i in range(50):
        rp.search_method()
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp_lhc': 50.000006}, 2: {'ka_rp_lhc': 0.0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    ns.shutdown()
    time.sleep(0.05)
    
#----------------------------------------------------------
# Tests for KA-Local
#----------------------------------------------------------

def test_karp_exploit_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLocal)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl_data') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 0.0
    
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('bb_lvl_read') == 1
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('current_design_variables') == {}
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_design_variables') == {}
    assert rp.get_attr('perturbation_size') == 0.05
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5
    assert rp.get_attr('_lvl_data') == None
    assert rp.get_attr('lvl_read') == None
    assert rp.get_attr('analyzed_design') == {}
    assert rp.get_attr('new_designs') == []

    ns.shutdown()
    time.sleep(0.05)

#----------------------------------------------------------
# Tests fopr KA-Local-HC
#----------------------------------------------------------

def test_karp_exploit_init_local_hill_climb():
    ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=ka_rp.KaLocalHC)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl_data') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_rp'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 0.0
    
    assert rp.get_attr('_lvl_data') == None
    assert rp.get_attr('lvl_read') == None
    assert rp.get_attr('analyzed_design') == {}
    assert rp.get_attr('new_designs') == []
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5  
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_design_variables') == {}
    assert rp.get_attr('bb_lvl_read') == 1
    assert rp.get_attr('_sm') == None
    assert rp.get_attr('sm_type') == 'interpolate'
    assert rp.get_attr('current_design_variables') == {}

    assert rp.get_attr('step_size') == 0.05
    assert rp.get_attr('step_rate') == 0.01
    assert rp.get_attr('step_limit') == 100
    assert rp.get_attr('convergence_criteria') == 0.001

    ns.shutdown()
    time.sleep(0.05)
    
def test_determine_model_applicability():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')

    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    
    rp.set_attr(current_design_variables={'height': 65.0, 'smear': 65.0, 'pu_content': 0.42})
    rp.determine_model_applicability('height')
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {}
    rp.set_attr(current_design_variables={'height': 85.0, 'smear': 65.0, 'pu_content': 0.42})
    rp.determine_model_applicability('height')
    
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {}
    
    rp.set_attr(current_design_variables={'height': 70.0, 'smear': 65.0, 'pu_content': 0.42})
    rp.determine_model_applicability('height')
    time.sleep(0.05)
    
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == ['core_[70.0, 65.0, 0.42]']

    ns.shutdown()
    time.sleep(0.05)
    
def test_exploit_handler_executor_pert():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp_exploit')
    
    rp = ns.proxy('ka_rp_exploit')
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    
    assert bb.get_attr('abstract_lvls')['level 3'] == {'new':{},'old':{}}
    
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_1', {'pareto type' : 'pareto', 'fitness function': 1.0})
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    rp.set_attr(new_designs=['core_1'])
    bb.send_executor()      
    time.sleep(0.05)
    
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[61.75, 65.0, 0.4]',
                                                           'core_[68.25, 65.0, 0.4]',
                                                           'core_[65.0, 61.75, 0.4]',
                                                           'core_[65.0, 68.25, 0.4]',
                                                           'core_[65.0, 65.0, 0.38]', 
                                                           'core_[65.0, 65.0, 0.42]']
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_1' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    
    ns.shutdown()
    time.sleep(0.05)

def test_exploit_handler_executor_rw():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(ka_rp.KaLocalRW, 'ka_rp_exploit')
    
    rp = ns.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=10893)
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
        
    bb.update_abstract_lvl(3, 'core_1', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                                         'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    bb.update_abstract_lvl(1, 'core_1', {'pareto type' : 'pareto', 'fitness function': 1.0})

    rp.set_attr(local_search='random walk')
    bb.set_attr(_ka_to_execute=('ka_rp_exploit', 2.0))
    rp.set_attr(new_designs=['core_1'])

    bb.send_executor()  
    time.sleep(0.05)
    assert [k for k in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == ['core_[65.0, 64.99541, 0.4]', 'core_[65.00093, 64.99541, 0.4]', 'core_[65.00093, 64.99541, 0.39677]', 'core_[65.01003, 64.99541, 0.39677]', 'core_[65.01003, 64.99541, 0.39262]', 'core_[65.01003, 64.9917, 0.39262]', 'core_[65.01003, 64.9831, 0.39262]', 'core_[65.01003, 64.9831, 0.38717]', 'core_[65.0023, 64.9831, 0.38717]', 'core_[65.0023, 64.98111, 0.38717]']
  
    ns.shutdown()
    time.sleep(0.05)  
    
def test_exploit_handler_trigger_publish():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga) 
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp')
    
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0}}
    assert bb.get_attr('_ka_to_execute') == (None, 0)
    
    bb.update_abstract_lvl(1, 'core 1', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    assert bb.get_attr('_kaar') == {1: {'ka_rp': 0}, 2: {'ka_rp':5.00001}}
    assert bb.get_attr('_ka_to_execute') == ('ka_rp', 5.00001)
    
    ns.shutdown()
    time.sleep(0.05)
    
    
def test_exploit_perturb_design():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp_exploit')

    rp = ns.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4}, 
                              'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0, 'burnup' : 50.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
 
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0, 65.0, 0.42]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0, 65.0, 0.42]'])
    rp.search_method()
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == [
                                                           'core_[61.75, 65.0, 0.4]', 
                                                           'core_[68.25, 65.0, 0.4]',
                                                           'core_[65.0, 61.75, 0.4]',
                                                           'core_[65.0, 68.25, 0.4]',
                                                           'core_[65.0, 65.0, 0.38]',]
    assert [core for core in bb.get_attr('abstract_lvls')['level 3']['old'].keys()] == ['core_[65.0, 65.0, 0.42]']
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0, 65.0, 0.42]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}

    ns.shutdown()
    time.sleep(0.05)
    
    
def test_exploit_perturb_design_discrete():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BenchmarkBbOpt)
    dv = {'x0' : {'options': ['0', '1', '2', '3'], 'default': '0', 'variable type': str},
          'x1' : {'options': ['0', '1', '2', '3'], 'default': '1', 'variable type': str},
          'x2' : {'options': ['0', '1', '2', '3'], 'default': '2', 'variable type': str},
          'x3' : {'options': ['0', '1', '2', '3'], 'default': '3', 'variable type': str}}
    obj = {'f1': {'ll': 80, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dv,objectives=obj)
    bb.set_attr(sm_type='tsp_benchmark')
    bb.set_attr(_sm=moo.optimization_test_functions('tsp'))
    bb.connect_agent(ka_rp.KaLocal, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_random_seed(seed=1)
    
    rp.set_attr(new_designs=['core_1'])
    rp.set_attr(_lvl_data={'core_1': {'design variables': {'x0': '0', 
                                                          'x1': '1',
                                                          'x2': '2',
                                                          'x3': '3'}}})
    rp.search_method()
    assert bb.get_blackboard()['level 3']['new'] == {'core_[2, 1, 2, 3]': {'design variables': {'x0': '2', 'x1': '1', 'x2': '2', 'x3': '3'}, 'objective functions': {'f1': 135.0}, 'constraints': {}}, 
                                                     'core_[0, 0, 2, 3]': {'design variables': {'x0': '0', 'x1': '0', 'x2': '2', 'x3': '3'}, 'objective functions': {'f1': 65.0}, 'constraints': {}}, 
                                                     'core_[0, 1, 0, 3]': {'design variables': {'x0': '0', 'x1': '1', 'x2': '0', 'x3': '3'}, 'objective functions': {'f1': 60.0}, 'constraints': {}}, 
                                                     'core_[0, 1, 2, 1]': {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '1'}, 'objective functions': {'f1': 90.0}, 'constraints': {}}}
    
    ns.shutdown()
    time.sleep(0.05)

    
def test_exploit_write_to_bb():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    ka = run_agent(name='ka_rp_exploit', base=ka_rp.KaLocal)
    bb.initialize_abstract_level_3()
    ka.add_blackboard(bb)
    ka.connect_writer()
    
    core_attrs = {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}
    ka.write_to_bb(ka.get_attr('bb_lvl_data'), 'core1', core_attrs, panel='new')
    ka.get_attr('_class')
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core1': {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}}
    assert bb.get_attr('_agent_writing') == False
    
    core_attrs = {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}
    ka.write_to_bb(ka.get_attr('bb_lvl_data'), 'core2', core_attrs, panel='new')
    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core1': {'design variables': {'height': 60.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}},
                                                              'core2': {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2},
                  'objective functions': {'cycle length': 100.0, 'reactivity swing': 110.0, 'burnup': 32.0, 'pu mass': 1000.0}}}
    assert bb.get_attr('_agent_writing') == False
    
    ns.shutdown()
    time.sleep(0.05)


#----------------------------------------------------------
# Tests for KA-Local-RW
#----------------------------------------------------------
    
def test_kalocalrw():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()
    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    bb.connect_agent(ka_rp.KaLocalRW, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=10893)

    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.4]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.4},
                                                          'objective functions': {'cycle length': 365.0, 'pu mass': 500.0, 'reactivity swing' : 600.0,'burnup' : 50.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.4]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0, 65.0, 0.4]'])
    rp.search_method()
    assert bb.get_attr('abstract_lvls')['level 1'] == {'core_[65.0, 65.0, 0.4]' : {'pareto type' : 'pareto', 'fitness function' : 1.0}}
    
    
    assert list(bb.get_attr('abstract_lvls')['level 3']['new'].keys()) == ['core_[65.0, 64.99541, 0.4]', 'core_[65.00093, 64.99541, 0.4]', 'core_[65.00093, 64.99541, 0.39677]', 'core_[65.01003, 64.99541, 0.39677]', 'core_[65.01003, 64.99541, 0.39262]', 'core_[65.01003, 64.9917, 0.39262]', 'core_[65.01003, 64.9831, 0.39262]', 'core_[65.01003, 64.9831, 0.38717]', 'core_[65.0023, 64.9831, 0.38717]', 'core_[65.0023, 64.98111, 0.38717]']
    ns.shutdown()
    time.sleep(0.05)
    
def test_determine_step_steepest_ascent():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(hc_type='steepest ascent')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    # Test an increase in burnup (greater than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert diff == 0.09
    assert pert == '+ height'
    
    # Test an increase in reactivity swing (less than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 680.11, 'burnup' : 61.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 61.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.053
    assert pert == '+ pu_content'
    
    # Test a postive a change in both objectives
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 680.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.138
    assert pert == '+ height'

    # Test a postive a change in both objectives (both have of ~0.078, but + pu_content is slightly greater})
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 661.51, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert round(diff, 3) == 0.078
    assert pert == '+ pu_content'
    
    # Test a case with no change in design variables
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 661.51, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 710.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert diff  == None
    assert pert == None
    
    ns.shutdown()
    time.sleep(0.05)

    
def test_determine_step_simple():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    # Test an increase in burnup (greater than test)
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert pert == '+ height'
    
    # Test multiple increases 
    base = {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}
    base_design =  {'reactivity swing' : 704.11, 'burnup' : 61.12}
    design_dict = {'+ pu_content' : {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.45}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 60.12}},
                   '+ height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 704.11, 'burnup' : 67.12}},
                   '- height' : {'design variables': {'height': 66.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                      'objective functions': {'reactivity swing' : 650.11, 'burnup' : 62.12}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    
    assert pert == '+ height' or '- height'

    ns.shutdown()
    time.sleep(0.05)
    
    
def test_determine_step_simple_discrete_dv():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BenchmarkBbOpt)
    dv = {'x0' : {'options': ['0', '1', '2', '3'], 'default': '0', 'variable type': str},
          'x1' : {'options': ['0', '1', '2', '3'], 'default': '1', 'variable type': str},
          'x2' : {'options': ['0', '1', '2', '3'], 'default': '2', 'variable type': str},
          'x3' : {'options': ['0', '1', '2', '3'], 'default': '3', 'variable type': str}}
    obj = {'f1': {'ll': 80, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dv,objectives=obj)
    bb.set_attr(sm_type='tsp_benchmark')
    bb.set_attr(_sm=moo.optimization_test_functions('tsp'))
    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_random_seed(seed=1)
    rp.set_attr(hc_type='steepest ascent')
    
    rp.set_attr(new_designs=['core_1'])
    rp.set_attr(_lvl_data={'core_1': {'design variables': {'x0': '0', 
                                                          'x1': '1',
                                                          'x2': '2',
                                                          'x3': '3'}}})
    

    # Test an increase in burnup (greater than test)
    base = {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '3'}
    base_design =  {'f1': 100}
    design_dict = {'+ x0' : {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '3'}, 
                           'objective functions': {'f1': 95}},
                   '+ x1' : {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '3'}, 
                           'objective functions': {'f1': 81}}}
    pert, diff = rp.determine_step(base, base_design, design_dict)
    assert pert == '+ x1'
    assert round(diff, 5) == 0.15833
    ns.shutdown()
    time.sleep(0.05)
    
    
def test_kalocalhc():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)

    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(step_size=0.1)
    rp.set_attr(step_rate=0.5)
    rp.set_attr(step_limit=5000)
    rp.set_attr(convergence_criteria=0.005)
    rp.set_attr(hc_type='steepest ascent')
    rp.set_random_seed(seed=1099)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    bb.update_abstract_lvl(3, 'core_[78.65, 65.0, 0.42]', {'design variables': {'height': 78.65, 'smear': 65.0, 'pu_content': 0.42}, 
                                                           'objective functions': {'reactivity swing' : 447.30449, 'burnup' : 490.0}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0, 65.0, 0.42]'])
    rp.search_method()
    time.sleep(0.05)
    
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] ==  ['core_[65.0, 65.0, 0.378]', 'core_[65.0, 65.0, 0.3402]', 'core_[65.0, 65.0, 0.30618]', 'core_[65.0, 65.0, 0.27556]', 'core_[65.0, 65.0, 0.248]', 'core_[65.0, 65.0, 0.2232]', 'core_[65.0, 65.0, 0.20088]', 'core_[65.0, 65.0, 0.18079]', 'core_[65.0, 65.0, 0.16271]', 'core_[71.5, 65.0, 0.16271]', 'core_[78.65, 65.0, 0.16271]', 'core_[78.65, 65.0, 0.14644]', 'core_[78.65, 65.0, 0.1318]', 'core_[78.65, 65.0, 0.11862]', 'core_[78.65, 68.25, 0.11862]', 'core_[78.65, 68.25, 0.12455]', 'core_[78.65, 69.95625, 0.12455]', 'core_[78.65, 69.95625, 0.12144]', 'core_[79.63313, 69.95625, 0.12144]', 'core_[79.63313, 69.95625, 0.12296]', 'core_[79.63313, 69.95625, 0.1245]', 'core_[79.63313, 69.95625, 0.12606]', 'core_[79.63313, 69.95625, 0.12527]']
   
    ns.shutdown()
    time.sleep(0.05)

def test_kalocalhc_simple():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_attr(step_size=0.75)
    rp.set_attr(step_rate=0.01)
    rp.set_attr(convergence_criteria=0.001)
    rp.set_random_seed(seed=1073)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.42},
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.set_attr(new_designs=['core_[65.0, 65.0, 0.42]'])
    rp.search_method()
    time.sleep(0.05)
    assert list(bb.get_attr('abstract_lvls')['level 3']['new']) == ['core_[65.0, 65.0, 0.105]', 'core_[65.0, 65.0, 0.02625]', 'core_[65.0, 65.0, 0.04594]', 'core_[65.0, 65.0, 0.01149]', 'core_[65.0, 65.0, 0.00287]', 'core_[65.0, 65.0, 0.00072]', 'core_[65.0, 65.0, 0.00018]', 'core_[65.0, 65.0, 5e-05]', 'core_[65.0, 65.0, 9e-05]', 'core_[65.0, 65.0, 0.00016]', 'core_[65.0, 65.0, 0.00028]', 'core_[65.0, 65.0, 0.00049]', 'core_[65.0, 65.0, 0.00012]', 'core_[65.0, 65.0, 3e-05]', 'core_[65.0, 65.0, 1e-05]', 'core_[65.0, 65.0, 0.0]']
   
    ns.shutdown()
    time.sleep(0.05)

def test_determine_step_simple_discrete_dv():
    ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BenchmarkBbOpt)
    dv = {'x0' : {'options': ['0', '1', '2', '3'], 'default': '0', 'variable type': str},
          'x1' : {'options': ['0', '1', '2', '3'], 'default': '1', 'variable type': str},
          'x2' : {'options': ['0', '1', '2', '3'], 'default': '2', 'variable type': str},
          'x3' : {'options': ['0', '1', '2', '3'], 'default': '3', 'variable type': str}}
    obj = {'f1': {'ll': 10, 'ul':200, 'goal': 'lt', 'variable type': float}}
    bb.initialize_abstract_level_3(design_variables=dv,objectives=obj)
    bb.set_attr(sm_type='tsp_benchmark')
    bb.set_attr(_sm=moo.optimization_test_functions('tsp'))
    bb.connect_agent(ka_rp.KaLocalHC, 'ka_rp')
    rp = ns.proxy('ka_rp')
    rp.set_attr(step_limit=10)
    rp.set_random_seed(seed=109873)
    rp.set_attr(hc_type='steepest ascent')
    
    bb.update_abstract_lvl(3, 'core_[3, 1, 2, 0]', {'design variables': {'x0': '0', 'x1': '1', 'x2': '2', 'x3': '3'},
                                                   'objective functions': {'f1': 95.0},
                                                   'constraints': {}}, panel='old')
    bb.update_abstract_lvl(1, 'core_[3, 1, 2, 0]', {'pareto type' : 'pareto', 'fitness function' : 1.0})

    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    rp.set_attr(new_designs=['core_[3, 1, 2, 0]'])
   
    rp.search_method()
    time.sleep(0.5)
    assert list(bb.get_attr('abstract_lvls')['level 3']['new']) ==  ['core_[0, 1, 0, 3]', 'core_[0, 1, 0, 1]', 'core_[0, 1, 0, 0]']
    
    ns.shutdown()
    time.sleep(0.05)
    
#----------------------------------------------------------
# Tests fopr KA-GA
#----------------------------------------------------------
    
def test_KaLocalGA():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_trigger_number=2)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.1]', {'design variables': {'height': 65.0, 'smear': 65.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.1]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.25]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.25}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 60.0, 0.25]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')

    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[65.0, 65.0, 0.25]', 'core_[70.0, 60.0, 0.1]']
    bb.update_abstract_lvl(3, 'core_[90.0, 80.0, 0.5]', {'design variables': {'height': 90.0, 'smear': 80.0, 'pu_content': 0.50},
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[90.0, 80.0, 0.5]', {'pareto type' : 'pareto', 'fitness function' : 1.0})    
    bb.update_abstract_lvl(3, 'core_[75.0, 65.0, 0.9]', {'design variables': {'height': 75.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                         'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[75.0, 65.0, 0.9]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp.set_attr(offspring_per_generation=2)
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()] == ['core_[65.0, 65.0, 0.25]', 'core_[70.0, 60.0, 0.1]', 'core_[75.0, 80.0, 0.5]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_KaLocalGA_linear_crossover():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_trigger_number=2)
    rp.set_attr(crossover_type='linear crossover')
    bb.update_abstract_lvl(3, 'core_[50.0, 60.0, 0.1]', {'design variables': {'height': 50.0, 'smear': 60.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[50.0, 60.0, 0.1]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 70.0, 0.2]', {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 70.0, 0.2]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[60.0, 65.0, 0.15]', 'core_[50.0, 55.0, 0.05]', 'core_[80.0, 70.0, 0.25]']
    solutions = ['core_[60.0, 65.0, 0.15]', 'core_[50.0, 55.0, 0.05]', 'core_[80.0, 70.0, 0.25]']
    for solution in solutions:
        assert solution in [x for x in bb.get_attr('abstract_lvls')['level 3']['new'].keys()]
    
    bb.update_abstract_lvl(3, 'core_[90.0, 80.0, 0.5]', {'design variables': {'height': 90.0, 'smear': 80.0, 'pu_content': 0.50},
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 65.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[90.0, 80.0, 0.5]', {'pareto type' : 'pareto', 'fitness function' : 1.0})    
    bb.update_abstract_lvl(3, 'core_[75.0, 65.0, 0.9]', {'design variables': {'height': 55.0, 'smear': 65.0, 'pu_content': 0.90}, 
                                                         'objective functions': {'reactivity swing' : 710.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[75.0, 65.0, 0.9]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    
    rp.set_attr(offspring_per_generation=4)
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[60.0, 65.0, 0.15]', 'core_[50.0, 55.0, 0.05]', 'core_[80.0, 70.0, 0.25]', 'core_[80.0, 75.0, 0.35]', 'core_[80.0, 70.0, 0.65]', 'core_[60.0, 65.0, 0.05]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_KaLocalGA_full():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=0.0)
    rp.set_attr(pf_size=2)
    bb.update_abstract_lvl(3, 'core_[65.0, 65.0, 0.42]', {'design variables': {'height': 65.0, 'smear': 65.0,  'pu_content': 0.42}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[65.0, 65.0, 0.42]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 60.0, 0.50]', {'design variables': {'height': 70.0, 'smear': 60.0, 'pu_content': 0.50}, 
                                                          'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 60.0, 0.50]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])

    assert rp.get_attr('analyzed_design') == {}
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    bb.send_executor()
    time.sleep(0.05)
    assert rp.get_attr('analyzed_design') == {'core_[65.0, 65.0, 0.42]': {'Analyzed': True}, 'core_[70.0, 60.0, 0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[65.0, 65.0, 0.5]', 'core_[70.0, 60.0, 0.42]']

    # Make sure we don't recombine already examined results
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    bb.send_executor()  
    time.sleep(0.05)
    assert rp.get_attr('analyzed_design') == {'core_[65.0, 65.0, 0.42]': {'Analyzed': True}, 'core_[70.0, 60.0, 0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[65.0, 65.0, 0.5]', 'core_[70.0, 60.0, 0.42]']

    # Reduce the PF size and ensure we don't execute the GA_KA
    rp.set_attr(pf_size=1)    
    bb.remove_bb_entry(1, 'core_[65.0, 65.0, 0.42]')
    bb.publish_trigger()
    time.sleep(0.05)
    bb.controller()
    bb.send_executor()  
    time.sleep(0.05)
    assert rp.get_attr('analyzed_design') == {'core_[65.0, 65.0, 0.42]': {'Analyzed': True}, 'core_[70.0, 60.0, 0.50]': {'Analyzed': True}}
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[65.0, 65.0, 0.5]', 'core_[70.0, 60.0, 0.42]']
    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kaga_random_mutation():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    genotype = {'height':70.0,'smear':65.0,'pu_content':0.5}
    new_genotype = rp.random_mutation(genotype)
    assert new_genotype == {'height': 70.0, 'smear': 65.0, 'pu_content': 0.50213}    
    ns.shutdown()
    time.sleep(0.05)
    
def test_kaga_non_uniform_mutation():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_ga')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_ga')
    rp.set_random_seed(seed=1073)
    genotype = {'height':55.0,'smear':65.0,'pu_content':0.5}
    new_genotype = rp.non_uniform_mutation(genotype)
    assert new_genotype == {'height': 55.0, 'smear': 65.0, 'pu_content': 0.83409}

    ns.shutdown()
    time.sleep(0.05)
    
def test_KaLocalGA_crossover_mutate():
    ns = run_nameserver()
    bb = run_agent(name='bb', base=bb_opt.BbOpt)

    bb.set_attr(sm_type='gpr')
    bb.set_attr(_sm=sm_ga)
    objs = {'reactivity swing': {'ll':0,   'ul':15000, 'goal':'lt', 'variable type': float},
            'burnup':           {'ll':0,   'ul':2000,  'goal':'gt', 'variable type': float}}
    bb.initialize_abstract_level_3(objectives=objs)
    bb.initialize_abstract_level_3()

    bb.connect_agent(ka_rp.KaLocalGA, 'ka_rp_exploit')
    ka = bb.get_attr('_proxy_server')
    rp = ka.proxy('ka_rp_exploit')
    rp.set_random_seed(seed=1073)
    rp.set_attr(mutation_rate=1.0)
    rp.set_attr(pf_trigger_number=2)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='random')
    bb.update_abstract_lvl(3, 'core_[50.0, 60.0, 0.1]', {'design variables': {'height': 50.0, 'smear': 60.0, 'pu_content': 0.1}, 
                                                         'objective functions': {'reactivity swing' : 704.11, 'burnup' : 61.}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[50.0, 60.0, 0.1]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    bb.update_abstract_lvl(3, 'core_[70.0, 70.0, 0.2]', {'design variables': {'height': 70.0, 'smear': 70.0, 'pu_content': 0.2}, 
                                                          'objective functions': {'reactivity swing' :650.11,'burnup' : 61.12}}, panel='old')
    
    bb.update_abstract_lvl(1, 'core_[70.0, 70.0, 0.2]', {'pareto type' : 'pareto', 'fitness function' : 1.0})
    rp.set_attr(lvl_read=bb.get_attr('abstract_lvls')['level 1'])
    rp.set_attr(_lvl_data=bb.get_attr('abstract_lvls')['level 3']['old'])
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[50.0, 60.0, 0.19013]', 'core_[70.0, 70.0, 0.1]']
    rp.set_random_seed(seed=1073)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='non-uniform')    
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[50.0, 60.0, 0.19013]', 'core_[70.0, 70.0, 0.1]', 'core_[50.0, 60.0, 0.32809]', 'core_[70.0, 50.0, 0.1]']
    rp.set_random_seed(seed=1073)
    rp.set_attr(crossover_type='nonsense')
    rp.set_attr(mutation_type='nonsense')    
    rp.search_method()
    rp.get_attr('_class')
    assert [x for x in bb.get_attr('abstract_lvls')['level 3']['new']] == ['core_[50.0, 60.0, 0.19013]', 'core_[70.0, 70.0, 0.1]', 'core_[50.0, 60.0, 0.32809]', 'core_[70.0, 50.0, 0.1]']
    
    ns.shutdown()
    time.sleep(0.05)
    
#----------------------------------------------------------
# Tests fopr KA-SM
#----------------------------------------------------------

def test_KaSm_init():
    ns = run_nameserver()
    rp = run_agent(name='ka_sm', base=ka_rp.KaLocalSm)
    
    assert rp.get_attr('bb') == None
    assert rp.get_attr('bb_lvl_data') == 3
    assert rp.get_attr('_entry') == None
    assert rp.get_attr('_entry_name') == None
    assert rp.get_attr('_writer_addr') == None
    assert rp.get_attr('_writer_alias') == None
    assert rp.get_attr('_executor_addr') == None
    assert rp.get_attr('_executor_alias') == None
    assert rp.get_attr('_trigger_response_addr') == None
    assert rp.get_attr('_trigger_response_alias') == 'trigger_response_ka_sm'
    assert rp.get_attr('_trigger_publish_addr') == None
    assert rp.get_attr('_trigger_publish_alias') == None
    assert rp.get_attr('_shutdown_alias') == None
    assert rp.get_attr('_shutdown_addr') == None
    assert rp.get_attr('_trigger_val') == 0.0
    
    assert rp.get_attr('_lvl_data') == None
    assert rp.get_attr('lvl_read') == None
    assert rp.get_attr('analyzed_design') == {}
    assert rp.get_attr('new_designs') == []
    assert rp.get_attr('_objective_accuracy') == 5
    assert rp.get_attr('_design_accuracy') == 5  
    assert rp.get_attr('current_objectives') == {}
    assert rp.get_attr('_objectives') == {}
    assert rp.get_attr('_design_variables') == {}
    assert rp.get_attr('bb_lvl_read') == 3
    assert rp.get_attr('current_design_variables') == {}

    assert rp.get_attr('sm_type') == 'gpr'
    assert rp.get_attr('_sm') == None

    ns.shutdown()
    time.sleep(0.05)
    
def test_KaSm_generate_sm():
    ns = run_nameserver()
    rp = run_agent(name='ka_sm', base=ka_rp.KaLocalSm)
    rp.set_attr(_design_variables={'a': {}, 'b': {}})
    rp.set_attr(_objectives={'c': {}, 'd': {}})
    rp.set_attr(sm_type='gpr')
    
    data = {}
    for i in range(25):
        data[i] = {'a': i, 'b': 10*i, 'c': i ** 2, 'd': (i + i) ** 2}

    rp.generate_sm(data)
    sm = rp.get_attr('_sm')
    obj = sm.predict('gpr', {'c': 4, 'd': 16}, output='dict')
    assert round(obj['a'], 5) == 2
    assert round(obj['b'], 5) == 20
    
    ns.shutdown()
    time.sleep(0.05)