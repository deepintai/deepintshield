from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import DeepintShield


def build_client(shield: "DeepintShield", *, passthrough: bool = False, **kwargs: Any):
    """Return a native ``openai.OpenAI`` client pre-wired to the DeepintShield gateway."""
    try:
        from openai import OpenAI
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install openai: pip install 'deepintshield[openai]'") from exc

    base_url = shield.openai_passthrough_base_url() if passthrough else shield.openai_base_url()
    return OpenAI(
        base_url=kwargs.pop("base_url", base_url),
        api_key=kwargs.pop("api_key", shield.api_key()),
        default_headers={**shield.headers(), **(kwargs.pop("default_headers", None) or {})},
        **kwargs,
    )
