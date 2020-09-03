import bb_opt
import plotly.express as px

class BenchmarkBB(bb_opt.BbOpt):
    
    def on_init(self):
        super().on_init()
        self._complete = False
        self.problem = 'benchmark'
        self.add_abstract_lvl(1, {'pareto type': str, 'fitness function': float})
        self.add_abstract_lvl(2, {'valid': bool})
        self.add_panel(2, ['new', 'old'])

        self.objectives = {'f1': {'ll':0, 'ul':1, 'goal':'lt', 'variable type': float},
                           'f2': {'ll':0, 'ul':1, 'goal':'lt', 'variable type': float}}
        self.design_variables =  {'x1':  {'ll':0, 'ul':1, 'variable type': float},
                                  'x2':  {'ll':0, 'ul':1, 'variable type': float}}
        
        self.hv_convergence = 1e-6
        self._sm = None
        self.sm_type = 'interpolate'
        
    def setup_benchmark(self, benchmark):
        pass

    def plot_progress(self):
        
        try:
            lvls = self.get_attr('abstract_lvls')
            objectives = self.get_attr('objectives')
            lvl_3 = {}
            for panel in lvls['level 3'].values():
                lvl_3.update(panel)    
            lvl_1 = lvls['level 1']

            obj_dict = {}
            objs = [x for x in objectives.keys()]
            for entry_name, entry in lvl_1.items():
                val = lvl_3[entry_name]['objective functions']
                for obj in objectives.keys():
                    if obj in obj_dict.keys():
                        obj_dict[obj].append(val[obj])
                    else:
                        obj_dict[obj] = [val[obj]]

            fig1 = px.scatter(x=obj_dict[objs[0]], y=obj_dict[objs[1]], labels={'x':'f1', 'y':'f2'})
            fig1.show()
        except KeyError:
            pass
        fig2 = px.line(x=[x for x in range(len(self.hv_list))], y=self.hv_list, labels={'x':'Trigger Value', 'y':"Hyper Volume"})        
        fig2.show()