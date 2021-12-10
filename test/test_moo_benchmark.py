import mabs.utils.moo_benchmarks as moo
import numpy as np

def test_sf_1():
    tsp = moo.optimization_test_functions('sf1')
    assert tsp.predict('sf1', [0]) == {'F': [0,4]}

def test_sf_2():
    tsp = moo.optimization_test_functions('sf2')
    assert tsp.predict('sf2', [0.5]) == {'F': [-0.5, 20.25]  }
    assert tsp.predict('sf2', [1.5]) == {'F': [-0.5, 12.25]  }
    assert tsp.predict('sf2', [3.5]) == {'F': [0.5, 2.25]  }

def test_zdt_1():
    tsp = moo.optimization_test_functions('zdt1')
    a = tsp.predict('zdt1', [0.25,0], num_vars=2)   
    assert np.ndarray.tolist(a['F']) == [0.25, 0.5]
    
def test_zdt_2():
    tsp = moo.optimization_test_functions('zdt2')
    a = tsp.predict('zdt2', [0,0.3], num_vars=2)   
    assert np.ndarray.tolist(a['F']) == [0.0, 3.6999999999999997]
    
def test_zdt_3():
    tsp = moo.optimization_test_functions('zdt3')
    a = tsp.predict('zdt3', [0.5,0], num_vars=2)   
    assert np.ndarray.tolist(a['F']) == [0.5, 0.2928932188134521]
    
def test_tsp():
    tsp = moo.optimization_test_functions('tsp')
    assert tsp.predict('tsp', [0,1,3,2]) == {'F': [80]}
    assert tsp.predict('tsp', [3,1,2,0]) == {'F': [95]}
    assert tsp.predict('tsp', [0,1,2,1]) == {'F': [90]}
    
def test_welded_beam():
    tsp = moo.optimization_test_functions('welded_beam')
    val = tsp.predict('welded_beam', [1.15081317, 1.15874195, 9.99999932, 4.99999488])
    val = [round(x, 6) for x in val['F'][0]]
    assert  val == [3.8159607e+01, 4.39e-04]
    
def test_truss_2d():
    tsp = moo.optimization_test_functions('truss2d')
    val = tsp.predict('truss_2d', [0.05,0.05,1.5])
    val = [round(x, 6) for x in val['F'][0]]
    assert  val == [0.303739, 1922.96068]    

def test_re21():
    tsp = moo.optimization_test_functions('re21')
    val = tsp.predict('re21', [0.5, 1.0, 1.0, 0.5])
    assert val == {'F': [782.842712474619, 0.08]}