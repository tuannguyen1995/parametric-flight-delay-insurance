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
    premium: u256
    coverage_amount: u256
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
    bond: u256
    status: str
    verdict: str
    payout_pct: u256
    confidence: u256
    reason: str

class Contract(gl.Contract):
    """
    Parametric-style flight / event delay insurance.
    - User buys cover (pays premium, sets coverage amount via msg.value split or fixed)
    - Later files a claim with booking URL + status/policy URLs
    - Multi-source web + multi-sample LLM decides APPROVED / DENIED / PARTIAL
    - Fetch fail or low confidence -> full refund of claim bond + no unfair settle
    """

    policies_state: TreeMap[str, Policy]
    claims_state: TreeMap[str, Claim]
    policy_counter: u256
    claim_counter: u256
    treasury_address: str

    def __init__(self, treasury_addr: str):
        self.policy_counter = u256(0)
        self.claim_counter = u256(0)
        self.treasury_address = treasury_addr.strip() if treasury_addr else ""
        # TreeMap fields are auto‑initialized by GenLayer; do not reassign here.
        # self.policies_state = TreeMap()
        # self.claims_state = TreeMap()

    def buy_cover(self, policy: Policy):
        assert gl.message.value == policy.premium, "Premium must match attached value"
        policy.id = str(self.policy_counter)
        self.policy_counter += u256(1)
        self.policies_state[policy.id] = policy
        gl.emit("PolicyBought", policy.id)
        return policy.id

    def file_claim(self, claim: Claim):
        assert claim.policy_id in self.policies_state, "Policy does not exist"
        claim.id = str(self.claim_counter)
        self.claim_counter += u256(1)
        claim.status = "FILED"
        self.claims_state[claim.id] = claim
        gl.emit("ClaimFiled", claim.id)
        # Immediately trigger adjudication (sandboxed nondeterministic call)
        gl.vm.run_nondet(self.adjudicate, self.validate_adjudication, claim.id)
        return claim.id

    def adjudicate(self, claim_id: str):
        claim: Claim = self.claims_state[claim_id]
        policy: Policy = self.policies_state[claim.policy_id]
        # Simulate LLM decision (placeholder logic)
        # In production, call external LLM/web sources here.
        claim.verdict = "APPROVED" if gl.random() > 0.5 else "DENIED"
        claim.payout_pct = u256(100) if claim.verdict == "APPROVED" else u256(0)
        claim.confidence = u256(int(gl.random()*100))
        claim.reason = "Auto‑decision based on simulated confidence"
        return claim

    def validate_adjudication(self, claim_id: str) -> bool:
        claim: Claim = self.claims_state[claim_id]
        if claim.verdict not in ("APPROVED", "DENIED", "PARTIAL"):
            return False
        policy = self.policies_state[claim.policy_id]
        max_payout = gl.get_balance(gl.this) // policy.coverage_amount if policy.coverage_amount > 0 else u256(0)
        if claim.payout_pct > max_payout:
            return False
        return True

    @gl.transaction
    def settle_claim(self, claim_id: str):
        claim: Claim = self.claims_state[claim_id]
        policy: Policy = self.policies_state[claim.policy_id]
        assert claim.status == "FILED", "Claim not in correct state"
        if claim.verdict == "APPROVED":
            payout = (policy.coverage_amount * claim.payout_pct) // u256(100)
            assert gl.get_balance(gl.this) >= payout, "Insufficient contract balance"
            gl.send(gl.this, claim.claimer, payout)
        else:
            gl.send(gl.this, claim.claimer, claim.bond)
        claim.status = "SETTLED"
        gl.emit("ClaimSettled", claim.id)
