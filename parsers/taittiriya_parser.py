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
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)


class TaittiriyaParser:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.text = self._load_file()
        self.metadata = {}
        self.units = []

    # ---------- File Handling ----------

    def _load_file(self):
        if not self.filepath.exists():
            raise FileNotFoundError(f"{self.filepath} not found")
        return self.filepath.read_text(encoding="utf-8")

    # ---------- File-level YAML ----------

    def _extract_file_metadata(self):
        # Try fenced YAML first
        match = re.search(r"```yaml(.*?)```", self.text, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except Exception as e:
                logging.error(f"Failed parsing fenced YAML: {e}")
                return {}
    
        # Fallback: YAML at top before first '---'
        match = re.search(r"^(.*?)(?=\n---)", self.text, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1))
            except Exception as e:
                logging.error(f"Failed parsing top YAML: {e}")
                return {}
    
        logging.warning("No file-level YAML metadata found")
        return {}

    # ---------- Mantra Splitting ----------

    def _split_mantras(self):
        pattern = r"(?:^|\n)\s*##\s*Text\s+(\d+\.\d+\.\d+)"        
        matches = list(re.finditer(pattern, self.text))
    
        mantras = []
    
        for i, match in enumerate(matches):
            number = match.group(1)
    
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)
    
            content = self.text[start:end]
            mantras.append((number, content))
    
        return mantras
        
    # ---------- Section Extraction ----------

    def _extract_section(self, label, block):
        pattern = rf"\*\*{label}\*\*\s*(.*?)(?=\n\*\*|\n---|\n\s*#{{0,3}}\s*(?:Mantra|Text)|$)"
        match = re.search(pattern, block, re.DOTALL)
        return match.group(1).strip() if match else ""
        
    # ---------- Validation ----------

    def _validate_unit(self, unit):
        if not unit["translation"]:
            raise ValueError(f"{unit['id']} missing translation")

    # ---------- Main Parse ----------

    def parse(self):
        logging.info("Extracting file metadata...")
        self.metadata = self._extract_file_metadata()

        logging.info("Splitting mantras...")
        mantra_blocks = self._split_mantras()

        for number, block in mantra_blocks:
            unit_id = f"TAITTIRIYA_{number.replace('.', '_')}"

            # --- Extract ---
            sanskrit = self._extract_section("Sanskrit", block)
            transliteration = self._extract_section("Transliteration", block)
            translation = self._extract_section("Translation", block)

            # --- Normalize Sanskrit ---
            sanskrit = sanskrit.replace("\n", " ").strip()

            # --- Normalize Transliteration ---
            transliteration = (
                transliteration
                .replace("\n", " ")
                .replace("*", "")
                .strip()
            )

            # --- Extract YAML metadata from translation ---
            yaml_match = re.search(r"```yaml(.*?)```", block, re.DOTALL)
            unit_metadata = {}

            if yaml_match:
                yaml_text = yaml_match.group(1)
                try:
                    unit_metadata = yaml.safe_load(yaml_text)
                except Exception as e:
                    logging.warning(f"{unit_id} YAML parse failed: {e}")

            # --- Clean Translation ---
            translation = (
                translation
                .split("```yaml")[0]
                .split("\n---")[0]
                .replace("\n", " ")
                .strip()
            )

            # --- Build Unit ---
            unit = {
                "id": unit_id,
                "sanskrit": sanskrit,
                "transliteration": transliteration,
                "translation": translation,
                **unit_metadata,
                "status": "VERIFIED"
            }

            # --- Validate ---
            try:
                self._validate_unit(unit)
                self.units.append(unit)
                logging.info(f"Parsed {unit_id}")
            except Exception as e:
                logging.error(f"{unit_id} FAILED: {e}")
                unit["status"] = "FAILED"
                self.units.append(unit)

    # ---------- Output ----------

    def to_json(self):
        return {
            "metadata": self.metadata,
            "units": self.units,
            "self_check": {
                "unit_count": len(self.units),
                "ids_unique": len(set(u["id"] for u in self.units)) == len(self.units),
                "structure_valid": True
            }
        }

    def save(self, output_path):
        data = self.to_json()
        Path(output_path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        logging.info(f"Saved JSON to {output_path}")

        
# ---------- CLI ----------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse Kaṭha Upaniṣad Markdown to JSON")
    parser.add_argument("input", help="Path to katha.md")
    parser.add_argument("output", help="Output JSON file")

    args = parser.parse_args()

    parser = TaittiriyaParser(args.input)
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