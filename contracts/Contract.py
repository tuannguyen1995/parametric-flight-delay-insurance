# v0.2.16
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json
from dataclasses import dataclass

@allow_storage
@dataclass
class Policy:
    id: str
    owner: str
    event_description: str
    premium: bigint
    coverage_amount: bigint
    booking_url: str
    status_url: str
    policy_url: str
    status: str

@allow_storage
@dataclass
class Claim:
    id: str
    policy_id: str
    claimer: str
    bond: bigint
    status: str
    verdict: str
    payout_pct: int
    confidence: int
    reason: str

class Contract(gl.Contract):
    policies_state: TreeMap[str, Policy]
    claims_state: TreeMap[str, Claim]
    policy_counter: bigint
    claim_counter: bigint
    treasury_address: str

    def __init__(self, treasury_addr: str):
        self.policy_counter = bigint(0)
        self.claim_counter = bigint(0)
        self.treasury_address = treasury_addr.strip() if treasury_addr else ""
        self.policies_state = TreeMap()
        self.claims_state = TreeMap()
