import json
import os
import unicodedata
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CORPUS_PATH = Path(os.environ.get(
    "AIM_CORPUS_DB",
    str(_REPO_ROOT / "corpus_database.json")
))

_CORPUS: list = None  # loaded once at first query


def _load() -> list:
    global _CORPUS
    if _CORPUS is None:
        data = json.loads(_CORPUS_PATH.read_text(encoding="utf-8"))
        _CORPUS = [u for rec in data for u in rec.get("units", [])]
    return _CORPUS


def _normalize(value: str) -> str:
    """Strip diacritics and lowercase for robust field-value matching."""
    if not value:
        return ""
    nfkd = unicodedata.normalize("NFKD", value)
    ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
    return ascii_str.lower().strip()


_ADHIKARA_ORDER = {"sarva": 0, "madhyama": 1, "uttama": 2}


def query(
    prakriya: str = None,
    pedagogical_stage: str = None,
    adhikara_level: str = None,
    ontological_scope: str = None,
    preferred_unit_ids: list = None,
    limit: int = 5,
) -> list:
    """
    Return corpus units matching the routing fields.
    Preferred IDs are returned first; remaining slots filled by field match.
    adhikara_level is inclusive-downward: querying madhyama also returns sarva.
    """
    units = _load()

    preferred_unit_ids = set(preferred_unit_ids or [])
    results = []

    # Preferred IDs first (exact)
    if preferred_unit_ids:
        for u in units:
            if u.get("id") in preferred_unit_ids:
                results.append(u)

    seen_ids = {u["id"] for u in results}
    norm_prakriya = _normalize(prakriya) if prakriya else None
    req_level = _ADHIKARA_ORDER.get(adhikara_level, 2) if adhikara_level else None

    for u in units:
        if len(results) >= limit:
            break
        if u.get("id") in seen_ids:
            continue

        if norm_prakriya:
            unit_prakriya = _normalize(u.get("prakriya", ""))
            if unit_prakriya != norm_prakriya:
                continue

        if pedagogical_stage and u.get("pedagogical_stage") != pedagogical_stage:
            continue

        if req_level is not None and u.get("adhikara_level"):
            u_level = _ADHIKARA_ORDER.get(u["adhikara_level"], 2)
            if u_level > req_level:
                continue

        if ontological_scope and u.get("ontological_scope") != ontological_scope:
            continue

        results.append(u)
        seen_ids.add(u["id"])

    return results[:limit]


def query_by_ids(unit_ids: list) -> list:
    """Return specific units by ID, preserving order."""
    units = _load()
    index = {u["id"]: u for u in units}
    return [index[uid] for uid in unit_ids if uid in index]
