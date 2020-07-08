import platypus as plat

def hypervolume_indicator(pf, lower_ref, upper_ref):
    """
    Calculates the hypervolume for the Pareto Front.
    """
    hyp = plat.indicators.Hypervolume(minimum=lower_ref, maximum=upper_ref)
    problem = plat.Problem(len(lower_ref),len(lower_ref))
    solutions = []
    for objs in pf:
        solution = plat.Solution(problem)
        solution.objectives = objs
        solutions.append(solution)
    return hyp.calculate(solutions)

def diversity_indicatory(pf_names, pf, lower_ref, upper_ref):
    """
    Determines how each solution contriutes to the pareto front.
    """
    
    hv_base = hypervolume_indicator(pf, lower_ref, upper_ref)
    diversity_dict = {}
    for num, core in enumerate(pf_names):
        pf_minus = copy.copy(pf)
        pf_minus.pop(num)
        hv_minus = hypervolume_indicator(pf_minus, lower_ref, upper_ref)
        diversity[core] = hv_base - hv_minus
        