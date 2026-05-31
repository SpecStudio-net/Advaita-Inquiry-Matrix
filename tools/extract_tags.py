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
from collections import defaultdict

corpus_root = "corpus"
tags = defaultdict(set)

for root, dirs, files in os.walk(corpus_root):
    for file in files:
        if file.endswith(".md"):

            path = os.path.join(root, file)

            with open(path, encoding="utf8") as f:
                text = f.read()

            blocks = re.findall(r"```yaml(.*?)```", text, re.S)

            for block in blocks:
                try:
                    data = yaml.safe_load(block)

                    for key, value in data.items():
                        if isinstance(value, str):
                            tags[key].add(value)

                except:
                    pass

for k,v in tags.items():
    print("\n",k)
    for i in sorted(v):
        print("   ",i)