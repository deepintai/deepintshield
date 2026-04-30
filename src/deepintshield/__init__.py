"""
DeepintShield — unified Python SDK.

Quick start
-----------

    from deepintshield import DeepintShield

    shield = DeepintShield(virtual_key="sk-...")
    openai_client = shield.openai()
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "hello"}],
    )

All traffic is routed to ``https://app.deepintshield.com``.
"""

from .client import DeepintShield
from .config import DEFAULT_BASE_URL, ShieldConfig
from .errors import DeepintShieldBlockedError, DeepintShieldError
from .rag import allowed_chunk_ids, build_chunk, filter_chunks
from .types import (
    NON_BLOCKING_DECISIONS,
    GuardrailDecision,
    GuardrailResult,
    GuardrailStage,
    RetrievedChunk,
    ToolInvocation,
)
from .version import __version__

# Backwards-compatible alias.
DeepintShieldClient = DeepintShield

__all__ = [
    "__version__",
    "DEFAULT_BASE_URL",
    "DeepintShield",
    "DeepintShieldClient",
    "DeepintShieldBlockedError",
    "DeepintShieldError",
    "GuardrailDecision",
    "GuardrailResult",
    "GuardrailStage",
    "NON_BLOCKING_DECISIONS",
    "RetrievedChunk",
    "ShieldConfig",
    "ToolInvocation",
    "allowed_chunk_ids",
    "build_chunk",
    "filter_chunks",
]
