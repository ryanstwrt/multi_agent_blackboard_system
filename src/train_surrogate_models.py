import sklearn
from sklearn import linear_model
from sklearn import gaussian_process
from sklearn.gaussian_process import kernels, GaussianProcessRegressor
from sklearn import neural_network
from sklearn import ensemble
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn import model_selection
from sklearn.pipeline import Pipeline
import numpy as np
import matplotlib.pyplot as plt
import skopt
from skopt import BayesSearchCV
from skopt.space import Categorical

class Surrogate_Models(object):
  """Class to hold the surrogate models"""
  def __init__(self):
    self.database = None
    self.ind_var = []
    self.obj_var = []

    self.random = None
    self.cv = 3
    self.number_iters = 50

    self.var_train = None
    self.var_test = None
    self.obj_test = None
    self.obj_train = None
    self.var_train_scaler = None
    self.var_test_scaler = None
    self.obj_train_scaler = None
    self.obj_test_scaler = None
    self.scaled_var_train = None
    self.scaled_var_test  = None
    self.scaled_obj_train = None
    self.scaled_obj_test  = None
    self.hyper_parameters = {}
    self.models = {}
    self._initialize_models()
    self._initialize_hyper_parameters()

  def _initialize_hyper_parameters(self):
      self.hyper_parameters['lr'] = None
      self.hyper_parameters['pr'] = {'poly__degree': (1,5)}
      self.hyper_parameters['gpr'] = {'alpha': (1e-11,1e-7,'log-uniform')}
      self.hyper_parameters['ann'] = {'hidden_layer_sizes': (2,200,'log-uniform'),
                                      'activation': Categorical(['tanh', 'relu', 'logistic']),
                                      'solver': Categorical(['lbfgs', 'sgd']),}
      self.hyper_parameters['rf'] = {'n_estimators': (10, 300, 'log-uniform')}

  def _initialize_models(self):
      self.models['lr']   = {'model': linear_model.LinearRegression()}
      self.models['pr']   = {'model': Pipeline([('poly', PolynomialFeatures()),
                                                ('linear', linear_model.LinearRegression(fit_intercept=False))])}
      self.models['gpr']  = {'model': gaussian_process.GaussianProcessRegressor(kernel=kernels.Matern(),optimizer='fmin_l_bfgs_b')}
      self.models['ann']  = {'model': neural_network.MLPRegressor(random_state=self.random, solver='lbfgs', activation='logistic')}
      self.models['rf']   = {'model': ensemble.RandomForestRegressor(random_state=self.random)}

  def _scale_data_sets(self):
    """Scale the training and test databases to have a mean of 0
    aids the fitting techniques"""
    self.var_train_scaler = StandardScaler()
    self.var_test_scaler = StandardScaler()
    self.obj_train_scaler = StandardScaler()
    self.obj_test_scaler = StandardScaler()
    self.var_train_scaler.fit(self.var_train)
    self.var_test_scaler.fit(self.var_test)
    self.obj_train_scaler.fit(self.obj_train)
    self.obj_test_scaler.fit(self.obj_test)

    self.scaled_var_train = self.var_train_scaler.transform(self.var_train)
    self.scaled_var_test  = self.var_test_scaler.transform(self.var_test)
    self.scaled_obj_train = self.obj_train_scaler.transform(self.obj_train)
    self.scaled_obj_test  = self.obj_test_scaler.transform(self.obj_test)

  def _split_database(self):
    """Split the database into seperate training and test sets"""
    self.var_train, self.var_test, self.obj_train, self.obj_test = model_selection.train_test_split(self.ind_var, self.obj_var, random_state=self.random)

  def _get_mse(self, model):
    "Get the Mean Square Error using the test database"
    from sklearn.metrics import mean_squared_error
    predict = [model.predict([val])[0] for val in self.scaled_var_test]
    known = self.scaled_obj_test
    return mean_squared_error(known, predict)

  def add_model(self, model_type, model):
      """Add a new model which is not pre-defined"""
      try:
          self.models[model_type] = {'model': model}
      except:
          print("Error: Model of type '{}' does not contain the correct format for function set_model. Please check sklearn for proper formatting.".format(model_type))

  def add_hyper_parameter(self, model_type, hyper_parameter):
      """Add a new hyper parameter to examine in the CV search space"""
      hyper_parameters = self.hyper_parameters[model_type]
      for hp in hyper_parameter:
           hyper_parameters[hp] = hyper_parameter[hp]

  def clear_surrogate_model(self):
      """Clear the the surrogate model of all values, but leave model types and hyper-parameters"""
      self.database = None
      self.ind_var = []
      self.obj_var = []
      self.var_train = None
      self.var_test = None
      self.obj_test = None
      self.obj_train = None
      self.var_train_scaler = None
      self.var_test_scaler = None
      self.obj_train_scaler = None
      self.obj_test_scaler = None
      self.scaled_var_train = None
      self.scaled_var_test  = None
      self.scaled_obj_train = None
      self.scaled_obj_test  = None

  def optimize_model(self, model_type, hp=None):
    """Update the model by optimizing it's hyper_parameters"""
    if hp:
        hyper_parameters = hp
    else:
        hyper_parameters = self.hyper_parameters[model_type]
    self.set_model(model_type, hyper_parameters)
    
  def return_best_model(self):
    """Return the best model, based on R-squared value"""
    best_model = None
    best_score = 0
    for k in self.models.keys():
        score = self.models[k]['score']
        if  score > best_score:
            best_score = score
            best_model = k
    return best_model



  def plot_validation_curve(self, model_type, hyper_parameter, hp_range):
      """Plot the validation curve for a model_type, given a particular hyper-parameter"""
      model = self.models[model_type]['model']

      train, test = model_selection.validation_curve(model, self.scaled_var_train, self.scaled_obj_train,
                                                     param_name=hyper_parameter, param_range=hp_range,n_jobs=20)
      tr_m = np.mean(train, axis = 1)
      tr_s = np.std(train, axis = 1)
      ts_m = np.mean(test, axis = 1)
      ts_s = np.std(test, axis = 1)

      plt.title("Validation Curve for {} with {}".format(model_type,hyper_parameter))
      plt.xlabel("{}".format(hyper_parameter))
      plt.ylabel("Score")
      lw = 2
      plt.plot(hp_range, tr_m, label="Training score", color="darkorange", lw=lw)
      plt.fill_between(hp_range, tr_m - tr_s, tr_m + tr_s, alpha=0.2, color="darkorange", lw=lw)
      plt.plot(hp_range, ts_m, label="Cross-validation score", color="navy", lw=lw)
      plt.fill_between(hp_range, ts_m - ts_s, ts_m + ts_s, alpha=0.2, color="navy", lw=lw)
      plt.legend(loc="best")
      plt.show()

  def set_model(self, model_type, hyper_parameters=None):
    """Create a surrogate model"""
    base_model = self.models[model_type]['model']
    hyper_model = self.models[model_type]['model']
    if hyper_parameters:
        hyper_model = BayesSearchCV(base_model, hyper_parameters, refit=True, n_jobs=16, 
                                    cv=self.cv, n_iter=self.number_iters, random_state=self.random)
        fit = hyper_model.fit(self.scaled_var_train,self.scaled_obj_train)
        r2_score = hyper_model.score(self.scaled_var_test,self.scaled_obj_test)
        mse_score = self._get_mse(hyper_model)
        self.models[model_type].update({'model': hyper_model, 
                                        'fit': fit, 
                                        'score': r2_score, 
                                        'mse_score': mse_score, 
                                        'hyper_parameters':hyper_model.best_params_, 
                                        'cv_results':hyper_model.cv_results_})
    else:
        fit = base_model.fit(self.scaled_var_train,self.scaled_obj_train)
        r2_score = base_model.score(self.scaled_var_test,self.scaled_obj_test)
        mse_score = self._get_mse(base_model)
        self.models[model_type].update({'fit': fit, 
                                        'score': r2_score, 
                                        'mse_score': mse_score, 
                                        'hyper_parameters': None, 
                                        'cv_results': None})

  def update_all_models(self):
    """update all models with new data"""
    for k in self.models.keys():
        if k != 'pr':
            self.set_model(k)

  def update_database(self, variables, objectives, database=None):
    """Update the database with new data
    Note: Make sure our ind and obj are staying together in the list"""
    
    if database:
        self.ind_var_names = variables
        self.dep_var_names = objectives
        for design in database.values():
            self.ind_var.append([design['independent variables'][x] for x in variables])
            self.obj_var.append([design['dependent variables'][x] for x in objectives])
    else:
        for var, obj in zip(variables, objectives):
            self.ind_var.append(var)
            self.obj_var.append(obj)
    self._split_database()
    self._scale_data_sets()  

  def predict(self, model_type, design, output='list'):
      """Return the value for a prediction using the trained set"""

      design = [[design[var] for var in self.ind_var_names]] if type(design) == dict else design
      scaled_var = self.var_train_scaler.transform(design)
      model = self.models[model_type]['fit']
      predictor = model.predict(scaled_var)
      inv_pred = self.obj_train_scaler.inverse_transform(predictor)
      obj = {name: inv_pred[0][num] for num, name in enumerate(self.dep_var_names)} if output == 'dict' else inv_pred  
      
      return obj   
    
  def update_model(self, model_type):
    """update a single model with new data"""
    self.set_model(model_type)