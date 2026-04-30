from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import DeepintShield


def build_client(shield: "DeepintShield", *, passthrough: bool = False, **kwargs: Any):
    """Return a native ``google.genai.Client`` pointed at the gateway."""
    try:
        from google import genai
        from google.genai.types import HttpOptions
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install google-genai: pip install 'deepintshield[genai]'") from exc

    base_url = shield.genai_passthrough_base_url() if passthrough else shield.genai_base_url()
    return genai.Client(
        api_key=kwargs.pop("api_key", shield.api_key()),
        http_options=kwargs.pop("http_options", HttpOptions(base_url=base_url, headers=shield.headers())),
        **kwargs,
    )
