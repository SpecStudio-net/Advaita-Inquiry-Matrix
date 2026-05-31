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


class BrihadaranyakaParser:
    """
    Parses brihadaranyaka_{adhyaya}_{brahmana}.md files produced by tools/scrape_bu.py.

    Heading format: ## Text {adhyaya}.{brahmana}.{mantra}
    Sections: **Sanskrit**, **Transliteration**, **Translation**
    Optional per-mantra ```yaml block for AIM metadata
    File-level ```yaml block for adhyaya/brahmana metadata
    """

    HEADING_RE = re.compile(
        r'^## Text (\d+)\.(\d+)\.(\d+)\s*$', re.MULTILINE
    )

    # Chapter-level AIM field defaults (refined by annotation passes later)
    # BU structure: adhyāya 1-2 = cosmogonic/upāsanā; 3-4 = Yājñavalkya dialogues (core);
    #               5 = upāsanā brāhmaṇas; 6 = concluding lineage/rites
    _ADHYAYA_DEFAULTS = {
        1: ('sarva',    'dual-register',  'śravaṇa',       'analytic_contemplative'),
        2: ('sarva',    'dual-register',  'śravaṇa',       'analytic_contemplative'),
        3: ('uttama',   'pāramārthika',   'manana',        'analytic_inquiry'),
        4: ('uttama',   'pāramārthika',   'nididhyāsana',  'direct_insight'),
        5: ('madhyama', 'dual-register',  'manana',        'analytic_contemplative'),
        6: ('sarva',    'vyavahārika',    'śravaṇa',       'analytic_contemplative'),
    }

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.text = self.filepath.read_text(encoding="utf-8")
        self.units = []
        self._file_meta = {}

    def parse(self):
        self._file_meta = self._extract_file_meta()
        matches = list(self.HEADING_RE.finditer(self.text))

        for i, m in enumerate(matches):
            adhyaya  = int(m.group(1))
            brahmana = int(m.group(2))
            mantra   = int(m.group(3))
            mantra_label = f"{adhyaya}.{brahmana}.{m.group(3)}"

            start = m.end()
            end   = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)
            chunk = self.text[start:end]

            unit_meta = self._extract_unit_meta(chunk)
            unit = self._build_unit(adhyaya, brahmana, mantra, mantra_label, chunk, unit_meta)
            if unit:
                self.units.append(unit)
                logging.info(f"Parsed {unit['id']}")

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
        m = re.search(r'```yaml\s*\n(.*?)```', chunk, re.DOTALL)
        if not m:
            return {}
        try:
            raw = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}
        _skip = {'id', 'adhyaya', 'brahmana', 'mantra', 'sanskrit',
                 'transliteration', 'translation', 'status'}
        return {k: v for k, v in raw.items() if k not in _skip}

    def _build_unit(self, adhyaya, brahmana, mantra, mantra_label, chunk, meta):
        translation = self._extract_section(chunk, 'Translation')
        if not translation:
            logging.warning(f"Mantra {mantra_label}: missing translation — skipping")
            return None

        sanskrit       = self._extract_section(chunk, 'Sanskrit')
        transliteration = self._extract_section(chunk, 'Transliteration')

        unit = {
            'id':              f"BRIHADARANYAKA_{adhyaya:02d}_{brahmana:02d}_{mantra:03d}",
            'adhyaya':         adhyaya,
            'brahmana':        brahmana,
            'mantra':          mantra,
            'mantra_label':    mantra_label,
            'sanskrit':        self._clean(sanskrit),
            'transliteration': self._clean(transliteration),
            'translation':     self._clean(translation),
            **meta,
            'status': 'VERIFIED',
        }
        return self._enrich(unit)

    def _enrich(self, unit):
        defaults = self._ADHYAYA_DEFAULTS.get(unit['adhyaya'])
        if not defaults:
            return unit
        adhikara, scope, stage, cog = defaults
        unit.setdefault('adhikāra_level',    adhikara)
        unit.setdefault('ontological_scope', scope)
        unit.setdefault('pedagogical_stage', stage)
        unit.setdefault('cognitive_mode',    cog)
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
                'text': 'brihadaranyaka_upanishad',
                'source': str(self.filepath),
                'adhyaya':  self._file_meta.get('adhyaya'),
                'brahmana': self._file_meta.get('brahmana'),
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


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('input')
    ap.add_argument('output')
    args = ap.parse_args()
    p = BrihadaranyakaParser(args.input)
    p.parse()
    p.save(args.output)
