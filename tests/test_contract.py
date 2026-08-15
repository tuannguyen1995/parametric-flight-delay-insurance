import pytest
import json

# Contract address on studionet
CONTRACT_ADDRESS = "0xFD48923F775996c912933C30D692237e9fB616Aa"

class TestViewMethods:
    """Tests that can run against the deployed contract on studionet."""

    def test_get_policy_not_found(self, gl_client):
        """
        Querying non-existent policy should raise UserError.
        Expected behavior: Calling get_policy with a non-existent ID throws an error.
        """
        # Note: If gl_client intercepts the revert, it might raise an exception.
        # Otherwise, we check the returned error message.
        try:
            gl_client.read_contract(CONTRACT_ADDRESS, "get_policy", ["non_existent_policy_id_999"])
            pytest.fail("Expected UserError or Exception for non-existent policy")
        except Exception as e:
            assert "Policy not found" in str(e) or "UserError" in str(e) or "revert" in str(e).lower()

    def test_get_claim_not_found(self, gl_client):
        """
        Querying non-existent claim should raise UserError.
        Expected behavior: Calling get_claim with a non-existent ID throws an error.
        """
        try:
            gl_client.read_contract(CONTRACT_ADDRESS, "get_claim", ["non_existent_claim_id_999"])
            pytest.fail("Expected UserError or Exception for non-existent claim")
        except Exception as e:
            assert "Claim not found" in str(e) or "UserError" in str(e) or "revert" in str(e).lower()


class TestInputValidation:
    """
    Tests validating input constraints. These document expected behavior for write methods.
    Since we cannot easily execute GenVM write methods in a pure unit test without a full 
    local node, these act as integration test stubs defining the expected logic and constraints.
    """

    def test_buy_cover_success(self):
        """
        buy insurance, then verify via get_policy_counter and get_policy.
        
        Expected logic flow:
        1. User calls `buy_cover` with valid parameters:
           - msg.value (premium) > 0
           - coverage_amount >= premium
           - event_description length >= 10
           - booking_url, status_url, policy_url start with http:// or https://
        2. Contract increments `policy_counter` and stores the new Policy object.
        3. A subsequent read to `get_policy_counter` reflects the new count.
        4. A subsequent read to `get_policy` with the new ID returns the policy JSON 
           with status="ACTIVE".
        """
        pass

    def test_buy_cover_zero_premium(self):
        """
        premium = 0 should raise UserError.
        
        Expected logic flow:
        1. User calls `buy_cover` but sets `gl.message.value` to 0.
        2. Contract evaluates `premium == 0`.
        3. Contract raises `UserError("Premium must be > 0")`.
        """
        pass

    def test_buy_cover_invalid_url(self):
        """
        non-http URL should raise UserError.
        
        Expected logic flow:
        1. User calls `buy_cover` with `booking_url="ftp://my-ticket.com"`.
        2. Contract iterates over URLs and checks `_is_http()`.
        3. Contract raises `UserError("booking_url must be http(s)")`.
        """
        pass

    def test_buy_cover_short_description(self):
        """
        description < 10 chars should raise UserError.
        
        Expected logic flow:
        1. User calls `buy_cover` with `event_description="Short"`.
        2. Contract evaluates `len(event_description) < 10`.
        3. Contract raises `UserError("event_description too short")`.
        """
        pass

    def test_buy_cover_coverage_less_than_premium(self):
        """
        coverage < premium should raise UserError.
        
        Expected logic flow:
        1. User calls `buy_cover` with `msg.value=100` and `coverage_amount=50`.
        2. Contract evaluates `coverage_amount < premium`.
        3. Contract raises `UserError("coverage_amount should be >= premium")`.
        """
        pass

    def test_file_claim_success(self):
        """
        file a claim on active policy, verify claim state and policy locked to CLAIMED.
        
        Expected logic flow:
        1. User calls `file_claim(policy_id="1")` where policy "1" is ACTIVE.
        2. Contract increments `claim_counter`.
        3. Contract creates Claim object with status="PENDING" and stores it.
        4. Contract updates Policy "1" status to "CLAIMED".
        """
        pass

    def test_file_claim_policy_not_found(self):
        """
        claim on non-existent policy should raise UserError.
        
        Expected logic flow:
        1. User calls `file_claim(policy_id="9999")`.
        2. Contract checks if "9999" is in `policies_state`.
        3. Contract raises `UserError("Policy not found")`.
        """
        pass

    def test_file_claim_inactive_policy(self):
        """
        claim on already-claimed policy should raise UserError.
        
        Expected logic flow:
        1. User calls `file_claim(policy_id="1")` where policy "1" has status "CLAIMED" or "SETTLED".
        2. Contract checks `p.status != "ACTIVE"`.
        3. Contract raises `UserError("Policy not active")`.
        """
        pass
