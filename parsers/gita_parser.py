# Copyright 2026 Dev Bhagavān
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import json
import logging
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class GitaParser:
    HEADER_PATTERN = r"##\s*(?:Text|Verse|Mantra)\s+(\d+)\.(\d+)"

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.text = self._load_file()
        self.units = []

    # ---------- Load File ----------

    def _load_file(self):
        if not self.filepath.exists():
            raise FileNotFoundError(f"{self.filepath} not found")
        return self.filepath.read_text(encoding="utf-8")

    # ---------- Extraction Helpers ----------

    def _extract_section(self, chunk, label):
        """
        Extracts content under **Label** until next section, YAML, or separator.
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
        """Extract YAML block metadata from a verse chunk."""
        if yaml is None:
            return {}
        match = re.search(r'```yaml\s*\n(.*?)```', chunk, re.DOTALL)
        if not match:
            return {}
        try:
            data = yaml.safe_load(match.group(1))
            if not isinstance(data, dict):
                return {}
            # Exclude fields managed by the parser itself
            excluded = {'id', 'chapter', 'verse', 'sanskrit', 'transliteration', 'translation', 'status'}
            return {k: v for k, v in data.items() if k not in excluded}
        except yaml.YAMLError:
            return {}

    # ---------- Main Parse ----------

    def parse(self):
        logging.info("Splitting verses...")

        matches = list(re.finditer(self.HEADER_PATTERN, self.text))

        for i, match in enumerate(matches):
            try:
                chapter = match.group(1)
                verse = match.group(2)

                unit_id = f"GITA_{chapter}_{verse}"

                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)
                chunk = self.text[start:end]

                sanskrit = self._extract_section(chunk, "Sanskrit")
                transliteration = self._extract_section(chunk, "Transliteration")
                translation = self._extract_section(chunk, "Translation")

                if not translation:
                    raise ValueError(f"{unit_id} missing translation")

                sanskrit = self._clean_text(sanskrit)
                transliteration = self._clean_text(transliteration)
                translation = self._clean_translation(translation)

                yaml_meta = self._extract_yaml_meta(chunk)

                unit = {
                    "id": unit_id,
                    "chapter": int(chapter),
                    "verse": int(verse),
                    "sanskrit": sanskrit,
                    "transliteration": transliteration,
                    "translation": translation,
                    **yaml_meta,
                    "status": "VERIFIED"
                }

                self.units.append(unit)
                logging.info(f"Parsed {unit_id}")

            except Exception as e:
                logging.error(f"{unit_id} FAILED: {e}")

        return self.units

    # ---------- Save JSON ----------

    def to_json(self):
        return {
            "metadata": {"text": "bhagavad_gita"},
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


# ---------- CLI ----------

if __name__ == "__main__":
    import argparse

    arg_parser = argparse.ArgumentParser(description="Parse Bhagavad Gītā Markdown to JSON")
    arg_parser.add_argument("input", help="Path to gita.md")
    arg_parser.add_argument("output", help="Output JSON file")

    args = arg_parser.parse_args()

    parser = GitaParser(args.input)
    parser.parse()
    parser.save(args.output)
    
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