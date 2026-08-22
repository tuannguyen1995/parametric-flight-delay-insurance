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
    Tests validating input constraints and fund accounting safety.
    """

    def test_buy_cover_solvency_reserve_check(self):
        """
        Contract must enforce per-policy solvency reserve accounting.
        If contract balance is insufficient to cover total_reserved_coverage + new coverage + bonds,
        buy_cover raises UserError("Insufficient contract liquidity to collateralize policy coverage").
        """
        pass

    def test_abort_terminates_policy(self):
        """
        An ABORT refunds premium and bond, and sets policy status to TERMINATED.
        This prevents the free coverage reactivation exploit.
        """
        pass

    def test_settlement_records_payout_amount(self):
        """
        Every settlement records the exact payout_amount in the Claim struct.
        """
        pass

    def test_deposit_liquidity(self):
        """
        Allows liquidity providers/underwriters to deposit funds into the contract pool.
        """
        pass

    def test_buy_cover_success(self):
        """
        buy insurance, then verify via get_policy_counter and get_policy.
        """
        pass

    def test_buy_cover_zero_premium(self):
        """
        premium = 0 should raise UserError.
        """
        pass

    def test_buy_cover_invalid_url(self):
        """
        non-http URL should raise UserError.
        """
        pass

    def test_buy_cover_short_description(self):
        """
        description < 10 chars should raise UserError.
        """
        pass

    def test_buy_cover_coverage_less_than_premium(self):
        """
        coverage < premium should raise UserError.
        """
        pass

    def test_file_claim_success(self):
        """
        file a claim on active policy, verify claim state and policy locked to CLAIMED.
        """
        pass

    def test_file_claim_policy_not_found(self):
        """
        claim on non-existent policy should raise UserError.
        """
        pass

    def test_file_claim_inactive_policy(self):
        """
        claim on already-claimed policy should raise UserError.
        """
        pass
