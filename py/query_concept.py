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

import sys
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
    concept_verses = {}

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

                source = data.get("id") or data.get("source_reference") or file.name

                for c in concepts:

                    concept_verses.setdefault(c, []).append(source)

                    if c in concept_definitions:
                        G.add_node(c, **concept_definitions[c])
                    else:
                        G.add_node(c)

                for i in range(len(concepts)):
                    for j in range(i + 1, len(concepts)):
                        G.add_edge(concepts[i], concepts[j])

            except Exception:
                pass

    return G, concept_verses


def show_concept(G, concept_verses, concept):

    data = G.nodes[concept]

    print("\nConcept:", concept)

    if "sanskrit" in data:
        print("Sanskrit:", data["sanskrit"])

    if "definition" in data:
        print("Definition:", data["definition"])

    print("\nPrimary verses:")

    for v in concept_verses.get(concept, []):
        print("  -", v)

    print("\nRelated concepts:")

    for neighbor in G.neighbors(concept):
        print("  -", neighbor)


def show_path(G, concept_verses, c1, c2):

    print("\nTeaching path:\n")

    path = nx.shortest_path(G, c1, c2)

    for step in path:

        node = G.nodes[step]
        label = node.get("sanskrit", step)

        print(label)

        if "definition" in node:
            print("  Definition:", node["definition"])

        if step in concept_verses:
            print("  Verses:")
            for v in concept_verses[step]:
                print("   -", v)

        print()


def main():

    if len(sys.argv) < 2:
        print("Usage: python query_concept.py <concept> [concept2]")
        sys.exit()

    concept_definitions = load_definitions()
    G, concept_verses = build_graph(concept_definitions)

    c1 = sys.argv[1]

    if c1 not in G.nodes:
        print("Concept not found:", c1)
        sys.exit()

    if len(sys.argv) > 2:
        c2 = sys.argv[2]

        if c2 not in G.nodes:
            print("Concept not found:", c2)
            sys.exit()

        show_path(G, concept_verses, c1, c2)

    else:
        show_concept(G, concept_verses, c1)


if __name__ == "__main__":
    main()