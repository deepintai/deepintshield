"""Generic MCP tool, content, and result types.

These types are framework-agnostic. Adapters convert them to whatever shape
their target framework expects.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Tool:
    """A single MCP tool exposed by a connected MCP client.

    `server` is the case-sensitive client name as registered in the MCP
    Registry. `name` is the bare tool name (no `<server>-` prefix). `schema`
    is the JSON Schema describing the tool's input parameters.
    """

    server: str
    name: str
    description: str = ""
    schema: dict[str, Any] = field(default_factory=dict)

    @property
    def qualified_name(self) -> str:
        """The DeepintShield-routable form: `<server>-<tool>`."""
        return f"{self.server}-{self.name}"

    @classmethod
    def from_qualified(cls, qualified: str, **rest: Any) -> "Tool":
        server, _, name = qualified.partition("-")
        return cls(server=server, name=name, **rest)


@dataclass
class ContentPart:
    """A single part of an MCP tool response."""

    type: str
    text: str | None = None
    data: str | None = None
    mime_type: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPResult:
    """Normalized response from `/v1/mcp/tool/execute`."""

    tool: str
    text: str
    parts: list[ContentPart]
    is_error: bool
    raw: dict[str, Any]

    def __str__(self) -> str:
        return self.text


def normalize_result(tool_name: str, body: dict[str, Any]) -> MCPResult:
    """Adapt the gateway's ChatMessage response into a uniform MCPResult."""
    raw_content = body.get("content")
    parts: list[ContentPart] = []
    text_chunks: list[str] = []

    if isinstance(raw_content, str):
        text_chunks.append(raw_content)
        parts.append(ContentPart(type="text", text=raw_content, raw={"type": "text", "text": raw_content}))
    elif isinstance(raw_content, list):
        for part in raw_content:
            if not isinstance(part, dict):
                text_chunks.append(str(part))
                parts.append(ContentPart(type="unknown", text=str(part), raw={"value": part}))
                continue
            ptype = part.get("type", "unknown")
            if ptype == "text" and "text" in part:
                text_chunks.append(part["text"])
                parts.append(ContentPart(type="text", text=part["text"], raw=part))
            elif ptype == "image":
                parts.append(
                    ContentPart(
                        type="image",
                        data=part.get("data"),
                        mime_type=part.get("mimeType") or part.get("mime_type"),
                        raw=part,
                    )
                )
            elif ptype == "resource":
                resource = part.get("resource") or {}
                text = resource.get("text")
                if text:
                    text_chunks.append(text)
                parts.append(ContentPart(type="resource", text=text, raw=part))
            else:
                parts.append(ContentPart(type=ptype, raw=part))
    elif raw_content is not None:
        text_chunks.append(json.dumps(raw_content))
        parts.append(ContentPart(type="json", text=text_chunks[-1], raw={"value": raw_content}))

    is_error = bool(body.get("is_error") or body.get("isError"))
    return MCPResult(
        tool=tool_name,
        text="\n".join(text_chunks),
        parts=parts,
        is_error=is_error,
        raw=body,
    )
