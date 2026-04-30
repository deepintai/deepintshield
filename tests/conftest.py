from __future__ import annotations

from typing import Any, Callable

import httpx
import pytest

from deepintshield import DeepintShield


@pytest.fixture
def mock_transport() -> Callable[[Callable[[httpx.Request], httpx.Response]], httpx.MockTransport]:
    def make(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.MockTransport:
        return httpx.MockTransport(handler)

    return make


@pytest.fixture
def shield_factory(mock_transport):
    def make(handler: Callable[[httpx.Request], httpx.Response]) -> DeepintShield:
        shield = DeepintShield(virtual_key="sk-bf-test")
        shield._client = httpx.Client(transport=mock_transport(handler))
        return shield

    return make


@pytest.fixture
def allow_response() -> dict[str, Any]:
    return {"result": {"decision": "allow", "reason": ""}}


@pytest.fixture
def block_response() -> dict[str, Any]:
    return {"result": {"decision": "block", "reason": "policy violation"}}
