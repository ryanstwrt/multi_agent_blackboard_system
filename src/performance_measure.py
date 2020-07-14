import platypus as plat
import math

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
    Needs to be completed
    """
    
    hv_base = hypervolume_indicator(pf, lower_ref, upper_ref)
    diversity_dict = {}
    for num, core in enumerate(pf_names):
        pf_minus = copy.copy(pf)
        pf_minus.pop(num)
        hv_minus = hypervolume_indicator(pf_minus, lower_ref, upper_ref)
        diversity[core] = hv_base - hv_minus

class diversity_comparison_indicator(object):
    
    def __init__(self, lb, ub, divisions, pf):
        self.ideal_point = lb
        self.nadir_point = ub
        self.num_objectives = len(self.nadir_point)
        print(self.num_objectives)
        self.div = divisions
        self.pf = {}
        self._hyperbox_grid = None
        self._pf_grid_coordinates = None

        self._grid_generator()
        for pf_set in pf:
            if self._pf_grid_coordinates:
                self._pf_grid_coordinates += self._pareto_grid_locations(pf_set)
            else:
                self._pf_grid_coordinates = self._pareto_grid_locations(pf_set)            
            self.pf.update(pf_set)
            
    def compute_dci(self, test_pf):
        """
        Calculate the diversity comparison indicator (DCI)
        """
        self.dc = {}
        m = self.num_objectives + 1
        for pf_grid_pos in self._pf_grid_coordinates:
            for obj_vector_name, obj_vector in test_pf.items():
                dist = self._pf_point_to_hyperbox(test_pf, pf_grid_pos)
                self.dc[pf_grid_pos] = (1 - dist**2 / m) if dist < math.sqrt(m) else 0
        
        self.dci = sum(self.dc.values())/ len(self.dc)
    
    def _grid_generator(self):
        """
        Generate the hyperbox size for each objective.
        """
        self._hyperbox_grid = {obj: (ul - self.ideal_point[obj])/self.div for obj,ul in self.nadir_point.items()}
    
    def _pareto_grid_locations(self, pf):
        """
        Place the pareto front into the vgrid framework.
        """
        _pf_grid_coordinates = [self._get_grid_location(soln) for soln in pf.values()]
        return _pf_grid_coordinates
        
    def _get_grid_location(self, obj_vector):
        """
        obj_vector : dict {obj_func1 : val,}
        """
        grid_location = []
        for obj, val in obj_vector.items():
            grid_location.append(int((val - self.ideal_point[obj]) / self._hyperbox_grid[obj]))
        return tuple(grid_location)
    
    def _hyperbox_distance(self, box_1, box_2):
        """
        Calculate the grid distance between two hyperboxes in the grid
        
        box_1 : tuple (obj_func1_box (int), obj_func2_box (int))
        box_2 : tuple (obj_func1_box, obj_func2_box)
        """
        grid_distance = sum([(val - box_2[num]) ** 2 for num, val in enumerate(box_1)])
        return math.sqrt(grid_distance)
    
    def _pf_point_to_hyperbox(self, test_pf, pf_grid_pos):
        """
        Calculate the shortest grid distance between a hyperbox (h) and pf approximation (P)
        box : dict {obj_func1 :val, }
        """
        test_pf_grid = self._pareto_grid_locations(test_pf)
        dist = [self._hyperbox_distance(obj_funcs, pf_grid_pos) for obj_funcs in test_pf_grid]
        return min(dist)