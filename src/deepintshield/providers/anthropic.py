from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import DeepintShield


def build_client(shield: "DeepintShield", *, passthrough: bool = False, **kwargs: Any):
    """Return a native ``anthropic.Anthropic`` client pointed at the gateway."""
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install anthropic: pip install 'deepintshield[anthropic]'") from exc

    base_url = shield.anthropic_passthrough_base_url() if passthrough else shield.anthropic_base_url()
    return anthropic.Anthropic(
        base_url=kwargs.pop("base_url", base_url),
        api_key=kwargs.pop("api_key", shield.api_key()),
        default_headers={**shield.headers(), **(kwargs.pop("default_headers", None) or {})},
        **kwargs,
    )
