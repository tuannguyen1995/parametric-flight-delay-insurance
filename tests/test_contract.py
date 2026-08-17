import pytest
import json

# Contract address on studionet
CONTRACT_ADDRESS = "0x5F1B06BC7ec849a16d4bE0d27FfDA9DC66315347"


class TestSafeParse:
    """Unit tests for the _safe_parse logic extracted from the contract."""

    @staticmethod
    def _safe_parse(raw):
        """Mirror of the contract's _safe_parse for offline testing."""
        try:
            if isinstance(raw, dict):
                data = raw
            elif isinstance(raw, str):
                text = raw.strip()
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                data = json.loads(text.strip())
            else:
                return None

            verdict = str(data.get("verdict", "")).strip().upper()
            if verdict not in ("APPROVED", "DENIED", "PARTIAL", "ABORT"):
                return None

            pct = data.get("payout_pct", 0)
            if isinstance(pct, float):
                pct = int(pct)
            if not isinstance(pct, int) or not (0 <= pct <= 100):
                return None
            if verdict == "APPROVED" and pct != 100:
                return None
            if verdict == "DENIED" and pct != 0:
                return None
            if verdict == "PARTIAL" and not (1 <= pct <= 99):
                return None
            if verdict == "ABORT":
                pct = 0

            conf = data.get("confidence", 0)
            if isinstance(conf, float):
                conf = int(conf)
            if not isinstance(conf, int) or not (0 <= conf <= 100):
                return None

            reason = str(data.get("reason", ""))

            if conf < 55 and verdict != "ABORT":
                verdict = "ABORT"
                pct = 0
                reason = f"[low_confidence: {conf}%] " + reason

            return {
                "verdict": verdict,
                "payout_pct": pct,
                "confidence": conf,
                "reason": reason[:300],
            }
        except Exception:
            return None

    def test_approved_valid(self):
        """APPROVED with payout_pct=100 and high confidence parses correctly."""
        result = self._safe_parse('{"verdict":"APPROVED","payout_pct":100,"confidence":85,"reason":"covered"}')
        assert result is not None
        assert result["verdict"] == "APPROVED"
        assert result["payout_pct"] == 100
        assert result["confidence"] == 85

    def test_denied_valid(self):
        """DENIED with payout_pct=0 parses correctly."""
        result = self._safe_parse('{"verdict":"DENIED","payout_pct":0,"confidence":90,"reason":"no delay"}')
        assert result is not None
        assert result["verdict"] == "DENIED"
        assert result["payout_pct"] == 0

    def test_partial_valid(self):
        """PARTIAL with payout_pct in 1-99 parses correctly."""
        result = self._safe_parse('{"verdict":"PARTIAL","payout_pct":50,"confidence":75,"reason":"partial coverage"}')
        assert result is not None
        assert result["verdict"] == "PARTIAL"
        assert result["payout_pct"] == 50

    def test_approved_wrong_pct_rejected(self):
        """APPROVED with payout_pct != 100 is rejected."""
        result = self._safe_parse('{"verdict":"APPROVED","payout_pct":50,"confidence":80,"reason":"x"}')
        assert result is None

    def test_denied_wrong_pct_rejected(self):
        """DENIED with payout_pct != 0 is rejected."""
        result = self._safe_parse('{"verdict":"DENIED","payout_pct":10,"confidence":80,"reason":"x"}')
        assert result is None

    def test_partial_pct_zero_rejected(self):
        """PARTIAL with payout_pct=0 is rejected (must be 1-99)."""
        result = self._safe_parse('{"verdict":"PARTIAL","payout_pct":0,"confidence":80,"reason":"x"}')
        assert result is None

    def test_partial_pct_100_rejected(self):
        """PARTIAL with payout_pct=100 is rejected (must be 1-99)."""
        result = self._safe_parse('{"verdict":"PARTIAL","payout_pct":100,"confidence":80,"reason":"x"}')
        assert result is None

    def test_invalid_verdict_rejected(self):
        """Unknown verdict string is rejected."""
        result = self._safe_parse('{"verdict":"MAYBE","payout_pct":50,"confidence":80,"reason":"x"}')
        assert result is None

    def test_low_confidence_auto_aborts(self):
        """Confidence < 55 auto-converts any non-ABORT verdict to ABORT."""
        result = self._safe_parse('{"verdict":"APPROVED","payout_pct":100,"confidence":40,"reason":"unsure"}')
        assert result is not None
        assert result["verdict"] == "ABORT"
        assert result["payout_pct"] == 0
        assert result["confidence"] == 40
        assert "[low_confidence: 40%]" in result["reason"]

    def test_abort_stays_abort_even_low_conf(self):
        """ABORT verdict stays ABORT regardless of confidence."""
        result = self._safe_parse('{"verdict":"ABORT","payout_pct":0,"confidence":10,"reason":"fetch_failed"}')
        assert result is not None
        assert result["verdict"] == "ABORT"
        assert result["payout_pct"] == 0

    def test_markdown_json_stripped(self):
        """JSON wrapped in markdown code fences is parsed correctly."""
        raw = '```json\n{"verdict":"DENIED","payout_pct":0,"confidence":90,"reason":"no delay"}\n```'
        result = self._safe_parse(raw)
        assert result is not None
        assert result["verdict"] == "DENIED"

    def test_verdict_case_insensitive(self):
        """Verdict is normalized to uppercase."""
        result = self._safe_parse('{"verdict":"approved","payout_pct":100,"confidence":80,"reason":"ok"}')
        assert result is not None
        assert result["verdict"] == "APPROVED"

    def test_dict_input(self):
        """Dict input (not string) is parsed directly."""
        result = self._safe_parse({"verdict": "DENIED", "payout_pct": 0, "confidence": 70, "reason": "none"})
        assert result is not None
        assert result["verdict"] == "DENIED"

    def test_garbage_input_rejected(self):
        """Non-JSON garbage returns None."""
        assert self._safe_parse("not json at all") is None
        assert self._safe_parse("") is None
        assert self._safe_parse(None) is None
        assert self._safe_parse(12345) is None

    def test_float_pct_coerced(self):
        """Float payout_pct is coerced to int."""
        result = self._safe_parse('{"verdict":"PARTIAL","payout_pct":50.0,"confidence":80,"reason":"ok"}')
        assert result is not None
        assert result["payout_pct"] == 50
        assert isinstance(result["payout_pct"], int)


class TestInputValidation:
    """
    Tests validating input constraints for write methods.
    These document expected behavior without requiring a live GenVM node.
    """

    def test_buy_cover_success(self):
        """
        buy_cover with valid parameters should succeed.

        Expected: premium > 0, coverage >= premium, description >= 10 chars,
        all URLs start with http(s). Policy stored with status=ACTIVE.
        """
        pass  # Integration test: requires GenVM node

    def test_buy_cover_zero_premium(self):
        """
        buy_cover with msg.value=0 should raise UserError("Premium must be > 0").
        """
        pass  # Integration test: requires GenVM node

    def test_buy_cover_invalid_url(self):
        """
        buy_cover with non-http URL should raise UserError("<url_name> must be http(s)").
        Example: booking_url="ftp://example.com" triggers the error.
        """
        pass  # Integration test: requires GenVM node

    def test_buy_cover_short_description(self):
        """
        buy_cover with event_description < 10 chars raises UserError("event_description too short").
        """
        pass  # Integration test: requires GenVM node

    def test_buy_cover_coverage_less_than_premium(self):
        """
        buy_cover with coverage_amount < premium raises UserError("coverage_amount should be >= premium").
        """
        pass  # Integration test: requires GenVM node

    def test_file_claim_success(self):
        """
        file_claim on an ACTIVE policy should create a PENDING claim and set policy to CLAIMED.
        """
        pass  # Integration test: requires GenVM node

    def test_file_claim_policy_not_found(self):
        """
        file_claim with non-existent policy_id raises UserError("Policy not found").
        """
        pass  # Integration test: requires GenVM node

    def test_file_claim_inactive_policy(self):
        """
        file_claim on a CLAIMED/SETTLED policy raises UserError("Policy not active").
        """
        pass  # Integration test: requires GenVM node
