from pymoo.factory import get_performance_indicator
import math
import numpy as np

def hypervolume_indicator(pf, upper_ref):
    """
    Calculates the hypervolume for the Pareto Front. 
    The PF needs to be scaled to calculate everything correctly.
    
    pf : list of lists
    lower_ref : list
    upper_ref : list
    """
    hv = get_performance_indicator("hv", ref_point=np.array(upper_ref))
    print(pf)
    print(np.array(pf))
    return float(hv.do(np.array(pf)))

class diversity_comparison_indicator(object):
    
    def __init__(self, lb, ub, pf, goal=None, div=None):
        self._ideal_point = lb
        self._nadir_point = ub
        self.num_objectives = len(self._nadir_point)
        self.goal = goal if goal else {obj: 'lt' for obj in self._ideal_point.keys()}
        self.div = div if div else {obj: abs(self._ideal_point[obj] - self._nadir_point[obj]) for obj in self._ideal_point.keys()}

        self.dc = {}
        self._pf = {}
        self.dci = 0
        self._hyperbox_grid = None
        self._pf_grid_coordinates = {}

        self._grid_generator()
        for pf_set in pf:
            self._pf.update(pf_set)
        self._remove_dominated_solutions()
        self._pf_grid_coordinates.update(self._pareto_grid_locations(self._pf))
    
            
    def compute_dci(self, test_pf):
        """
        Calculate the diversity comparison indicator (DCI)
        """
        self.dc = {}
        self.dc_pf = {}
        m = self.num_objectives + 1
        for name, pf_grid_pos in self._pf_grid_coordinates.items():
            dist = self._pf_point_to_hyperbox(test_pf, pf_grid_pos)
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

    def _remove_dominated_solutions(self):
        """
        Remove any domianted entry in the Pareto front so it does not count towards the dci value
        """
        pf = {}
        for solution_name, solution_1 in self._pf.items():
            optimal = self._determine_dominated_solutions(solution_1)
            if optimal:
                pf.update({solution_name: solution_1})
        self._pf = pf
    
    def _convert_to_minimize(self, obj, obj_val):
        if self.goal[obj] == 'gt':
            return -obj_val
        elif self.goal[obj] =='lt':
            return obj_val
        elif self.goal[obj][0] =='et':
            target = self.goal[obj][1]
            return abs(target - obj_val)        
    
    def _determine_dominated_solutions(self, sol_1):
        """
        Determine if one solutions dominates another
        """
        for sol_2 in self._pf.values():
            optimal = 0
            if sol_1 != sol_2:
                for obj in self.goal.keys():
                    sol_1_val = self._convert_to_minimize(obj, sol_1[obj])
                    sol_2_val = self._convert_to_minimize(obj, sol_2[obj])
                    optimal += 1 if sol_1_val <= sol_2_val else 0
                if optimal == 0:
                    return False
        
        return True
