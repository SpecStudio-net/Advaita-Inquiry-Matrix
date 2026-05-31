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

import os
import json
import re
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(BASE_DIR, "..", "corpus")
OUTPUT_FILE = os.path.join(BASE_DIR, "..", "corpus_database.json")

heading_re = re.compile(r'^##\s+(Mantra|Text)\s+.*', re.MULTILINE)
comment_re = re.compile(r'<!--(.*?)-->', re.S)

records = []


def parse_metadata(raw):

    raw = raw.strip()

    try:
        data = yaml.safe_load(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    meta = {}

    for line in raw.splitlines():

        line = line.strip()

        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        meta[key.strip()] = value.strip()

    return meta


for root, dirs, files in os.walk(CORPUS_DIR):

    for fname in files:

        if not fname.endswith(".md"):
            continue

        path = os.path.join(root, fname)

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        headings = list(heading_re.finditer(text))

        for i, h in enumerate(headings):

            start = h.start()

            if i + 1 < len(headings):
                end = headings[i + 1].start()
            else:
                end = len(text)

            block = text[start:end]

            meta = {}

            comment = comment_re.search(block)

            if comment:
                meta = parse_metadata(comment.group(1))

            record = {}

            if isinstance(meta, dict):
                record.update(meta)

            if "pedagogical_role" in record and "pedagogical_stage" not in record:
                record["pedagogical_stage"] = record["pedagogical_role"]

            record["text"] = block.strip()
            record["source_path"] = path
            record["id"] = f"{path}:{i+1}"

            records.append(record)


print("Loaded records:", len(records))

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(records, f, indent=2, ensure_ascii=False)

print("Database written to corpus_database.json")