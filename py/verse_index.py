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

root = "./corpus/upanishads"

index = []

for subdir, dirs, files in os.walk(root):
    for file in files:
        if file.endswith(".md"):
            path = os.path.relpath(os.path.join(subdir, file), root)
            index.append(path)

index.sort()

with open("upanishad_index.txt", "w") as f:
    for item in index:
        f.write(item + "\n")

print("Index written to upanishad_index.txt")