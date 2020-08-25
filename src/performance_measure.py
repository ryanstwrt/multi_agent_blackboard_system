import platypus as plat
import math

def hypervolume_indicator(pf, lower_ref, upper_ref):
    """
    Calculates the hypervolume for the Pareto Front.
    """
    hyp = plat.indicators.Hypervolume(minimum=lower_ref, maximum=upper_ref)
    problem = plat.Problem(len(lower_ref),len(upper_ref))
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
    
    def __init__(self, lb, ub, pf, div=None):
        self._ideal_point = lb
        self._nadir_point = ub
        self.num_objectives = len(self._nadir_point)
        self.div = div if div else {obj: abs(self._ideal_point[obj] - self._nadir_point[obj]) for obj in self._ideal_point.keys()}

        self.dc = {}
        self.dci = 0
        self._hyperbox_grid = None
        self._pf_grid_coordinates = {}

        self._grid_generator()
        for pf_set in pf:
            self._pf_grid_coordinates.update(self._pareto_grid_locations(pf_set))       
            
    def compute_dci(self, test_pf):
        """
        Calculate the diversity comparison indicator (DCI)
        """
        self.dc = {}
        self.dc_pf = {}
        m = self.num_objectives + 1
        for name, pf_grid_pos in self._pf_grid_coordinates.items():
            dist = self._pf_point_to_hyperbox(test_pf, pf_grid_pos)
            # Currently we overwrite a grid position, we should figure out a way to hold this information and compare them.
            # Fixed this, but now we have too many solutions present and this throws off our DCI 
            dc = (1 - dist**2 / m) if dist < math.sqrt(m) else 0
            self.dc[name] = {'grid position': pf_grid_pos, 'contribution degree': dc}
        
        _dci = {}
        for x in self.dc.values():
            pos = x['grid position']
            dc = x['contribution degree']
            if pos in _dci.keys():
                pass
            else:
                _dci[pos] = dc
        self.dci = sum([x for x in _dci.values()])/ len(_dci)
    
            
        #self.dci = sum([x['contribution degree'] for x in self.dc.values()])/ len(self.dc)
    
    def _grid_generator(self):
        """
        Generate the hyperbox size for each objective.
        """
        self._hyperbox_grid = {obj: (self._nadir_point[obj] - self._ideal_point[obj])/self.div[obj] for obj in self._nadir_point.keys()}
    
    def _pareto_grid_locations(self, pf):
        """
        Place the pareto front into the grid framework.
        """
        _pf_grid_coordinates = {design : self._get_grid_location(soln) for design, soln in pf.items()}
        return _pf_grid_coordinates
        
    def _get_grid_location(self, obj_vector):
        """
        obj_vector : dict {obj_func1 : val,}
        """
        grid_location = []
        for obj, val in obj_vector.items():
            grid_location.append(int((val - self._ideal_point[obj]) / self._hyperbox_grid[obj]))
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
        test_pf_grid = [x for x in test_pf_grid.values()]
        dist = [self._hyperbox_distance(obj_funcs, pf_grid_pos) for obj_funcs in test_pf_grid]
        return min(dist)