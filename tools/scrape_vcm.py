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
Extract Vivekacūḍāmaṇi from Keynote HTML export.

Each Keynote HTML export stores one PDF per slide in UUID subdirectories.
header.json gives the slide order. Each verse has ~3 slides:
  1. Intro: chandas label + Sanskrit + IAST  (em-dash count low, no English prose)
  2. Padānvaya: word-by-word analysis        (em-dash count high)
  3. Translation: Sanskrit + IAST + English  (em-dash count low, has English prose)

Parts cover verse ranges:
  Part 1: 1-66    (169 slides)
  Part 2: 67-136  (195 slides)
  Part 3: 137-193 (159 slides)

Output: corpus/vcm/vivekacudamani_{verse:03d}.md  (one file per verse)

Usage:
  python tools/scrape_vcm.py
  python tools/scrape_vcm.py --dry-run
  python tools/scrape_vcm.py --verse 8   # single verse for testing
"""

import re
import json
import logging
import argparse
from pathlib import Path

try:
    from pdfminer.high_level import extract_text
except ImportError:
    raise SystemExit("pdfminer.six required: pip3 install pdfminer.six")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PARTS = [
    "/Users/adyasaktisvami/Documents/Vivkekacūḍāmaṇiḥ/HTML/Vivekacūḍāmaṇiḥ Part 1",
    "/Users/adyasaktisvami/Documents/Vivkekacūḍāmaṇiḥ/HTML/Vivekacūḍāmaṇiḥ Part 2",
    "/Users/adyasaktisvami/Documents/Vivkekacūḍāmaṇiḥ/HTML/Vivekacūḍāmaṇiḥ Part 3",
]

OUTPUT_DIR = "corpus/vcm"

FILE_HEADER = """\
# Vivekacūḍāmaṇi — Verse {verse}

```yaml
text: vivekacudamani
verse: {verse}
source: Swami Mādhavānanda, Advaita Ashrama
```

---

## Text {verse}

**Sanskrit**

{sanskrit}

**Transliteration**

{iast}

**Translation**

{translation}

---
"""


# ── helpers ──────────────────────────────────────────────────────────────────

def has_devanagari(text):
    return bool(re.search(r'[ऀ-ॿ]', text))


def verse_nums(text):
    return [int(n) for n in re.findall(r'\|\|\s*(\d+)\s*\|\|', text)]


def em_dash_count(text):
    return len(re.findall(r'[\wāīūṭḍṇṣśñḥṃḷṝṚ]+—', text))


def is_chandas_label(line):
    return bool(re.search(r'\bchandas\b', line))


def is_iast_line(line):
    """IAST lines start with lowercase and contain diacritic characters (ā, ī, ū, etc.)."""
    return bool(re.match(r'^[a-z]', line) and re.search(r'[āīūṭḍṇṣśñḥṃḷṝṚ]', line))


def extract_translation_text(after_iast):
    """
    Extract English prose from the text that follows the IAST marker.
    Stops at the next verse's Devanagari, chandas label, IAST marker,
    or any IAST-looking line (signals we are in a padānvaya slide, not translation).
    Strips surrounding quotation marks if present.
    """
    lines = []
    for raw in after_iast.split('\n'):
        line = raw.strip()
        if not line:
            continue
        if has_devanagari(line):
            break
        if is_chandas_label(line):
            break
        if re.search(r'\|\|\s*\d+\s*\|\|', line):
            break
        # An IAST-looking line after the marker means we're in a padānvaya slide
        if is_iast_line(line):
            break
        # Section headings (e.g. "Attaining Yogārūdha") are short lines without sentence-ending punctuation
        if len(line.split()) <= 4 and not re.search(r'[.!?;,]$', line) and re.match(r'^[A-Z]', line):
            break
        lines.append(line)

    text = ' '.join(lines).strip()
    # Strip surrounding quotes added by the Keynote template
    text = re.sub(r'^["""]+|["""]+$', '', text).strip()
    return text


def classify_and_extract(text, verse_num):
    """
    Returns (slide_type, sanskrit, iast, translation) for a given verse number.
    slide_type: 'translation' | 'padanvaya' | 'intro' | 'header'
    """
    nums = verse_nums(text)
    if not nums:
        return 'header', '', '', ''

    # Split on the IAST marker for this verse
    marker_re = re.compile(rf'\|\|\s*{verse_num}\s*\|\|')
    split = marker_re.split(text, maxsplit=1)
    if len(split) < 2:
        # Verse marker not found — likely padānvaya with repeated markers
        if em_dash_count(text) > 5:
            return 'padanvaya', '', '', ''
        return 'intro', '', '', ''

    before, after = split[0], split[1]

    # Extract translation from after block (stops at chandas/Devanagari/next marker)
    translation = extract_translation_text(after)
    if not translation:
        return 'intro', '', '', ''

    # Check em-dashes only in the extracted translation (not the full slide).
    # Padānvaya definitions always have Sanskrit-word—meaning pairs; prose translations don't.
    if em_dash_count(translation) > 2:
        return 'padanvaya', '', '', ''

    # Extract Sanskrit (Devanagari lines from before block)
    deva_lines = [l.strip() for l in before.split('\n')
                  if has_devanagari(l) and l.strip()]
    sanskrit = '\n'.join(deva_lines)

    # Extract IAST (non-Devanagari, non-header lines from before block)
    iast_lines = []
    for l in before.split('\n'):
        l = l.strip()
        if not l:
            continue
        if has_devanagari(l):
            continue
        if is_chandas_label(l):
            continue
        if re.match(r'^(Invocation|Attaining|Part|Section|Chapter)', l, re.IGNORECASE):
            continue
        # Must look like IAST (contains diacritic chars or starts with lowercase)
        if re.search(r'[āīūṭḍṇṣśñḥṃḷṝṚ]', l) or re.match(r'^[a-z]', l):
            iast_lines.append(l)

    iast = '\n'.join(iast_lines).strip()
    # Append the closing marker
    if iast:
        iast += f' || {verse_num} ||'

    return 'translation', sanskrit, iast, translation


# ── main extraction ───────────────────────────────────────────────────────────

def load_all_slides():
    """
    Returns ordered list of (part_num, slide_idx, text) for all slides across parts.
    Only slides whose PDFs exist are included.
    """
    slides = []
    for part_num, part_path in enumerate(PARTS, 1):
        base = Path(part_path) / 'assets'
        with open(base / 'header.json') as f:
            header = json.load(f)

        for slide_idx, uid in enumerate(header['slideList'], 1):
            pdf = base / uid / 'assets' / f'{uid}.pdf'
            if not pdf.exists():
                logging.warning(f"Part {part_num} slide {slide_idx}: no PDF ({uid})")
                continue
            try:
                text = extract_text(str(pdf))
            except Exception as e:
                logging.warning(f"Part {part_num} slide {slide_idx}: extract failed — {e}")
                continue
            slides.append((part_num, slide_idx, text))

    return slides


def build_verse_map(slides):
    """
    Returns {verse_num: {'sanskrit': str, 'iast': str, 'translation': str}}.
    For each verse, prefers the translation slide; fills missing Sanskrit from
    other slides that contain the same verse number.
    """
    # Pass 1: collect translation slides
    verse_map = {}
    sanskrit_pool = {}  # verse_num → list of Sanskrit strings

    for part_num, slide_idx, text in slides:
        nums = verse_nums(text)
        if not nums:
            continue

        primary = min(nums)

        # Collect Sanskrit from any slide containing this verse
        deva_lines = [l.strip() for l in text.split('\n')
                      if has_devanagari(l) and l.strip()]
        if deva_lines:
            sanskrit_pool.setdefault(primary, [])
            sanskrit_pool[primary].append('\n'.join(deva_lines))

        slide_type, sanskrit, iast, translation = classify_and_extract(text, primary)

        if slide_type == 'translation':
            if primary not in verse_map:
                verse_map[primary] = {'sanskrit': sanskrit, 'iast': iast, 'translation': translation}
                logging.info(f"  Verse {primary}: extracted from part {part_num} slide {slide_idx}")
            else:
                # Keep if existing translation is empty
                if not verse_map[primary]['translation']:
                    verse_map[primary]['translation'] = translation
                if not verse_map[primary]['iast'] and iast:
                    verse_map[primary]['iast'] = iast

    # Pass 2: fill missing Sanskrit from pool
    for verse_num, data in verse_map.items():
        if not data['sanskrit'] and verse_num in sanskrit_pool:
            # Take the longest Sanskrit block (most complete)
            data['sanskrit'] = max(sanskrit_pool[verse_num], key=len)

    return verse_map


def write_verse(verse_num, data, output_dir, dry_run=False):
    sanskrit = data['sanskrit'].strip()
    iast = data['iast'].strip()
    translation = data['translation'].strip()

    if not translation:
        logging.warning(f"Verse {verse_num}: no translation — skipping")
        return False

    content = FILE_HEADER.format(
        verse=verse_num,
        sanskrit=sanskrit or '(Sanskrit not extracted)',
        iast=iast or '(IAST not extracted)',
        translation=translation,
    )

    filename = f"vivekacudamani_{verse_num:03d}.md"
    if dry_run:
        preview = translation[:80].replace('\n', ' ')
        logging.info(f"  DRY RUN: {filename} → {preview}…")
        return True

    path = output_dir / filename
    path.write_text(content, encoding='utf-8')
    logging.info(f"  Wrote {path}")
    return True


def scrape(dry_run=False, only_verse=None):
    output_dir = Path(OUTPUT_DIR)
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    logging.info("Loading slides from all 3 parts…")
    slides = load_all_slides()
    logging.info(f"Loaded {len(slides)} slides total")

    logging.info("Building verse map…")
    verse_map = build_verse_map(slides)
    logging.info(f"Found {len(verse_map)} verses")

    written = 0
    for verse_num in sorted(verse_map):
        if only_verse is not None and verse_num != only_verse:
            continue
        if write_verse(verse_num, verse_map[verse_num], output_dir, dry_run):
            written += 1

    logging.info(f"Done — {written} verses written")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="Extract VCM from Keynote HTML export")
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--verse', type=int, metavar='N', help='Extract single verse for testing')
    args = ap.parse_args()
    scrape(dry_run=args.dry_run, only_verse=args.verse)
