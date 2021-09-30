from osbrain import run_nameserver
from osbrain import run_agent
import mabs.ka.ka_s.latin_hypercube as lhc
import mabs.bb.blackboard_optimization as bb_opt
from mabs.utils.problem import BenchmarkProblem
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
    lhd = rp.get_attr('lhd')
    assert lhd == [[0.31191957728746655, 0.9491875753985664, 0.1091439896126579, 0.1011100149287789], [0.3489618056174793, 0.25870131205635843, 0.007117453248059203, 0.8337779098269228], [0.39179868546846086, 0.5156405449267081, 0.36088631631715734, 0.13755167713123542], [0.5299399217184587, 0.9169527003874893, 0.940106621381224, 0.4966205055203018], [0.20264029047647297, 0.6030505119988312, 0.8870451399813448, 0.5507285093402349], [0.08864094060375974, 0.2987781290495534, 0.24286586660242518, 0.01627725899672589], [0.5607062929911114, 0.965696662300339, 0.9235619420595819, 0.9439263124555183], [0.4311431835011612, 0.05436698447648722, 0.3342073822654635, 0.925036660374928], [0.7665147317498194, 0.4632799078575382, 0.09459846214462148, 0.5342131867835719], [0.10613657060288659, 0.15288643322276646, 0.687401920648945, 0.20438779181610828], [0.22650959207467888, 0.27466993519783994, 0.20058532022672215, 0.4112263940689919], [0.9425113429044941, 0.035135916536563644, 0.6280215387083696, 0.6901568930700536], [0.25975277914730033, 0.5552668111526785, 0.35770939710990124, 0.666817645943099], [0.16524195183344775, 0.0884876343235781, 0.43533415451863594, 0.6477928209501944], [0.6891499089737797, 0.6903784508924382, 0.3829338927387737, 0.16947031043076824], [0.611618949547566, 0.36197169137813606, 0.7383770210388333, 0.23696646617949252], [0.05498301948134661, 0.5299487147814417, 0.49996255378632853, 0.07377918369538064], [0.9862241883170961, 0.44040434114502697, 0.9917246248809087, 0.6392722373572922], [0.017826451336479466, 0.7762221912944784, 0.7810427488692436, 0.6059182656526317], [0.27220474768951486, 0.8277777643127028, 0.6165613668473745, 0.35225313605260744], [0.440714349327796, 0.12857473536160421, 0.7072450368345973, 0.76396860340395], [0.5094682744418657, 0.8876248947578692, 0.046578252639894534, 0.26091329921406714], [0.8250563364348825, 0.2195797709205764, 0.9610403461750422, 0.9081942873539829], [0.06293093912414088, 0.06510607776428565, 0.840999920905795, 0.33237237494926053], [0.48134000100694974, 0.415024003267946, 0.1715617508837805, 0.8108556400847968], [0.7181196840788726, 0.5743827578521749, 0.5699607667592258, 0.08673178481708908], [0.850137215134317, 0.23105390195607758, 0.6453487772571346, 0.8465027854710394], [0.2890460715907129, 0.10008040990853478, 0.5381329874395767, 0.4572945171244503], [0.6610639624508315, 0.32021766247161243, 0.26160884068451656, 0.8626783876604087], [0.19629543786736392, 0.3446133943827901, 0.3157193933680521, 0.8861648960005136], [0.7963854631864223, 0.31830966174416664, 0.4408651836255723, 0.03538110932968111], [0.5469053129712221, 0.660062418618913, 0.034441644482956335, 0.1570457475966135], [0.3331109919730137, 0.5838130634843711, 0.8680940980900645, 0.30978188991977984], [0.9329670436480404, 0.9972304601991466, 0.8286633024806983, 0.990270049518392], [0.14006347004578054, 0.804952567509355, 0.14317508868319737, 0.7421721089165694], [0.7328934947684282, 0.426554386033845, 0.13713486597548694, 0.39333988805820186], [0.6273622749699795, 0.014420205584720094, 0.7632477382805003, 0.7972388246374948], [0.37736254914813716, 0.3996544619615771, 0.5571762912919849, 0.47795169050739855], [0.477960825049331, 0.8400877929602721, 0.7412738296754573, 0.517540613116595], [0.40610812208380515, 0.4946508203790589, 0.41302306191346994, 0.18691500824973178], [0.12015303316928863, 0.9214297136229501, 0.6673197030191738, 0.9708737154105588], [0.5841579185228817, 0.7876370396582142, 0.1819440297090245, 0.7127809229329886], [0.8841705023685792, 0.16793534282426642, 0.47980678916225766, 0.04746251608346475], [0.7402255748137496, 0.6331509950761277, 0.06149123952860425, 0.37931546420513684], [0.9016321185551147, 0.18869631717047047, 0.8179216542711232, 0.42938241131245847], [0.6408270962873299, 0.6419089304961952, 0.5172007843904326, 0.2591120619863837], [0.8646919208130771, 0.7193502235996229, 0.5817971946069063, 0.737318807579994], [0.9719233080580196, 0.7489524616403902, 0.9094827107430165, 0.2881490531937126], [0.02536800202628143, 0.8614056510957716, 0.2865464091390519, 0.5972493310208327], [0.8068767680986667, 0.724821380475579, 0.23345349055487025, 0.5780804465638789]]
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
    
def test_parallel_lhc():
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
    rp.set_attr(samples=10)
    rp.set_attr(parallel=True, debug_wait=True, debug_wait_time=0.01, max_sub_agents=5)
    
    rp.generate_lhc()
    bb.set_attr(_ka_to_execute=('ka_rp_lhc', 2))
    bb.send_executor()
    time.sleep(2.5)

    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core_[0.18139,0.12684,0.96443]': {'design variables': {'x0': 0.18139, 'x1': 0.12684, 'x2': 0.96443}, 'objective functions': {'f0': 2.1190738426582367, 'f1': 14.587594737113415, 'f2': 75.39691254251544}, 'constraints': {}}, 'core_[0.67299,0.0721,0.54244]': {'design variables': {'x0': 0.67299, 'x1': 0.0721, 'x2': 0.54244}, 'objective functions': {'f0': 4.61228911288365, 'f1': 59.35843367329734, 'f2': 31.083769533438904}, 'constraints': {}}, 'core_[0.41465,0.74572,0.88567]': {'design variables': {'x0': 0.41465, 'x1': 0.74572, 'x2': 0.88567}, 'objective functions': {'f0': 8.309003134288304, 'f1': 2.8332528522593328, 'f2': 15.72921630706779}, 'constraints': {}}, 'core_[0.27221,0.5432,0.40746]': {'design variables': {'x0': 0.27221, 'x1': 0.5432, 'x2': 0.40746}, 'objective functions': {'f0': 0.9346434912756234, 'f1': 0.7859814926633004, 'f2': 4.600322019987911}, 'constraints': {}}, 'core_[0.08913,0.42553,0.70555]': {'design variables': {'x0': 0.08913, 'x1': 0.42553, 'x2': 0.70555}, 'objective functions': {'f0': 0.21322616444605622, 'f1': 0.28785757687901187, 'f2': 5.1208588293589665}, 'constraints': {}}, 'core_[0.7004,0.84287,0.17568]': {'design variables': {'x0': 0.7004, 'x1': 0.84287, 'x2': 0.17568}, 'objective functions': {'f0': 31.656450289355174, 'f1': 5.901477136410571, 'f2': 16.06561258817735}, 'constraints': {}}, 'core_[0.80077,0.27691,0.03559]': {'design variables': {'x0': 0.80077, 'x1': 0.27691, 'x2': 0.03559}, 'objective functions': {'f0': 20.433920249114152, 'f1': 53.35872085851703, 'f2': 18.359463875861188}, 'constraints': {}}, 'core_[0.98776,0.63366,0.33731]': {'design variables': {'x0': 0.98776, 'x1': 0.63366, 'x2': 0.33731}, 'objective functions': {'f0': 54.29977444142359, 'f1': 31.392512339221533, 'f2': 1.0618708898873195}, 'constraints': {}}, 'core_[0.37183,0.33289,0.63068]': {'design variables': {'x0': 0.37183, 'x1': 0.33289, 'x2': 0.63068}, 'objective functions': {'f0': 8.518648508865729, 'f1': 17.071331691397805, 'f2': 43.23173994136983}, 'constraints': {}}, 'core_[0.5689,0.90032,0.27492]': {'design variables': {'x0': 0.5689, 'x1': 0.90032, 'x2': 0.27492}, 'objective functions': {'f0': 27.291834015029206, 'f1': 3.0216478747757587, 'f2': 22.97089478413592}, 'constraints': {}}}
    ns.shutdown() 
    time.sleep(0.1) 
    
def test_serial_lhc():
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
    rp.set_attr(samples=10)
    rp.set_attr(parallel=False, debug_wait=True, debug_wait_time=0.01)

    rp.generate_lhc()
    bb.set_attr(_ka_to_execute=('ka_rp_lhc', 2))
    bb.send_executor()
    time.sleep(0.5)

    assert bb.get_attr('abstract_lvls')['level 3']['new'] == {'core_[0.18139,0.12684,0.96443]': {'design variables': {'x0': 0.18139, 'x1': 0.12684, 'x2': 0.96443}, 'objective functions': {'f0': 2.1190738426582367, 'f1': 14.587594737113415, 'f2': 75.39691254251544}, 'constraints': {}}, 'core_[0.67299,0.0721,0.54244]': {'design variables': {'x0': 0.67299, 'x1': 0.0721, 'x2': 0.54244}, 'objective functions': {'f0': 4.61228911288365, 'f1': 59.35843367329734, 'f2': 31.083769533438904}, 'constraints': {}}, 'core_[0.41465,0.74572,0.88567]': {'design variables': {'x0': 0.41465, 'x1': 0.74572, 'x2': 0.88567}, 'objective functions': {'f0': 8.309003134288304, 'f1': 2.8332528522593328, 'f2': 15.72921630706779}, 'constraints': {}}, 'core_[0.27221,0.5432,0.40746]': {'design variables': {'x0': 0.27221, 'x1': 0.5432, 'x2': 0.40746}, 'objective functions': {'f0': 0.9346434912756234, 'f1': 0.7859814926633004, 'f2': 4.600322019987911}, 'constraints': {}}, 'core_[0.08913,0.42553,0.70555]': {'design variables': {'x0': 0.08913, 'x1': 0.42553, 'x2': 0.70555}, 'objective functions': {'f0': 0.21322616444605622, 'f1': 0.28785757687901187, 'f2': 5.1208588293589665}, 'constraints': {}}, 'core_[0.7004,0.84287,0.17568]': {'design variables': {'x0': 0.7004, 'x1': 0.84287, 'x2': 0.17568}, 'objective functions': {'f0': 31.656450289355174, 'f1': 5.901477136410571, 'f2': 16.06561258817735}, 'constraints': {}}, 'core_[0.80077,0.27691,0.03559]': {'design variables': {'x0': 0.80077, 'x1': 0.27691, 'x2': 0.03559}, 'objective functions': {'f0': 20.433920249114152, 'f1': 53.35872085851703, 'f2': 18.359463875861188}, 'constraints': {}}, 'core_[0.98776,0.63366,0.33731]': {'design variables': {'x0': 0.98776, 'x1': 0.63366, 'x2': 0.33731}, 'objective functions': {'f0': 54.29977444142359, 'f1': 31.392512339221533, 'f2': 1.0618708898873195}, 'constraints': {}}, 'core_[0.37183,0.33289,0.63068]': {'design variables': {'x0': 0.37183, 'x1': 0.33289, 'x2': 0.63068}, 'objective functions': {'f0': 8.518648508865729, 'f1': 17.071331691397805, 'f2': 43.23173994136983}, 'constraints': {}}, 'core_[0.5689,0.90032,0.27492]': {'design variables': {'x0': 0.5689, 'x1': 0.90032, 'x2': 0.27492}, 'objective functions': {'f0': 27.291834015029206, 'f1': 3.0216478747757587, 'f2': 22.97089478413592}, 'constraints': {}}}
    

    ns.shutdown() 
    time.sleep(0.1)        
