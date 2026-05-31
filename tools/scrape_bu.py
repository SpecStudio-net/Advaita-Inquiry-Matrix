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
Scrape Bṛhadāraṇyaka Upaniṣad from wisdomlib.org
Source: Swami Mādhavānanda (1950, Advaita Ashrama). Translation only — no commentary.

wisdomlib page structure per mantra:
  <p><strong>Verse 1.2.1</strong></p>
  <blockquote>
    <p>Devanagari Sanskrit ॥ १ ॥</p>
    <p>IAST transliteration || 1 ||</p>
    <p>1. English translation...</p>
  </blockquote>
  <p>Commentary... (skipped)</p>

Produces one markdown file per brāhmaṇa:
  corpus/upanishads/brihadaranyaka/brihadaranyaka_{adhyaya}_{brahmana}.md

Usage:
  python tools/scrape_bu.py
  python tools/scrape_bu.py --dry-run
  python tools/scrape_bu.py --section 1.2    # one section only (for testing)
"""

import re
import time
import argparse
import logging
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE_URL = "https://www.wisdomlib.org"
TOC_URL  = f"{BASE_URL}/hinduism/book/the-brihadaranyaka-upanishad"
HEADERS  = {"User-Agent": "Mozilla/5.0 (compatible; AIM-research-scraper/1.0; educational)"}
DELAY    = 2.0

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# ── HTTP ──────────────────────────────────────────────────────────────────────

def fetch(url):
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except URLError as e:
        raise RuntimeError(f"Fetch failed for {url}: {e}")


# ── TOC parsing ───────────────────────────────────────────────────────────────

ROMAN = {
    'I':1,'II':2,'III':3,'IV':4,'V':5,'VI':6,'VII':7,'VIII':8,'IX':9,'X':10,
    'XI':11,'XII':12,'XIII':13,'XIV':14,'XV':15,
}

def roman_to_int(s):
    return ROMAN.get(s.upper().strip())


def extract_toc_links(html):
    """
    Return ordered list of (adhyaya, brahmana, url).

    TOC labels:
      'Chapter I'       → marks start of adhyāya 1 (skip the link itself)
      'Section II - …'  → brāhmaṇa within current adhyāya
    """
    pattern = re.compile(
        r'<a\s[^>]*href="(/hinduism/book/the-brihadaranyaka-upanishad/d/doc\d+\.html)"[^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE,
    )
    current_chapter = 0
    seen_urls = set()
    results = []

    for href, raw_label in pattern.findall(html):
        label = re.sub(r'<[^>]+>', '', raw_label).strip()
        url = BASE_URL + href
        if url in seen_urls:
            continue
        seen_urls.add(url)

        # "Chapter I" → update adhyāya counter, skip link
        m = re.match(r'^Chapter\s+([IVX]+)$', label, re.IGNORECASE)
        if m:
            ch = roman_to_int(m.group(1))
            if ch:
                current_chapter = ch
            continue

        # "Section II - …" → record (adhyāya, brāhmaṇa, url)
        m = re.match(r'^Section\s+([IVX]+)', label, re.IGNORECASE)
        if m and current_chapter > 0:
            sec = roman_to_int(m.group(1))
            if sec:
                results.append((current_chapter, sec, url))
                logging.debug(f"  TOC: {current_chapter}.{sec} = {label!r}")

    return results


# ── Section page parsing ──────────────────────────────────────────────────────

def strip_tags(html):
    """Remove all HTML tags and collapse whitespace."""
    text = re.sub(r'<[^>]+>', '', html)
    return re.sub(r'\s+', ' ', text).strip()


def has_devanagari(text):
    return bool(re.search(r'[ऀ-ॿ]', text))


def is_iast_verse(text):
    """IAST transliteration ends with the verse-number marker || N || (or variants)."""
    return bool(re.search(r'\|\|\s*\d+\s*\|\|', text))


def extract_mantras(html, adhyaya, brahmana):
    """
    Extract per-mantra dicts from one section page.

    Structure on each wisdomlib BU section page:
      <p><strong>Verse {id}</strong></p>
      <blockquote>
        <p>Sanskrit Devanagari</p>
        <p>IAST transliteration</p>
        <p>N. English translation (N = mantra number)</p>
      </blockquote>
      <p>Commentary...</p>   ← skip
    """
    # Strip script/style noise
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Match: verse label paragraph → immediately following blockquote.
    # Two page variants observed:
    #   <strong>Verse 1.2.1</strong>           (no colon, no <br>)
    #   <strong>Verse 4.5.1:<br />\n</strong>  (colon + <br> inside strong)
    pattern = re.compile(
        r'<p[^>]*>\s*<strong>\s*(?:Verse|Mantra)\s+(\d+\.\d+\.\d+)\s*:?'
        r'(?:\s*<br\s*/?>\s*)?</strong>\s*</p>'
        r'\s*<blockquote[^>]*>(.*?)</blockquote>',
        re.DOTALL | re.IGNORECASE,
    )

    mantras = []
    for m in pattern.finditer(html):
        mantra_id = m.group(1)
        bq_html   = m.group(2)

        # Extract the three paragraphs from the blockquote
        raw_paras = re.findall(r'<p[^>]*>(.*?)</p>', bq_html, re.DOTALL | re.IGNORECASE)
        paras = [strip_tags(p) for p in raw_paras]
        paras = [p for p in paras if p]

        sanskrit_parts = []
        iast_parts = []
        translation_parts = []

        for p in paras:
            if has_devanagari(p):
                sanskrit_parts.append(p)
            elif is_iast_verse(p):
                # IAST ends with || N || verse marker
                iast_parts.append(p)
            else:
                # English translation; strip leading "1. " or "l. " numbering
                clean = re.sub(r'^[\dl]\.\s*', '', p)
                translation_parts.append(clean)

        if not translation_parts:
            logging.warning(f"  Mantra {mantra_id}: no translation found — skipping")
            continue

        mantras.append({
            'id':             mantra_id,
            'sanskrit':       '\n\n'.join(sanskrit_parts),
            'transliteration': '\n\n'.join(iast_parts),
            'translation':    '\n\n'.join(translation_parts),
        })

    # ── Fallback: unlabelled sections (e.g. 5.15 prayer) ──────────────────────
    # Some sections have blockquotes without a preceding "Verse X.Y.Z" label.
    # Treat each blockquote as a sequential mantra.
    if not mantras:
        bq_pattern = re.compile(r'<blockquote[^>]*>(.*?)</blockquote>', re.DOTALL | re.IGNORECASE)
        for seq, bq_m in enumerate(bq_pattern.finditer(html), start=1):
            bq_html = bq_m.group(1)
            raw_paras = re.findall(r'<p[^>]*>(.*?)</p>', bq_html, re.DOTALL | re.IGNORECASE)
            paras = [strip_tags(p) for p in raw_paras]
            paras = [p for p in paras if p]
            if not paras:
                continue
            sanskrit_parts, iast_parts, translation_parts = [], [], []
            for p in paras:
                if has_devanagari(p):
                    sanskrit_parts.append(p)
                elif is_iast_verse(p):
                    iast_parts.append(p)
                else:
                    clean = re.sub(r'^[\dl]\.\s*', '', p)
                    translation_parts.append(clean)
            if not translation_parts and not sanskrit_parts:
                continue
            mantras.append({
                'id':              f"{adhyaya}.{brahmana}.{seq}",
                'sanskrit':        '\n\n'.join(sanskrit_parts),
                'transliteration': '\n\n'.join(iast_parts),
                'translation':     '\n\n'.join(translation_parts),
            })

    return mantras


# ── Markdown generation ───────────────────────────────────────────────────────

FILE_HEADER = """\
# Bṛhadāraṇyaka Upaniṣad — Adhyāya {adhyaya}, Brāhmaṇa {brahmana}

```yaml
text: brihadaranyaka_upanishad
adhyaya: {adhyaya}
brahmana: {brahmana}
source: Swami Mādhavānanda (1950), Advaita Ashrama
```

---
"""


def mantra_to_md(m):
    lines = [f"## Text {m['id']}\n"]
    if m['sanskrit']:
        lines.append(f"**Sanskrit**\n\n{m['sanskrit']}\n")
    if m['transliteration']:
        lines.append(f"**Transliteration**\n\n{m['transliteration']}\n")
    lines.append(f"**Translation**\n\n{m['translation']}\n")
    lines.append("---\n")
    return '\n'.join(lines)


def build_md(adhyaya, brahmana, mantras):
    header = FILE_HEADER.format(adhyaya=adhyaya, brahmana=brahmana)
    return header + '\n'.join(mantra_to_md(m) for m in mantras)


# ── Main ──────────────────────────────────────────────────────────────────────

def scrape(output_dir, dry_run=False, only_section=None):
    output_dir = Path(output_dir)
    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    logging.info(f"Fetching TOC: {TOC_URL}")
    toc_html = fetch(TOC_URL)
    toc_links = extract_toc_links(toc_html)
    logging.info(f"Found {len(toc_links)} section links")

    if not toc_links:
        logging.error("No section links found — check TOC URL or page structure")
        return

    for adhyaya, brahmana, url in sorted(toc_links):
        section_key = f"{adhyaya}.{brahmana}"
        if only_section and section_key != only_section:
            continue

        logging.info(f"Fetching {section_key}: {url}")
        try:
            html = fetch(url)
        except RuntimeError as e:
            logging.error(str(e))
            time.sleep(DELAY)
            continue

        mantras = extract_mantras(html, adhyaya, brahmana)
        logging.info(f"  → {len(mantras)} mantras")

        if not mantras:
            logging.warning(f"  No mantras extracted for {section_key} — skipping")
            time.sleep(DELAY)
            continue

        filename = f"brihadaranyaka_{adhyaya}_{brahmana}.md"
        content  = build_md(adhyaya, brahmana, mantras)

        if dry_run:
            preview = mantras[0]['translation'][:100].replace('\n', ' ')
            logging.info(f"  DRY RUN: would write {filename}")
            logging.info(f"  First mantra: {mantras[0]['id']} — {preview}…")
        else:
            path = output_dir / filename
            path.write_text(content, encoding="utf-8")
            logging.info(f"  Wrote {path}")

        time.sleep(DELAY)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Scrape BU from wisdomlib (translation only)")
    ap.add_argument("--output-dir", default="corpus/upanishads/brihadaranyaka")
    ap.add_argument("--dry-run", action="store_true",
                    help="Fetch and parse but don't write files")
    ap.add_argument("--section", metavar="ADH.BRAH",
                    help="Fetch only one section e.g. 1.2")
    args = ap.parse_args()
    scrape(args.output_dir, dry_run=args.dry_run, only_section=args.section)
