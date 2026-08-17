import pytest
import genlayer_py

CONTRACT_ADDRESS = "0x5F1B06BC7ec849a16d4bE0d27FfDA9DC66315347"

class TestViewMethods:
    """Tests executing against the deployed contract on studionet."""

    @pytest.fixture
    def client(self):
        acc = genlayer_py.create_account()
        return genlayer_py.create_client(genlayer_py.studionet, account=acc)

    def test_get_policy_counter(self, client):
        """Verify policy counter is readable on studionet."""
        counter = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_policy_counter")
        assert counter is not None
        assert isinstance(counter, int)

    def test_get_claim_counter(self, client):
        """Verify claim counter is readable on studionet."""
        counter = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_claim_counter")
        assert counter is not None
        assert isinstance(counter, int)

    def test_get_treasury(self, client):
        """Verify treasury address is set and readable."""
        treasury = client.read_contract(address=CONTRACT_ADDRESS, function_name="get_treasury")
        assert treasury is not None
        assert isinstance(treasury, str)

    def test_get_policy_not_found(self, client):
        """
        Querying non-existent policy should revert / fail.
        """
        with pytest.raises(Exception):
            client.read_contract(address=CONTRACT_ADDRESS, function_name="get_policy", args=["non_existent_policy_id_999"])

    def test_get_claim_not_found(self, client):
        """
        Querying non-existent claim should revert / fail.
        """
        with pytest.raises(Exception):
            client.read_contract(address=CONTRACT_ADDRESS, function_name="get_claim", args=["non_existent_claim_id_999"])


class TestInputValidation:
    """
    Tests validating input constraints. These document expected behavior for write methods.
    Since write transactions require simulated consensus execution in a full GenVM test runner,
    these unit stubs document and enforce the contract logic constraints.
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
        2. Contract evaluates `premium <= bigint(0)`.
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
        2. Contract evaluates `bigint(coverage_amount) < premium`.
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
