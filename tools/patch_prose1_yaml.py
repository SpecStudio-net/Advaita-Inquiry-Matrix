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

"""
Add AIM-standard YAML blocks to all 44 Text sections of upadesa_prose_1.md.

Cluster assignments from the file's own cluster_map:
  C1 (1-8):   adhikāri_qualification     śravaṇa         dual-register
  C2 (9-24):  identity_deconstruction    manana          dual-register
  C3 (25-32): bheda_niṣedha              manana          dual-register
  C4 (33-36): locus_analysis             manana          dual-register
  C5 (37-44): avidyā_exposure            nididhyāsana    pāramārthika
"""
import re
from pathlib import Path

FILEPATH = Path("corpus/prakaranas/upadesa/upadesa_prose_1.md")

# ── cluster assignments ──────────────────────────────────────────────────────
def cluster(n):
    if 1  <= n <= 8:  return 'C1'
    if 9  <= n <= 24: return 'C2'
    if 25 <= n <= 32: return 'C3'
    if 33 <= n <= 36: return 'C4'
    if 37 <= n <= 44: return 'C5'
    raise ValueError(f"No cluster for text {n}")

CLUSTER_META = {
    'C1': dict(prakriyā='adhikāri_qualification',  scope='dual-register',  stage='śravaṇa',      cog='analytic_contemplative'),
    'C2': dict(prakriyā='identity_deconstruction', scope='dual-register',  stage='manana',        cog='analytic_inquiry'),
    'C3': dict(prakriyā='bheda_niṣedha',           scope='dual-register',  stage='manana',        cog='analytic_contemplative'),
    'C4': dict(prakriyā='locus_analysis',          scope='dual-register',  stage='manana',        cog='analytic_contemplative'),
    'C5': dict(prakriyā='avidyā_exposure',         scope='pāramārthika',   stage='nididhyāsana',  cog='direct_insight'),
}

def yaml_block(n):
    c = cluster(n)
    m = CLUSTER_META[c]
    return (
        f"```yaml\n"
        f"id: UPADESA_PROSE_01_{n:03d}\n"
        f"prakriyā: {m['prakriyā']}\n"
        f"ontological_scope: {m['scope']}\n"
        f"adhikāra_level: uttama\n"
        f"cognitive_mode: {m['cog']}\n"
        f"pedagogical_stage: {m['stage']}\n"
        f"```"
    )

# ── patch ────────────────────────────────────────────────────────────────────
text = FILEPATH.read_text(encoding="utf-8")

# Find all "## Text N" headings
HEADING_RE = re.compile(r'^(## Text (\d+))\s*$', re.MULTILINE)

# Check which sections already have an AIM-standard yaml block with 'id:'
AIM_YAML_RE = re.compile(r'```yaml.*?id:\s*UPADESA_PROSE_01_', re.DOTALL)

matches = list(HEADING_RE.finditer(text))
patched = 0
# Work in reverse so offsets stay valid
for m in reversed(matches):
    n = int(m.group(2))
    insert_pos = m.end()  # right after the heading line

    # Check if this section already has an AIM yaml block
    next_heading = matches[matches.index(m) + 1].start() if matches.index(m) + 1 < len(matches) else len(text)
    section = text[insert_pos:next_heading]
    if AIM_YAML_RE.search(section):
        continue  # already patched

    block = '\n\n' + yaml_block(n) + '\n'
    text = text[:insert_pos] + block + text[insert_pos:]
    patched += 1

FILEPATH.write_text(text, encoding="utf-8")
print(f"Patched {patched} text sections.")
