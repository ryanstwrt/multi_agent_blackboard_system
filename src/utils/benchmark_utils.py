from pymoo.factory import get_performance_indicator, get_reference_directions, get_problem
import numpy as np

def get_indicator(indicator, benchmark_name, bb_pf):

    given_pf = np.array(bb_pf)
    ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)
    if benchmark_name in ['welded_beam','truss2d']:
        known_pf = get_problem(benchmark_name).pareto_front()
    else:
        known_pf = get_problem(benchmark_name).pareto_front(ref_dirs)

    gd_ = get_performance_indicator(indicator, known_pf)
    return float(gd_.calc(given_pf))