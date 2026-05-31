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
import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "corpus_database.json")


# --------------------------------------------------
# Load corpus
# --------------------------------------------------

with open(DB_PATH, "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"\nCorpus loaded: {len(records)} teaching units\n")


# --------------------------------------------------
# Build stage index
# --------------------------------------------------

stage_index = {}

for r in records:

    stage = r.get("pedagogical_stage")

    if not stage:
        continue

    stage_index.setdefault(stage, []).append(r)


print("Stage index sizes:\n")

for s in sorted(stage_index):

    print(f"{s} {len(stage_index[s])}")

print()


# --------------------------------------------------
# Student state detection
# --------------------------------------------------

def detect_student_state(q):

    q = q.lower()

    if "suffer" in q or "pain" in q or "why me" in q:
        return "grief"

    if "who am i" in q or "self" in q:
        return "inquiry"

    return "curiosity"


# --------------------------------------------------
# State → stage mapping
# --------------------------------------------------

STATE_STAGE_MAP = {

    "grief": [
        "existential-warning",
        "existential-release",
        "perceptual-reframing"
    ],

    "inquiry": [
        "perceptual-reframing",
        "ontological-deepening",
        "participatory-recognition"
    ],

    "curiosity": [
        "compressed-totality",
        "ontological-deepening"
    ]
}


# --------------------------------------------------
# Retrieve teachings
# --------------------------------------------------

def retrieve_teachings(stages, n=3):

    candidates = []

    for s in stages:

        if s in stage_index:
            candidates.extend(stage_index[s])

    if not candidates:
        return []

    random.shuffle(candidates)

    return candidates[:n]


# --------------------------------------------------
# Display teaching
# --------------------------------------------------

def display(t):

    print("\n--- Teaching Unit ---\n")

    print("ID:", t.get("id"))

    if "pedagogical_stage" in t:
        print("Stage:", t["pedagogical_stage"])

    if "prakriyā" in t:
        print("Prakriyā:", t["prakriyā"])


# --------------------------------------------------
# Interactive loop
# --------------------------------------------------

print("AIM Teaching Engine\n")
print("Ask a question about the Self, suffering, or liberation.")
print("Type 'quit' to exit.\n")

while True:

    q = input("\nStudent: ")

    if q.lower() == "quit":
        break

    state = detect_student_state(q)

    print("\nDetected student state:", state)

    stages = STATE_STAGE_MAP.get(state, [])

    teachings = retrieve_teachings(stages)

    if not teachings:
        print("\nNo teachings found.")
        continue

    print("\nTeacher response:")

    for t in teachings:
        display(t)