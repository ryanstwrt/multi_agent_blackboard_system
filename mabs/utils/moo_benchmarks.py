import pymoo.problems as mop
from pymoo.factory import get_problem
import numpy as np
import time
import math
import mabs.utils.reproblems as reprob

class optimization_test_functions(object):
    
    def __init__(self, test):
        self.test_name = test

    def predict(self, test_name, x, num_vars=2, num_objs=None):
        if self.test_name == 'sf1':
            return self.schaffer_func_1(x)
        elif self.test_name == 'sf2':
            return self.schaffer_func_2(x)
        elif 'zdt' in self.test_name:
            return self.zdt(x, num_vars)
        elif self.test_name == 'tsp':
            return self.tsp(x)
        elif self.test_name == 'tsp_perm':
            return self.tsp_perm(x)        
        elif self.test_name == 'welded_beam':
            return self.welded_beam(x)
        elif self.test_name == 'truss2d':
            return self.truss2d(x)
        elif 'dtlz' in self.test_name:
            return self.dtlz(x, num_vars, num_objs)
        elif 'cre' in self.test_name:
            return self.crep(x)
        elif 're' in self.test_name:
            return self.rep(x)
    
    def schaffer_func_1(self, x):
        """
        MOO Benchmark test function Schaffer Function N. 1
        x varies between values of -A to A, where A from 10 to 10^5 are typically successful, higher values increase the difficulty of the problem
        """
        f1 = x[0] ** 2
        f2 = (x[0]-2) ** 2
        return {'F': [float(f1),float(f2)]}

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
        return {'F': [float(f1),float(f2)]}
    
    def zdt(self, x, num_vars):
        """
        ZDT Benchmark from pymop
        """
        problem = get_problem(self.test_name, n_var=num_vars)
        #problem = mop.ZDT1(n_var=num_vars)
        soln = problem.evaluate(x, return_values_of=['F','G'], return_as_dictionary=True)
        return soln


    def dtlz(self, x, num_vars, num_objs):
        problem = get_problem(self.test_name, n_var=num_vars, n_obj=num_objs)
        soln = problem.evaluate(x, return_values_of=['F','G'], return_as_dictionary=True)
        return soln     
    
    def tsp(self, x):
        """
        traveling sales person
        """
        if type(x[0]) == str:
            x = [int(y) for y in x]
        graph = [[0, 10, 15, 20], [10, 0, 35, 25], 
                 [15, 35, 0, 30], [20, 25, 30, 0]]

        path = 0
        k = 0
        for j in x:
            path += graph[k][j]
            k=j
        path += graph[k][0]
        return {'F': [path]}
        
    def tsp_perm(self, x):
        """
        traveling sales person - permutation 
        """
        if type(x[0][0]) == str:
            x = [int(y) for y in x[0]]
        graph = [[0, 10, 15, 20], [10, 0, 35, 25], 
                 [15, 35, 0, 30], [20, 25, 30, 0]]

        path = 0
        k = 0
        for j in x:
            path += graph[k][j]
            k=j
        path += graph[k][0]
        return {'F': [path]}   
    
    def welded_beam(self, x):
        problem = get_problem('welded_beam')
        soln = problem.evaluate(x, return_values_of=['F','G'], return_as_dictionary=True)
        return soln
    
    def truss2d(self, x):
        problem = get_problem('truss2d')
        soln = problem.evaluate(x, return_values_of=['F','G'], return_as_dictionary=True)
        return soln    
        
    def rep(self, x):
        problem = reprob.get_problem(self.test_name)    
        objs = problem.evaluate(x)
        return {'F': objs.tolist()}
    
    def crep(self, x):
        problem = reprob.get_problem(self.test_name)    
        objs, consts = problem.evaluate(x)
        return {'F': objs.tolist(), 'G': consts.tolist()}