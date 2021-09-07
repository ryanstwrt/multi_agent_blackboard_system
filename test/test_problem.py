import mabs.utils.problem as problem
from mabs.utils.moo_benchmarks import optimization_test_functions as otf

def test_init():
    prob = problem.Problem()
    assert prob.dvs == None
    assert prob.objs == None
    assert prob.cons == []

def test_init_benchmark():
    dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
    objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}  
        
    prob = problem.BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')  
    assert prob.dvs == dvs
    assert prob.objs == objs
    assert prob.cons == {}   
    assert prob.benchmark_name == 'dtlz1'
    assert type(prob.benchmark) == type(otf('dtlz1'))
    
def test_benchmark_evaluate():
    dvs = {'x{}'.format(x):{'ll':0.0, 'ul':1.0, 'variable type': float} for x in range(3)}
    objs = {'f{}'.format(x): {'ll':0.0, 'ul':1000, 'goal':'lt', 'variable type': float} for x in range(3)}  
        
    prob = problem.BenchmarkProblem(design_variables=dvs,
                         objectives=objs,
                         constraints={},
                         benchmark_name = 'dtlz1')
    objectives, constraints = prob.evaluate({'x1': 0.5, 'x2': 0.5, 'x3': 0.5})
    assert objectives == {'f0': 0.125, 'f1': 0.125, 'f2': 0.25}
    assert constraints == {}
    