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

import csv
from collections import defaultdict

INPUT_FILE = "UNKNOWN_TAG_RESOLUTION.csv"

clusters = defaultdict(list)

with open(INPUT_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        tag = row["Tag"]

        # use prefix before first underscore
        prefix = tag.split("_")[0]

        clusters[prefix].append(tag)

print("\nTag Clusters\n")

for prefix in sorted(clusters):

    print(f"\n=== {prefix} ({len(clusters[prefix])}) ===")

    for tag in sorted(clusters[prefix]):
        print(tag)