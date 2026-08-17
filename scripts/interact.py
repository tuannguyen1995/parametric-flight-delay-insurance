import json
import genlayer_py

CONTRACT_ADDRESS = "0x5F1B06BC7ec849a16d4bE0d27FfDA9DC66315347"

account = genlayer_py.create_account()
client = genlayer_py.create_client(genlayer_py.studionet, account=account)

def read_contract_method(method_name: str, *args):
    """Helper to read a public view method from the contract."""
    try:
        kwargs = {"args": list(args)} if args else {}
        result = client.read_contract(address=CONTRACT_ADDRESS, function_name=method_name, **kwargs)
        print(f"{method_name}{args} => {result}")
        return result
    except Exception as e:
        print(f"Error calling {method_name}{args}: {e}")
        return None

if __name__ == "__main__":
    print(f"--- Interacting with deployed contract on studionet ({CONTRACT_ADDRESS}) ---")
    read_contract_method("get_policy_counter")
    read_contract_method("get_claim_counter")
    read_contract_method("get_treasury")
    read_contract_method("get_policy", "1")
    read_contract_method("get_claim", "1")
