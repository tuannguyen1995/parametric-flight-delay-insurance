import pytest
import json
import time

def test_flight_insurance(gl_client):
    contract_addr = "0xFD48923F775996c912933C30D692237e9fB616Aa"
    
    # Example input/output from studionet
    pid = gl_client.read_contract(contract_addr, "get_policy_counter")
    print("Current Policy Counter:", pid)
    
    # We just do a basic view test to ensure it connects and returns a value without error
    assert pid is not None
