import src.train_surrogate_models as tm
from sklearn.gaussian_process import kernels
import numpy as np
import sklearn
from sklearn import linear_model
from sklearn import datasets
import pandas as pd
import warnings
import skopt
from skopt.space import Categorical
warnings.filterwarnings("ignore")
from collections import Counter

def test_surrogate_model_init():
    sm = tm.Surrogate_Models()
    assert sm.database == None
    assert sm.ind_var == []
    assert sm.obj_var == []

    assert sm.random == None
    assert sm.cv == 3
    assert sm.number_iters == 50
    
    assert sm.var_test == None
    assert sm.var_train == None
    assert sm.obj_test == None
    assert sm.obj_train == None
    assert sm.var_test_scaler == None
    assert sm.var_train_scaler == None
    assert sm.obj_test_scaler == None
    assert sm.obj_train_scaler == None
    assert sm.scaled_var_train == None
    assert sm.scaled_var_test  == None
    assert sm.scaled_obj_train == None
    assert sm.scaled_obj_test  == None

    given_hp = {'lr': None,
                'pr': {'poly__degree': (1,5)},
                'gpr': {'alpha': (1e-11,1e-7,'log-uniform')},
                'ann': {'hidden_layer_sizes': (2,200,'log-uniform'),
                        'activation': Categorical(['tanh', 'relu', 'logistic']),
                        'solver': Categorical(['lbfgs', 'sgd'])},
                'rf': {'n_estimators': (10,300, 'log-uniform')}}
    for m in ['lr', 'pr', 'gpr', 'ann', 'rf']:
        assert m in sm.models.keys()
        assert m in sm.hyper_parameters.keys()
        assert sm.hyper_parameters[m] == given_hp[m]

def test_train_test_split():
    sm = tm.Surrogate_Models()
    sm.ind_var, sm.obj_var = datasets.load_linnerud(return_X_y=True)
    sm._split_database()
    assert len(sm.var_test) == 5
    assert len(sm.var_train) == 15
    assert len(sm.obj_test) == 5
    assert len(sm.obj_train) == 15

def equal_ignore_order(a, b):
    """ Use only when elements are neither hashable nor sortable! """
    unmatched = list(b)
    for element in a:
        try:
            unmatched.remove(element)
        except ValueError:
            return element
    return True

def test_update_database():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    sm.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
    ind_var_given = [[ 11, 230,  80,], [  6,  70,  31,], [  2, 110,  43,], [ 14, 215, 105,], [ 15, 225,  73,], [  4,  60,  25,], [ 12, 105,  37,], [ 12, 101, 101,], [ 13, 210, 115,], [ 13, 155,  58,], [  2, 110,  60,], [ 15, 200,  40,], [  6, 125,  40,], [  8, 101,  38,], [ 17, 120,  38,]]
    obj_var_given = [[157,  32,  52,], [193,  36,  46,], [138,  33,  68,], [154,  34,  64,], [156,  33,  54,], [176,  37,  54,], [162,  35,  62,], [193,  38,  58,], [166,  33,  52,], [189,  35,  46,], [189,  37,  52,], [176,  31,  74,], [167,  34,  60,], [211,  38,  56,], [169,  34,  50,]]
    np.testing.assert_array_equal(sm.var_train, ind_var_given)
    np.testing.assert_array_equal(sm.obj_train, obj_var_given)
    assert len(sm.var_test) == 5
    assert len(sm.obj_test) == 5

    sm.update_database([[ 12, 250,  85,],[ 12, 250,  85,],], [[165,  33,  57,],[165,  33,  57,]])
    assert len(sm.var_train) == 16
    assert len(sm.obj_train) == 16
    assert len(sm.var_test) == 6
    assert len(sm.obj_test) == 6

def test_update_database_dict():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    test_dict = {}
    
    i = 0
    for ind, obj in zip(variables, objectives):
        test_dict['core {}'.format(i)] = {'independent variables': {}, 'dependent variables': {}}
        test_dict['core {}'.format(i)]['independent variables'] = {'a': ind[0], 'b': ind[1], 'c': ind[2]}
        test_dict['core {}'.format(i)]['dependent variables'] = {'d': obj[0], 'e': obj[1], 'f': obj[2]}
        i +=1
    
    sm.update_database(['a','b','c'], ['d','e','f'], database=test_dict)
    ind_var_given = [[ 11, 230,  80,], [  6,  70,  31,], [  2, 110,  43,], [ 14, 215, 105,], [ 15, 225,  73,], [  4,  60,  25,], [ 12, 105,  37,], [ 12, 101, 101,], [ 13, 210, 115,], [ 13, 155,  58,], [  2, 110,  60,], [ 15, 200,  40,], [  6, 125,  40,], [  8, 101,  38,], [ 17, 120,  38,]]
    obj_var_given = [[157,  32,  52,], [193,  36,  46,], [138,  33,  68,], [154,  34,  64,], [156,  33,  54,], [176,  37,  54,], [162,  35,  62,], [193,  38,  58,], [166,  33,  52,], [189,  35,  46,], [189,  37,  52,], [176,  31,  74,], [167,  34,  60,], [211,  38,  56,], [169,  34,  50,]]
    np.testing.assert_array_equal(sm.var_train, ind_var_given)
    np.testing.assert_array_equal(sm.obj_train, obj_var_given)
    assert len(sm.var_test) == 5
    assert len(sm.obj_test) == 5

    test_dict = {'core 100': {'independent variables': {'a':12,'b':250,'c':85}, 'dependent variables': {'d': 165,'e':33,'f': 57}},
                 'core 101': {'independent variables': {'a':12,'b':250,'c':85}, 'dependent variables': {'d': 165,'e':33,'f': 57}}}
    sm.update_database(['a','b','c'], ['d','e','f'], database=test_dict)
    assert len(sm.var_train) == 16
    assert len(sm.obj_train) == 16
    assert len(sm.var_test) == 6
    assert len(sm.obj_test) == 6
    
def test_clear_database():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    sm.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
    ind_var_given = [[ 11, 230,  80,], [  6,  70,  31,], [  2, 110,  43,], [ 14, 215, 105,], [ 15, 225,  73,], [  4,  60,  25,], [ 12, 105,  37,], [ 12, 101, 101,], [ 13, 210, 115,], [ 13, 155,  58,], [  2, 110,  60,], [ 15, 200,  40,], [  6, 125,  40,], [  8, 101,  38,], [ 17, 120,  38,]]
    obj_var_given = [[157,  32,  52,], [193,  36,  46,], [138,  33,  68,], [154,  34,  64,], [156,  33,  54,], [176,  37,  54,], [162,  35,  62,], [193,  38,  58,], [166,  33,  52,], [189,  35,  46,], [189,  37,  52,], [176,  31,  74,], [167,  34,  60,], [211,  38,  56,], [169,  34,  50,]]
    np.testing.assert_array_equal(sm.var_train, ind_var_given)
    np.testing.assert_array_equal(sm.obj_train, obj_var_given)
    sm.clear_surrogate_model()

    assert sm.database == None
    assert sm.ind_var == []
    assert sm.obj_var == []
    assert sm.random == 57757
    assert sm.var_test == None
    assert sm.var_train == None
    assert sm.obj_test == None
    assert sm.obj_train == None
    assert sm.var_test_scaler == None
    assert sm.var_train_scaler == None
    assert sm.obj_test_scaler == None
    assert sm.obj_train_scaler == None
    assert sm.scaled_var_train == None
    assert sm.scaled_var_test  == None
    assert sm.scaled_obj_train == None
    assert sm.scaled_obj_test  == None

def test_scale_datasets():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    sm.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))

    assert sm.var_train_scaler.mean_.all() == np.array([[10,         142.46666667,  58.93333333]]).all()
    assert sm.var_train_scaler.var_.all() == np.array([[22.8,        3171.71555556,  795.92888889]]).all()
    assert sm.var_test_scaler.mean_.all() == np.array([[7.8, 154.8, 104.4]]).all()
    assert sm.var_test_scaler.var_.all() == np.array([[34.16, 5246.16, 6053.44]]).all()
    assert sm.obj_train_scaler.mean_.all() == np.array([[173.06666667,  34.66666667,  56.53333333]]).all()
    assert sm.obj_train_scaler.var_.all() == np.array([[341.79555556,   4.35555556,  58.38222222]]).all()
    assert sm.obj_test_scaler.mean_.all() == np.array([[195.2,  37.6,  54.8]]).all()
    assert sm.obj_test_scaler.var_.all() == np.array([[923.76,  19.44,  20.16]]).all()

model = tm.Surrogate_Models()
variables, objectives = datasets.load_linnerud(return_X_y=True)
model.random = 57757
model.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
model._initialize_models()

def test_initialize_models():
    models = model.models
    assert 'lr' in models
    assert 'pr' in models
    assert 'gpr' in models
    assert 'ann' in models
    assert 'rf' in models

def test_linear_model():
    model.set_model('lr')
    linear_model = model.models['lr']
    assert linear_model['model'] != None
    assert linear_model['fit'] != None
    assert linear_model['score'] == 0.3546058200687729
    assert linear_model['mse_score'] == 0.6453941799312272

def test_poly_model():
    model.set_model('pr')
    poly_model = model.models['pr']
    assert poly_model['model'] != None
    assert poly_model['fit'] != None
    assert poly_model['score'] == -0.22259110245070493
    assert poly_model['mse_score'] == 1.2225911024507052

def test_grp_model():
    model.set_model('gpr')
    gpr_model = model.models['gpr']
    assert gpr_model['model'] != None
    assert gpr_model['fit'] != None
    assert gpr_model['score'] == 0.0
    assert gpr_model['mse_score'] == 1.0

def test_ann_model():
    model.set_model('ann')
    ann_model = model.models['ann']
    assert ann_model['model'] != None
    assert ann_model['fit'] != None
    assert ann_model['score'] == -0.8124181759959282
    assert ann_model['mse_score'] == 1.8124181759959297

def test_rf_model():
    model.set_model('rf')
    rf_model = model.models['rf']
    assert rf_model['model'] != None
    assert rf_model['fit'] != None
    assert rf_model['score'] == 0.1770111582876811
    assert rf_model['mse_score'] == 0.822988841712319

def test_add_model():
    ridge = linear_model.Ridge()
    model.add_model('ridge', ridge)
    assert 'ridge' in model.models

def test_set_added_model():
    ridge = linear_model.Ridge()
    model.add_model('ridge', ridge)
    model.set_model('ridge')
    ridge_model = model.models['ridge']
    assert ridge_model['model'] != None
    assert ridge_model['fit'] != None
    assert ridge_model['score'] == 0.3602889061502321

def test_add_hyper_parameter_update():
    assert model.hyper_parameters['ann'] == {'hidden_layer_sizes': (2,200,'log-uniform'),
                        'activation': Categorical(['tanh', 'relu', 'logistic']),
                        'solver': Categorical(['lbfgs', 'sgd'])}
    model.add_hyper_parameter('ann', {'hidden_layer_sizes': (25,125)})
    assert model.hyper_parameters['ann'] == {'hidden_layer_sizes': (25,125),
            'activation': Categorical(['tanh', 'relu', 'logistic']),
            'solver': Categorical(['lbfgs', 'sgd'])}

def test_add_hyper_parameter_new():
    assert model.hyper_parameters['ann'] == {'hidden_layer_sizes': (25,125),
                        'activation': Categorical(['tanh', 'relu', 'logistic']),
                        'solver': Categorical(['lbfgs', 'sgd'])}
    model.add_hyper_parameter('ann', {'learning_rate': ('constant', 'adaptive')})
    assert model.hyper_parameters['ann'] == {'hidden_layer_sizes': (25,125),
                        'activation': Categorical(['tanh', 'relu', 'logistic']),
                        'solver': Categorical(['lbfgs', 'sgd']),
                        'learning_rate': ('constant', 'adaptive')}

def test_add_hyper_parameter_poly():
    assert model.hyper_parameters['pr'] == {'poly__degree': (1,5)}
    model.add_hyper_parameter('pr', {'poly__degree': (3,5,8)})
    assert model.hyper_parameters['pr'] == {'poly__degree': (3,5,8)}

def test_update_model():
    model.set_model('lr')
    linear_model = model.models['lr']
    assert linear_model['score'] == 0.3546058200687729
    model.update_database([[ 15, 150,  65,],[ 13, 550,  90,],], [[205,  38,  47,],[145,  32,  77,]])
    model.update_model('lr')
    linear2_model = model.models['lr']
    assert linear2_model['score'] == -0.5475314374931772

def test_update_all_models():
    model2 = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    model2.random = 57757
    model2.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
    model2._initialize_models()

    model_list = ['lr', 'pr', 'gpr', 'ann', 'rf']
    model_scores = [0.3546058200687729, -0.2225911024507033, 0.0, -0.8124181759959282, 0.1770111582876811, ]
    model_scores2 = [-0.5475314374931772, -0.2225911024507033,  0.0, -1.0503029979397898, 0.033954767107108486, ]
    for model_type in model_list:
        model2.set_model(model_type)
    for model_type, model_score in zip(model_list, model_scores):
        assert np.allclose(model2.models[model_type]['score'], model_score, rtol=1e-05)
        
    model2.update_database([[ 15, 150,  65,],[ 13, 550,  90,],], [[205,  38,  47,],[145,  32,  77,]])
    model2.update_all_models()
    for model_type, model_score in zip(model_list, model_scores2):
        assert np.allclose(model2.models[model_type]['score'], model_score, rtol=1e-5)

# TODO: Add tests for optimizing all regression techniques        

def test_optimize_pr():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    sm.cv = 3
    sm.number_iters = 3
    sm.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
    sm._initialize_models()

    sm.set_model('pr')
    poly_model = sm.models['pr']
    assert poly_model['score'] == -0.22259110245070493
    assert poly_model['mse_score'] == 1.2225911024507052
    hyper_parameters = {'poly__degree': (2,4)}
    sm.optimize_model('pr', hyper_parameters)
    optimized_pr_model = sm.models['pr']
    assert optimized_pr_model['score'] == -9.2227093574984
    assert optimized_pr_model['mse_score'] == 10.222709357498402
    assert optimized_pr_model['hyper_parameters'] == {'poly__degree': 4}
    
def test_optimize_ann():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    sm.cv = 3
    sm.number_iters = 3
    sm.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
    sm._initialize_models()

    sm.set_model('ann')
    ann_model = sm.models['ann']
    assert ann_model['score'] == -0.8124181759959282
    assert ann_model['mse_score'] == 1.8124181759959297
    hyper_parameters = {'hidden_layer_sizes': (10,25)}
    sm.optimize_model('ann', hyper_parameters)
    optimized_ann_model = sm.models['ann']
    assert optimized_ann_model['score'] == -1.3392896377969676
    assert optimized_ann_model['mse_score'] == 2.339289637796968
    assert optimized_ann_model['hyper_parameters'] == {'hidden_layer_sizes': 15}

def test_return_best_model():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    sm.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
    sm._initialize_models()
    model_list = ['lr', 'pr', 'gpr', 'ann', 'rf']
    for model_type in model_list:
        sm.set_model(model_type)
        print(model_type, sm.models[model_type]['score'])
    best_model = sm.return_best_model()
    assert best_model == 'lr'

def test_predict():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    sm.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
    sm._initialize_models()
    sm.set_model('ann')
    pred = sm.predict('ann', [[11, 230, 80]])
    assert np.ndarray.tolist(pred) == [[158.64501384843928, 31.922021142788957, 52.673575073769754]]
    
def test_predict_dict():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    test_dict = {}
    
    i = 0
    for ind, obj in zip(variables, objectives):
        test_dict['core {}'.format(i)] = {'independent variables': {}, 'dependent variables': {}}
        test_dict['core {}'.format(i)]['independent variables'] = {'a': ind[0], 'b': ind[1], 'c': ind[2]}
        test_dict['core {}'.format(i)]['dependent variables'] = {'d': obj[0], 'e': obj[1], 'f': obj[2]}
        i +=1
    
    sm.update_database(['a','b','c'], ['d','e','f'], database=test_dict)
    sm._initialize_models()
    sm.set_model('ann')
    pred = sm.predict('ann', {'a':11, 'b':230, 'c':80}, output='dict')
    assert pred == {'d':158.64501384843928, 'e':31.922021142788957, 'f':52.673575073769754}


def test_mse():
    sm = tm.Surrogate_Models()
    variables, objectives = datasets.load_linnerud(return_X_y=True)
    sm.random = 57757
    sm.update_database(np.ndarray.tolist(variables), np.ndarray.tolist(objectives))
    sm._initialize_models()
    model_list = ['lr', 'pr',  'gpr', 'ann', 'rf']
    mse_val = [0.6453941799312272, 1.2225911024507052, 1.0, 1.8124181759959297, 0.822988841712319]
    for known_mse, model_type in zip(mse_val, model_list):
        sm.set_model(model_type)
        assert sm._get_mse(sm.models[model_type]['model']) == known_mse
