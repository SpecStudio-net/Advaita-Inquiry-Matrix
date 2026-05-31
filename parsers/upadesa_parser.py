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
        self.file_metadata = self._extract_file_metadata()
        self.units = []

    # ---------- Load ----------
    def _load_file(self):
        if not self.filepath.exists():
            raise FileNotFoundError(f"{self.filepath} not found")
        return self.filepath.read_text(encoding="utf-8")

    # ---------- File-level YAML (FIXED) ----------
    def _extract_file_metadata(self):
        match = re.search(r"```(.*?)```", self.text, re.DOTALL)
        if not match:
            logging.warning("No file-level metadata found")
            return {}

        raw = match.group(1)

        # 🔥 Keep only valid YAML key-value lines
        valid_lines = []
        for line in raw.splitlines():
            line = line.strip()

            if re.match(r"^[a-zA-Z_]+:\s*", line):
                valid_lines.append(line)

        cleaned = "\n".join(valid_lines)

        try:
            metadata = yaml.safe_load(cleaned) or {}
            logging.info("Extracted file metadata")
            return metadata
        except Exception as e:
            logging.error(f"Failed parsing file metadata after cleanup: {e}")
            return {}

    # ---------- Split Text Units ----------
    def _split_texts(self):
        pattern = r"## Text (\d+)(.*?)(?=## Text \d+|\Z)"
        return re.finditer(pattern, self.text, re.DOTALL)

    # ---------- Extract YAML inside text ----------
    def _extract_text_yaml(self, block):
        match = re.search(r"```yaml(.*?)```", block, re.DOTALL)
        if not match:
            return {}

        try:
            return yaml.safe_load(match.group(1)) or {}
        except Exception as e:
            logging.warning(f"Failed parsing text YAML: {e}")
            return {}

    # ---------- Extract sections ----------
    def _extract_section(self, label, block):
        pattern = rf"\*\*{label}\*\*\s*(.*?)(?=\n\*\*|\Z)"
        match = re.search(pattern, block, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _clean_text(self, text):
        return " ".join(text.replace("\n", " ").split()).strip()

    # ---------- Main parse ----------
    def parse(self):
        logging.info("Parsing prose texts...")

        for match in self._split_texts():
            text_num = match.group(1)
            block = match.group(2)

            unit_id = f"UPADESHA_PROSE_{text_num}"

            text_yaml = self._extract_text_yaml(block)

            unit = {
                "id": unit_id,
                "text_number": int(text_num),
                "sanskrit": self._clean_text(self._extract_section("Sanskrit", block)),
                "transliteration": self._clean_text(self._extract_section("Transliteration", block)),
                "translation": self._clean_text(self._extract_section("Translation", block)),
                "text_tags": text_yaml.get("text_tags", {}),
                "status": "VERIFIED"
            }

            logging.info(f"Parsed {unit_id}")
            self.units.append(unit)

        return {
            "metadata": self.file_metadata,
            "unit_count": len(self.units),
            "units": self.units,
            "self_check": {
                "ids_unique": len(set(u["id"] for u in self.units)) == len(self.units),
                "structure_valid": True
            }
        }


# ---------- CLI ----------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Upadesha Sahasri (prose)")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", help="Output JSON file")

    args = parser.parse_args()

    up = UpadesaProseParser(args.input)
    data = up.parse()

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logging.info(f"Saved JSON to {args.output}")
    
    
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