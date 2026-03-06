import json
from pathlib import Path

import rag_benchmark


def _write_queries_jsonl(path: Path, query_rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in query_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_qrels_lines(path: Path) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def _batch_result(key: str, text: str) -> dict:
    return {
        "key": key,
        "response": {
            "candidates": [
                {"content": {"parts": [{"text": text}]}}
            ]
        },
    }


def test_parse_source_chunk_id_valid_and_invalid_formats():
    assert rag_benchmark.parse_source_chunk_id("q1_for_Hind_chunk20") == "Hind_chunk20"
    assert rag_benchmark.parse_source_chunk_id("q9_for_Rules_and_Regs_chunk7") == "Rules_and_Regs_chunk7"

    assert rag_benchmark.parse_source_chunk_id("q1_Hind_chunk20") is None
    assert rag_benchmark.parse_source_chunk_id("q1_for_Hind_chunkX") is None
    assert rag_benchmark.parse_source_chunk_id("q1_for__chunk3") is None


def test_batch_fetch_forces_source_even_when_all_llm_labels_zero(tmp_path, monkeypatch):
    queries_file = tmp_path / "queries.jsonl"
    qrels_file = tmp_path / "qrels.tsv"
    _write_queries_jsonl(
        queries_file,
        [{"query_id": "q1_for_doc_chunk3", "text": "sample query"}],
    )

    results = [
        _batch_result("q1_for_doc_chunk3|||another_doc", '{"relevance": 0}')
    ]
    updated = []

    class FakeBatchManager:
        def download_results(self, _batch_id):
            return results

        def update_batch_status(self, batch_id, status):
            updated.append((batch_id, status))

    monkeypatch.setattr(rag_benchmark, "BatchManager", FakeBatchManager)
    monkeypatch.setattr(rag_benchmark.cfg, "queries_file", str(queries_file))
    monkeypatch.setattr(rag_benchmark.cfg, "qrels_file", str(qrels_file))

    assert rag_benchmark.generate_qrels(batch_fetch_id="batch-1") is True

    lines = _read_qrels_lines(qrels_file)
    assert lines == ["q1_for_doc_chunk3\tdoc_chunk3\t1"]
    assert updated == [("batch-1", "FETCHED_SUCCESSFULLY")]


def test_batch_fetch_deduplicates_when_source_already_positive(tmp_path, monkeypatch):
    queries_file = tmp_path / "queries.jsonl"
    qrels_file = tmp_path / "qrels.tsv"
    _write_queries_jsonl(
        queries_file,
        [{"query_id": "q1_for_doc_chunk3", "text": "sample query"}],
    )

    results = [
        _batch_result("q1_for_doc_chunk3|||doc_chunk3", '{"relevance": 1}'),
        _batch_result("q1_for_doc_chunk3|||doc_chunk3", '{"relevance": 1}'),
    ]

    class FakeBatchManager:
        def download_results(self, _batch_id):
            return results

        def update_batch_status(self, _batch_id, _status):
            return None

    monkeypatch.setattr(rag_benchmark, "BatchManager", FakeBatchManager)
    monkeypatch.setattr(rag_benchmark.cfg, "queries_file", str(queries_file))
    monkeypatch.setattr(rag_benchmark.cfg, "qrels_file", str(qrels_file))

    assert rag_benchmark.generate_qrels(batch_fetch_id="batch-2") is True

    lines = _read_qrels_lines(qrels_file)
    assert lines == ["q1_for_doc_chunk3\tdoc_chunk3\t1"]


def test_batch_fetch_adds_source_for_queries_missing_in_batch_results(tmp_path, monkeypatch):
    queries_file = tmp_path / "queries.jsonl"
    qrels_file = tmp_path / "qrels.tsv"
    _write_queries_jsonl(
        queries_file,
        [
            {"query_id": "q1_for_DocA_chunk1", "text": "query 1"},
            {"query_id": "q2_for_DocB_chunk2", "text": "query 2"},
        ],
    )

    results = [
        _batch_result("q1_for_DocA_chunk1|||alt_doc_for_q1", '{"relevance": 1}')
    ]

    class FakeBatchManager:
        def download_results(self, _batch_id):
            return results

        def update_batch_status(self, _batch_id, _status):
            return None

    monkeypatch.setattr(rag_benchmark, "BatchManager", FakeBatchManager)
    monkeypatch.setattr(rag_benchmark.cfg, "queries_file", str(queries_file))
    monkeypatch.setattr(rag_benchmark.cfg, "qrels_file", str(qrels_file))

    assert rag_benchmark.generate_qrels(batch_fetch_id="batch-3") is True

    lines = _read_qrels_lines(qrels_file)
    parsed = {tuple(line.split("\t")) for line in lines}
    assert parsed == {
        ("q1_for_DocA_chunk1", "DocA_chunk1", "1"),
        ("q1_for_DocA_chunk1", "alt_doc_for_q1", "1"),
        ("q2_for_DocB_chunk2", "DocB_chunk2", "1"),
    }


def test_non_batch_forces_source_and_deduplicates_candidates(tmp_path, monkeypatch):
    qrels_file = tmp_path / "qrels.tsv"
    corpus = {
        "doc_chunk1": "source text",
        "other_doc": "another text",
    }
    queries = {
        "q1_for_doc_chunk1": "what is in source text?",
    }

    class FakeCollection:
        def query(self, query_texts, n_results):
            return {
                "ids": [["doc_chunk1", "other_doc", "other_doc"]],
                "documents": [["source text", "another text", "another text"]],
            }

    class FakeClient:
        def get_collection(self, _name):
            return FakeCollection()

    monkeypatch.setattr(rag_benchmark, "load_corpus_from_file", lambda _path: corpus)
    monkeypatch.setattr(rag_benchmark, "load_queries_from_file", lambda _path: queries)
    monkeypatch.setattr(rag_benchmark, "initialize_collection", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(rag_benchmark, "get_chromadb_client", lambda: FakeClient())
    monkeypatch.setattr(rag_benchmark, "generate_content", lambda *_args, **_kwargs: '{"relevance": 1}')

    monkeypatch.setattr(rag_benchmark.cfg, "embedding_models", [{"model_name": "m", "collection_name": "c"}])
    monkeypatch.setattr(rag_benchmark.cfg, "qrels_embedding_model_index", 0)
    monkeypatch.setattr(rag_benchmark.cfg, "candidate_pool_size", 3)
    monkeypatch.setattr(rag_benchmark.cfg, "llm_timeout", 0)
    monkeypatch.setattr(rag_benchmark.cfg, "qrels_file", str(qrels_file))
    monkeypatch.setattr(rag_benchmark.cfg, "queries_file", str(tmp_path / "queries.jsonl"))
    monkeypatch.setattr(rag_benchmark.cfg, "corpus_file", str(tmp_path / "corpus.jsonl"))

    assert rag_benchmark.generate_qrels() is True

    lines = _read_qrels_lines(qrels_file)
    parsed = {tuple(line.split("\t")) for line in lines}
    assert parsed == {
        ("q1_for_doc_chunk1", "doc_chunk1", "1"),
        ("q1_for_doc_chunk1", "other_doc", "1"),
    }
