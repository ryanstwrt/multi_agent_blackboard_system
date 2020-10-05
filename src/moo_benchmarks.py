import pymop.problems as mop

class optimization_test_functions(object):
    
    def __init__(self, test):
        self.test_name = test

    def predict(self, test_name, x, num_vars=None, num_objs=None):
        if self.test_name == 'sf1':
            return self.schaffer_func_1(x)
        elif self.test_name == 'sf2':
            return self.schaffer_func_2(x)
        elif self.test_name == 'zdt1':
            return self.zdt_1(x, num_vars)
        elif self.test_name == 'zdt2':
            return self.zdt_2(x)
        elif self.test_name == 'zdt3':
            return self.zdt_3(x)
        
    
    def schaffer_func_1(self, x):
        """
        MOO Benchmark test function Schaffer Function N. 1
        x varies between values of -A to A, where A from 10 to 10^5 are typically successful, higher values increase the difficulty of the problem
        """
        f1 = x[0] ** 2
        f2 = (x[0]-2) ** 2
        return [f1, f2]

    def schaffer_func_2(self, x):
        """
        MOO Benchmark test function Schaffer Function N. 2
        x varies between -5 and 10
        """  
        x = x[0]
        
        if x <= 1:
            f1 = -x
        elif x <= 3:
            f1 = x-2
        elif x <= 4:
            f1 = 4-x
        else:
            f1 = x-4
            
        f2 = (x-5) ** 2        
        return [float(f1),float(f2)]
    
    def zdt_1(self, x, num_vars):
        """
        DTLZ Benchmark 1 from pymop
        """
        problem = mop.ZDT1(n_var=num_vars)
        soln = problem.evaluate(x)
        return soln

    def zdt_2(self, x, num_vars):
        """
        DTLZ Benchmark 2 from pymop
        """
        problem = mop.ZDT2(n_var=num_vars)
        soln = problem.evaluate(x)
        return soln
    
    def zdt_3(self, x, num_vars):
        """
        DTLZ Benchmark 3 from pymop
        """
        problem = mop.ZDT3(n_var=num_vars)
        soln = problem.evaluate(x)
        return soln