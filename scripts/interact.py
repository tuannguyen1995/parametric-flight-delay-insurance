import json
from genlayer import gl_client

# Contract address (replace with your deployed address)
CONTRACT_ADDRESS = "0xFD48923F775996c912933C30D692237e9fB616Aa"

# Initialize a client for the appropriate network (studionet by default)
client = gl_client.NetworkClient(network="studionet")

def read_contract_method(method_name: str, *args):
    """Helper to read a public view method from the contract."""
    try:
        result = client.read_contract(CONTRACT_ADDRESS, method_name, *args)
        print(f"{method_name}{args} => {result}")
        return result
    except Exception as e:
        print(f"Error calling {method_name}{args}: {e}")
        return None

if __name__ == "__main__":
    # Example calls
    read_contract_method("get_policy_counter")
    read_contract_method("get_claim_counter")
    # Fetch a specific policy (use an existing ID, e.g., "1")
    read_contract_method("get_policy", "1")
    # Fetch a specific claim (use an existing ID, e.g., "1")
    read_contract_method("get_claim", "1")
    # Get treasury address
    read_contract_method("get_treasury")
