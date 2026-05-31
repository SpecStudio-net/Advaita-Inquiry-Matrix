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


class VCMParser:
    """
    Parses vivekacudamani_{verse:03d}.md files produced by tools/scrape_vcm.py.

    Heading format: ## Text {verse}
    Sections: **Sanskrit**, **Transliteration**, **Translation**
    File-level yaml block for verse metadata.
    """

    HEADING_RE = re.compile(r'^## Text (\d+)\s*$', re.MULTILINE)

    # Section-level AIM defaults based on VCM's pedagogical arc.
    # VCM verse ranges (approx.):
    #   1-30:   Eligibility, nature of bondage, role of guru (śravaṇa)
    #   31-80:  Viveka — discrimination of self/non-self (manana)
    #   81-140: Deep inquiry into nature of Brahman / ātman (manana → nididhyāsana)
    #   141-193: Liberation, direct experience, mahāvākya fruition (nididhyāsana)

    def _section_defaults(self, verse):
        if verse <= 30:
            return ('madhyama', 'dual-register',  'sravana',      'analytic_contemplative')
        if verse <= 80:
            return ('uttama',   'dual-register',  'manana',       'analytic_inquiry')
        if verse <= 140:
            return ('uttama',   'paramarathika',  'manana',       'analytic_inquiry')
        return ('uttama',       'paramarathika',  'nididhyasana', 'direct_insight')

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.text = self.filepath.read_text(encoding='utf-8')
        self.units = []
        self._file_meta = {}

    def parse(self):
        self._file_meta = self._extract_file_meta()
        matches = list(self.HEADING_RE.finditer(self.text))

        for i, m in enumerate(matches):
            verse = int(m.group(1))
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)
            chunk = self.text[start:end]

            unit = self._build_unit(verse, chunk)
            if unit:
                self.units.append(unit)
                logging.info(f"Parsed VCM {unit['id']}")

        return self.units

    def _extract_file_meta(self):
        m = re.search(r'```yaml\s*\n(.*?)```', self.text, re.DOTALL)
        if not m:
            return {}
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def _extract_unit_meta(self, chunk):
        # The chunk is everything after "## Text N". The file-level yaml block sits before
        # that heading so it never appears in the chunk. The annotation block added by
        # patch_vcm.py is the only yaml block present in the chunk.
        m = re.search(r'```yaml\s*\n(.*?)```', chunk, re.DOTALL)
        if not m:
            return {}
        try:
            raw = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}
        _skip = {'id', 'verse', 'text', 'source', 'sanskrit', 'transliteration', 'translation', 'status'}
        return {k: v for k, v in raw.items() if k not in _skip}

    def _build_unit(self, verse, chunk):
        translation = self._extract_section(chunk, 'Translation')
        if not translation:
            logging.warning(f"Verse {verse}: missing translation — skipping")
            return None

        sanskrit = self._extract_section(chunk, 'Sanskrit')
        transliteration = self._extract_section(chunk, 'Transliteration')
        meta = self._extract_unit_meta(chunk)

        unit = {
            'id':              f"VCM_{verse:03d}",
            'verse':           verse,
            'sanskrit':        self._clean(sanskrit),
            'transliteration': self._clean(transliteration),
            'translation':     self._clean(translation),
            **meta,
            'status':          'VERIFIED',
        }
        return self._enrich(unit)

    def _enrich(self, unit):
        adhikara, scope, stage, cog = self._section_defaults(unit['verse'])
        unit.setdefault('adhikara_level',    adhikara)
        unit.setdefault('ontological_scope', scope)
        unit.setdefault('pedagogical_stage', stage)
        unit.setdefault('cognitive_mode',    cog)
        unit.setdefault('prakriya',          'viveka-vairagya')
        return unit

    def _extract_section(self, chunk, label):
        pattern = rf'\*\*{label}\*\*\s*(.*?)(?=\n\*\*|\n---|\n```|\Z)'
        m = re.search(pattern, chunk, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ''

    def _clean(self, text):
        return ' '.join(text.replace('\n', ' ').split()).strip()

    def to_json(self):
        return {
            'metadata': {
                'text':   'vivekacudamani',
                'source': str(self.filepath),
                'verse':  self._file_meta.get('verse'),
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


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('output')
    args = ap.parse_args()
    p = VCMParser(args.input)
    p.parse()
    p.save(args.output)
