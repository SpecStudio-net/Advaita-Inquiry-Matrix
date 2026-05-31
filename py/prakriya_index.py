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
from collections import defaultdict

root = "./corpus"

prakriya_map = defaultdict(list)

for subdir, dirs, files in os.walk(root):
    for file in files:
        if file.endswith(".md"):
            path = os.path.join(subdir, file)

            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if "prakriyā:" in line:
                        prakriya = line.split("prakriyā:")[1].strip()
                        prakriya_map[prakriya].append(path)

print("\nPrakriyā Index\n")

for prakriya in sorted(prakriya_map):
    print(prakriya)

    for location in prakriya_map[prakriya]:
        print("   ", location)

    print()