from __future__ import annotations

import json

import httpx
import pytest

from deepintshield import DeepintShieldBlockedError, ToolInvocation


def _responder(payload: dict):
    def handler(request: httpx.Request) -> httpx.Response:
        handler.last = request
        return httpx.Response(200, json=payload)

    handler.last = None
    return handler


def test_check_input_posts_input_stage(shield_factory, allow_response):
    handler = _responder(allow_response)
    shield = shield_factory(handler)
    result = shield.agent.check_input("hello there")
    body = json.loads(handler.last.content.decode())
    assert body["stage"] == "input"
    assert body["input"] == "hello there"
    assert result.allowed is True


def test_check_output_posts_output_stage(shield_factory, allow_response):
    handler = _responder(allow_response)
    shield = shield_factory(handler)
    shield.agent.check_output("assistant reply")
    body = json.loads(handler.last.content.decode())
    assert body["stage"] == "output"
    assert body["output"] == "assistant reply"


def test_evaluate_tool_without_server_label_uses_action_stage(shield_factory, allow_response):
    handler = _responder(allow_response)
    shield = shield_factory(handler)
    shield.agent.evaluate_tool(
        name="read_file",
        args={"path": "/tmp/x"},
        action_class="read",
    )
    body = json.loads(handler.last.content.decode())
    assert body["stage"] == "action"
    assert body["tool_name"] == "read_file"
    assert body["action_class"] == "read"
    assert "/tmp/x" in body["tool_input"]


def test_evaluate_tool_with_server_label_uses_mcp_stage(shield_factory, allow_response):
    handler = _responder(allow_response)
    shield = shield_factory(handler)
    shield.agent.evaluate_tool(
        invocation=ToolInvocation(
            tool_name="create_issue",
            tool_input={"title": "bug"},
            server_label="github-mcp",
            action_class="write",
        ),
    )
    body = json.loads(handler.last.content.decode())
    assert body["stage"] == "mcp"
    assert body["server_label"] == "github-mcp"


def test_evaluate_tool_requires_name_or_invocation(shield_factory, allow_response):
    shield = shield_factory(_responder(allow_response))
    with pytest.raises(ValueError):
        shield.agent.evaluate_tool()


def test_evaluate_tool_raises_on_block_by_default(shield_factory, block_response):
    shield = shield_factory(_responder(block_response))
    with pytest.raises(DeepintShieldBlockedError) as exc:
        shield.agent.evaluate_tool(name="drop_table", action_class="write")
    assert exc.value.stage == "action"
    assert exc.value.decision == "block"


def test_evaluate_tool_does_not_raise_when_disabled(shield_factory, block_response):
    shield = shield_factory(_responder(block_response))
    result = shield.agent.evaluate_tool(
        name="drop_table", action_class="write", raise_on_block=False
    )
    assert result.blocked is True


def test_tool_decorator_guards_before_calling_function(shield_factory, allow_response):
    handler = _responder(allow_response)
    shield = shield_factory(handler)

    @shield.agent.tool(action_class="write")
    def write_file(path: str, content: str) -> str:
        return f"wrote {content} to {path}"

    result = write_file("/tmp/hi", "hello")
    assert result == "wrote hello to /tmp/hi"
    body = json.loads(handler.last.content.decode())
    assert body["stage"] == "action"
    assert body["tool_name"] == "write_file"
    assert body["action_class"] == "write"


def test_tool_decorator_blocks_before_calling_function(shield_factory, block_response):
    shield = shield_factory(_responder(block_response))
    calls: list = []

    @shield.agent.tool(action_class="write")
    def rm_rf(path: str) -> None:
        calls.append(path)

    with pytest.raises(DeepintShieldBlockedError):
        rm_rf("/")
    assert calls == []
