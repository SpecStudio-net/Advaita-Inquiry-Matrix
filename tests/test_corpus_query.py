"""
Tests for engine/corpus_query.py.

Uses AIM_CORPUS_DB env var to point at a tiny synthetic corpus so tests
run without the full corpus_database.json being present.
"""

import json
import os
import pytest


SYNTHETIC_CORPUS = [
    {
        "metadata": {"text": "katha_upanishad"},
        "units": [
            {
                "id": "katha_1_1_1",
                "prakriya": "drashtr-svarupa",
                "pedagogical_stage": "sravana",
                "adhikara_level": "sarva",
                "ontological_scope": "dual-register",
                "translation": "The Self is the knower, not the known.",
            },
            {
                "id": "katha_2_1_1",
                "prakriya": "avastha-traya-analysis",
                "pedagogical_stage": "manana",
                "adhikara_level": "madhyama",
                "ontological_scope": "dual-register",
                "translation": "In sleep the objects vanish; the Self remains.",
            },
            {
                "id": "katha_2_3_1",
                "prakriya": "pancakosa-viveka",
                "pedagogical_stage": "nididhyasana",
                "adhikara_level": "uttama",
                "ontological_scope": "paramarathika",
                "translation": "Beyond the bliss sheath, the Self alone shines.",
            },
        ],
    },
]


@pytest.fixture(autouse=True)
def synthetic_corpus_db(tmp_path, monkeypatch):
    db = tmp_path / "corpus_database.json"
    db.write_text(json.dumps(SYNTHETIC_CORPUS), encoding="utf-8")
    monkeypatch.setenv("AIM_CORPUS_DB", str(db))
    # Reload module to pick up new path and reset the cache
    import importlib
    import engine.corpus_query as cq
    cq._CORPUS = None
    importlib.reload(cq)


import engine.corpus_query as cq


def test_query_by_prakriya():
    results = cq.query(prakriya="drashtr-svarupa")
    assert len(results) == 1
    assert results[0]["id"] == "katha_1_1_1"

def test_query_by_stage():
    results = cq.query(pedagogical_stage="manana")
    assert any(u["id"] == "katha_2_1_1" for u in results)

def test_query_adhikara_inclusive_downward():
    """madhyama should return sarva units too (inclusive-downward)."""
    results = cq.query(adhikara_level="madhyama")
    ids = {u["id"] for u in results}
    assert "katha_1_1_1" in ids   # sarva — within madhyama
    assert "katha_2_1_1" in ids   # madhyama — exact

def test_query_adhikara_sarva_excludes_higher():
    results = cq.query(adhikara_level="sarva")
    ids = {u["id"] for u in results}
    assert "katha_1_1_1" in ids
    assert "katha_2_1_1" not in ids   # madhyama > sarva
    assert "katha_2_3_1" not in ids   # uttama > sarva

def test_query_ontological_scope():
    results = cq.query(ontological_scope="paramarathika")
    assert all(u["ontological_scope"] == "paramarathika" for u in results)
    assert any(u["id"] == "katha_2_3_1" for u in results)

def test_query_limit():
    results = cq.query(limit=1)
    assert len(results) <= 1

def test_query_no_match_returns_empty():
    results = cq.query(prakriya="nonexistent-prakriya-xyz")
    assert results == []

def test_query_by_ids():
    results = cq.query_by_ids(["katha_2_3_1", "katha_1_1_1"])
    ids = [u["id"] for u in results]
    assert ids == ["katha_2_3_1", "katha_1_1_1"]   # order preserved

def test_query_by_ids_missing_silently_dropped():
    results = cq.query_by_ids(["katha_1_1_1", "does-not-exist"])
    assert len(results) == 1
    assert results[0]["id"] == "katha_1_1_1"

def test_query_preferred_ids_first():
    results = cq.query(
        prakriya="drashtr-svarupa",
        preferred_unit_ids=["katha_2_3_1"],
        limit=5,
    )
    # preferred ID should appear first even if it doesn't match prakriya filter
    assert results[0]["id"] == "katha_2_3_1"
