from src.ka.ka_s.base import KaLocal
import numpy as np
from numpy import random
from pymoo.model.problem import Problem
from pymoo.factory import get_algorithm, get_termination, get_reference_directions
from pymoo.model.callback import Callback
from pymoo.optimize import minimize
from pymoo.model.population import Population
from pymoo.model.evaluator import Evaluator
import src.utils.utilities as utils


class PyMooAlgorithm(KaLocal):

    def on_init(self):
        super().on_init()
        self.pymoo_algorithm_name = 'nsga2'
        self._class = 'local search pymoo {}'.format(self.pymoo_algorithm_name)
        self._base_trigger_val         = 6.00000001
        self.termination_type = 'n_eval'
        self.termination_criteria = 250
        self.termination = None
        self.ref_dir_type = 'das-dennis'
        self.n_partitions = 12
        self.pop_size = 25
        self.n_offspring = 10
        self.initial_pop = None
        self.ref_dirs = None       
    
    class PyMooProblem(Problem):
    
        def __init__(self, ka_s,
                           n_var=2,
                           n_obj=2,
                           n_constr=2,
                           xl=np.array([0,0]),
                           xu=np.array([1,1]),
                           **kwargs):
            super().__init__(n_var=n_var,
                             n_obj=n_obj,
                             n_constr=n_constr,
                             xl=xl,
                             xu=xu,
                             **kwargs)
            
            self.base = ka_s
        
        def _evaluate(self, X, out, *args, **kwargs):
            obj = []
            const = []
            self.base.current_design_variables = {k:float(X[num]) for num, k in enumerate(self.base._design_variables.keys())}
            self.base.calc_objectives()
            obj.append([utils.convert_objective_to_minimize(self.base._objectives[obj], x) for obj, x in self.base.current_objectives.items()])

            if self.base._constraints:      
                const.append([-utils.scale_value(self.base.current_constraints[con], con_dict) for con, con_dict in self.base._constraints.items()])   
                              
            self.base.write_to_bb(self.base.bb_lvl_data, self.base._entry_name, self.base._entry, panel='new')
            self.base.clear_entry()  
            
            out["F"] = np.array(obj)
            out["G"] = np.array(const)
            
    def handler_trigger_publish(self, message):
        """
        Read the BB level and determine if an entry is available.
        GA is currently triggered if we find that the PF level has solutions that it has not analyzed greater than some aribratry amount pf_size.
        
        Paremeters
        ----------
        message : str
            Required message from BB
        
        Returns
        -------
        send : message
            _trigger_response_alias : int
                Alias for the trigger response 
            name : str
                Alias for the agent, such that the trigger value get assigned to the right agent on the BB
            _trigger_val : int
                Trigger value for knowledge agent
        """
        lvl = message['level {}'.format(self.bb_lvl_read)]
        
        pf_size = 0
        if self.bb_lvl_read != 1:
            for panel in lvl.values():
                pf_size += len(panel)
        else:
            pf_size += len(lvl.keys())         

        self._trigger_val = self._base_trigger_val if pf_size >= self.pop_size else 0
        self.send(self._trigger_response_alias, (self.name, self._trigger_val))
        self.log_debug('Agent {} triggered with trigger val {}'.format(self.name, self._trigger_val))            
    
    def get_pf(self):
        population = list(self.lvl_read) if self.bb_lvl_read == 1 else list({**self.lvl_read['new'], **self.lvl_read['old']})

        pop_array = np.zeros([len(population),len(self._design_variables.keys())])
        for num, individual in enumerate(population):
            pop_array[num] = np.array([self._lvl_data[individual]['design variables'][dv] for dv in self._design_variables.keys()])
            
        return pop_array
    
    def setup_problem(self):
        self.termination = get_termination(self.termination_type, self.termination_criteria)
        self.ref_dirs = get_reference_directions(self.ref_dir_type, len(self._design_variables), n_partitions=self.n_partitions)  
        self._problem = self.PyMooProblem(self,
                                         n_var=len(self._design_variables),
                                         n_obj=len(self._objectives),
                                         n_constr=len(self._constraints),
                                         xl=np.array([x['ll'] for x in self._design_variables.values()]),
                                         xu=np.array([x['ul'] for x in self._design_variables.values()]),
                                         elementwise_evaluation=True)
        self._problem.base = self
        # Grab the design variables for the current PF
        self.initial_pop = self.get_pf()
        pop = Population.new('X', self.initial_pop)
        
        if self.pymoo_algorithm_name == 'nsga2':
            self.algorithm = get_algorithm(self.pymoo_algorithm_name,
                                           sampling = pop,
                                           pop_size=self.pop_size,
                                           n_offpsring=self.n_offspring)
        elif self.pymoo_algorithm_name == 'moead':
            self.algorithm = get_algorithm(self.pymoo_algorithm_name,
                                           ref_dirs=self.ref_dirs,
                                            n_neighbors=15,
                                            decomposition="pbi",
                                            prob_neighbor_mating=0.7)          
        else:
            self.algorithm = get_algorithm(self.pymoo_algorithm_name,
                                           ref_dirs=self.ref_dirs,
                                           sampling = pop,
                                           pop_size=self.pop_size,
                                           n_offpsring=self.n_offspring)            

        
    def search_method(self):
        """
        Determine the core design variables using a monte carlo (stochastic) method.
        """        
        self.setup_problem()
        self.problem_results = minimize(self._problem, 
                                        self.algorithm, 
                                        self.termination,
                                        seed=1,
                                        verbose=False)
        
        self.log_debug('Core design variables determined: {}'.format(self.current_design_variables))
    