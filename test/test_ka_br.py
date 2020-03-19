import osbrain
from osbrain import run_nameserver
from osbrain import run_agent
import blackboard
import ka
import pandas as pd
import time
import os
import ka_br

def test_kabr_init():
    ns = run_nameserver()
    ka_b = run_agent(name='ka_br', base=ka_br.KaBr)
    assert ka_b.get_attr('bb') == None
    assert ka_b.get_attr('bb_lvl') == 0
    assert ka_b.get_attr('_entry') == None
    assert ka_b.get_attr('_entry_name') == None
    assert ka_b.get_attr('_writer_addr') == None
    assert ka_b.get_attr('_writer_alias') == None
    assert ka_b.get_attr('executor_addr') == None
    assert ka_b.get_attr('executor_alias') == None
    assert ka_b.get_attr('_trigger_response_addr') == None
    assert ka_b.get_attr('_trigger_response_alias') == 'trigger_response_ka_br'
    assert ka_b.get_attr('_trigger_publish_addr') == None
    assert ka_b.get_attr('_trigger_publish_alias') == None
    assert ka_b.get_attr('_trigger_val') == 0
    
    ns.shutdown()
    time.sleep(0.2)

def test_kabr_lvl2_init():
    ns = run_nameserver()
    ka_br2 = run_agent(name='ka_br_lvl2', base=ka_br.KaBr_lvl2)
    assert ka_br2.get_attr('bb') == None
    assert ka_br2.get_attr('bb_lvl') == 1
    assert ka_br2.get_attr('_entry') == None
    assert ka_br2.get_attr('_entry_name') == None
    assert ka_br2.get_attr('_writer_addr') == None
    assert ka_br2.get_attr('_writer_alias') == None
    assert ka_br2.get_attr('executor_addr') == None
    assert ka_br2.get_attr('executor_alias') == None
    assert ka_br2.get_attr('_trigger_response_addr') == None
    assert ka_br2.get_attr('_trigger_response_alias') == 'trigger_response_ka_br_lvl2'
    assert ka_br2.get_attr('_trigger_publish_addr') == None
    assert ka_br2.get_attr('_trigger_publish_alias') == None
    assert ka_br2.get_attr('_trigger_val') == 0
    assert ka_br2.get_attr('bb_lvl_read') == 2
    assert ka_br2.get_attr('desired_results') == None
    
    ns.shutdown()
    time.sleep(0.2)