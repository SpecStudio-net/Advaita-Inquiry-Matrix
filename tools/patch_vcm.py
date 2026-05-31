#!/usr/bin/env python3
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
Annotate Vivekacūḍāmaṇi corpus files with AIM schema fields.

Applies two layers:
  1. SECTION_META — verse-range defaults (finer-grained than the parser's broad defaults)
  2. VERSE_OVERRIDES — mantra-level overrides for key philosophical passages

Run from the AIM project root:
  python tools/patch_vcm.py
  python tools/patch_vcm.py --dry-run

The patch is idempotent: re-running will not duplicate YAML blocks.
"""

import re
import sys
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

CORPUS_DIR = Path("corpus/vcm")

# ── Section-level defaults (finer resolution than parser defaults) ─────────────
#
# (adhikara_level, ontological_scope, pedagogical_stage, cognitive_mode, prakriya)
# These apply to verse ranges and override the parser's broad 4-bucket defaults.
#
# VCM arc:
#   1-10:   Preamble — eligibility, rarity of human birth, guru's role
#  11-30:   Foundational viveka — discrimination of self vs. non-self
#  31-66:   Qualifications deepened — vairāgya, śamādi-ṣaṭka, mumukṣutva
#  67-100:  Analysis of the five sheaths (pañcakośa-viveka)
# 101-140:  Direct nature of ātman — witness, pure intelligence
# 141-175:  Māyā, mind, avidyā — obstacles to recognition
# 176-193:  Liberation, jīvanmukti, culmination
#
SECTION_META = {
    # verse_start: (adhikara, scope,            stage,          cog,                  prakriya)
     1: ('sarva',    'dual-register',  'sravana',       'analytic_contemplative', 'adhikari-qualification'),
    11: ('madhyama', 'dual-register',  'sravana',       'analytic_contemplative', 'viveka-vairagya'),
    31: ('madhyama', 'dual-register',  'manana',        'analytic_inquiry',       'shamadi-shatka'),
    67: ('uttama',   'dual-register',  'manana',        'analytic_inquiry',       'pancakosa-viveka'),
   101: ('uttama',   'paramarathika',  'manana',        'analytic_inquiry',       'atman-nature-inquiry'),
   141: ('uttama',   'dual-register',  'manana',        'analytic_inquiry',       'maya-avidya-analysis'),
   176: ('uttama',   'paramarathika',  'nididhyasana',  'direct_insight',         'jivanmukti-description'),
}

def get_section_defaults(verse):
    """Return section defaults for the given verse number."""
    best_start = max(k for k in SECTION_META if k <= verse)
    return SECTION_META[best_start]

# ── Verse-level overrides ─────────────────────────────────────────────────────
#
# Only fields that differ from section defaults need to be specified here.
# Each entry: verse_num → dict of AIM fields.
#
VERSE_OVERRIDES = {
    # ── Mumukṣutva / eligibility cluster ──
    3: dict(
        prakriya='mumukshutva-pointing',
        pedagogical_role='qualification-criterion',
        note='Three rare gifts — human birth, longing for liberation, perfected teacher',
    ),
    5: dict(
        prakriya='samsara-diagnosis',
        pedagogical_role='aversion-arousal',
    ),
    7: dict(
        prakriya='samsara-diagnosis',
        pedagogical_role='aversion-arousal',
        note='Immortality cannot be gained by wealth — śruti reference',
    ),
    9: dict(
        prakriya='atman-as-refuge-pointing',
        pedagogical_stage='manana',
        ontological_scope='paramarathika',
        note='Raise yourself by yourself from the ocean of samsara through discrimination',
    ),

    # ── Guru-upadesa cluster ──
    8: dict(
        prakriya='guru-upadesa',
        pedagogical_role='method-prescription',
        note='The learned man should approach a great guru and abide by his words',
    ),
    15: dict(
        prakriya='guru-upadesa',
        pedagogical_role='method-prescription',
    ),
    19: dict(
        prakriya='guru-upadesa',
        pedagogical_role='method-prescription',
    ),
    25: dict(
        prakriya='guru-upadesa',
        pedagogical_stage='manana',
        pedagogical_role='direct-pointing',
        note='Sraddha in guru and scripture as prerequisite for manana',
    ),

    # ── Viveka definition ──
    20: dict(
        prakriya='viveka-definition',
        pedagogical_stage='sravana',
        ontological_scope='dual-register',
        pedagogical_role='foundational-teaching',
        note='Brahman alone is Real, the universe is unreal — definition of viveka',
    ),

    # ── Sham-adi-shatka (qualifications) cluster ──
    29: dict(
        prakriya='shamadi-shatka',
        pedagogical_role='qualification-criterion',
        note='Calmness and other practices bear fruit only with intense vairagya and mumukshutva',
    ),
    31: dict(
        prakriya='bhakti-as-atma-vichara',
        ontological_scope='paramarathika',
        pedagogical_stage='manana',
        pedagogical_role='direct-pointing',
        note='Bhakti defined as seeking one\'s real nature — highest qualification',
    ),

    # ── Rope-snake analogy ──
    12: dict(
        prakriya='analogy-based-pointing',
        pedagogical_role='analogy',
        note='Rope-snake: conviction of rope\'s reality ends the fear born of the snake',
    ),
    138: dict(
        prakriya='analogy-based-pointing',
        pedagogical_role='analogy',
        note='Rope-snake: ajnana (tamas) causes misidentification of Self with non-Self',
    ),

    # ── Sense-object vairagya ──
    77: dict(
        prakriya='vairagya-arousal',
        pedagogical_role='aversion-arousal',
        note='Sense objects more virulent than poison — even a glance is fatal',
    ),
    80: dict(
        prakriya='vairagya-arousal',
        pedagogical_stage='manana',
        pedagogical_role='method-prescription',
        note='Sword of mature dispassion slays the crocodile of sense-objects',
    ),

    # ── Pañcakośa-viveka (five sheaths) ──
    84: dict(
        prakriya='pancakosa-viveka',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
        pedagogical_role='negation-pointing',
        note='Body is an instrument for realizing Paramātman — not the Self',
    ),
    165: dict(
        prakriya='pancakosa-viveka',
        pedagogical_role='negation-pointing',
        note='Prāṇa-kośa analysis — vital sheath is not the Self',
    ),
    167: dict(
        prakriya='pancakosa-viveka',
        pedagogical_role='negation-pointing',
        note='Manomaya-kośa / vijñānamaya-kośa — cognitive sheaths are not the Self',
    ),
    183: dict(
        prakriya='pancakosa-viveka',
        ontological_scope='paramarathika',
        pedagogical_stage='manana',
        pedagogical_role='negation-pointing',
        note='Manomaya-kośa cannot be Paramātman — has beginning, end, modifications, is an object',
    ),

    # ── Turīya / witness-consciousness pointing ──
    99: dict(
        prakriya='atman-as-witness-pointing',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='direct-pointing',
        note='In dream, the Self shines as witness — uncontaminated by activities of the mind',
    ),
    101: dict(
        prakriya='atman-as-witness-pointing',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='direct-pointing',
        note='Blindness/deafness belong to the eye/ear, not to the witness Self',
    ),
    125: dict(
        prakriya='atman-as-witness-pointing',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='direct-pointing',
        note='Substratum of I-consciousness, witness of the three states, beyond the five sheaths — that is the Ātman',
    ),
    135: dict(
        prakriya='atman-as-witness-pointing',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='direct-pointing',
        note='The Ātman: pure intelligence, without qualities, illumining all material world — different from prakriti',
    ),

    # ── Jīva-Brahman identity direct statement ──
    47: dict(
        prakriya='jiva-brahman-identity',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='direct-pointing',
        note='You are the Supreme Self — bondage is due to association with ignorance alone',
    ),
    56: dict(
        prakriya='advaita-culmination',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='direct-pointing',
        note='Liberation only through realization of the oneness of Brahman and Ātman — not yoga, sankhya, action, or learning',
    ),
    189: dict(
        prakriya='brahman-nature-pointing',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='direct-pointing',
        note='Self is Absolute Knowledge, shines within',
    ),
    192: dict(
        prakriya='adhyasa-inquiry',
        pedagogical_stage='manana',
        ontological_scope='paramarathika',
        pedagogical_role='negation-pointing',
        note='Disciple\'s question: beginningless superimposition — how then is liberation possible?',
    ),

    # ── Māyā analysis ──
    65: dict(
        prakriya='guru-upadesa',
        ontological_scope='dual-register',
        pedagogical_stage='manana',
        pedagogical_role='analogy',
        note='Treasure hidden by earth: pure Truth hidden by Maya, found only through guru + manana + dhyana',
    ),
    123: dict(
        prakriya='mithya-pointing',
        pedagogical_stage='manana',
        ontological_scope='paramarathika',
        pedagogical_role='negation-pointing',
        note='Maya and its effects from mahat to body are asat — unreal',
    ),
    162: dict(
        prakriya='adhyasa-diagnosis',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
        pedagogical_role='negation-pointing',
        note='Scholar with book-learning who misidentifies body-sheaths with Self cannot attain liberation',
    ),

    # ── Mind as obstacle and means ──
    172: dict(
        prakriya='manas-viveka',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
        pedagogical_role='method-prescription',
        note='Mind creates bondage, mind brings liberation — wind gathers and disperses clouds',
    ),
    175: dict(
        prakriya='viveka-vairagya',
        pedagogical_stage='manana',
        ontological_scope='dual-register',
        pedagogical_role='method-prescription',
        note='Discrimination and renunciation purify the mind and qualify it for liberation',
    ),
    176: dict(
        prakriya='manas-viveka',
        pedagogical_stage='nididhyasana',
        ontological_scope='dual-register',
        pedagogical_role='aversion-arousal',
        note='Tiger called mind wanders in forest of sense-objects — seekers should not go there',
    ),
    181: dict(
        prakriya='manas-viveka',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='method-prescription',
        note='Purified mind makes liberation as easy as picking a fruit in the palm',
    ),

    # ── Jīvanmukti / liberation description ──
    150: dict(
        prakriya='jnana-as-means',
        pedagogical_stage='nididhyasana',
        ontological_scope='paramarathika',
        pedagogical_role='analogy',
        note='Moss removed — water seen clearly: jnana removes avidya covering the Self',
    ),
    193: dict(
        prakriya='samsara-inquiry',
        pedagogical_stage='manana',
        ontological_scope='paramarathika',
        pedagogical_role='direct-pointing',
        note='Disciple\'s closing question: if jiva-state is beginningless, how can liberation occur?',
    ),
}

# ── Patch engine ──────────────────────────────────────────────────────────────

HEADING_RE = re.compile(r'^## Text \d+\s*$', re.MULTILINE)


def build_yaml_block(fields):
    lines = ['```yaml']
    for k, v in fields.items():
        if isinstance(v, str):
            safe = v.replace("'", "\\'")
            lines.append(f"  {k}: '{safe}'")
        else:
            lines.append(f"  {k}: {v}")
    lines.append('```')
    return '\n'.join(lines)


def patch_file(filepath, fields, dry_run=False):
    text = filepath.read_text(encoding='utf-8')

    # Find the single mantra section (one per VCM file)
    m = HEADING_RE.search(text)
    if not m:
        logging.warning(f"{filepath.name}: no heading found — skipping")
        return False

    # Idempotency check
    if 'prakriya:' in text:
        logging.debug(f"{filepath.name}: already annotated — skipping")
        return False

    # Insert YAML block before the '---' separator that closes the mantra
    sep_pos = text.rfind('\n---\n')
    if sep_pos == -1:
        logging.warning(f"{filepath.name}: no closing --- found — skipping")
        return False

    yaml_block = build_yaml_block(fields)
    new_text = text[:sep_pos] + '\n\n' + yaml_block + text[sep_pos:]

    if dry_run:
        logging.info(f"DRY RUN: would patch {filepath.name}")
        return True

    filepath.write_text(new_text, encoding='utf-8')
    return True


def patch_all(dry_run=False):
    files = sorted(CORPUS_DIR.glob('vivekacudamani_*.md'))
    patched = 0
    skipped = 0

    for filepath in files:
        # Parse verse number from filename
        m = re.search(r'vivekacudamani_(\d+)\.md', filepath.name)
        if not m:
            continue
        verse = int(m.group(1))

        # Build fields: start from section defaults, then apply overrides
        adhikara, scope, stage, cog, prakriya = get_section_defaults(verse)
        fields = {
            'adhikara_level':    adhikara,
            'ontological_scope': scope,
            'pedagogical_stage': stage,
            'cognitive_mode':    cog,
            'prakriya':          prakriya,
        }

        if verse in VERSE_OVERRIDES:
            fields.update(VERSE_OVERRIDES[verse])

        if patch_file(filepath, fields, dry_run):
            patched += 1
            logging.info(f"Patched verse {verse:3d}: prakriya={fields.get('prakriya')}")
        else:
            skipped += 1

    logging.info(f"Done — {patched} patched, {skipped} skipped")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Annotate VCM corpus with AIM schema fields')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    patch_all(dry_run=args.dry_run)
