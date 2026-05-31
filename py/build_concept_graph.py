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
import networkx as nx
import matplotlib.pyplot as plt

DEFINITIONS_FILE = Path("./corpus/metadata/concept_definitions.md")

definitions_text = DEFINITIONS_FILE.read_text()

definition_block = re.findall(r"```yaml(.*?)```", definitions_text, re.DOTALL)[0]

concept_definitions = yaml.safe_load(definition_block)["concepts"]

CORPUS_DIR = Path("./corpus")

G = nx.Graph()

for file in CORPUS_DIR.rglob("*.md"):

    text = file.read_text()
    yaml_blocks = re.findall(r"```yaml(.*?)```", text, re.DOTALL)

    for block in yaml_blocks:
        try:
            data = yaml.safe_load(block)
    
            if isinstance(data, dict) and "concepts" in data:
                concepts = data["concepts"]
    
                if concepts:
                    for c in concepts:
                        if c in concept_definitions:
                            G.add_node(c, **concept_definitions[c])
                        else:
                            G.add_node(c)
    
                    for i in range(len(concepts)):
                        for j in range(i + 1, len(concepts)):
                            G.add_edge(concepts[i], concepts[j])
    
        except:
            pass

print("\nConcept nodes:")
print(G.nodes())

print("\nConcept connections:")
for edge in G.edges():
    print(edge)
    
print("\nConcept centrality:")
centrality = nx.degree_centrality(G)

for concept, score in sorted(centrality.items(), key=lambda x: x[1], reverse=True):
    print(concept, round(score,3))
    
import matplotlib.pyplot as plt

plt.figure(figsize=(8,6))

pos = nx.spring_layout(G, seed=42)

labels = {n: G.nodes[n].get("sanskrit", n) for n in G.nodes()}

nx.draw(
    G,
    pos,
    labels=labels,
    node_size=3000,
    node_color="lightgoldenrodyellow",
    font_size=10,
    edge_color="gray"
)

plt.title("AIM Concept Graph")
plt.show()