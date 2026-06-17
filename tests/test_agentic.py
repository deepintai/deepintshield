from __future__ import annotations

import json

import httpx
import pytest

from deepintshield import GuardrailDenied


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path.endswith("/vk-credential-info"):
        return httpx.Response(200, json={"provider_type": "", "agent_configured": False})
    if path.endswith("/agentic-security/decide"):
        body = json.loads(request.content)
        tool = body["tool"]
        if tool == "deny.me":
            return httpx.Response(
                200,
                json={"verdict": "DENY", "decision_id": "d1", "reason": "nope", "policy_id": "p1"},
            )
        if tool == "mask.me":
            return httpx.Response(
                200, json={"verdict": "MASK", "decision_id": "d2", "obligations": ["mask:pii"]}
            )
        return httpx.Response(200, json={"verdict": "ALLOW", "decision_id": "d3"})
    return httpx.Response(404, json={})


def test_discovery(shield_factory):
    shield = shield_factory(_handler)
    info = shield.agentic.credential_info
    assert info.agent_configured is False
    assert info.provider_type == ""


def test_decide_allow_returns_decision(shield_factory):
    shield = shield_factory(_handler)
    decision = shield.agentic.decide(tool="something", args={"x": 1})
    assert decision.verdict.value == "ALLOW"
    assert decision.decision_id == "d3"


def test_tool_allow_runs_body(shield_factory):
    shield = shield_factory(_handler)

    @shield.agentic.tool("allow.me")
    def double(x: int) -> int:
        return x * 2

    assert double(21) == 42


def test_tool_deny_raises(shield_factory):
    shield = shield_factory(_handler)

    @shield.agentic.tool("deny.me")
    def run() -> str:
        return "ran"

    with pytest.raises(GuardrailDenied) as exc:
        run()
    assert exc.value.decision_id == "d1"
    assert exc.value.policy_id == "p1"


def test_tool_mask_redacts_pii_kwargs(shield_factory):
    shield = shield_factory(_handler)
    captured: dict = {}

    @shield.agentic.tool("mask.me")
    def report(**kwargs) -> str:
        captured.update(kwargs)
        return "ok"

    report(email="jane@example.com", name="Jane")
    assert captured["email"] == "***"  # masked
    assert captured["name"] == "Jane"  # untouched


def test_guardrail_denied_is_deepintshield_error(shield_factory):
    # Unified hierarchy: a single except DeepintShieldError catches PDP denials.
    from deepintshield import DeepintShieldError

    shield = shield_factory(_handler)

    @shield.agentic.tool("deny.me")
    def run() -> str:
        return "ran"

    with pytest.raises(DeepintShieldError):
        run()
