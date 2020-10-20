import h5py
import numpy as np
import src.outputInterface as OI

class h5Interface(object):
    
    def __init__(self, output_name='SFR_DB'):
        self.mcnp_file_name = None
        self.core_name = None
        self.params = None
        self.h5File = None
        self.outputInterface = None
        self.assembly_ind_vars = None
        self.output_name = output_name
        self.dt_str = h5py.string_dtype(encoding='utf-8')

    def add_reactor(self, file_name, path=''):
        """Add a reactor to the database"""
        self.path = path
        self.mcnp_file_name = file_name
        self.params = file_name.split('_')[1:]        
        self.get_core_name()
        self.get_reactor_ind_vars()

        bu = True if self.assembly_ind_vars['condition'] == b'BU' else False
        self.get_outputInterface(bu=bu)
        if self.base_core not in self.h5file.keys():
            self.initialize_reactor_entry()
        else:
            self.h5file[self.base_core].create_group(self.core_name)        
        self.fill_reactor_entry()

    def convert_assembly_parameters(self, params, step):
        """Write the assembly paramaters for each time step in a burnup
        TODO: Find a way to incorporate attributes (H5 attrs) for units perhaps?
        TODO: Add assembly power as a H5 group"""
        core_group = self.h5file[self.base_core][self.core_name][step]['assemblies']
        for k,v in params.items():
            str_a = str(k)
            core_group.create_group(str_a)
            for assem_param, val in v.items():
                if assem_param == 'actinide inventory':
                    core_group[str_a].create_group(assem_param)
                    for num, nuclide in enumerate(val.index):
                        core_group[str_a][assem_param][str(nuclide)] = val.iloc[num]
                else:
                    core_group[str_a][assem_param] = [val]
                    
    def convert_rx_parameters(self, params, step):
        """Write the reactor parameters for each step."""
        core_group = self.h5file[self.base_core][self.core_name][step]['rx_parameters']
        for k,v in params.items():
            if 'precursor' in k:
                core_group.create_group(k)
                for pre, val in v[step].items():
                    if type(val) == str: #skip the units, this will be removed from output
                        pass
                    else:
                        core_group[k][pre] = [val]
            else: 
                core_group[k] = [v[0]]
        
    def create_h5(self):
        """Create an H5 database"""
        self.h5file = h5py.File(self.output_name + '.h5', 'w')

    def get_core_name(self):
        """Get the core name based on output file name"""
        self.params[-1] = self.params[-1].split('.')[0]
        if len(self.params) == 4:
            self.base_core = '_'.join(self.params[:-1])
        else:
            self.base_core = '_'.join(self.params)
        self.core_name = '_'.join(self.params)
          
    def get_outputInterface(self, bu=False):
        """Read in the output file, and create an outputInterface instnace"""
        self.outputInterface = OI.OutputReader('{}/{}'.format(self.path,self.mcnp_file_name), burnup=bu)
        self.outputInterface.read_input_file()        

    def get_reactor_ind_vars(self):
        """Baed on the file name, glean information on the core design"""
        condition = ''
        for params in self.params:
            if 'FS' in params:
                smear = float(params[2:])
            elif 'H' in params:
                height = float(params[1:])
            elif 'Zr' in params:
                if '27U10Zr' in params:
                    pu_content = 0
                elif '3Pu24U10Zr' in params:
                    pu_content = 0.10
                elif '7Pu20U10Zr' in params:
                    pu_content = 0.25
                elif '11Pu16U10Zr' in params:
                    pu_content = 0.40
                elif '15Pu12U10Zr' in params:
                    pu_content = 0.555555                      
                elif '20Pu7U10Zr' in params:
                    pu_content = 0.75
                elif '23Pu4U10Zr' in params:
                    pu_content = 0.875
                elif '27Pu0U10Zr' in params:
                    pu_content = 1.0
                else:
                    print('Warning: Plutonium content unknown for material {}. Please add an elif statment.'.format(params))
                    pu_content = 0.0
                u_content = 1.0 - pu_content
            else:
                condition = params
        self.assembly_ind_vars = {'smear': smear,
                                'height': height,
                                'pu_content': pu_content,
                                'u_content': u_content,
                                'condition': np.string_(condition)}    
        
    def fill_reactor_entry(self):
        """Given the information from the outputInterface, fill the database entry"""    
        for step, params in  self.outputInterface.cycle_dict.items():
            self.h5file[self.base_core][self.core_name].create_group(step)
            self.h5file[self.base_core][self.core_name][step].create_group('rx_parameters')
            self.h5file[self.base_core][self.core_name][step].create_group('assemblies')
            for k, v in params.items():
                if k == 'rx_parameters':
                    self.convert_rx_parameters(v, step)
                elif k == 'assemblies':
                    self.convert_assembly_parameters(v, step)

    def initialize_reactor_entry(self):
        """If the reactor is new, create an entry for it in the database"""
        self.h5file.create_group(self.base_core)
        self.h5file[self.base_core].create_group(self.core_name)
        self.h5file[self.base_core].create_group('independent variables')
        for k,v in self.assembly_ind_vars.items():
            self.h5file[self.base_core]['independent variables'][k] = [v]

    def read_h5(self, path):
        """Read an H5 file and create an h5 interface"""
        self.h5file = h5py.File(path, 'r+')
        