from src.utils.moo_benchmarks import optimization_test_functions as otf

class Problem():
    """
    Define a problem for the optimization benchmark to solve.
    
    Requires 
    """
    
    def __init__(self,
                 design_variables=None,
                 objectives=None,
                 constraints=[]):
        self.dvs = design_variables
        self.objs = objectives
        self.cons = constraints
    
    def evaluate(self, design_variables, objectives, constraints):
        ...
        
class BenchmarkProblem(Problem):
    def __init__(self,
                 design_variables=None,
                 objectives=None,
                 constraints=[],
                 benchmark_name=None):
    
        super().__init__(design_variables=design_variables,
                 objectives=objectives,
                 constraints=constraints,)
        self.benchmark_name=benchmark_name
        self.benchmark = otf(self.benchmark_name)
    
    def evaluate(self, design_variables):
        """
        Calculate the objectives based on a benchmark problem
        """
        objs = {}
        cnsts = {}        
        design = [x for x in design_variables.values()]
        obj_dict = self.benchmark.predict(self.benchmark_name, design, num_vars=len(design), num_objs=len(self.objs))
        for num, obj in enumerate(self.objs.keys()):
            if self.objs[obj]['variable type'] == float:
                objs[obj] = float(obj_dict['F'][num])
            elif self.objs[obj]['variable type'] == str:
                objs[obj] = str(obj_dict[num])
        for num, cnst in enumerate(self.cons.keys()):
            cnsts[cnst] = float(obj_dict['G'][num])
        
        return objs, cnsts
