import src.utils.reproblems as re
import numpy as np

def test_RE21():
    prob = re.get_problem('re21')
    dv = [x for x in prob.lbound]
    assert np.array_equal(list(prob.evaluate(dv)), [1237.8414230005442, 4.00000000e-02])

def test_RE22():
    prob = re.get_problem('re22')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [921.0, 0.0])
    
def test_RE23():
    prob = re.get_problem('re23')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [815927.1875, 0.0])   

def test_RE24():
    prob = re.get_problem('re24')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [6004.0, 0.0])   
    
def test_RE25():
    prob = re.get_problem('re25')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [133.23965941470632, 58.623043478260875])   
    
def test_RE31():
    prob = re.get_problem('re31')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [816.2277660168379, 0.3333333333333333, 816.1277660168379])   

def test_RE32():
    prob = re.get_problem('re32')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [333.9095, 0.00043904, 0.0])   
    
def test_RE33():
    prob = re.get_problem('re33')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [5.306700000000001, 1.139072039072039, 0.0])   

def test_RE34():
    prob = re.get_problem('re34')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [1704.5588675, 10.551600000000002, 0.10239999999999988])   
    
def test_RE35():
    prob = re.get_problem('re35')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [7144.6949677849625, 694.5866953529555, 0.5])   
    
def test_RE36():
    prob = re.get_problem('re36')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [5.931, 60.0, 0.35572067522723994])   
    
def test_RE37():
    prob = re.get_problem('re37')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [0.20513999999999996, 0.8773999999999998, 0.2837999999999997])       
    
def test_RE41():
    prob = re.get_problem('re41')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [42.768012, 3.58525, 10.61064375, 0.0])       

def test_RE42():
    prob = re.get_problem('re42')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [-378.91220009923603, 20026.606947160206, 25779.574892815603, 9768.32795415733])     

def test_RE61():
    prob = re.get_problem('re61')
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [83060.744, 1350.0, 2853468.96494178, 447902.6720089092, 11122.222222222223, 0.0])     
    
def test_RE91():
    prob = re.get_problem('re91', set_random_seed=True)
    dv = [x for x in prob.ubound]
    assert np.array_equal(list(prob.evaluate(dv)), [42.689262, 0.30089314518650334, 70.89411900853725, 0.6089737559216486, 0.6957173289353097, 0.7764735991507811, 0.902893583459356, 0.8705852775230852, 0.7872379873021488])     

def test_CRE21():
    prob = re.get_problem('cre21')
    dv = [x for x in prob.ubound]
    soln = prob.evaluate(dv)
    assert np.array_equal(list(soln[0]), [816.2277660168379, 0.3333333333333333])
    assert np.array_equal(list(soln[1]), [816.1277660168379, 0.0, 0.0])   
    
def test_CRE22():
    prob = re.get_problem('cre22')
    dv = [x for x in prob.ubound]
    soln = prob.evaluate(dv)
    assert np.array_equal(list(soln[0]), [333.9095, 0.00043904])
    assert np.array_equal(list(soln[1]), [0.0, 0.0, 0.0, 0.0])   

def test_CRE23():
    prob = re.get_problem('cre23')
    dv = [x for x in prob.ubound]
    soln = prob.evaluate(dv)
    assert np.array_equal(list(soln[0]), [5.306700000000001, 1.139072039072039])
    assert np.array_equal(list(soln[1]), [0.0, 0.0, 0.0, 0.0])   

def test_CRE24():
    prob = re.get_problem('cre24')
    dv = [x for x in prob.ubound]
    soln = prob.evaluate(dv)
    assert np.array_equal(list(soln[0]), [7144.6949677849625, 694.5866953529555])
    assert np.array_equal(list(soln[1]), [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0])   
    
def test_CRE25():
    prob = re.get_problem('cre25')
    dv = [x for x in prob.ubound]
    soln = prob.evaluate(dv)
    assert np.array_equal(list(soln[0]), [5.931, 60.0])
    assert np.array_equal(list(soln[1]), [0.35572067522723994])       
    
def test_CRE31():
    prob = re.get_problem('cre31')
    dv = [x for x in prob.ubound]
    soln = prob.evaluate(dv)
    assert np.array_equal(list(soln[0]), [42.768012, 3.58525, 10.61064375])
    assert np.array_equal(list(soln[1]), [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])    

def test_CRE32():
    prob = re.get_problem('cre32')
    dv = [x for x in prob.ubound]
    soln = prob.evaluate(dv)
    assert np.array_equal(list(soln[0]), [-378.91220009923603, 20026.606947160206, 25779.574892815603])
    assert np.array_equal(list(soln[1]), [0.0, 0.0, 4.426131511528606, 0.0, 0.0, 9761.18636618978, 0.0, 0.0, 2.715456456020493])    

def test_CRE51():
    prob = re.get_problem('cre51')
    dv = [x for x in prob.ubound]
    soln = prob.evaluate(dv)
    assert np.array_equal(list(soln[0]), [83060.744, 1350.0, 2853468.96494178, 447902.6720089092, 11122.222222222223])
    assert np.array_equal(list(soln[1]), [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])        
    