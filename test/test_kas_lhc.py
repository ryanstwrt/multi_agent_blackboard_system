from osbrain import run_nameserver
from osbrain import run_agent
import src.ka.ka_s.latin_hypercube as lhc
import src.bb.blackboard_optimization as bb_opt
from src.utils.problem import BenchmarkProblem
import time
    
dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}
        
problem = BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')      
    
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
    assert rp.get_attr('execute_once') == True
    
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
                                                 'variable type': dict},
                                   'test': {'options': [0.1,0.2,0.3], 'variable type': list}})    
    rp.generate_lhc()
    lhd = rp.get_attr('lhd')
    assert lhd == [[0.49289349476842825, 0.27333988805820186, 0.6094827107430164, 0.28938241131245845, 0.7480195854625139, 0.1395797709205764], [0.6016321185551147, 0.691488020645436, 0.5210427488692436, 0.7823414987673968, 0.6953079763371324, 0.9686285231606767], [0.17975277914730028, 0.03538110932968111, 0.9807374655759333, 0.6763990356740751, 0.9149377116621581, 0.9172192207680246], [0.2629338927387737, 0.39808044656387903, 0.8131122694424359, 0.4973188075799941, 0.5486633024806984, 0.061110014928778884], [0.6235619420595818, 0.625036660374928, 0.6410403461750422, 0.7429453327709236, 0.2131109919730137, 0.5861648960005136], [0.826468260740148, 0.12869631717047048, 0.3499399217184587, 0.9212525052738724, 0.32946827444186566, 0.35421318678357183], [0.07459846214462147, 0.9065111872435628, 0.3841579185228818, 0.6291875753985664, 0.8741619941206642, 0.8177997741338301], [0.32134000100694976, 0.89457277420174, 0.9365325432265544, 0.5665027854710395, 0.3817971946069063, 0.7607013625661175], [0.44106396245083146, 0.8525194770337183, 0.1628658666024252, 0.8205489856413714, 0.7020227408917629, 0.48895246164039013], [0.8829534891803508, 0.4392722373572922, 0.9116518259102385, 0.3707285093402348, 0.7687142106733572, 0.3743827578521749], [0.6717246248809088, 0.17870131205635842, 0.4208270962873299, 0.9766673106032758, 0.06914398961265789, 0.7881217460913061], [0.6519233080580197, 0.11704574759661349, 0.2157193933680521, 0.10793534282426642, 0.9998396532677207, 0.15696646617949253], [0.017826451336479466, 0.7490264667775205, 0.007117453248059203, 0.6508737154105588, 0.932602063128339, 0.02746251608346475], [0.41161894954756606, 0.18091329921406712, 0.4781196840788726, 0.6081942873539828, 0.15345349055487026, 0.9481071019658578], [0.08015303316928864, 0.28655438603384503, 0.7240850551933599, 0.5162221912944784, 0.6129670436480403, 0.7048402574588648], [0.8592856022063304, 0.5276370396582142, 0.9761994197681401, 0.09755167713123543, 0.27302306191347, 0.4503784508924382], [0.7450391354662579, 0.825124913621794, 0.12194402970902453, 0.5876248947578692, 0.8802738395600584, 0.09288643322276646], [0.034441644482956335, 0.7892116849063968, 0.03498301948134661, 0.3499487147814416, 0.25179868546846085, 0.8202402650016997], [0.14058532022672215, 0.5600877929602722, 0.33996255378632856, 0.9550603831816886, 0.620106621381224, 0.9894163467183544], [0.3008651836255723, 0.2419716913781361, 0.24088631631715735, 0.1510539019560776, 0.4253487772571345, 0.5537779098269228], [0.10317508868319734, 0.8015554120232528, 0.41656136684737455, 0.01627725899672589, 0.4491499089737797, 0.4277928209501944], [0.13629543786736392, 0.014420205584720094, 0.2661081220838052, 0.9852482625702698, 0.23770939710990124, 0.5249525675093549], [0.21191957728746655, 0.5508556400847968, 0.7996412744910674, 0.1269150082497318, 0.5268767680986667, 0.0484876343235781], [0.3899607667592258, 0.9355790685024163, 0.3771762912919848, 0.7020293474325577, 0.4672450368345972, 0.5614056510957717], [0.6875493284522128, 0.6702700495183921, 0.5065147317498194, 0.275024003267946, 0.08006347004578053, 0.2596544619615771], [0.35720078439043257, 0.48482138047557893, 0.317960825049331, 0.47935022359962287, 0.18654640913905188, 0.6905757707564758], [0.5579216542711232, 0.7773951284942847, 0.09713486597548693, 0.8968243997484964, 0.9491761699677655, 0.728710444012548], [0.8111929013977655, 0.6456966623003391, 0.18904607159071288, 0.8153243724316767, 0.7262787714220051, 0.20021766247161246], [0.23420738226546348, 0.37526681115267846, 0.8988962086508828, 0.9188262222993779, 0.17220474768951485, 0.9224756500595784], [0.7813089340448321, 0.8688181557828213, 0.7525392553294992, 0.053779183695380636, 0.8561669883953668, 0.870168161470967], [0.9280875213153227, 0.4030505119988312, 0.7707529967857859, 0.6852870834868686, 0.6705473979934937, 0.6572304601991467], [0.5363854631864223, 0.21830966174416663, 0.5841705023685791, 0.20978188991977983, 0.026578252639894533, 0.41315099507612774], [0.9948119705978282, 0.9940732369213049, 0.8777728520847147, 0.30327990785753817, 0.8337354583499348, 0.3356405449267081], [0.5012738296754573, 0.2323723749492605, 0.04149123952860425, 0.2246133943827901, 0.5032477382805003, 0.6014297136229501], [0.18160884068451655, 0.14438779181610828, 0.4473197030191738, 0.5372388246374948, 0.005368002026281429, 0.015135916536563642], [0.8773759996074881, 0.06673178481708908, 0.49837702103883325, 0.060080409908534776, 0.5646919208130771, 0.39724933102083276], [0.7033708795606225, 0.5021721089165694, 0.5450563364348826, 0.8782106154372681, 0.36070629299111134, 0.18814905319371258], [0.9530939922307764, 0.9757155137126817, 0.839586480066712, 0.17911206198638369, 0.3198067891622577, 0.27122639406899196], [0.3669053129712221, 0.4701568930700535, 0.2289618056174793, 0.4219089304961952, 0.11156175088378051, 0.3179516905073986], [0.4280215387083697, 0.357540613116595, 0.2953341545186359, 0.40591826565263184, 0.12264029047647296, 0.6771851751799831], [0.25736254914813717, 0.3172945171244503, 0.1465095920746789, 0.846615193780093, 0.7810224992094903, 0.280404341145027], [0.7353990715851918, 0.440062418618913, 0.6856601839562259, 0.38381306348437116, 0.5870451399813448, 0.7496376173424926], [0.29114318350116125, 0.3346508203790589, 0.10524195183344776, 0.5477777643127028, 0.04864094060375973, 0.8574214176248327], [0.5880940980900645, 0.04510607776428564, 0.06613657060288658, 0.3366205055203018, 0.28071434932779604, 0.23225313605260742], [0.9160507374409113, 0.9512828799287927, 0.8433743358953605, 0.7253204591914217, 0.4802255748137496, 0.4727809229329886], [0.9674937660486146, 0.08857473536160422, 0.6225113429044941, 0.4468176459430989, 0.3581329874395766, 0.10947031043076824], [0.7760420733687627, 0.5826783876604087, 0.9441936794214595, 0.7609988009572338, 0.6462241883170962, 0.8862619715372274], [0.042930939124140886, 0.7377204081265246, 0.5609999209057951, 0.034366984476487214, 0.8142715060131518, 0.50396860340395], [0.5701372151343169, 0.6169527003874893, 0.7148427553131095, 0.19877812904955341, 0.9703950367491533, 0.6239263124555183], [0.467401920648945, 0.7100953140241681, 0.6684281193323344, 0.25931546420513685, 0.4073622749699796, 0.1746699351978399]]
    ns.shutdown()
    time.sleep(0.1) 
    
def test_search_method():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    rp = run_agent(name='ka_rp', base=lhc.LatinHypercube)
    rp.set_random_seed(seed=10997)
    
    rp.set_attr(_design_variables={'height':    {'ll': 50, 'ul': 80, 'variable type': float},
                                  'smear':      {'ll': 50, 'ul': 70, 'variable type': float},
                                  'pu_content': {'ll': 0,  'ul': 1,  'variable type': float},
                                  'position' :  {'options': ['exp_a', 'exp_b', 'exp_c', 'exp_d', 'no_exp'], 'default': 'no_exp', 'variable type': str},})   
    rp.set_attr(samples=2)
    rp.generate_lhc()
    lhd = rp.get_attr('lhd')[0]
    rp.set_attr(_lvl_data={'core_[63.36984,57.2101,0.17794,exp_c]': {},
                           'core_[69.026,67.56796,0.86104,no_exp]': {}})
    print(lhd)
    rp.search_method()
    design = rp.get_attr('current_design_variables')

    assert lhd == [0.44566128341198663, 0.36050513961800235, 0.17793633120148006, 0.40693147491814724]
    assert design == {'height': 69.026, 'smear': 67.56796, 'pu_content': 0.86104, 'position': 'no_exp'}
        
    ns.shutdown()
    time.sleep(0.1)  

def test_handler_executor():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.initialize_metadata_level()    
    bb.connect_agent(lhc.LatinHypercube, 'ka_rp_lhc')
    
    rp = ns.proxy('ka_rp_lhc')
    rp.set_attr(problem=problem)    
    rp.set_attr(_trigger_val=2)
    rp.set_random_seed(seed=10997)
    rp.set_attr(samples=2)
    rp.generate_lhc()
    bb.set_attr(_ka_to_execute=('ka_rp_lhc', 2))
    bb.send_executor()
    time.sleep(0.5)

    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core_[0.26666,0.04467,0.6786]': {'design variables': {'x0': 0.26666, 'x1': 0.04467, 'x2': 0.6786}, 'objective functions': {'f0': 0.4869665852855559, 'f1': 10.414456859656372, 'f2': 29.979936507589112}, 'constraints': {}}, 'core_[0.96089,0.52036,0.10726]': {'design variables': {'x0': 0.96089, 'x1': 0.52036, 'x2': 0.10726}, 'objective functions': {'f0': 6.662459472035095, 'f1': 6.141098587837098, 'f2': 0.5211284910047987}, 'constraints': {}}}
    assert rp.get_attr('_trigger_val') ==  0.0    
    assert ns.agents() == ['blackboard', 'ka_rp_lhc']

    ns.shutdown() 
    time.sleep(0.1)
    
def test_handler_executor_multiple():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.initialize_metadata_level()
    bb.connect_agent(lhc.LatinHypercube, 'ka_rp_lhc')
    
    rp = ns.proxy('ka_rp_lhc')
    rp.set_attr(problem=problem)    
    rp.set_attr(execute_once=False)
    rp.set_attr(_trigger_val=2)
    rp.set_random_seed(seed=10997)
    rp.set_attr(samples=2)
    rp.generate_lhc()
    bb.set_attr(_ka_to_execute=('ka_rp_lhc', 2))
    bb.send_executor()
    time.sleep(0.5)

    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core_[0.26666,0.04467,0.6786]': {'design variables': {'x0': 0.26666, 'x1': 0.04467, 'x2': 0.6786}, 'objective functions': {'f0': 0.4869665852855559, 'f1': 10.414456859656372, 'f2': 29.979936507589112}, 'constraints': {}}, 'core_[0.96089,0.52036,0.10726]': {'design variables': {'x0': 0.96089, 'x1': 0.52036, 'x2': 0.10726}, 'objective functions': {'f0': 6.662459472035095, 'f1': 6.141098587837098, 'f2': 0.5211284910047987}, 'constraints': {}}}

    bb.publish_trigger()
    assert rp.get_attr('_trigger_val') ==  2.000006    
    assert ns.agents() == ['blackboard', 'ka_rp_lhc']

    ns.shutdown() 
    time.sleep(0.1)    

def test_handler_trigger_publish():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
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
    
def test_force_shutdown():
    try:
        ns = run_nameserver()
    except OSError:
        time.sleep(0.5)
        ns = run_nameserver()
    bb = run_agent(name='blackboard', base=bb_opt.BbOpt)
    bb.initialize_abstract_level_3(objectives=objs, design_variables=dvs)
    bb.initialize_metadata_level()
    bb.connect_agent(lhc.LatinHypercube, 'ka_rp_lhc')
    rp = ns.proxy('ka_rp_lhc')
    rp.set_random_seed(seed=10997)
    rp.set_attr(_trigger_val=5, samples=10)   
    rp.set_attr(problem=problem, debug_wait=True, debug_wait_time=0.05)    
    rp.generate_lhc()
    bb.set_attr(final_trigger=0, _kaar = {0: {}, 1: {'ka_rp_lhc': 2}}, _ka_to_execute=('ka_rp_lhc', 2))    
    bb.send_executor()
    bb.send_shutdown()
    time.sleep(0.15)
    assert ns.agents() == ['blackboard']
    assert list(bb.get_blackboard()['level 3']['new'].keys()) == ['core_[0.18139,0.12684,0.96443]']

    ns.shutdown() 
    time.sleep(0.1)   