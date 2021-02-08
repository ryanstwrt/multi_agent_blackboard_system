from src.ka.ka_s.base import KaLocal
from numpy import random


class RandomWalk(KaLocal):
    
    def on_init(self):
        super().on_init()
        self._base_trigger_val = 5.00001
        self.step_size = 0.01
        self.walk_length = 10
        self._class = 'local search random walk'
        
    def search_method(self):
        """
        Basic random walk algorithm for searching around a viable design.
        """
        core = random.choice(self.new_designs)
        entry = self.lvl_read[core]
        design = self._lvl_data[core]['design variables']
        
        for x in enumerate(range(self.walk_length)):
            dv = random.choice(list(self._design_variables))
            step = round(random.random() * self.step_size, self._design_accuracy)
            direction = random.choice(['+','-'])
            design[dv] = design[dv] + step if direction == '+' else design[dv] - step
            design[dv] = round(design[dv], self._design_accuracy)
            self.current_design_variables = design
            self.determine_model_applicability(dv)
        self.analyzed_design[core] = {'Analyzed': True, 'HV': 0.0}