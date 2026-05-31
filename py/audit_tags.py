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
import re
import csv
import yaml

CORPUS_DIR = "corpus"
REGISTRY_FILE = "system/architecture/core/AIM_TAG_REGISTRY.md"

VALIDATED_FIELDS = {
    "cluster",
    "prakriyā",
    "pedagogical_role",
    "adhikāra_level",
    "cognitive_mode",
    "pedagogical_stage",
    "student_state",
    "teacher_strategy",
    "practice_mode",
    "integration_domain",
    "action_model",
    "psychological_mode"
}

# -----------------------------
# Load registry values
# -----------------------------

registry_values = set()

with open(REGISTRY_FILE, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("##"):
            registry_values.add(line)

print("Registry values:", len(registry_values))

# -----------------------------
# Extract YAML blocks
# -----------------------------

yaml_pattern = r"```yaml(.*?)```"

unknown = {}

for root, dirs, files in os.walk(CORPUS_DIR):
    for file in files:

        if not file.endswith(".md"):
            continue

        path = os.path.join(root, file)

        with open(path, encoding="utf-8") as f:
            text = f.read()

        blocks = re.findall(yaml_pattern, text, re.S)

        for block in blocks:

            try:
                data = yaml.safe_load(block)

                if not isinstance(data, dict):
                    continue

                for key, value in data.items():
                
                    if key not in VALIDATED_FIELDS:
                        continue
                    if isinstance(value, list):
                        for v in value:
                            v = str(v)
                            if v not in registry_values:
                                unknown.setdefault(v, path)
                    else:
                        value = str(value)
                        if value not in registry_values:
                            unknown.setdefault(value, path)

            except Exception:
                pass

# -----------------------------
# Write resolution sheet
# -----------------------------

with open("UNKNOWN_TAG_RESOLUTION.csv","w",newline="",encoding="utf-8") as f:

    writer = csv.writer(f)
    writer.writerow(["Tag","Example File","Suggested Action"])

    for tag,path in sorted(unknown.items()):
        writer.writerow([tag,path,"REVIEW"])

print("Unknown tags:", len(unknown))
print("Resolution sheet written to UNKNOWN_TAG_RESOLUTION.csv")