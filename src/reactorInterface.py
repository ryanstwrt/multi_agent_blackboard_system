from scipy.interpolate import interp1d as interp
import math

class reactorInterface(object):
    """The reactor interface is an easy way to explore different parameters within a specific reactor.
    This includes multiple methods to query the database."""
    def __init__(self, reactor):
        self.rx = reactor
        self.rx_name = self.rx.name.split('/')[-1]
        self.assemblies = {}
        self.rx_step_params = {}
        self.rx_base = {}
        self.rx_void = {}
        self.rx_temp = {}
        
        self.init_base()
        self.init_void()
        self.init_temp()
        self.init_burnup()
        self.density = 0.4014*self.rx['independent variables']['pu_content'][0]+15.47
                        
    def init_base(self):
        """Initialize the base core"""
        try:
            self.rx_base = self.rx[self.rx_name]['step_0']['rx_parameters']
        except KeyError:
            print("Warning: Core {} does not have a base core.".format(self.rx_name))

    def init_void(self):
        """Initialize the voided core"""
        try:
            self.rx_void = self.rx['{}_Void'.format(self.rx_name)]['step_0']['rx_parameters']
        except KeyError:
            print("Warning: Core {} does not have a voided core.".format(self.rx_name))            

    def init_temp(self):
        """Initialize the 600K core"""
        try:
            self.rx_temp = self.rx['{}_600K'.format(self.rx_name)]['step_0']['rx_parameters']
        except KeyError:
            print("Warning: Core {} does not have a 600K core.".format(self.rx_name))            
            
    def init_burnup(self):
        """Initialize burnup core(s)"""
        try:
            self.assemblies = {}
            self.rx_step_params = {}
            for step in self.rx['{}_BU'.format(self.rx_name)].keys():
                self.rx_step_params[step] = self.rx['{}_BU'.format(self.rx_name)][step]['rx_parameters']
                self.assemblies[step] = self.rx['{}_BU'.format(self.rx_name)][step]['assemblies']
        except KeyError:
            print("Warning: Core {} does not have a burnup core. No assemblies are present".format(self.rx_name))    
    
    def get_assembly_avg(self, time, param):
        """Get the average parameter of an assembly based on the time in the cycle"""
        assem_tot = 0
        for num, assem in enumerate(self.assemblies['step_0'].keys()):
            val = self.extrapolate_value('time', param, time, assem=assem)
            assem_tot += val
        return assem_tot/num

    def get_assembly_to_avg(self, time, param, assem):
        """Get the ratio of the given assembly paramter to the average value"""
        avg = self.get_assembly_avg(time, param)
        specific = self.extrapolate_value('time', param, time, assem=assem)
        return specific / avg  

    def get_assembly_min(self, time, param):
        """Get the min parameter of an assembly based on the time in the cycle"""
        assem_min = 1E100
        for assem in self.assemblies['step_0'].keys():
            val = self.extrapolate_value('time', param, time, assem=assem)
            if val < assem_min:
                assem_min = val
                assem_name = assem
        return (assem_name, assem_min)        
    
    def get_assembly_max(self, time, param):
        """Get the max parameter of an assembly based on the time in the cycle"""
        assem_max = 0
        for assem in self.assemblies['step_0'].keys():
            val = self.extrapolate_value('time', param, time, assem=assem)
            if val > assem_max:
                assem_max = val
                assem_name = assem 
        return (assem_name, assem_max) 
    
    def get_peak_to_average(self, time, param):
        """Get the peak to average value for a core"""
        avg = self.get_assembly_avg(time, param)
        peak_assem, peak_val = self.get_assembly_max(time, param)
        return (peak_assem, peak_val / avg)
    
    def get_doppler_coefficient(self):
        """Calculate the Doppler Coefficient for the reactor"""
        keff_low = self.rx_temp['keff'][0]
        keff_high = self.rx_base['keff'][0]
        doppler = (keff_high - keff_low) / (keff_high*keff_low) * 1E5
        return doppler
    
    def get_void_coefficient(self):
        """Calculate the void coefficient"""
        keff_base = self.rx_base['keff'][0]
        keff_void = self.rx_void['keff'][0]
        void = (keff_void - keff_base) / (keff_void*keff_base*99.99) *1E5
        return void
    
    def extrapolate_value(self, param1, param2, value, assem=False, fit_type='linear'):
        """Interpolate/extrapolate a value if needed."""
        params1 = self.get_bu_list(param1, assem)
        params2 = self.get_bu_list(param2, assem)
        #Try function is only here until the database is complete
        try:
            interp_func = interp(params1, params2, kind=fit_type, fill_value="extrapolate")
            return interp_func(value).flat[0] #flatten the array and return just the value
        except ValueError:
            pass

    def get_bu_list(self, param, assem):
        if 'time' in param:
            # Grab the first assembly to get the time
            p = [time_step['1002'][param][0] for time_step in self.assemblies.values()]
        elif assem:
            p = [time_step[assem][param][0] for time_step in self.assemblies.values()]
        else:
            p = [time_step[param][0] for time_step in self.rx_step_params.values()]
        return p
        
    def get_reactivity_swing(self, boc, eoc):
        """Get the reactivity swing (in pcm) between two times"""
        keff_init = self.extrapolate_value('time', 'keff', boc)
        keff_final = self.extrapolate_value('time', 'keff', eoc)
        return (keff_init - keff_final)/(keff_init) * 1E5

    def get_assembly_pu_mass(self):
        """Get the mass of a fuel assembly"""
        height = self.rx['independent variables']['height'][0]
        smear  = self.rx['independent variables']['smear'][0]
        pu_content = self.rx['independent variables']['pu_content'][0]
        inner_clad_radius = 0.358
        fuel_radius = math.sqrt(smear/100) * inner_clad_radius
        fuel_pin_mass = height * math.pi * fuel_radius ** 2 * self.density
        pu_pin_mass = fuel_pin_mass * pu_content
        assembly_mass = pu_pin_mass * 271 / 1000
        return assembly_mass
