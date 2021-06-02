import src.utils.benchmark_utils as bu
import numpy as np

def test_get_indicator():
    pf = np.array([[0.25, 0.5, 0.75]])
    val = bu.get_indicator('gd', 'asdf', pf)
    assert val == 0
    val = bu.get_indicator('gd', 're31', pf)
    assert round(val,3) == 21.755

def test_get_pf():
    pf = bu.get_re_pf('re31')
    assert len(pf) == 1500