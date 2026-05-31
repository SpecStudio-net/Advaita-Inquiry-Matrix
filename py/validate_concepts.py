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

import yaml
import re
from pathlib import Path

# location of corpus
CORPUS_DIR = Path("./corpus")

# load concept index
concept_index_file = CORPUS_DIR / "metadata" / "concept_index.md"
concept_index_text = concept_index_file.read_text()

index_yaml = re.findall(r"```yaml(.*?)```", concept_index_text, re.DOTALL)[0]
concept_index = yaml.safe_load(index_yaml)["concepts"]

valid_concepts = set(concept_index.keys())

print("\nValid concepts:")
print(valid_concepts)
print()

errors = []

# scan corpus
for file in CORPUS_DIR.rglob("*.md"):

    text = file.read_text()
    yaml_blocks = re.findall(r"```yaml(.*?)```", text, re.DOTALL)

    for block in yaml_blocks:

        try:
            data = yaml.safe_load(block)

            if isinstance(data, dict) and "concepts" in data:
                for c in data["concepts"]:

                    if c not in valid_concepts:
                        errors.append((file, c))

        except Exception as e:
           print(f"\nYAML parse error in {file}")
           print("First 200 characters of block:")
           print(block[:200])
           print("Error:", e)

# report
if not errors:
    print("✔ No concept errors found.")
else:
    print("Concept errors:\n")
    for f, c in errors:
        print(f"{f} → {c}")