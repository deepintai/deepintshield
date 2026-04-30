from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Mapping

from .types import RetrievedChunk

if TYPE_CHECKING:
    from .client import DeepintShield


def build_chunk(content: str, chunk_id: str, document_id: str, **kwargs: Any) -> RetrievedChunk:
    return RetrievedChunk(chunk_id=chunk_id, document_id=document_id, content=content, **kwargs)


def allowed_chunk_ids(response: Mapping[str, Any]) -> set[str]:
    result = response.get("result", {}) or {}
    trace = result.get("trace", {}) or {}
    retrieved = trace.get("retrieved_chunks", []) or []
    return {str(c.get("chunk_id", "")).strip() for c in retrieved if str(c.get("chunk_id", "")).strip()}


def filter_chunks(chunks: Iterable[RetrievedChunk], response: Mapping[str, Any]) -> list[RetrievedChunk]:
    allowed = allowed_chunk_ids(response)
    return [chunk for chunk in chunks if chunk.chunk_id in allowed]


class RAGSurface:
    """RAG-focused helpers: evaluate a query over retrieved chunks, filter, or both."""

    def __init__(self, client: "DeepintShield") -> None:
        self._client = client

    def evaluate(
        self,
        *,
        query: str,
        chunks: Iterable[RetrievedChunk | Mapping[str, Any]],
        source_id: str | None = None,
        requester: str | None = None,
        requester_role: str | None = None,
        app_name: str | None = None,
        agent_name: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        persist: bool | None = None,
    ) -> dict[str, Any]:
        chunks_payload = [
            c.to_payload() if isinstance(c, RetrievedChunk) else dict(c)
            for c in chunks
        ]
        body: dict[str, Any] = {
            "query": query,
            "requester": requester or self._client.requester,
            "requester_role": requester_role or self._client.requester_role,
            "app_name": app_name or self._client.app_name,
            "agent_name": agent_name or self._client.agent_name,
            "persist": self._client.persist if persist is None else persist,
            "retrieved_chunks": chunks_payload,
        }
        if source_id:
            body["source_id"] = source_id
        if metadata:
            body["metadata"] = dict(metadata)
        return self._client.request("POST", "/api/rag-security/evaluate", json_body=body)

    def filter(
        self,
        *,
        query: str,
        chunks: Iterable[RetrievedChunk],
        source_id: str | None = None,
        **kwargs: Any,
    ) -> tuple[list[RetrievedChunk], dict[str, Any]]:
        """Evaluate and return (allowed_chunks, raw_response)."""
        chunk_list = list(chunks)
        response = self.evaluate(query=query, chunks=chunk_list, source_id=source_id, **kwargs)
        return filter_chunks(chunk_list, response), response
