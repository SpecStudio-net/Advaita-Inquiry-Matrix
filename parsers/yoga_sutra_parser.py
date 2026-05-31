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


class YogaSutraParser:
    """
    Parses yoga_sutra_{pada}.md files produced by tools/generate_yoga_sutras.py.

    Heading format: ## Text {pada}.{sutra}
    Sections: **Sanskrit** (optional), **Transliteration**, **Translation**
    Per-unit YAML block follows the translation.
    """

    HEADING_RE = re.compile(r'^## Text (\d+)\.(\d+)\s*$', re.MULTILINE)

    # Pada-level defaults for adhikara and cognitive tone
    _PADA_DEFAULTS = {
        1: ('madhyama', 'dual-register',   'sravana',      'analytic_contemplative'),
        2: ('madhyama', 'dual-register',   'sravana',      'analytic_contemplative'),
        3: ('madhyama', 'dual-register',   'sravana',      'analytic_contemplative'),
        4: ('uttama',   'paramarathika',   'nididhyasana', 'direct_insight'),
    }

    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.text = self.filepath.read_text(encoding='utf-8')
        self.units = []
        self._file_meta = {}

    def parse(self):
        self._file_meta = self._extract_file_meta()
        matches = list(self.HEADING_RE.finditer(self.text))

        for i, m in enumerate(matches):
            pada = int(m.group(1))
            sutra = int(m.group(2))
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)
            chunk = self.text[start:end]

            unit = self._build_unit(pada, sutra, chunk)
            if unit:
                self.units.append(unit)
                logging.info(f"Parsed YS {unit['id']}")

        return self.units

    def _extract_file_meta(self):
        m = re.search(r'```yaml\s*\n(.*?)```', self.text, re.DOTALL)
        if not m:
            return {}
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def _build_unit(self, pada, sutra, chunk):
        translation = self._extract_section(chunk, 'Translation')
        if not translation:
            logging.warning(f"YS {pada}.{sutra}: missing translation — skipping")
            return None

        sanskrit = self._extract_section(chunk, 'Sanskrit')
        transliteration = self._extract_section(chunk, 'Transliteration')
        unit_meta = self._extract_unit_meta(chunk)

        unit = {
            'id':              f"YS_{pada}_{sutra:02d}",
            'pada':            pada,
            'sutra':           sutra,
            'sutra_label':     f"{pada}.{sutra}",
            'sanskrit':        self._clean(sanskrit),
            'transliteration': self._clean(transliteration),
            'translation':     self._clean(translation),
            'status':          'VERIFIED',
        }
        unit.update(unit_meta)
        return self._apply_defaults(unit)

    def _extract_unit_meta(self, chunk):
        m = re.search(r'```yaml\s*\n(.*?)```', chunk, re.DOTALL)
        if not m:
            return {}
        try:
            raw = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}
        skip = {'id', 'pada', 'sutra', 'sutra_label', 'sanskrit',
                'transliteration', 'translation', 'status'}
        return {k: v for k, v in raw.items() if k not in skip}

    def _apply_defaults(self, unit):
        defaults = self._PADA_DEFAULTS.get(unit['pada'])
        if defaults:
            adhikara, scope, stage, cog = defaults
            unit.setdefault('adhikara_level',    adhikara)
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
                'text':   'yoga_sutras',
                'source': str(self.filepath),
                'pada':   self._file_meta.get('pada'),
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
    p = YogaSutraParser(args.input)
    p.parse()
    p.save(args.output)
