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

import re
import json
import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class UpadesaMetricalParser:
    # Matches: ## Text 13.1  or  ## Text 13.2-3
    HEADING_RE = re.compile(r'^## Text (\d+)\.(\d+(?:-\d+)?)\s*$', re.MULTILINE)

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.text = self.filepath.read_text(encoding="utf-8")
        self.units = []
        self._structure = 'A' if '```yaml' in self.text else 'B'

    # ---------- Public ----------

    def parse(self):
        if self._structure == 'A':
            self._parse_a()
        else:
            self._parse_b()
        return self.units

    # ---------- Structure A: fenced YAML after heading ----------

    def _parse_a(self):
        matches = list(self.HEADING_RE.finditer(self.text))
        for i, m in enumerate(matches):
            chapter = int(m.group(1))
            verse_str = m.group(2)
            verse = int(verse_str.split('-')[0])

            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)
            chunk = self.text[start:end]

            meta = {}
            yaml_m = re.search(r'```yaml\s*\n(.*?)```', chunk, re.DOTALL)
            if yaml_m:
                try:
                    raw = yaml.safe_load(yaml_m.group(1)) or {}
                    tags = raw.get('text_tags', raw)
                    meta = self._normalize_meta(tags)
                except yaml.YAMLError as e:
                    logging.warning(f"YAML error at {chapter}.{verse_str}: {e}")

            unit = self._build_unit(chapter, verse, verse_str, chunk, meta)
            if unit:
                self.units.append(unit)
                logging.info(f"Parsed {unit['id']}")

    # ---------- Structure B: inline text_tags before heading ----------

    def _parse_b(self):
        matches = list(self.HEADING_RE.finditer(self.text))
        for i, m in enumerate(matches):
            chapter = int(m.group(1))
            verse_str = m.group(2)
            verse = int(verse_str.split('-')[0])

            # Content: after the heading until the next heading
            content_start = m.end()
            content_end = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)
            chunk = self.text[content_start:content_end]

            # Preamble: from end of previous heading to start of this heading
            prev_end = matches[i - 1].end() if i > 0 else 0
            preamble = self.text[prev_end:m.start()]

            meta = self._extract_meta_b(preamble)

            unit = self._build_unit(chapter, verse, verse_str, chunk, meta)
            if unit:
                self.units.append(unit)
                logging.info(f"Parsed {unit['id']}")

    def _extract_meta_b(self, preamble):
        idx = preamble.rfind('text_tags:')
        if idx == -1:
            return {}
        block = preamble[idx:].strip()
        try:
            raw = yaml.safe_load(block) or {}
            tags = raw.get('text_tags', {}) if isinstance(raw, dict) else {}
            return self._normalize_meta(tags) if isinstance(tags, dict) else {}
        except yaml.YAMLError:
            return {}

    # ---------- Chapter-level enrichment ----------

    # Inferred from adhikāra_level labels and chapter-level metadata in source files.
    # Chapters 11-13 have explicit chapter YAML (dominant_prakriya, ontological_focus)
    # confirming pāramārthika / nididhyāsana. Chapters 1-10 are inferred from their
    # adhikari_level label: beginner=śravaṇa, intermediate=manana, advanced/stabilization=nididhyāsana.
    _CHAPTER_DEFAULTS = {
        # ch: (adhikāra_level,      ontological_scope, pedagogical_stage,  cognitive_mode)
        1:  ('beginner',       'dual-register',   'śravaṇa',         'analytic_contemplative'),
        2:  ('intermediate',   'dual-register',   'manana',           'analytic_contemplative'),
        3:  ('intermediate',   'dual-register',   'manana',           'analytic_contemplative'),
        4:  ('advanced',       'dual-register',   'nididhyāsana',    'contemplative_analysis'),
        5:  ('beginner',       'dual-register',   'śravaṇa',         'analytic_contemplative'),
        6:  ('intermediate',   'dual-register',   'manana',           'analytic_contemplative'),
        7:  ('advanced',       'dual-register',   'nididhyāsana',    'contemplative_analysis'),
        8:  ('advanced',       'dual-register',   'nididhyāsana',    'contemplative_analysis'),
        9:  ('stabilization',  'pāramārthika',    'nididhyāsana',    'direct_insight'),
        10: ('stabilization',  'pāramārthika',    'nididhyāsana',    'direct_insight'),
        11: ('uttama',         'pāramārthika',    'nididhyāsana',    'direct_insight'),
        12: ('uttama',         'pāramārthika',    'nididhyāsana',    'direct_insight'),
        13: ('uttama',         'pāramārthika',    'nididhyāsana',    'direct_insight'),
    }

    def _enrich(self, unit):
        ch = unit['chapter']
        defaults = self._CHAPTER_DEFAULTS.get(ch)
        if not defaults:
            return unit
        adhikara, scope, stage, cog = defaults
        unit.setdefault('adhikāra_level', adhikara)
        unit.setdefault('ontological_scope', scope)
        unit.setdefault('pedagogical_stage', stage)
        unit.setdefault('cognitive_mode', cog)
        return unit

    # ---------- Shared helpers ----------

    def _normalize_meta(self, tags):
        meta = {}
        if 'prakriya' in tags:
            meta['prakriyā'] = tags['prakriya']
        if 'adhikari_level' in tags:
            meta['adhikāra_level'] = tags['adhikari_level']
        if 'operation' in tags:
            meta['operation'] = tags['operation']
        return meta

    def _build_unit(self, chapter, verse, verse_str, chunk, meta):
        translation = self._extract_section(chunk, 'Translation')
        if not translation:
            logging.warning(f"Chapter {chapter} verse {verse_str}: missing translation")
            return None

        sanskrit = self._extract_section(chunk, 'Sanskrit')
        transliteration = self._extract_section(chunk, 'Transliteration')

        unit = {
            'id': f"UPADESA_METRICAL_{chapter:02d}_{verse:03d}",
            'chapter': chapter,
            'verse': verse,
            'verse_label': verse_str,
            'sanskrit': self._clean(sanskrit),
            'transliteration': self._clean(transliteration),
            'translation': self._clean(translation),
            **meta,
            'status': 'VERIFIED',
        }
        return self._enrich(unit)

    def _extract_section(self, chunk, label):
        pattern = rf'\*\*{label}\*\*\s*(.*?)(?=\n\*\*|\n---|\n```|\Z)'
        m = re.search(pattern, chunk, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ''

    def _clean(self, text):
        return ' '.join(text.replace('\n', ' ').split()).strip()

    # ---------- Output ----------

    def to_json(self):
        return {
            'metadata': {
                'text': 'upadesa_sahasri_metrical',
                'source': str(self.filepath),
            },
            'units': self.units,
            'self_check': {
                'unit_count': len(self.units),
                'ids_unique': len(set(u['id'] for u in self.units)) == len(self.units),
            },
        }

    def save(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, indent=2, ensure_ascii=False)
        logging.info(f"Saved to {output_path}")


# ---------- CLI ----------

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('output')
    args = ap.parse_args()
    p = UpadesaMetricalParser(args.input)
    p.parse()
    p.save(args.output)
