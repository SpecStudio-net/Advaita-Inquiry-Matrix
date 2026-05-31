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
Add per-mantra AIM YAML blocks to BU adhyāya 1–2 and 5–6 markdown files.
"""

import re
from pathlib import Path

CORPUS_DIR = Path("corpus/upanishads/brihadaranyaka")

# ── Brāhmaṇa-level defaults ──────────────────────────────────────────────────
BRAHMANA_META = {
    # ── Adhyāya 1: cosmogonic/upāsanā ──────────────────────────────────────
    (1, 1): dict(
        prakriyā='cosmological-upāsanā-meditation',
        pedagogical_role='establish-sacrificial-horse-as-cosmic-body',
        adhikāra_level='sarva',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='vyavahārika',
    ),
    (1, 2): dict(
        prakriyā='cosmogonic-narration',
        pedagogical_role='narrate-creation-through-death-and-desire',
        adhikāra_level='sarva',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (1, 3): dict(
        prakriyā='prāṇa-supremacy-upāsanā',
        pedagogical_role='establish-prāṇa-as-victor-over-all-faculties',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (1, 4): dict(
        prakriyā='ātman-as-primal-self-narration',
        pedagogical_role='reveal-ātman-as-primal-ground-of-creation',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (1, 5): dict(
        prakriyā='tripartite-cosmos-upāsanā',
        pedagogical_role='establish-prāṇa-as-cosmic-sustainer',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (1, 6): dict(
        prakriyā='tripartite-cosmos-upāsanā',
        pedagogical_role='establish-three-aspects-of-cosmos-as-prāṇa',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    # ── Adhyāya 2: mixed upāsanā and inquiry ───────────────────────────────
    (2, 1): dict(
        prakriyā='upāsanā-correction',
        pedagogical_role='expose-limits-of-object-meditations-on-brahman',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (2, 2): dict(
        prakriyā='prāṇa-description-upāsanā',
        pedagogical_role='describe-prāṇa-as-cosmic-body',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (2, 3): dict(
        prakriyā='saguṇa-nirguṇa-brahman-distinction',
        pedagogical_role='distinguish-formed-and-formless-brahman',
        adhikāra_level='uttama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (2, 4): dict(
        prakriyā='mahāvākya-prakriyā',
        pedagogical_role='establish-ātman-as-sole-object-of-love',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    (2, 5): dict(
        prakriyā='madhu-vidyā-upāsanā',
        pedagogical_role='establish-mutual-interdependence-as-honey',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (2, 6): dict(
        prakriyā='guru-paramparā-transmission',
        pedagogical_role='authenticate-teaching-through-lineage',
        adhikāra_level='sarva',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    # ── Adhyāya 5: short upāsanā brāhmaṇas ────────────────────────────────
    (5, 1): dict(
        prakriyā='pūrṇatva-pointing',
        pedagogical_role='reveal-brahman-as-infinite-fullness',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    (5, 2): dict(
        prakriyā='ethical-discipline-instruction',
        pedagogical_role='prescribe-dama-dana-daya-as-inner-discipline',
        adhikāra_level='sarva',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='vyavahārika',
    ),
    (5, 3): dict(
        prakriyā='brahman-as-heart-upāsanā',
        pedagogical_role='identify-hṛdaya-as-brahman',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (5, 4): dict(
        prakriyā='satya-brahman-upāsanā',
        pedagogical_role='identify-satya-as-brahman',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (5, 5): dict(
        prakriyā='satya-brahman-upāsanā',
        pedagogical_role='establish-satya-brahman-in-solar-orb-and-eye',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (5, 6): dict(
        prakriyā='mind-brahman-upāsanā',
        pedagogical_role='identify-brahman-as-resplendent-mind-within',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (5, 7): dict(
        prakriyā='lightning-brahman-upāsanā',
        pedagogical_role='identify-brahman-as-lightning-dispelling-darkness',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (5, 8): dict(
        prakriyā='vedic-speech-upāsanā',
        pedagogical_role='identify-vedic-speech-as-cow-sustaining-all',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (5, 9): dict(
        prakriyā='vaiśvānara-upāsanā',
        pedagogical_role='identify-digestive-fire-as-vaiśvānara-brahman',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (5, 10): dict(
        prakriyā='cosmic-path-upāsanā',
        pedagogical_role='establish-post-mortem-path-through-cosmic-fire',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (5, 11): dict(
        prakriyā='tapas-upāsanā',
        pedagogical_role='identify-illness-as-highest-austerity',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (5, 12): dict(
        prakriyā='food-prāṇa-brahman-inquiry',
        pedagogical_role='refute-food-and-prāṇa-as-ultimate-brahman',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (5, 13): dict(
        prakriyā='prāṇa-cosmic-identity',
        pedagogical_role='identify-prāṇa-with-vedic-hymns-and-kṣatra',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (5, 14): dict(
        prakriyā='gāyatrī-upāsanā',
        pedagogical_role='identify-gāyatrī-as-foundation-of-all-worlds',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
    (5, 15): dict(
        prakriyā='soham-liberation-prayer',
        pedagogical_role='identify-self-with-solar-puruṣa-through-prayer',
        adhikāra_level='uttama',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    # ── Adhyāya 6: concluding brāhmaṇas ────────────────────────────────────
    (6, 1): dict(
        prakriyā='prāṇa-supremacy-inquiry',
        pedagogical_role='establish-prāṇa-as-supreme-among-faculties',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (6, 2): dict(
        prakriyā='pañcāgni-vidyā',
        pedagogical_role='reveal-rebirth-mechanism-through-five-fires',
        adhikāra_level='madhyama',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    (6, 3): dict(
        prakriyā='karmakāṇḍa-instruction',
        pedagogical_role='prescribe-rites-for-worldly-attainment',
        adhikāra_level='sarva',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='vyavahārika',
    ),
    (6, 4): dict(
        prakriyā='karmakāṇḍa-instruction',
        pedagogical_role='prescribe-conception-and-birth-rites',
        adhikāra_level='sarva',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='vyavahārika',
    ),
    (6, 5): dict(
        prakriyā='guru-paramparā-transmission',
        pedagogical_role='authenticate-teaching-through-lineage',
        adhikāra_level='sarva',
        cognitive_mode='analytic_contemplative',
        pedagogical_stage='śravaṇa',
        ontological_scope='dual-register',
    ),
}

# ── Mantra-level overrides ────────────────────────────────────────────────────
MANTRA_OVERRIDES = {
    # 1.2 — cosmogony with self-identification
    '1.2.6': dict(prakriyā='ritual-self-identification', pedagogical_role='describe-prajāpati-sacrificing-himself'),
    '1.2.7': dict(prakriyā='ritual-self-identification', pedagogical_role='establish-body-as-sacrifice-soham'),

    # 1.3 — prāṇa carries faculties beyond death
    '1.3.7':  dict(pedagogical_role='establish-prāṇa-as-victor-over-asuras'),
    '1.3.8':  dict(prakriyā='prāṇa-as-liberator', pedagogical_role='identify-prāṇa-as-Ayāsya'),
    '1.3.9':  dict(prakriyā='prāṇa-as-liberator', pedagogical_role='establish-prāṇa-as-beyond-death'),
    '1.3.10': dict(prakriyā='prāṇa-as-liberator', pedagogical_role='describe-prāṇa-removing-evil-from-faculties'),
    '1.3.17': dict(prakriyā='prāṇa-cosmological-identity', pedagogical_role='establish-prāṇa-as-enjoyer-of-all-food'),

    # 1.4 — key mantras
    '1.4.7':  dict(prakriyā='nāmarūpa-viveka', pedagogical_role='distinguish-nāma-rūpa-as-differentiation-of-brahman'),
    '1.4.8':  dict(
        prakriyā='ātman-as-innate-love-pointing',
        pedagogical_role='reveal-ātman-as-dearest-of-all',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    '1.4.10': dict(
        prakriyā='aham-brahma-asmi-mahāvākya',
        pedagogical_role='declare-aham-brahmasmi-as-primal-recognition',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    '1.4.17': dict(
        prakriyā='ātman-as-innate-love-pointing',
        pedagogical_role='reveal-ātman-as-source-of-all-longing',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),

    # 2.1 — Gārgya-Ajātaśatru dialogue
    '2.1.1':  dict(prakriyā='upāsanā-correction', pedagogical_role='establish-proud-teacher-as-student'),
    '2.1.14': dict(prakriyā='adhikāra-reversal', pedagogical_role='acknowledge-limits-of-object-meditations'),
    '2.1.15': dict(prakriyā='adhikāra-reversal', pedagogical_role='reverse-teacher-student-roles'),
    '2.1.16': dict(
        prakriyā='avasthā-traya-analysis',
        pedagogical_role='describe-deep-sleep-return-to-prāṇa',
        cognitive_mode='analytic_inquiry',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
    ),
    '2.1.17': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-ātman-absorbing-faculties-in-sleep'),
    '2.1.18': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-dream-as-ātman-projections'),
    '2.1.19': dict(prakriyā='avasthā-traya-analysis', pedagogical_role='describe-return-from-deep-sleep'),
    '2.1.20': dict(
        prakriyā='ātman-as-source-of-creation-pointing',
        pedagogical_role='reveal-ātman-as-self-projecting-ground-through-spider-analogy',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),

    # 2.3 — neti neti culmination
    '2.3.6':  dict(
        prakriyā='neti-neti-negation',
        pedagogical_role='establish-brahman-as-beyond-all-description-neti-neti',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),

    # 2.4 — Maitreyī I (parallel to 4.5)
    '2.4.1':  dict(prakriyā='adhikāra-discrimination', pedagogical_role='establish-context-of-renunciation', pedagogical_stage='śravaṇa', ontological_scope='vyavahārika'),
    '2.4.2':  dict(prakriyā='adhikāra-discrimination', pedagogical_role='reject-wealth-as-path-to-immortality', pedagogical_stage='śravaṇa', ontological_scope='vyavahārika'),
    '2.4.3':  dict(prakriyā='adhikāra-discrimination', pedagogical_role='establish-seekers-question-about-immortality', pedagogical_stage='śravaṇa', ontological_scope='vyavahārika'),
    '2.4.4':  dict(prakriyā='adhikāra-discrimination', pedagogical_role='affirm-maitreyī-as-qualified-seeker', pedagogical_stage='śravaṇa', ontological_scope='vyavahārika'),
    '2.4.5':  dict(
        prakriyā='mahāvākya-prakriyā',
        pedagogical_role='establish-ātman-as-true-object-of-love',
    ),
    '2.4.7':  dict(prakriyā='analogy-based-pointing', pedagogical_role='drum-analogy-for-ātman-as-ground'),
    '2.4.8':  dict(prakriyā='analogy-based-pointing', pedagogical_role='conch-analogy-for-ātman-as-ground'),
    '2.4.9':  dict(prakriyā='analogy-based-pointing', pedagogical_role='vīṇā-analogy-for-ātman-as-ground'),
    '2.4.10': dict(prakriyā='analogy-based-pointing', pedagogical_role='fire-smoke-analogy-for-scripture-as-breath'),
    '2.4.11': dict(prakriyā='analogy-based-pointing', pedagogical_role='ocean-analogy-for-ātman-as-one-goal'),
    '2.4.12': dict(
        prakriyā='analogy-based-pointing',
        pedagogical_role='salt-lump-analogy-for-pure-undifferentiated-ātman',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),
    '2.4.13': dict(prakriyā='confusion-clarification', pedagogical_role='acknowledge-paradox-of-duality-disappearing'),
    '2.4.14': dict(
        prakriyā='advaita-culmination',
        pedagogical_role='establish-duality-as-condition-for-perception-ātman-as-prajñāna-ghana',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),

    # 2.5 — honey doctrine culmination
    '2.5.15': dict(
        prakriyā='ātman-as-sovereign-ground',
        pedagogical_role='reveal-ātman-as-king-underlying-all-honey-relations',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),

    # 5.1 — pūrṇa mantra
    '5.1.1':  dict(
        prakriyā='pūrṇatva-pointing',
        pedagogical_role='establish-brahman-as-pūrṇa-fullness-beyond-addition-and-subtraction',
    ),

    # 5.14 — Gāyatrī and turīya foot
    '5.14.4': dict(
        prakriyā='turīya-pointing',
        pedagogical_role='identify-fourth-foot-of-gāyatrī-as-supramundane-brahman',
        cognitive_mode='direct_insight',
        pedagogical_stage='nididhyāsana',
        ontological_scope='pāramārthika',
    ),

    # 5.15 — soham prayer
    '5.15.1': dict(
        prakriyā='soham-liberation-prayer',
        pedagogical_role='identify-dying-self-with-solar-puruṣa-sohamasmi',
    ),

    # 6.2 — pañcāgni vidyā key mantras
    '6.2.8':  dict(prakriyā='pañcāgni-vidyā', pedagogical_role='introduce-five-fire-doctrine'),
    '6.2.9':  dict(prakriyā='pañcāgni-vidyā', pedagogical_role='describe-heaven-as-first-fire'),
    '6.2.10': dict(prakriyā='pañcāgni-vidyā', pedagogical_role='describe-cloud-as-second-fire'),
    '6.2.11': dict(prakriyā='pañcāgni-vidyā', pedagogical_role='describe-earth-as-third-fire'),
    '6.2.12': dict(prakriyā='pañcāgni-vidyā', pedagogical_role='describe-man-as-fourth-fire'),
    '6.2.13': dict(prakriyā='pañcāgni-vidyā', pedagogical_role='describe-woman-as-fifth-fire'),
    '6.2.14': dict(prakriyā='pañcāgni-vidyā', pedagogical_role='describe-liberation-through-offering'),
    '6.2.15': dict(
        prakriyā='devayāna-liberation-path',
        pedagogical_role='establish-path-of-no-return-for-brahman-knowers',
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
        orig_i = len(matches) - 1 - i
        section_start = m.end()
        section_end = matches[orig_i + 1].start() if orig_i + 1 < len(matches) else len(text)
        section = text[section_start:section_end]

        if AIM_YAML_RE.search(section):
            continue

        meta = dict(default)
        meta.update(MANTRA_OVERRIDES.get(label, {}))

        sep_match = re.search(r'\n---\s*\n?', section)
        if not sep_match:
            print(f"  WARN: no --- in {label}")
            continue

        insert_abs = section_start + sep_match.start()
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
    for adhyaya, brahmana_range in [(1, range(1, 7)), (2, range(1, 7)),
                                     (5, range(1, 16)), (6, range(1, 6))]:
        for brahmana in brahmana_range:
            path = CORPUS_DIR / f"brihadaranyaka_{adhyaya}_{brahmana}.md"
            if not path.exists():
                continue
            total += patch_file(path, adhyaya, brahmana)
    print(f"\nTotal patched: {total} mantras")
