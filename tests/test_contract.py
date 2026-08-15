import pytest
import json
import time

def test_flight_insurance(gl_client):
    contract_addr = "0x0D85870E741E6D086D6E32E54214AC1FfCD8DED8"
    
    # Example input/output from studionet
    pid = gl_client.read_contract(contract_addr, "get_policy_counter")
    print("Current Policy Counter:", pid)
    
    # We just do a basic view test to ensure it connects and returns a value without error
    assert pid is not None
