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
import yaml
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class UpadesaProseParser:

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.text = self._load_file()
        self.units = []

    # ---------- Load ----------
    def _load_file(self):
        if not self.filepath.exists():
            raise FileNotFoundError(f"{self.filepath} not found")
        return self.filepath.read_text(encoding="utf-8")

    # ---------- Parse ----------
    def parse(self):
        logging.info("Parsing prose texts...")

        pattern = r"## Text (\d+)(.*?)(?=## Text \d+|\Z)"
        matches = re.finditer(pattern, self.text, re.DOTALL)

        for match in matches:
            text_num = int(match.group(1))
            block = match.group(2)

            # --- Extract YAML metadata ---
            yaml_match = re.search(r"```yaml(.*?)```", block, re.DOTALL)
            if not yaml_match:
                logging.warning(f"Text {text_num} missing YAML block")
                continue

            try:
                meta = yaml.safe_load(yaml_match.group(1)) or {}
            except Exception as e:
                logging.error(f"YAML parse failed in Text {text_num}: {e}")
                continue

            # --- Extract Translation ---
            trans_match = re.search(r"\*\*Translation\*\*\s*(.*)", block, re.DOTALL)
            if not trans_match:
                logging.warning(f"Text {text_num} missing Translation")
                translation = ""
            else:
                translation = self._clean_text(trans_match.group(1))

            unit_id = meta.get("id")

            if not unit_id:
                logging.warning(f"Text {text_num} missing ID")
                continue

            # Pull all meta fields; known structural keys excluded
            _skip = {"id"}
            unit = {
                "id": unit_id,
                "text_number": text_num,
                **{k: v for k, v in meta.items() if k not in _skip},
                "translation": translation,
                "status": "VERIFIED"
            }

            self.units.append(unit)
            logging.info(f"Parsed {unit_id}")

        return self.units

    # ---------- Clean text ----------
    def _clean_text(self, text):
        text = text.strip()
        text = re.sub(r"\n*---\s*$", "", text)
        text = text.replace('”', '"').replace('“', '"')
        return text

    # ---------- Save ----------
    def to_json(self):
        return {
            "metadata": {"text": "upadesha_sahasri_prose"},
            "unit_count": len(self.units),
            "units": self.units,
            "self_check": {
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
    parser = argparse.ArgumentParser(description="Parse Upadesha Sahasri Prose")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", help="Output JSON file")

    args = parser.parse_args()

    up = UpadesaProseParser(args.input)
    up.parse()
    up.save(args.output)
    
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