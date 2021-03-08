import src.utils.performance_measure as pm
import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
from src.ka.ka_s.hill_climb import HillClimb
import src.bb.blackboard_optimization as bb_opt
import pickle
import time
import copy
import math

def test_hypervolume_indicator_base():    
    ref_point = [1,1]
    pf =[[.5,0.5]]
    assert pm.hypervolume_indicator(pf, ref_point) == 0.25    
    
def test_dci_init():
    lb = {'f1':0, 'f2':0}
    ub = {'f1':5, 'f2':5}
    div = {'f1': 5, 'f2': 5}
    pf = {'a': {'f1':0.25, 'f2':4.5}, 
          'b': {'f1':0.75, 'f2':3.5}, 
          'c': {'f1':2.5, 'f2':2.5}, 
          'd': {'f1':4.25, 'f2':0.5},
          'e': {'f1':5.0,   'f2':5.0}}
    goal = {'f1': 'lt', 'f2': 'lt'}

    dci = pm.diversity_comparison_indicator(lb, ub, [pf], goal=goal, div=div)
    
    assert dci._ideal_point == lb
    assert dci._nadir_point == ub
    assert dci.num_objectives == 2
    assert dci.div == div
    assert dci._hyperbox_grid == {'f1': 1, 'f2': 1}
    assert dci._pf_grid_coordinates == {'a': (0,4), 'b': (0,3), 'c': (2,2), 'd': (4,0)}

def test_dci_hyperbox_distance():
    lb = {'f1':0, 'f2':0}
    ub = {'f1':5, 'f2':5}
    div = {'f1': 5, 'f2': 5}
    pf = {'a': {'f1':0.25, 'f2':4.5}, 
          'b': {'f1':0.75, 'f2':3.5}, 
          'c': {'f1':2.5, 'f2':2.5}, 
          'd': {'f1':4.25, 'f2':0.5}}    

    dci = pm.diversity_comparison_indicator(lb, ub, [pf], div=div)
    dist = dci._hyperbox_distance((0,3), (2,2))
    assert dist == math.sqrt(5)
    
def test_dci_pf_point_to_hyperbox():
    lb = {'f1':0, 'f2':0}
    ub = {'f1':5, 'f2':5}
    div = {'f1': 5, 'f2': 5}
    pf = {'a': {'f1':0.25, 'f2':4.5}, 
          'b': {'f1':0.75, 'f2':3.5}, 
          'c': {'f1':2.5, 'f2':2.5}, 
          'd': {'f1':4.25, 'f2':0.5}}    

    dci = pm.diversity_comparison_indicator(lb, ub, [pf], div=div)  
    dist = dci._pf_point_to_hyperbox(pf, (1,3))
    assert dist == 1

def test_dci():
    lb = {'f1':0, 'f2':0}
    ub = {'f1':8, 'f2':8}
    div = {'f1': 8, 'f2': 8}
    pf1 = {'a': {'f1':0.5, 'f2':6.5}, 
          'b':  {'f1':1.5, 'f2':4.5}, 
          'c':  {'f1':2.5, 'f2':2.5}, 
          'd':  {'f1':4.5, 'f2':2.5},
          'e':  {'f1':5.5, 'f2':1.5},
          'f':  {'f1':7.5, 'f2':0.5}}
    pf2 = {'g': {'f1':0.5, 'f2':7.5}, 
          'h':  {'f1':0.5, 'f2':6.5}, 
          'i':  {'f1':4.5, 'f2':1.5}, 
          'j':  {'f1':6.5, 'f2':0.5},
          'k':  {'f1':7.5, 'f2':0.5}}
    pf3 = {'l': {'f1':1.5, 'f2':4.5}, 
          'm':  {'f1':1.5, 'f2':3.5}, 
          'n':  {'f1':3.5, 'f2':2.5}, 
          'o':  {'f1':3.5, 'f2':2.5},
          'p':  {'f1':4.5, 'f2':2.5}}
    pfs = [pf1, pf2, pf3]
    
    dci = pm.diversity_comparison_indicator(lb, ub, pfs, div=div)
    
    dci._grid_generator()
    dci.compute_dci(pf1)
    assert round(dci.dci,3) == 0.848
    dci.compute_dci(pf2)
    assert round(dci.dci,3) == 0.606
    dci.compute_dci(pf3)
    assert round(dci.dci,3) == 0.515
    
def test_dci_gt():
    lb = {'f1':0, 'f2':0}
    ub = {'f1':8, 'f2':8}
    div = {'f1': 8, 'f2': 8}
    goal = {'f1': 'lt', 'f2': 'gt'}
    pf1 = {'a': {'f1':4.5, 'f2':6.5}, 
          'b':  {'f1':2.5, 'f2':4.5}}
    pf2 = {'g': {'f1':3.5, 'f2':5.5}, 
          'h':  {'f1':5.5, 'f2':7.5}}

    pfs = [pf1, pf2]

    dci = pm.diversity_comparison_indicator(lb, ub, pfs, goal=goal)
    
    dci._grid_generator()
    dci.compute_dci(pf1)
    assert round(dci.dci,3) == 0.667
    dci.compute_dci(pf2)
    assert round(dci.dci,3) == 0.667
