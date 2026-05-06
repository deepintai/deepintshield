from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

DEFAULT_BASE_URL = "https://app.deepintshield.com"


def _normalize_base_url(value: str | None) -> str:
    if value is None:
        return DEFAULT_BASE_URL
    cleaned = value.strip().rstrip("/")
    return cleaned or DEFAULT_BASE_URL


@dataclass(slots=True)
class ShieldConfig:
    virtual_key: str = ""
    base_url: str = DEFAULT_BASE_URL
    timeout: float = 30.0
    app_name: str = "deepintshield"
    agent_name: str = "deepintshield-agent"
    requester: str = "sdk-user"
    requester_role: str = "member"
    persist: bool = True
    default_headers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.base_url = _normalize_base_url(self.base_url)

    @classmethod
    def from_env(cls) -> "ShieldConfig":
        return cls(
            virtual_key=(os.getenv("DEEPINTSHIELD_VIRTUAL_KEY") or "").strip(),
            base_url=_normalize_base_url(os.getenv("DEEPINTSHIELD_BASE_URL")),
            timeout=float(os.getenv("DEEPINTSHIELD_TIMEOUT", "30")),
            app_name=os.getenv("DEEPINTSHIELD_APP_NAME", "deepintshield"),
            agent_name=os.getenv("DEEPINTSHIELD_AGENT_NAME", "deepintshield-agent"),
            requester=os.getenv("DEEPINTSHIELD_REQUESTER", "sdk-user"),
            requester_role=os.getenv("DEEPINTSHIELD_REQUESTER_ROLE", "member"),
            persist=os.getenv("DEEPINTSHIELD_PERSIST", "true").lower() not in {"0", "false", "no"},
        )
