from __future__ import annotations

from deepintshield import DeepintShieldBlockedError, DeepintShieldError


def test_from_response_prefers_error_message():
    err = DeepintShieldError.from_response(
        429, {"error": {"message": "rate limited"}}
    )
    assert err.status_code == 429
    assert err.message == "rate limited"


def test_from_response_falls_back_to_top_level_message():
    err = DeepintShieldError.from_response(500, {"message": "boom"})
    assert err.message == "boom"


def test_from_response_generates_default_when_missing():
    err = DeepintShieldError.from_response(404, {})
    assert "404" in err.message


def test_blocked_error_captures_stage_and_decision():
    err = DeepintShieldBlockedError(
        "blocked", stage="input", decision="block", reason="pii detected"
    )
    assert err.stage == "input"
    assert err.decision == "block"
    assert err.reason == "pii detected"
    assert isinstance(err, DeepintShieldError)
