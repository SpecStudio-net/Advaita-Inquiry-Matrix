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

import json
from collections import Counter
from difflib import SequenceMatcher

# -------------------------------------
# Load corpus database
# -------------------------------------

with open("corpus_database.json", encoding="utf-8") as f:
    records = json.load(f)

# -------------------------------------
# Collect prakriyā labels
# -------------------------------------

prakriyas = []

for r in records:

    if "prakriyā" in r:

        v = r["prakriyā"]

        if isinstance(v, list):
            prakriyas.extend(v)
        else:
            prakriyas.append(v)

counts = Counter(prakriyas)

labels = list(counts.keys())

# -------------------------------------
# Similarity clustering
# -------------------------------------

clusters = []

visited = set()

for label in labels:

    if label in visited:
        continue

    cluster = [label]
    visited.add(label)

    for other in labels:

        if other in visited:
            continue

        sim = SequenceMatcher(None, label, other).ratio()

        if sim > 0.65:
            cluster.append(other)
            visited.add(other)

    clusters.append(cluster)

# -------------------------------------
# Sort clusters by size
# -------------------------------------

clusters.sort(key=len, reverse=True)

print("\nPrakriyā clusters\n")

for c in clusters[:30]:

    total = sum(counts[x] for x in c)

    print(f"\nCluster size {len(c)}  (occurrences {total})")

    for x in c:
        print(" ", x, ":", counts[x])