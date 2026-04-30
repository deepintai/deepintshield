from __future__ import annotations

import json

import httpx
import pytest

from deepintshield import DeepintShield, DeepintShieldError
from deepintshield.config import DEFAULT_BASE_URL


def test_defaults_to_production_base_url():
    shield = DeepintShield(virtual_key="sk-bf-1")
    assert shield.base_url == DEFAULT_BASE_URL
    assert shield.virtual_key == "sk-bf-1"


def test_headers_include_virtual_key():
    shield = DeepintShield(virtual_key="sk-bf-1")
    headers = shield.headers()
    assert headers["x-bf-vk"] == "sk-bf-1"
    assert headers["content-type"] == "application/json"


def test_headers_extra_overrides_default():
    shield = DeepintShield(virtual_key="sk-bf-1", default_headers={"x-custom": "a"})
    headers = shield.headers(extra={"x-custom": "b"})
    assert headers["x-custom"] == "b"


def test_missing_virtual_key_raises():
    shield = DeepintShield()
    with pytest.raises(DeepintShieldError):
        shield.virtual_key_or_raise()


def test_endpoint_helpers_point_at_gateway_routes():
    shield = DeepintShield(virtual_key="sk-bf-1")
    assert shield.openai_base_url() == f"{DEFAULT_BASE_URL}/openai"
    assert shield.anthropic_base_url() == f"{DEFAULT_BASE_URL}/anthropic"
    assert shield.bedrock_endpoint_url() == f"{DEFAULT_BASE_URL}/bedrock"
    assert shield.genai_base_url() == f"{DEFAULT_BASE_URL}/genai"
    assert shield.langchain_base_url() == f"{DEFAULT_BASE_URL}/langchain"
    assert shield.litellm_base_url() == f"{DEFAULT_BASE_URL}/litellm"
    assert shield.pydanticai_base_url() == f"{DEFAULT_BASE_URL}/pydanticai"
    assert shield.openai_passthrough_base_url() == f"{DEFAULT_BASE_URL}/openai_passthrough/v1"
    assert shield.anthropic_passthrough_base_url() == f"{DEFAULT_BASE_URL}/anthropic_passthrough"
    assert shield.genai_passthrough_base_url() == f"{DEFAULT_BASE_URL}/genai_passthrough"


def test_from_env(monkeypatch):
    monkeypatch.setenv("DEEPINTSHIELD_VIRTUAL_KEY", "sk-bf-env")
    monkeypatch.setenv("DEEPINTSHIELD_APP_NAME", "test-app")
    shield = DeepintShield.from_env()
    assert shield.virtual_key == "sk-bf-env"
    assert shield.base_url == DEFAULT_BASE_URL
    assert shield.app_name == "test-app"


def test_context_manager_closes_http_client():
    with DeepintShield(virtual_key="sk-bf-1") as shield:
        assert isinstance(shield._client, httpx.Client)
    assert shield._client.is_closed


def test_request_raises_on_http_error(shield_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            json={"error": {"message": "boom"}},
        )

    shield = shield_factory(handler)
    with pytest.raises(DeepintShieldError) as exc:
        shield.request("POST", "/v1/chat/completions", json_body={})
    assert exc.value.status_code == 500
    assert "boom" in exc.value.message


def test_chat_posts_to_openai_compatible_endpoint(shield_factory):
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.content.decode()
        captured["vk"] = request.headers.get("x-bf-vk")
        return httpx.Response(200, json={"choices": [{"message": {"content": "hi"}}]})

    shield = shield_factory(handler)
    response = shield.chat(model="gpt-4o-mini", messages=[{"role": "user", "content": "hi"}])
    assert response["choices"][0]["message"]["content"] == "hi"
    assert captured["url"].endswith("/v1/chat/completions")
    assert captured["vk"] == "sk-bf-test"
    body = json.loads(captured["body"])
    assert body["model"] == "gpt-4o-mini"
    assert body["stream"] is False
