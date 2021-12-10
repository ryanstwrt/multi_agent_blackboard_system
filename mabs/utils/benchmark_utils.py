from pymoo.factory import get_performance_indicator, get_reference_directions, get_problem
import numpy as np
import os

def get_indicator(indicator, benchmark_name, bb_pf, path_to_pf='../../test/benchmark_problems/approximated_Pareto_fronts/'):
  
    given_pf = np.array(bb_pf)
    ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)
    if benchmark_name in ['welded_beam','truss2d']:
        known_pf = get_problem(benchmark_name).pareto_front()
    elif 're' in benchmark_name:
        known_pf = get_re_pf(benchmark_name, path_to_pf=path_to_pf)
    elif 'zdt' in benchmark_name or 'dtlz' in benchmark_name:
        known_pf = get_problem(benchmark_name).pareto_front(ref_dirs)
    else:
        return 0.0

    indicator = get_performance_indicator(indicator, known_pf)
    return float(indicator.do(given_pf))


def get_re_pf(benchmark, path_to_pf='../../test/benchmark_problems/approximated_Pareto_fronts/'):
   # home = os.getenv("HOME")
    path = path_to_pf + 'reference_points_{}.dat'.format(benchmark.upper())
    pf = []
    with open(path, 'r') as f:
        for line in f:
            pf.append([float(x) for x in line.split(' ')])
            
    return np.array(pf)
    