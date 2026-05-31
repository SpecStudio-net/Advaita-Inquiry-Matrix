import os
import importlib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)

_REPO_ROOT = Path(__file__).resolve().parent
CORPUS_ROOT = str(_REPO_ROOT / "corpus")


# Canonical text names for corpus_database.json metadata
TEXT_NAMES = {
    "mundaka":          "mundaka_upanishad",
    "katha":            "katha_upanishad",
    "mandukya":         "mandukya_upanishad",
    "atmabodha":        "atmabodha",
    "gita":             "bhagavad_gita",
    "upadesa_metrical": "upadesa_sahasri_metrical",
    "upadesa_prose":    "upadesha_sahasri_prose",
    "taittiriya":       "taittiriya_upanishad",
    "aitareya":         "aitareya_upanishad",
    "chandogya":        "chandogya_upanishad",
    "isha":             "isha_upanishad",
    "brihadaranyaka":   "brihadaranyaka_upanishad",
    "vivekacudamani":   "vivekacudamani",
    "kena":             "kena_upanishad",
    "yoga_sutra":       "yoga_sutras",
}

# 🔒 EXPLICIT PARSER MAP (no guessing)
PARSER_MAP = {
    "mundaka": ("parsers.mundaka_parser", "MundakaParser"),
    "katha": ("parsers.katha_parser", "KathaParser"),
    "mandukya": ("parsers.mandukya_parser", "MandukyaParser"),
    "atmabodha": ("parsers.atmabodha_parser", "AtmaBodhaParser"),
    "gita": ("parsers.gita_parser", "GitaParser"),
    "upadesa_metrical": ("parsers.upadesa_metrical_parser", "UpadesaMetricalParser"),
    "upadesa_prose": ("parsers.upadesa_parser2", "UpadesaProseParser"),
    "taittiriya": ("parsers.taittiriya_parser", "TaittiriyaParser"),
    "aitareya": ("parsers.aitareya_parser", "AitareyaParser"),
    "chandogya": ("parsers.chandogya_parser", "ChandogyaParser"),
    "isha": ("parsers.isha_parser", "IshaParser"),
    "brihadaranyaka": ("parsers.brihadaranyaka_parser", "BrihadaranyakaParser"),
    "vivekacudamani": ("parsers.vcm_parser", "VCMParser"),
    "kena": ("parsers.kena_parser", "KenaParser"),
    "yoga_sutra": ("parsers.yoga_sutra_parser", "YogaSutraParser"),
}


def infer_key(filepath):
    filename = os.path.basename(filepath)
    # Match by filename prefix — longest key wins (more specific beats less specific)
    for key in sorted(PARSER_MAP.keys(), key=len, reverse=True):
        if filename.startswith(key):
            return key
    # Fall back to directory components
    parts = filepath.lower().split(os.sep)
    for part in parts:
        if part in PARSER_MAP:
            return part
    return None


_FIELD_ALIASES = {
    "prakriyā":     "prakriya",
    "adhikāra_level": "adhikara_level",
    "pedagogical_stage": "pedagogical_stage",  # keep; already consistent
}

_DIACRITIC_TO_ASCII = {
    "prakriyā":       "prakriya",
    "adhikāra_level": "adhikara_level",
    "ontological_scope": "ontological_scope",
}


def _normalize_unit_fields(unit):
    """Rename diacritic field names to their ASCII equivalents in place."""
    for diac, ascii_key in _DIACRITIC_TO_ASCII.items():
        if diac in unit and ascii_key not in unit:
            unit[ascii_key] = unit.pop(diac)
    return unit


def normalize(parser, filepath, key=None):
    if hasattr(parser, "to_json"):
        result = parser.to_json()
    elif hasattr(parser, "data"):
        result = parser.data
    elif hasattr(parser, "units"):
        result = {"metadata": {"source": filepath}, "units": parser.units}
    elif hasattr(parser, "verses"):
        result = {"metadata": {"source": filepath}, "units": parser.verses}
    else:
        raise ValueError(f"{parser.__class__.__name__} has no usable output")

    if key:
        meta = result.setdefault("metadata", {})
        meta.setdefault("text", TEXT_NAMES.get(key, key))
        meta.setdefault("source", filepath)

    for unit in result.get("units", []):
        _normalize_unit_fields(unit)

    return result


def safe_parse(filepath):
    key = infer_key(filepath)

    if not key:
        logging.warning(f"SKIP (no parser): {filepath}")
        return None

    module_name, class_name = PARSER_MAP[key]

    try:
        module = importlib.import_module(module_name)
        ParserClass = getattr(module, class_name)

        parser = ParserClass(filepath)
        parser.parse()

        result = normalize(parser, filepath, key=key)

        logging.info(f"LOADED: {filepath}")
        return result

    except Exception as e:
        logging.error(f"ERROR: {filepath}\n{e}")
        return None


def load_corpus():
    results = []

    for root, _, files in os.walk(CORPUS_ROOT):
        if os.path.basename(root) == "metadata":
            continue

        for file in files:
            if not file.endswith(".md"):
                continue

            filepath = os.path.join(root, file)
            parsed = safe_parse(filepath)

            if parsed:
                results.append(parsed)

    return results


def save_corpus(data, output_path=None):
    if output_path is None:
        output_path = str(_REPO_ROOT / "corpus_database.json")
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"Saved {len(data)} records to {output_path}")


if __name__ == "__main__":
    data = load_corpus()
    print(f"\nLoaded records: {len(data)}")
    save_corpus(data)
    print("corpus_database.json written.")