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
Patch upadesa_prose_2.md and upadesa_prose_3.md:
  - Add: prakriyā, ontological_scope, adhikāra_level, cognitive_mode
  - Normalize: pedagogical_stage → canonical AIM values
  - Add pedagogical_stage to prose_3 units 1-5 (currently missing)

All fields inserted after the 'id:' line. Stage normalization done in-place.
"""
import re
import yaml
from pathlib import Path

BASE = Path("corpus/prakaranas/upadesa")

YAML_BLOCK_RE = re.compile(r'(```yaml\s*\n)(.*?)(```)', re.DOTALL)

# ── prose_2 stage → canonical ──────────────────────────────────────────────
STAGE_NORM = {
    "diagnosis":      "manana",
    "discrimination": "manana",
    "negation":       "manana",
    "direct_pointing": "nididhyāsana",
}

# ── prakriyā/scope/cognitive by unit id for prose_2 ───────────────────────
# Units with special handling keyed by id suffix (001-006 and 035,053,066)
PROSE2_SPECIAL = {
    "001": ("samsara_inquiry",      "vyavahārika",   "analytic_inquiry"),
    "002": ("liberation_framework", "vyavahārika",   "analytic_contemplative"),
    "003": ("samsara_inquiry",      "vyavahārika",   "analytic_inquiry"),
    "004": ("liberation_framework", "vyavahārika",   "analytic_contemplative"),
    "005": ("samsara_inquiry",      "vyavahārika",   "analytic_inquiry"),
    "006": ("mahāvākya_prakriyā",   "pāramārthika",  "direct_insight"),
    "035": ("direct_pointing",      "pāramārthika",  "direct_insight"),
    "053": ("direct_pointing",      "pāramārthika",  "direct_insight"),
    "066": ("direct_pointing",      "pāramārthika",  "direct_insight"),
}

# Default by original stage for prose_2 texts 7+ (not in PROSE2_SPECIAL)
PROSE2_STAGE_DEFAULT = {
    "diagnosis":       ("adhyāsa_inquiry",   "dual-register",  "analytic_inquiry"),
    "discrimination":  ("adhyāsa_analysis",  "dual-register",  "analytic_contemplative"),
    "negation":        ("negation_correction","dual-register",  "analytic_contemplative"),
    "direct_pointing": ("direct_pointing",   "pāramārthika",   "direct_insight"),
}

# ── prose_3 per-unit spec ─────────────────────────────────────────────────
# key = id value from YAML block
PROSE3_MAP = {
    "UPADESA_PROSE_03_001": {
        "prakriyā": "samsara_analysis",
        "ontological_scope": "dual-register",
        "adhikāra_level": "uttama",
        "cognitive_mode": "analytic_contemplative",
        "pedagogical_stage": "manana",
    },
    "UPADESA_PROSE_03_002": {
        "prakriyā": "samsara_analysis",
        "ontological_scope": "dual-register",
        "adhikāra_level": "uttama",
        "cognitive_mode": "analytic_contemplative",
        "pedagogical_stage": "manana",
    },
    "UPADESA_PROSE_03_003": {
        "prakriyā": "svarūpa_stabilization",
        "ontological_scope": "pāramārthika",
        "adhikāra_level": "uttama",
        "cognitive_mode": "direct_insight",
        "pedagogical_stage": "nididhyāsana",
    },
    "UPADESA_PROSE_03_004": {
        "prakriyā": "svarūpa_stabilization",
        "ontological_scope": "pāramārthika",
        "adhikāra_level": "uttama",
        "cognitive_mode": "direct_insight",
        "pedagogical_stage": "nididhyāsana",
    },
    "UPADESA_PROSE_03_005": {
        "prakriyā": "svarūpa_stabilization",
        "ontological_scope": "pāramārthika",
        "adhikāra_level": "uttama",
        "cognitive_mode": "direct_insight",
        "pedagogical_stage": "nididhyāsana",
    },
    "UPADESA_PROSE_03_001_A": {
        "prakriyā": "samsara_analysis",
        "ontological_scope": "dual-register",
        "adhikāra_level": "uttama",
        "cognitive_mode": "analytic_contemplative",
        # stage already: discrimination → manana (normalized separately)
    },
    "UPADESA_PROSE_03_002_A": {
        "prakriyā": "samsara_analysis",
        "ontological_scope": "dual-register",
        "adhikāra_level": "uttama",
        "cognitive_mode": "analytic_contemplative",
    },
    "UPADESA_PROSE_03_003_A": {
        "prakriyā": "svarūpa_stabilization",
        "ontological_scope": "pāramārthika",
        "adhikāra_level": "uttama",
        "cognitive_mode": "direct_insight",
    },
    "UPADESA_PROSE_03_004_A": {
        "prakriyā": "svarūpa_stabilization",
        "ontological_scope": "pāramārthika",
        "adhikāra_level": "uttama",
        "cognitive_mode": "direct_insight",
    },
    "UPADESA_PROSE_03_005_A": {
        "prakriyā": "svarūpa_stabilization",
        "ontological_scope": "pāramārthika",
        "adhikāra_level": "uttama",
        "cognitive_mode": "direct_insight",
    },
}


def patch_prose2(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    blocks = list(YAML_BLOCK_RE.finditer(text))
    patches = []

    for match in blocks:
        body = match.group(2)
        try:
            data = yaml.safe_load(body)
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        if any(k in data for k in ('title', 'text_type', 'schema_version', 'macro_prakriyā')):
            continue

        unit_id = data.get('id', '')
        orig_stage = data.get('pedagogical_stage', '')

        # Determine suffix (last 3 digits of id)
        suffix = unit_id[-3:] if len(unit_id) >= 3 else ''

        if suffix in PROSE2_SPECIAL:
            prakriya, scope, cog_mode = PROSE2_SPECIAL[suffix]
        elif orig_stage in PROSE2_STAGE_DEFAULT:
            prakriya, scope, cog_mode = PROSE2_STAGE_DEFAULT[orig_stage]
        else:
            print(f"  UNHANDLED: {unit_id} stage={orig_stage}")
            continue

        new_stage = STAGE_NORM.get(orig_stage, orig_stage)

        # Build new body
        lines = body.split('\n')
        new_lines = []
        inserted = False
        for line in lines:
            # Normalize stage in-place
            if re.match(r'pedagogical_stage\s*:', line):
                line = f'pedagogical_stage: {new_stage}'

            new_lines.append(line)

            # Insert new fields after 'id:' line
            if not inserted and re.match(r'id\s*:', line):
                if 'prakriyā' not in data:
                    new_lines.append(f'prakriyā: {prakriya}')
                if 'ontological_scope' not in data:
                    new_lines.append(f'ontological_scope: {scope}')
                if 'adhikāra_level' not in data:
                    new_lines.append(f'adhikāra_level: uttama')
                if 'cognitive_mode' not in data:
                    new_lines.append(f'cognitive_mode: {cog_mode}')
                inserted = True

        new_body = '\n'.join(new_lines)
        if new_body != body:
            patches.append((match.start(2), match.end(2), new_body))

    if not patches:
        return 0

    result = text
    for start, end, new_body in reversed(patches):
        result = result[:start] + new_body + result[end:]
    filepath.write_text(result, encoding="utf-8")
    return len(patches)


def patch_prose3(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    blocks = list(YAML_BLOCK_RE.finditer(text))
    patches = []

    for match in blocks:
        body = match.group(2)
        try:
            data = yaml.safe_load(body)
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue

        unit_id = data.get('id', '')
        spec = PROSE3_MAP.get(unit_id)
        if not spec:
            print(f"  UNHANDLED prose_3 unit: {unit_id}")
            continue

        orig_stage = data.get('pedagogical_stage', '')

        lines = body.split('\n')
        new_lines = []
        inserted = False
        for line in lines:
            # Normalize stage in-place
            if re.match(r'pedagogical_stage\s*:', line):
                new_stage = STAGE_NORM.get(orig_stage, orig_stage)
                line = f'pedagogical_stage: {new_stage}'
            new_lines.append(line)

            # Insert new fields after 'id:' line
            if not inserted and re.match(r'id\s*:', line):
                for field in ('prakriyā', 'ontological_scope', 'adhikāra_level', 'cognitive_mode'):
                    if field not in data and field in spec:
                        new_lines.append(f'{field}: {spec[field]}')
                # Add pedagogical_stage if missing
                if 'pedagogical_stage' not in data and 'pedagogical_stage' in spec:
                    new_lines.append(f'pedagogical_stage: {spec["pedagogical_stage"]}')
                inserted = True

        new_body = '\n'.join(new_lines)
        if new_body != body:
            patches.append((match.start(2), match.end(2), new_body))

    if not patches:
        return 0

    result = text
    for start, end, new_body in reversed(patches):
        result = result[:start] + new_body + result[end:]
    filepath.write_text(result, encoding="utf-8")
    return len(patches)


if __name__ == "__main__":
    p2 = BASE / "upadesa_prose_2.md"
    p3 = BASE / "upadesa_prose_3.md"

    n2 = patch_prose2(p2)
    print(f"prose_2: {n2} units patched")

    n3 = patch_prose3(p3)
    print(f"prose_3: {n3} units patched")
