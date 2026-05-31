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
import networkx as nx
from pathlib import Path

CORPUS_DIR = Path("./corpus")
DEFINITIONS_FILE = Path("./corpus/metadata/concept_definitions.md")


def load_definitions():
    text = DEFINITIONS_FILE.read_text()
    block = re.findall(r"```yaml(.*?)```", text, re.DOTALL)[0]
    return yaml.safe_load(block)["concepts"]


def build_graph(concept_definitions):

    G = nx.Graph()

    for file in CORPUS_DIR.rglob("*.md"):

        text = file.read_text()
        yaml_blocks = re.findall(r"```yaml(.*?)```", text, re.DOTALL)

        for block in yaml_blocks:
            try:
                data = yaml.safe_load(block)

                if not isinstance(data, dict):
                    continue

                concepts = data.get("concepts")
                if not concepts:
                    continue

                for c in concepts:
                    if c in concept_definitions:
                        G.add_node(c, **concept_definitions[c])
                    else:
                        G.add_node(c)

                for i in range(len(concepts)):
                    for j in range(i + 1, len(concepts)):
                        G.add_edge(concepts[i], concepts[j])

            except Exception:
                pass

    return G


concept_definitions = load_definitions()
G = build_graph(concept_definitions)

centrality = nx.degree_centrality(G)

print("\nConcept centrality:\n")

for concept, score in sorted(centrality.items(), key=lambda x: x[1], reverse=True):

    label = G.nodes[concept].get("sanskrit", concept)

    print(f"{label:20} {score:.3f}")