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


def parse_list(value):
    if not value.startswith("[") or not value.endswith("]"):
        return value

    content = value[1:-1].strip()

    # Empty list case
    if content == "":
        return []

    # Range case: 0--5
    if "--" in content:
        start, end = content.split("--")
        return list(range(int(start), int(end) + 1))

    items = content.split(",")

    parsed = []
    for item in items:
        item = item.strip()

        if item == "":
            continue  # 🔥 skip empty values

        if item.isdigit():
            parsed.append(int(item))
        else:
            parsed.append(item)

    return parsed

def parse_metadata_block(block):
    metadata = {}
    lines = block.strip().split("\n")

    for line in lines:
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value.startswith("[") and value.endswith("]"):
            metadata[key] = parse_list(value)
        else:
            metadata[key] = value

    return metadata


def extract_section(block, section_name):
    pattern = rf"\*\*{section_name}\*\*\s*(.*?)(?=\n\*\*|\n<!--|\n>|\n---|\Z)"
    match = re.search(pattern, block, re.DOTALL)
    return match.group(1).strip() if match else ""


def _parse_text(text):
    headers = list(re.finditer(r'^## Mantra.*$', text, re.MULTILINE))

    units = []

    for i, header in enumerate(headers):
        start = header.start()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)

        block = text[start:end]

        unit_id = header.group().replace("## ", "").strip()

        sanskrit = extract_section(block, "Sanskrit")
        transliteration = extract_section(block, "Transliteration")
        translation = extract_section(block, "Translation")

        # Extract HTML metadata only (authoritative)
        metadata_matches = re.findall(r'<!--(.*?)-->', block, re.DOTALL)
        metadata = {}

        for m in metadata_matches:
            metadata.update(parse_metadata_block(m))

        units.append({
            "id": unit_id,
            "sanskrit": sanskrit,
            "transliteration": transliteration,
            "translation": translation,
            **metadata
        })

    return {
        "text_id": "isopanisad",
        "unit_count": len(units),
        "units": units
    }


class IshaParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self._data = None
        self.units = []

    def parse(self):
        with open(self.filepath, "r", encoding="utf-8") as f:
            text = f.read()
        self._data = _parse_text(text)
        self.units = self._data["units"]

    def to_json(self):
        return self._data


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "corpus/upanishads/isha/isha.md"
    parser = IshaParser(path)
    parser.parse()
    result = parser.to_json()
    with open("Isha.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Parsed {result['unit_count']} units successfully.")