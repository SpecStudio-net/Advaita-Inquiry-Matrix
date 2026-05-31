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
import yaml

corpus_root = "corpus"
rows = []

for root, dirs, files in os.walk(corpus_root):
    for f in files:
        if f.endswith(".md"):
            path = os.path.join(root, f)

            with open(path, "r", encoding="utf8") as file:
                text = file.read()

            yaml_blocks = re.findall(r"```yaml(.*?)```", text, re.S)

            for block in yaml_blocks:
                try:
                    data = yaml.safe_load(block)

                    rows.append({
                        "file": path,
                        "cluster": data.get("cluster"),
                        "prakriya": data.get("prakriyā"),
                        "role": data.get("pedagogical_role"),
                        "adhikara": data.get("adhikāra_level")
                    })

                except:
                    pass


with open("AIM_CORPUS_INDEX.md","w",encoding="utf8") as out:

    out.write("# AIM Corpus Index\n\n")
    out.write("| File | Cluster | Prakriyā | Role | Adhikāra |\n")
    out.write("|------|---------|----------|------|----------|\n")

    for r in rows:
        out.write(f"| {r['file']} | {r['cluster']} | {r['prakriya']} | {r['role']} | {r['adhikara']} |\n")