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
Add per-mantra AIM YAML blocks to BU adhyāya 3–4 markdown files.

Annotation scheme:
  - Brāhmaṇa-level defaults for all mantras
  - Mantra-level overrides for key passages (antaryāmin, neti-neti, turīya,
    Maitreyī, etc.)
"""

import re
from pathlib import Path

CORPUS_DIR = Path("corpus/upanishads/brihadaranyaka")

# ── Brāhmaṇa-level defaults ──────────────────────────────────────────────────
BRAHMANA_META = {
    (3, 1): dict(
        prakriyā='ritual-cosmological-correspondence',
        pedagogical_role='establish-cosmological-frame',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (3, 2): dict(
        prakriyā='karma-rebirth-inquiry',
        pedagogical_role='establish-karma-liberation-frame',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (3, 3): dict(
        prakriyā='cosmological-ground-inquiry',
        pedagogical_role='point-to-cosmic-foundation',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (3, 4): dict(
        prakriyā='ātman-as-witness-pointing',
        pedagogical_role='direct-recognition-of-witnessing-consciousness',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    (3, 5): dict(
        prakriyā='liberation-through-prajñā',
        pedagogical_role='define-liberation-as-brahman-knowledge',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    (3, 6): dict(
        prakriyā='akāśa-ground-inquiry',
        pedagogical_role='establish-cosmic-weave-metaphor',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (3, 7): dict(
        prakriyā='antaryāmin-revelation',
        pedagogical_role='reveal-inner-controller-as-ātman',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    (3, 8): dict(
        prakriyā='akṣara-brahman-pointing',
        pedagogical_role='establish-imperishable-ground-of-existence',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    (3, 9): dict(
        prakriyā='progressive-negation',
        pedagogical_role='reduce-multiplicity-to-non-dual-ground',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (4, 1): dict(
        prakriyā='sequential-brahman-definitions',
        pedagogical_role='refine-progressive-definitions-of-brahman',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (4, 2): dict(
        prakriyā='ātman-exposition',
        pedagogical_role='direct-teaching-of-ātman-as-pure-consciousness',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    (4, 3): dict(
        prakriyā='avasthā-traya-analysis',
        pedagogical_role='reveal-consciousness-through-three-states',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (4, 4): dict(
        prakriyā='karma-liberation-mechanism',
        pedagogical_role='explain-death-rebirth-and-liberation',
        adhikāra_level='uttama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (4, 5): dict(
        prakriyā='mahāvākya-prakriyā',
        pedagogical_role='establish-ātman-as-all-through-negation-of-other',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    (4, 6): dict(
        prakriyā='guru-paramparā-transmission',
        pedagogical_role='authenticate-teaching-through-lineage',
        adhikāra_level='uttama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
}

# ── Mantra-level overrides ────────────────────────────────────────────────────
# Keyed by mantra_label string e.g. '3.9.26'
MANTRA_OVERRIDES = {
    # 3.7 — antaryāmin: first mantra sets the cosmological frame
    '3.7.1': dict(pedagogical_role='pose-antaryāmin-inquiry'),

    # 3.8 — akṣara: 3.8.8 is the direct witness-consciousness pointing
    '3.8.8': dict(
        pedagogical_role='direct-recognition-of-witness-consciousness',
        cognitive_mode='direct_insight',
    ),
    '3.8.11': dict(
        pedagogical_role='establish-cosmic-imperishable-as-ground-of-all',
    ),
    '3.8.12': dict(
        pedagogical_role='establish-cosmic-imperishable-as-ground-of-all',
    ),

    # 3.9 — progressive reduction of gods
    '3.9.1':  dict(prakriyā='progressive-negation', pedagogical_role='pose-question-how-many-gods'),
    '3.9.2':  dict(prakriyā='progressive-negation', pedagogical_role='reduce-3306-to-33-gods'),
    '3.9.3':  dict(prakriyā='progressive-negation', pedagogical_role='identify-vasus-and-rudras'),
    '3.9.4':  dict(prakriyā='progressive-negation', pedagogical_role='identify-rudras-as-organs'),
    '3.9.5':  dict(prakriyā='progressive-negation', pedagogical_role='identify-ādityas-as-months'),
    '3.9.6':  dict(prakriyā='progressive-negation', pedagogical_role='reduce-to-six-then-three'),
    '3.9.7':  dict(prakriyā='progressive-negation', pedagogical_role='identify-six-as-three-worlds'),
    '3.9.8':  dict(prakriyā='progressive-negation', pedagogical_role='reduce-to-two-then-one'),
    '3.9.9':  dict(prakriyā='progressive-negation', pedagogical_role='resolve-multiplicity-to-one-prāṇa'),
    # 3.9.10-17 — "he who knows that being..."
    '3.9.10': dict(prakriyā='ātman-as-inner-ground-pointing', pedagogical_role='point-to-ātman-as-ground-of-earth', ontological_scope='pāramārthika'),
    '3.9.11': dict(prakriyā='ātman-as-inner-ground-pointing', pedagogical_role='point-to-ātman-as-ground-of-desire', ontological_scope='pāramārthika'),
    '3.9.12': dict(prakriyā='ātman-as-inner-ground-pointing', pedagogical_role='point-to-ātman-as-ground-of-form', ontological_scope='pāramārthika'),
    '3.9.13': dict(prakriyā='ātman-as-inner-ground-pointing', pedagogical_role='point-to-ātman-as-ground-of-ether', ontological_scope='pāramārthika'),
    '3.9.14': dict(prakriyā='ātman-as-inner-ground-pointing', pedagogical_role='point-to-ātman-as-ground-of-darkness', ontological_scope='pāramārthika'),
    '3.9.15': dict(prakriyā='ātman-as-inner-ground-pointing', pedagogical_role='point-to-ātman-as-ground-of-colour', ontological_scope='pāramārthika'),
    '3.9.16': dict(prakriyā='ātman-as-inner-ground-pointing', pedagogical_role='point-to-ātman-as-ground-of-water', ontological_scope='pāramārthika'),
    '3.9.17': dict(prakriyā='ātman-as-inner-ground-pointing', pedagogical_role='point-to-ātman-as-ground-of-generation', ontological_scope='pāramārthika'),
    # 3.9.26 — neti-neti culmination
    '3.9.26': dict(
        prakriyā='neti-neti-negation',
        pedagogical_role='establish-brahman-through-negation-of-all-substrates',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    '3.9.27': dict(prakriyā='neti-neti-negation', pedagogical_role='culminate-inquiry-in-silence'),
    '3.9.28': dict(prakriyā='neti-neti-negation', pedagogical_role='conclude-with-tree-ātman-metaphor', ontological_scope='pāramārthika'),

    # 4.3 — light sequence → self
    '4.3.1':  dict(prakriyā='progressive-withdrawal-to-ātman', pedagogical_role='establish-inquiry-frame'),
    '4.3.2':  dict(prakriyā='progressive-withdrawal-to-ātman', pedagogical_role='point-sun-as-light'),
    '4.3.3':  dict(prakriyā='progressive-withdrawal-to-ātman', pedagogical_role='point-moon-as-light'),
    '4.3.4':  dict(prakriyā='progressive-withdrawal-to-ātman', pedagogical_role='point-fire-as-light'),
    '4.3.5':  dict(prakriyā='progressive-withdrawal-to-ātman', pedagogical_role='point-speech-as-light'),
    '4.3.6':  dict(prakriyā='progressive-withdrawal-to-ātman', pedagogical_role='reveal-ātman-as-ultimate-light', ontological_scope='pāramārthika', cognitive_mode='direct_insight'),
    '4.3.7':  dict(prakriyā='ātman-as-witness-pointing', pedagogical_role='identify-ātman-as-pure-vijñāna', ontological_scope='pāramārthika', cognitive_mode='direct_insight', pedagogical_stage='nididhyāsana'),
    # dream state
    '4.3.8':  dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-jīva-in-waking-state'),
    '4.3.9':  dict(prakriyā='avasthā-traya-analysis', pedagogical_role='introduce-dream-as-third-abode'),
    '4.3.10': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-dream-creation'),
    '4.3.11': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-puruṣa-in-dream'),
    '4.3.12': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-puruṣa-as-immortal-mover'),
    '4.3.13': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-dream-as-projective-consciousness'),
    '4.3.14': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='warn-against-disturbing-dreamer'),
    '4.3.15': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-transition-from-waking'),
    '4.3.16': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-transition-from-dream'),
    '4.3.17': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-transition-to-deep-sleep'),
    # approach to deep sleep
    '4.3.18': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-consciousness-moving-between-states'),
    '4.3.19': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-resting-in-prāṇa', ontological_scope='pāramārthika'),
    '4.3.20': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-hitā-nerves-and-subtle-body'),
    # deep sleep — key mantras
    '4.3.21': dict(
        prakriyā='turīya-pointing',
        pedagogical_role='reveal-pure-consciousness-in-deep-sleep',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    '4.3.22': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='negate-all-dualities-in-deep-sleep', ontological_scope='pāramārthika'),
    '4.3.23': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='explain-witness-in-deep-sleep', ontological_scope='pāramārthika'),
    '4.3.24': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='explain-witness-in-deep-sleep', ontological_scope='pāramārthika'),
    '4.3.25': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='explain-witness-in-deep-sleep', ontological_scope='pāramārthika'),
    '4.3.26': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='explain-witness-in-deep-sleep', ontological_scope='pāramārthika'),
    '4.3.27': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='explain-witness-in-deep-sleep', ontological_scope='pāramārthika'),
    '4.3.28': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='explain-witness-in-deep-sleep', ontological_scope='pāramārthika'),
    '4.3.30': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='explain-witness-in-deep-sleep', ontological_scope='pāramārthika'),
    '4.3.32': dict(
        prakriyā='turīya-pointing',
        pedagogical_role='reveal-ātman-as-one-witness-without-a-second',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    # liberation
    '4.3.33': dict(prakriyā='karma-liberation-mechanism', pedagogical_role='contrast-jīvanmukta-with-worldly'),
    '4.3.34': dict(prakriyā='karma-liberation-mechanism', pedagogical_role='describe-liberation-process'),
    '4.3.35': dict(prakriyā='karma-liberation-mechanism', pedagogical_role='describe-prāṇa-in-liberation'),
    '4.3.36': dict(prakriyā='karma-liberation-mechanism', pedagogical_role='describe-departure-of-vijñāna'),
    '4.3.37': dict(prakriyā='karma-liberation-mechanism', pedagogical_role='describe-prāṇas-gathering-for-liberation'),
    '4.3.38': dict(prakriyā='karma-liberation-mechanism', pedagogical_role='describe-liberation-as-prāṇa-dissolution'),

    # 4.5 — Maitreyī dialogue
    '4.5.1':  dict(prakriyā='adhikāra-discrimination', pedagogical_role='establish-context-of-renunciation', pedagogical_stage='śravaṇa', ontological_scope='vyavahārika'),
    '4.5.2':  dict(prakriyā='adhikāra-discrimination', pedagogical_role='offer-wealth-as-test', pedagogical_stage='śravaṇa', ontological_scope='vyavahārika'),
    '4.5.3':  dict(prakriyā='adhikāra-discrimination', pedagogical_role='reject-wealth-as-path-to-immortality', pedagogical_stage='śravaṇa', ontological_scope='vyavahārika'),
    '4.5.4':  dict(prakriyā='adhikāra-discrimination', pedagogical_role='establish-seekers-question-about-immortality', pedagogical_stage='śravaṇa', ontological_scope='vyavahārika'),
    '4.5.5':  dict(
        prakriyā='mahāvākya-prakriyā',
        pedagogical_role='establish-ātman-as-true-object-of-love',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    '4.5.7':  dict(prakriyā='mahāvākya-prakriyā', pedagogical_role='establish-ātman-as-ground-of-all-roles'),
    '4.5.8':  dict(prakriyā='analogy-based-pointing', pedagogical_role='drum-analogy-for-ātman-as-ground'),
    '4.5.10': dict(prakriyā='analogy-based-pointing', pedagogical_role='vīṇā-analogy-for-ātman-as-ground'),
    '4.5.11': dict(prakriyā='analogy-based-pointing', pedagogical_role='fire-smoke-analogy-for-scripture-as-breath'),
    '4.5.12': dict(prakriyā='analogy-based-pointing', pedagogical_role='ocean-analogy-for-ātman-as-one-goal'),
    '4.5.13': dict(
        prakriyā='analogy-based-pointing',
        pedagogical_role='salt-lump-analogy-for-pure-undifferentiated-ātman',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    '4.5.14': dict(prakriyā='confusion-clarification', pedagogical_role='acknowledge-paradox-of-duality-disappearing'),
    '4.5.15': dict(
        prakriyā='advaita-culmination',
        pedagogical_role='establish-duality-as-condition-for-perception-ātman-as-vijñāna-ghana',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
}


# ── YAML block builder ────────────────────────────────────────────────────────

def yaml_block(meta):
    lines = ['```yaml']
    for k, v in meta.items():
        lines.append(f'{k}: {v}')
    lines.append('```')
    return '\n'.join(lines)


# ── Patch engine ──────────────────────────────────────────────────────────────

HEADING_RE = re.compile(r'^(## Text (\d+)\.(\d+)\.(\d+))\s*$', re.MULTILINE)
AIM_YAML_RE = re.compile(r'```yaml.*?prakriyā:', re.DOTALL)


def patch_file(path, adhyaya, brahmana):
    text = path.read_text(encoding='utf-8')
    default = BRAHMANA_META.get((adhyaya, brahmana))
    if not default:
        print(f"SKIP: no meta for {adhyaya}.{brahmana}")
        return 0

    matches = list(HEADING_RE.finditer(text))
    patched = 0

    for i, m in enumerate(reversed(matches)):
        label = f"{m.group(2)}.{m.group(3)}.{m.group(4)}"
        section_start = m.end()
        # Determine section end
        orig_i = len(matches) - 1 - i
        section_end = matches[orig_i + 1].start() if orig_i + 1 < len(matches) else len(text)
        section = text[section_start:section_end]

        # Skip if already annotated with prakriyā
        if AIM_YAML_RE.search(section):
            continue

        # Build meta for this mantra
        meta = dict(default)
        override = MANTRA_OVERRIDES.get(label, {})
        meta.update(override)

        # Find insertion point: after **Translation** content, before `---`
        sep_match = re.search(r'\n---\s*\n?', section)
        if not sep_match:
            print(f"  WARN: no --- separator in {label}")
            continue

        insert_rel = sep_match.start()  # insert before ---
        insert_abs = section_start + insert_rel

        block = '\n\n' + yaml_block(meta) + '\n'
        text = text[:insert_abs] + block + text[insert_abs:]
        patched += 1

    if patched:
        path.write_text(text, encoding='utf-8')
        print(f"Patched {patched} mantras in {path.name}")
    else:
        print(f"No changes needed: {path.name}")
    return patched


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    total = 0
    for adhyaya in (3, 4):
        for brahmana in range(1, 10):
            path = CORPUS_DIR / f"brihadaranyaka_{adhyaya}_{brahmana}.md"
            if not path.exists():
                continue
            total += patch_file(path, adhyaya, brahmana)
    print(f"\nTotal patched: {total} mantras")
