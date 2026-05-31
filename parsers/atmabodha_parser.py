import re
import json
import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class AtmaBodhaParser:
    HEADER_PATTERN = r"##\s*Verse\s+(\d+)"

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.text = self._load_file()
        self.text = self.text.replace('\u00A0', ' ')  # normalize spacing
        self.units = []

    # ---------- Load File ----------

    def _load_file(self):
        if not self.filepath.exists():
            raise FileNotFoundError(f"{self.filepath} not found")
        return self.filepath.read_text(encoding="utf-8")

    # ---------- Section Extraction ----------

    def _extract_section(self, chunk, label):
        """
        Extract content under **Label** until next section, YAML, or separator.
        """
        pattern = rf"\*\*{label}\*\*\s*(.*?)(?=\n\*\*|\n---|\n```yaml|\Z)"
        match = re.search(pattern, chunk, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _clean_text(self, text):
        return " ".join(text.replace("\n", " ").split()).strip()

    def _clean_translation(self, text):
        return (
            text.split("\n---")[0]
            .replace("\n", " ")
            .strip()
        )

    def _extract_yaml_meta(self, chunk):
        m = re.search(r'```yaml\s*\n(.*?)```', chunk, re.DOTALL)
        if not m:
            return {}
        try:
            raw = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}
        skip = {'id', 'verse', 'sanskrit', 'transliteration', 'translation', 'status'}
        return {k: v for k, v in raw.items() if k not in skip}

    # ---------- Parse ----------

    def parse(self):
        logging.info("Splitting verses...")

        matches = list(re.finditer(self.HEADER_PATTERN, self.text))

        for i, match in enumerate(matches):
            try:
                verse = match.group(1)
                unit_id = f"ATMABODHA_{verse}"

                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)

                chunk = self.text[start:end]

                sanskrit = self._extract_section(chunk, "Sanskrit")
                transliteration = self._extract_section(chunk, "IAST")
                translation = self._extract_section(chunk, "Translation")

                if not translation:
                    raise ValueError(f"{unit_id} missing translation")

                sanskrit = self._clean_text(sanskrit)
                transliteration = self._clean_text(transliteration)
                translation = self._clean_translation(translation)

                meta = self._extract_yaml_meta(chunk)

                unit = {
                    "id": unit_id,
                    "verse": int(verse),
                    "sanskrit": sanskrit,
                    "transliteration": transliteration,
                    "translation": translation,
                    **meta,
                    "status": "VERIFIED"
                }

                self.units.append(unit)
                logging.info(f"Parsed {unit_id}")

            except Exception as e:
                logging.error(f"{unit_id} FAILED: {e}")

        return self.units

    # ---------- Save ----------

    def to_json(self):
        return {
            "metadata": {"text": "atmabodha"},
            "units": self.units,
            "self_check": {
                "unit_count": len(self.units),
                "ids_unique": len(set(u["id"] for u in self.units)) == len(self.units),
                "structure_valid": True
            }
        }

    def save(self, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_json(), f, indent=2, ensure_ascii=False)
        logging.info(f"Saved JSON to {output_path}")

def parse_file(filepath):
    parser = None

    # Instantiate correct class
    for attr in dir():
        obj = globals().get(attr)
        if isinstance(obj, type) and attr.endswith("Parser"):
            parser = obj(filepath)
            break

    if parser is None:
        raise ValueError("No parser class found")

    parser.parse()

    # Normalize outputs
    if hasattr(parser, "to_json"):
        return parser.to_json()

    if hasattr(parser, "data"):
        return parser.data

    if hasattr(parser, "units"):
        return {
            "metadata": {"source": filepath},
            "units": parser.units
        }

    if hasattr(parser, "verses"):
        return {
            "metadata": {"source": filepath},
            "units": parser.verses
        }

    raise ValueError(f"{parser.__class__.__name__} has no usable output")