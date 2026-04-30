from __future__ import annotations

import json
import os
from typing import Any, Iterable, Mapping

import httpx

from .config import DEFAULT_BASE_URL, ShieldConfig
from .errors import DeepintShieldBlockedError, DeepintShieldError
from .types import GuardrailResult, RetrievedChunk, ToolInvocation


class DeepintShield:
    """
    Unified DeepintShield client.

    >>> shield = DeepintShield(virtual_key="sk-...")
    >>> openai = shield.openai()               # native openai.OpenAI pointed at the gateway
    >>> resp = shield.chat(model="gpt-4o-mini", messages=[...])
    >>> shield.rag.filter(query="...", chunks=[...])
    >>> shield.agent.evaluate_tool(name="read_file", args={"path": "/tmp"})
    """

    def __init__(
        self,
        virtual_key: str | None = None,
        *,
        timeout: float = 30.0,
        default_headers: Mapping[str, str] | None = None,
        app_name: str = "deepintshield",
        agent_name: str = "deepintshield-agent",
        requester: str = "sdk-user",
        requester_role: str = "member",
        persist: bool = True,
    ) -> None:
        self.base_url = DEFAULT_BASE_URL
        self.virtual_key = (virtual_key or "").strip() or None
        self.timeout = timeout
        self.default_headers = dict(default_headers or {})
        self.app_name = app_name
        self.agent_name = agent_name
        self.requester = requester
        self.requester_role = requester_role
        self.persist = persist
        self._client = httpx.Client(timeout=timeout)

        from .rag import RAGSurface
        from .agent import AgentSurface
        from .providers import ProviderRegistry

        self.rag = RAGSurface(self)
        self.agent = AgentSurface(self)
        self.providers = ProviderRegistry(self)

    # ─────────────────────────── constructors / context ──────────────────────

    @classmethod
    def from_env(cls) -> "DeepintShield":
        cfg = ShieldConfig.from_env()
        return cls(
            virtual_key=cfg.virtual_key,
            timeout=cfg.timeout,
            app_name=cfg.app_name,
            agent_name=cfg.agent_name,
            requester=cfg.requester,
            requester_role=cfg.requester_role,
            persist=cfg.persist,
        )

    @classmethod
    def from_config(cls, config: ShieldConfig) -> "DeepintShield":
        return cls(
            virtual_key=config.virtual_key,
            timeout=config.timeout,
            default_headers=config.default_headers,
            app_name=config.app_name,
            agent_name=config.agent_name,
            requester=config.requester,
            requester_role=config.requester_role,
            persist=config.persist,
        )

    def __enter__(self) -> "DeepintShield":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # ─────────────────────────── keys and headers ────────────────────────────

    def virtual_key_or_raise(self) -> str:
        if not self.virtual_key:
            raise DeepintShieldError("DEEPINTSHIELD_VIRTUAL_KEY is required")
        return self.virtual_key

    def api_key(self) -> str:
        return self.virtual_key_or_raise()

    def headers(self, extra: Mapping[str, str] | None = None) -> dict[str, str]:
        out = {"content-type": "application/json", **self.default_headers}
        if self.virtual_key:
            out["x-bf-vk"] = self.virtual_key
        if extra:
            out.update(dict(extra))
        return out

    # ─────────────────────────── provider endpoints ──────────────────────────

    def endpoint(self, provider: str) -> str:
        return f"{self.base_url}/{provider.strip('/')}"

    def openai_base_url(self) -> str:
        return self.endpoint("openai")

    def anthropic_base_url(self) -> str:
        return self.endpoint("anthropic")

    def bedrock_endpoint_url(self) -> str:
        return self.endpoint("bedrock")

    def genai_base_url(self) -> str:
        return self.endpoint("genai")

    def langchain_base_url(self) -> str:
        return self.endpoint("langchain")

    def litellm_base_url(self) -> str:
        return self.endpoint("litellm")

    def pydanticai_base_url(self) -> str:
        return self.endpoint("pydanticai")

    def openai_passthrough_base_url(self) -> str:
        return f"{self.base_url}/openai_passthrough/v1"

    def anthropic_passthrough_base_url(self) -> str:
        return f"{self.base_url}/anthropic_passthrough"

    def genai_passthrough_base_url(self) -> str:
        return f"{self.base_url}/genai_passthrough"

    # ─────────────────────────── provider shortcuts ──────────────────────────

    def openai(self, *, passthrough: bool = False, **kwargs: Any):
        from .providers.openai import build_client
        return build_client(self, passthrough=passthrough, **kwargs)

    def anthropic(self, *, passthrough: bool = False, **kwargs: Any):
        from .providers.anthropic import build_client
        return build_client(self, passthrough=passthrough, **kwargs)

    def bedrock(self, **kwargs: Any):
        from .providers.bedrock import build_client
        return build_client(self, **kwargs)

    def genai(self, *, passthrough: bool = False, **kwargs: Any):
        from .providers.genai import build_client
        return build_client(self, passthrough=passthrough, **kwargs)

    def langchain(self, model: str = "gpt-4o-mini", **kwargs: Any):
        from .providers.langchain import build_client
        return build_client(self, model=model, **kwargs)

    def langgraph(self):
        from .providers.langgraph import LangGraphShield
        return LangGraphShield(self)

    def litellm(self):
        from .providers.litellm import LiteLLMShield
        return LiteLLMShield(self)

    def pydanticai(self, model: str = "gpt-4o-mini", **kwargs: Any):
        from .providers.pydanticai import build_agent
        return build_agent(self, model=model, **kwargs)

    # ─────────────────────────── HTTP + guardrails ───────────────────────────

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Mapping[str, Any] | None = None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> dict[str, Any]:
        response = self._client.request(
            method=method,
            url=f"{self.base_url}{path}",
            headers=self.headers(extra_headers),
            json=json_body,
        )
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}
        if response.status_code >= 400:
            raise DeepintShieldError.from_response(response.status_code, payload)
        return payload

    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        stream: bool = False,
        extra_headers: Mapping[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Unified chat completion via the gateway OpenAI-compatible endpoint."""
        return self.request(
            "POST",
            "/v1/chat/completions",
            json_body={"model": model, "messages": messages, "stream": stream, **kwargs},
            extra_headers=extra_headers,
        )

    def evaluate_guardrail(
        self,
        *,
        stage: str,
        actor_type: str = "sdk_user",
        actor_id: str | None = None,
        actor_role: str | None = None,
        actor_customer_id: str | None = None,
        actor_team_id: str | None = None,
        model: str | None = None,
        provider: str | None = None,
        input: str | None = None,
        output: str | None = None,
        tool_input: str | None = None,
        server_label: str | None = None,
        tool_name: str | None = None,
        action_class: str | None = None,
        domains: list[str] | None = None,
        app_name: str | None = None,
        agent_name: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        persist: bool | None = None,
    ) -> GuardrailResult:
        body: dict[str, Any] = {
            "stage": stage,
            "actor_type": actor_type,
            "actor_id": actor_id or self.requester,
            "actor_role": actor_role or self.requester_role,
            "model": model,
            "provider": provider,
            "input": input,
            "output": output,
            "tool_input": tool_input,
            "server_label": server_label,
            "tool_name": tool_name,
            "action_class": action_class,
            "domains": domains or [],
            "app_name": app_name or self.app_name,
            "agent_name": agent_name or self.agent_name,
            "persist": self.persist if persist is None else persist,
        }
        if actor_customer_id:
            body["actor_customer_id"] = actor_customer_id
        if actor_team_id:
            body["actor_team_id"] = actor_team_id
        if metadata:
            body["metadata"] = dict(metadata)
        payload = self.request("POST", "/api/guardrails/evaluate", json_body=body)
        return GuardrailResult.from_response(stage, payload)

    def guard(
        self,
        *,
        stage: str,
        raise_on_block: bool = True,
        **kwargs: Any,
    ) -> GuardrailResult:
        """Evaluate a guardrail and optionally raise on block."""
        result = self.evaluate_guardrail(stage=stage, **kwargs)
        if raise_on_block and result.blocked:
            raise DeepintShieldBlockedError(
                f"DeepintShield blocked at stage={stage}: {result.reason or result.decision}",
                stage=stage,
                decision=result.decision,
                reason=result.reason,
                payload=result.raw,
            )
        return result
