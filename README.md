# Parametric Flight & Event Delay Insurance

An Intelligent Contract primitive for GenLayer that implements parametric insurance for flights, events, and other time-bound activities. It autonomously adjudicates claims using web data and multi-sample LLM consensus.

## Purpose

Traditional delay insurance requires manual claim processing, which is slow and opaque. This Intelligent Contract automates the entire lifecycle:
1. **Buy Cover**: Users pay a premium and set a coverage amount, providing links to event tracking pages.
2. **File Claim**: Users or anyone can file a claim, locking the policy.
3. **Autonomous Adjudication**: The contract fetches live booking, status, and policy data from the web, and an LLM adjudicates the claim.
4. **Instant Settlement**: If approved, the payout is automatically transferred to the owner.

## Public API

### Write Methods
- `buy_cover(event_description: str, coverage_amount: bigint, booking_url: str, status_url: str, policy_url: str)`: Buy insurance cover. `msg.value` sets the premium.
- `file_claim(policy_id: str)`: Trigger a claim for an active policy. Optional `msg.value` acts as a spam-deterrent bond.
- `adjudicate(claim_id: str)`: Run the GenLayer consensus to validate the claim and settle the payout or refund.

### View Methods
- `get_policy(policy_id: str) -> str`: Returns policy details as JSON.
- `get_claim(claim_id: str) -> str`: Returns claim details as JSON.
- `get_policy_counter() -> bigint`
- `get_claim_counter() -> bigint`
- `get_treasury() -> str`

## How Consensus / The Validator Works

This contract uses a custom `validator_fn` that ensures agreement on the **meaning** of the decision, not just the format.

1. **Leader Execution**: The leader fetches the URL data and runs the LLM prompt twice (multi-sampling) to extract a `verdict`, `payout_pct`, and `confidence`.
2. **Validation**: The validator re-runs the exact same data-fetching and LLM prompts locally.
3. **Meaningful Agreement**: The validator does **not** simply check if the leader's output is valid JSON. Instead, it strictly enforces that its own independent `verdict`, `payout_pct`, and `confidence` exactly match the leader's. If the validator's LLM reaches a different conclusion based on the evidence, the transaction is rejected. This prevents malicious leaders from forging favorable claims.

## Deployment

The contract is deployed and actively testable on GenLayer's StudioNet.

- **Network:** `studionet`

### Example Input/Output

**Input:**
```python
# Reading the policy counter from the deployed contract
counter = gl_client.read_contract(
    "0xFD48923F775996c912933C30D692237e9fB616Aa",
    "get_policy_counter"
)
```

**Real Result:**
```python
> print(counter)
1
```
*(This confirms the contract is active and has successfully tracked at least 1 policy purchase on studionet).*
