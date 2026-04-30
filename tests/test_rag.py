from __future__ import annotations

import json

import httpx

from deepintshield import RetrievedChunk, allowed_chunk_ids, build_chunk, filter_chunks


def test_build_chunk_roundtrips_required_fields():
    chunk = build_chunk(content="hi", chunk_id="c1", document_id="d1", trust_score=91)
    assert chunk.chunk_id == "c1"
    assert chunk.document_id == "d1"
    assert chunk.content == "hi"
    assert chunk.trust_score == 91


def test_allowed_chunk_ids_reads_trace():
    response = {
        "result": {
            "trace": {
                "retrieved_chunks": [
                    {"chunk_id": "a"},
                    {"chunk_id": "b"},
                    {"chunk_id": ""},
                ]
            }
        }
    }
    assert allowed_chunk_ids(response) == {"a", "b"}


def test_allowed_chunk_ids_empty_when_no_trace():
    assert allowed_chunk_ids({}) == set()


def test_filter_chunks_removes_blocked():
    chunks = [
        RetrievedChunk(chunk_id="a", document_id="d", content="x"),
        RetrievedChunk(chunk_id="b", document_id="d", content="y"),
    ]
    response = {"result": {"trace": {"retrieved_chunks": [{"chunk_id": "a"}]}}}
    filtered = filter_chunks(chunks, response)
    assert [c.chunk_id for c in filtered] == ["a"]


def test_rag_evaluate_posts_correct_shape(shield_factory):
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content.decode())
        return httpx.Response(
            200,
            json={"result": {"trace": {"retrieved_chunks": [{"chunk_id": "c1"}]}}},
        )

    shield = shield_factory(handler)
    chunks = [build_chunk(content="hello", chunk_id="c1", document_id="d1")]
    result = shield.rag.evaluate(query="what is hello?", chunks=chunks, source_id="kb")

    assert captured["url"].endswith("/api/rag-security/evaluate")
    assert captured["body"]["query"] == "what is hello?"
    assert captured["body"]["source_id"] == "kb"
    assert captured["body"]["retrieved_chunks"][0]["chunk_id"] == "c1"
    assert result["result"]["trace"]["retrieved_chunks"][0]["chunk_id"] == "c1"


def test_rag_filter_returns_allowed_and_raw(shield_factory):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"result": {"trace": {"retrieved_chunks": [{"chunk_id": "keep"}]}}},
        )

    shield = shield_factory(handler)
    chunks = [
        build_chunk(content="a", chunk_id="keep", document_id="d"),
        build_chunk(content="b", chunk_id="drop", document_id="d"),
    ]
    allowed, raw = shield.rag.filter(query="q", chunks=chunks)
    assert [c.chunk_id for c in allowed] == ["keep"]
    assert "result" in raw
