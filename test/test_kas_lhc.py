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
                                   'test': {'options': [0.1,0.2,0.3], 'variable type': list}})    
    rp.generate_lhc()
    print()
    lhd = rp.get_attr('lhd')
    print(lhd)
    assert lhd == [[0.31191957728746655, 0.9491875753985664, 0.1091439896126579, 0.1011100149287789], [0.3489618056174793, 0.25870131205635843, 0.007117453248059203, 0.8337779098269228], [0.39179868546846086, 0.5156405449267081, 0.36088631631715734, 0.13755167713123542], [0.5299399217184587, 0.9169527003874893, 0.940106621381224, 0.4966205055203018], [0.20264029047647297, 0.6030505119988312, 0.8870451399813448, 0.5507285093402349], [0.08864094060375974, 0.2987781290495534, 0.24286586660242518, 0.01627725899672589], [0.5607062929911114, 0.965696662300339, 0.9235619420595819, 0.9439263124555183], [0.4311431835011612, 0.05436698447648722, 0.3342073822654635, 0.925036660374928], [0.7665147317498194, 0.4632799078575382, 0.09459846214462148, 0.5342131867835719], [0.10613657060288659, 0.15288643322276646, 0.687401920648945, 0.20438779181610828], [0.22650959207467888, 0.27466993519783994, 0.20058532022672215, 0.4112263940689919], [0.9425113429044941, 0.035135916536563644, 0.6280215387083696, 0.6901568930700536], [0.25975277914730033, 0.5552668111526785, 0.35770939710990124, 0.666817645943099], [0.16524195183344775, 0.0884876343235781, 0.43533415451863594, 0.6477928209501944], [0.6891499089737797, 0.6903784508924382, 0.3829338927387737, 0.16947031043076824], [0.611618949547566, 0.36197169137813606, 0.7383770210388333, 0.23696646617949252], [0.05498301948134661, 0.5299487147814417, 0.49996255378632853, 0.07377918369538064], [0.9862241883170961, 0.44040434114502697, 0.9917246248809087, 0.6392722373572922], [0.017826451336479466, 0.7762221912944784, 0.7810427488692436, 0.6059182656526317], [0.27220474768951486, 0.8277777643127028, 0.6165613668473745, 0.35225313605260744], [0.440714349327796, 0.12857473536160421, 0.7072450368345973, 0.76396860340395], [0.5094682744418657, 0.8876248947578692, 0.046578252639894534, 0.26091329921406714], [0.8250563364348825, 0.2195797709205764, 0.9610403461750422, 0.9081942873539829], [0.06293093912414088, 0.06510607776428565, 0.840999920905795, 0.33237237494926053], [0.48134000100694974, 0.415024003267946, 0.1715617508837805, 0.8108556400847968], [0.7181196840788726, 0.5743827578521749, 0.5699607667592258, 0.08673178481708908], [0.850137215134317, 0.23105390195607758, 0.6453487772571346, 0.8465027854710394], [0.2890460715907129, 0.10008040990853478, 0.5381329874395767, 0.4572945171244503], [0.6610639624508315, 0.32021766247161243, 0.26160884068451656, 0.8626783876604087], [0.19629543786736392, 0.3446133943827901, 0.3157193933680521, 0.8861648960005136], [0.7963854631864223, 0.31830966174416664, 0.4408651836255723, 0.03538110932968111], [0.5469053129712221, 0.660062418618913, 0.034441644482956335, 0.1570457475966135], [0.3331109919730137, 0.5838130634843711, 0.8680940980900645, 0.30978188991977984], [0.9329670436480404, 0.9972304601991466, 0.8286633024806983, 0.990270049518392], [0.14006347004578054, 0.804952567509355, 0.14317508868319737, 0.7421721089165694], [0.7328934947684282, 0.426554386033845, 0.13713486597548694, 0.39333988805820186], [0.6273622749699795, 0.014420205584720094, 0.7632477382805003, 0.7972388246374948], [0.37736254914813716, 0.3996544619615771, 0.5571762912919849, 0.47795169050739855], [0.477960825049331, 0.8400877929602721, 0.7412738296754573, 0.517540613116595], [0.40610812208380515, 0.4946508203790589, 0.41302306191346994, 0.18691500824973178], [0.12015303316928863, 0.9214297136229501, 0.6673197030191738, 0.9708737154105588], [0.5841579185228817, 0.7876370396582142, 0.1819440297090245, 0.7127809229329886], [0.8841705023685792, 0.16793534282426642, 0.47980678916225766, 0.04746251608346475], [0.7402255748137496, 0.6331509950761277, 0.06149123952860425, 0.37931546420513684], [0.9016321185551147, 0.18869631717047047, 0.8179216542711232, 0.42938241131245847], [0.6408270962873299, 0.6419089304961952, 0.5172007843904326, 0.2591120619863837], [0.8646919208130771, 0.7193502235996229, 0.5817971946069063, 0.737318807579994], [0.9719233080580196, 0.7489524616403902, 0.9094827107430165, 0.2881490531937126], [0.02536800202628143, 0.8614056510957716, 0.2865464091390519, 0.5972493310208327], [0.8068767680986667, 0.724821380475579, 0.23345349055487025, 0.5780804465638789]]
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