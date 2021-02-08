import numpy as np
import pandas as pd

class OutputReader(object):
    """
    This class reads in an mcnp output file and parses the appropriate data
    """
    
    def __init__(self, f, burnup=False):
        """Initialize the OutputReader with the file name, and read in the file"""
        self.file_path = f
        try:
            file = open(f, 'r')
        except FileNotFoundError:
            raise NameError("File {} does not exist. Enter a valid path name".format(f))
        split_f = f.split('/')[-1]
        self.core_name = split_f.split('.')[0]
        self.output = file.readlines()
        file.close()
        
        self.burnup = burnup
        self.cycles = 0
        self.cycle_dict = {}

    def get_assembly_parameters(self):
        """Get the assembly specific parametsr (burnup, power fraction, actinide inventory)"""
        self.cycles = len(self.cycle_dict)
        for cycle in range(self.cycles):
            self.cycle_dict['step_{}'.format(cycle)]['assemblies'] = {}
        correct_area = False
        
        for line_num, line in enumerate(self.output):
            if 'Individual Material Burnup' in line:
                correct_area = True
            if 'Material #: ' in line and correct_area:
                self.scrap_assembly_power(self.output[line_num:line_num+4+self.cycles])
            elif 'print table 220' in line: #Break before we get to summed materials
                break
            elif 'nuclide data are sorted by increasing zaid for material' in line:
                material = int(self.output[line_num].split(' ')[10])
                self.scrap_assembly_nuclide_data(self.output[line_num:line_num+self.cycles*60], material) 
                #This is a bit sloppy as it will run into the nonactide inventory data, a better method could be implemented later.
        self.convert_assembly_params()

    def get_global_parameters(self):
        "Get the global parameters for a specific cycle"
        current_step = 0
        correct_area = True
        for line_num, line in enumerate(self.output):
            if 'Correcter' in line:
                correct_area = True
            elif 'Predictor' in line:
                correct_area = False
            if 'keff = ' in line and correct_area:
                self.cycle_dict['step_{}'.format(current_step)] = {}
                self.scrap_rx_params(self.output[line_num:line_num+83], current_step)
                current_step += 1
        self.convert_rx_params()
                        
    def convert_rx_params(self):
        """Convert reactor parameters from dictionary to pandas dataframe"""
        
        for step in self.cycle_dict.keys():
            df = pd.DataFrame(index=[step])
            rx = self.cycle_dict[step]['rx_parameters']
            df['keff'] = rx['keff']
            df['keff unc'] =  rx['keff_unc']
            
            if 'seconds' in rx['prompt_removal_lifetime'][2]:
                df['prompt removal lifetime'] = rx['prompt_removal_lifetime'][0]
                df['prompt removal lifetime unc'] = rx['prompt_removal_lifetime'][1]
            else:
                print('Warning: Units for prompt removal lifetime not recognized. Create an elif statment to convert units.')
            if 'mev' in rx['avg_n_lethargy_fission'][1]:
                df['avg n lethargy fission'] = rx['avg_n_lethargy_fission'][0]
            else:
                print('Warning: Units for avg n lethargy fission not recognized. Create an elif statment to convert units.')
            if 'mev' in rx['avg_n_energy_fission'][1]:
                df['avg n energy fission'] = rx['avg_n_energy_fission'][0]
            else:
                print('Warning: Units for avg n energy fission not recognized. Create an elif statment to convert units.')
            
            df['thermal fission frac'] = rx['thermal_fission_frac'] / 100
            df['epithermal fission frac'] = rx['epithermal_fission_frac'] / 100
            df['fast fission frac'] = rx['fast_fission_frac'] / 100
            df['avg n gen per abs fission'] = rx['avg_n_gen_per_abs_fission']
            df['avg n gen per abs all'] = rx['avg_n_gen_per_abs_all']
            df['avg n gen per fission'] = rx['avg_n_gen_per_fission']
            df['lifetime escape'] = rx['lifespan_esc']
            df['lifetime capture'] = rx['lifespan_capt']
            df['lifetime fission'] = rx['lifespan_fission']
            df['lifetime removal'] = rx['lifespan_rem']
            df['frac escape'] = rx['frac_esc']
            df['frac capture'] = rx['frac_capt']
            df['frac fission'] = rx['frac_fission']
            df['frac removal'] = rx['frac_rem']

            if 'nsec' in rx['generation_time'][2]:
                df['generation time'] = rx['generation_time'][0] * 10E-9
                df['generation time unc'] = rx['generation_time'][1] * 10E-9
            elif 'usec' in rx['generation_time'][2]:
                df['generation time'] = rx['generation_time'][0] * 10E-6
                df['generation time unc'] = rx['generation_time'][1] * 10E-6
            else:
                print('Warning: Units for generation time not recognized. Create an elif statment to convert units.')
            
            if 'nsec' in rx['rossi-alpha'][2]:
                df['rossi-alpha'] = rx['rossi-alpha'][0] / 10E-9
                df['rossi-alpha unc'] = rx['rossi-alpha'][1] / 10E-9
            elif 'usec' in rx['rossi-alpha'][2]:
                df['rossi-alpha'] = rx['rossi-alpha'][0] / 10E-6
                df['rossi-alpha unc'] = rx['rossi-alpha'][1] / 10E-6
            else:
                print('Warning: Units for rossi-alpha not recognized. Create an elif statment to convert units.')
            
            df['beta'] = rx['beta'][0]
            df['beta unc'] = rx['beta'][1]
            for k,v in rx['precursors'].items():
                df['precursor {}'.format(k)] = [v] 
                
            self.cycle_dict[step]['rx_parameters'] = df
                
    def convert_assembly_params(self):
        """Convert assembly parameters from a dictionary to a pandas dataframe"""
        df = pd.DataFrame
        for cycle in self.cycle_dict.keys():
            for material in self.cycle_dict[cycle]['assemblies']:
                temp_db = pd.DataFrame(self.cycle_dict[cycle]['assemblies'][material]['actinide inventory'])
                self.cycle_dict[cycle]['assemblies'][material]['actinide inventory'] = temp_db.T       

    def read_input_file(self):
        """Read in a full input file"""
        self.get_global_parameters()
        if self.burnup:
            self.get_assembly_parameters()
        
    def scrap_assembly_power(self, line_list):
        temp_dict = {}
        material = int(line_list[0].split(' ')[3])
        temp_dict['material'] = material
        power_dict = {}
        for time_step in range(self.cycles):
            power = {'duration': float(line_list[4+time_step].split('  ')[2]),
                     'time': float(line_list[4+time_step].split('  ')[3]),
                     'power fraction': float(line_list[4+time_step].split('  ')[5]),
                     'burnup': float(line_list[4+time_step].split('  ')[8]),}
            self.cycle_dict['step_{}'.format(time_step)]['assemblies'][material] = power           

    def scrap_assembly_nuclide_data(self, line_list, material):
        """Scrap the actinide materials data"""
        for line_num, line in enumerate(line_list):
            if 'actinide inventory' in line:
                actinides = True
                time_step = int(line.split(' ')[11][:-1]) #-1 drops the comma after step #,
                zaid_dict = {}
            try:
                mass = float(line.split('  ')[3])
                if mass > 0.0:
                    zaid = int(line.split('  ')[2])
                    zaid_dict[zaid] = {'mass': mass,
                                       'activity': float(line.split('  ')[4]),
                                       'specific activity': float(line.split('  ')[5]),
                                       'atom density': float(line.split('  ')[6]),
                                       'atom fraction': float(line.split('  ')[7]),
                                       'mass fraction': float(line.split('  ')[8])}
            except:
                pass
            if 'totals' in line:
                self.cycle_dict['step_{}'.format(time_step)]['assemblies'][material]['actinide inventory'] = zaid_dict
            elif 'nonactinide' in line:
                break        
        
    def scrap_rx_params(self, line_list, time_step):
        "Grab all of the raw global reactor parameters assocaited with an specific time step"
        temp_dict = {}
        temp_dict[time_step] = {}
        time_dict = temp_dict[time_step]
        time_dict['keff'] = float(line_list[0].split(' ')[9])
        time_dict['keff_unc'] = float(line_list[0].split(' ')[-4])

        time_dict['prompt_removal_lifetime'] = (float(line_list[4].split(' ')[10]),
                                                float(line_list[4].split(' ')[-2]), 
                                                line_list[4].split(' ')[11])
        
        time_dict['avg_n_lethargy_fission'] = (float(line_list[6].split(' ')[9]), 
                                               line_list[6].split(' ')[10])
        time_dict['avg_n_energy_fission'] = (float(line_list[7].split(' ')[13]), 
                                             line_list[7].split(' ')[14])
        
        time_dict['thermal_fission_frac'] = float(line_list[10].split('%')[0][-5:])
        time_dict['epithermal_fission_frac'] = float(line_list[10].split('%')[1][-5:])
        time_dict['fast_fission_frac'] = float(line_list[10].split('%')[2][-5:])
        
        avg_n_per_absorption_fission = (float(line_list[12].split('=')[1][:13]),
                                        float(line_list[13].split('=')[1][:13]),
                                        float(line_list[15].split('=')[1][:6]))
        time_dict['avg_n_gen_per_abs_fission'] = avg_n_per_absorption_fission[0]
        time_dict['avg_n_gen_per_abs_all'] = avg_n_per_absorption_fission[1]
        time_dict['avg_n_gen_per_fission'] = avg_n_per_absorption_fission[2]

        time_dict['lifespan_esc'] = float(line_list[59].split('   ')[5])
        time_dict['lifespan_capt'] = float(line_list[59].split('   ')[6])
        time_dict['lifespan_fission'] = float(line_list[59].split('   ')[7])
        time_dict['lifespan_rem'] = float(line_list[59].split('   ')[8])
        time_dict['frac_esc'] = float(line_list[60].split('   ')[5])
        time_dict['frac_capt'] = float(line_list[60].split('   ')[6])
        time_dict['frac_fission'] = float(line_list[60].split('   ')[7])
        time_dict['frac_rem'] = float(line_list[60].split('   ')[8])

        try:
            time_dict['generation_time'] = (float(line_list[68].split('   ')[5]),
                                            float(line_list[68].split('   ')[7]),
                                            line_list[68].split('   ')[8])
        except ValueError:
            time_dict['generation_time'] = (float(line_list[68].split('   ')[6]),
                                            float(line_list[68].split('   ')[8]),
                                            line_list[68].split('   ')[9])
            

        time_dict['rossi-alpha'] = (float(line_list[69].split('   ')[4]),
                                    float(line_list[69].split('   ')[5]),
                                    line_list[69].split('   ')[6])
        
        time_dict['beta'] = (float(line_list[70].split('   ')[7]),
                             float(line_list[70].split('   ')[9]))
        
        precursor = {}
        for num, line in enumerate(line_list[77:83]):
            precursor[num+1] = {'beta-eff': float(line.split('     ')[3]),
                                 'beta-eff unc': float(line.split('     ')[4]),
                                 'energy': float(line.split('     ')[5]),
                                 'energy unc': float(line.split('     ')[6]),
                                 'energy_units': 'MeV',
                                 'lambda-i': float(line.split('     ')[7]),
                                 'lambda-i unc': float(line.split('     ')[8]),
                                 'lambda-i_units': '(/sec)',
                                 'half-life': float(line.split('     ')[9]),
                                 'half-life_units': '(sec)'}
        time_dict['precursors'] = precursor

        self.cycle_dict['step_{}'.format(time_step)]['rx_parameters'] = time_dict
