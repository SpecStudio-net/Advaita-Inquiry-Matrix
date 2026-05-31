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


class KenaParser:
    """
    Parses kena_{khanda}.md files produced by tools/generate_kena.py.

    Heading format: ## Text {khanda}.{mantra}
    Sections: **Sanskrit** (optional), **Transliteration**, **Translation**
    """

    HEADING_RE = re.compile(r'^## Text (\d+)\.(\d+)\s*$', re.MULTILINE)

    # AIM defaults per khaṇḍa
    # Khaṇḍa 1: Five-fold negation (neti-neti style) — direct apophatic pointing
    # Khaṇḍa 2: Epistemological paradox — pratibodha-viditam
    # Khaṇḍas 3-4: Yaksha narrative + summary teaching
    _KHANDA_DEFAULTS = {
        1: ('uttama',   'paramarathika', 'manana',       'analytic_inquiry',       'apophatic-pointing'),
        2: ('uttama',   'paramarathika', 'nididhyasana', 'direct_insight',         'brahman-epistemology'),
        3: ('madhyama', 'dual-register', 'sravana',      'analytic_contemplative', 'narrative-upadesa'),
        4: ('uttama',   'paramarathika', 'manana',       'analytic_inquiry',       'brahman-nature-pointing'),
    }

    # Mantra-level overrides for key passages
    _MANTRA_OVERRIDES = {
        (1, 1): dict(prakriya='inquiry-opening',   pedagogical_role='inquiry-arousal',
                     note='The opening inquiry — by what is everything moved? Points to the unmoved mover.'),
        (1, 2): dict(prakriya='atman-as-witness-pointing', pedagogical_stage='nididhyasana',
                     pedagogical_role='direct-pointing',
                     note='Ear of the ear — Brahman as the inner witness behind all faculties.'),
        (1, 3): dict(prakriya='apophatic-pointing', pedagogical_role='negation-pointing',
                     note='Na tatra caksur gacchati — the eye, mind, speech cannot reach Brahman.'),
        (1, 4): dict(prakriya='beyond-known-unknown', pedagogical_stage='nididhyasana',
                     pedagogical_role='direct-pointing',
                     note='Anyad eva tad viditad — Brahman is other than the known and above the unknown.'),
        (1, 5): dict(prakriya='neti-neti-negation',  pedagogical_role='negation-pointing',
                     note='Yad vacā — not what speech expresses; Brahman is the ground of speech.'),
        (1, 6): dict(prakriya='neti-neti-negation',  pedagogical_role='negation-pointing',
                     note='Yan manasa — not what the mind thinks; Brahman prompts all cognition.'),
        (1, 7): dict(prakriya='neti-neti-negation',  pedagogical_role='negation-pointing',
                     note='Yac caksusa — not what the eye sees; Brahman is the seer behind seeing.'),
        (1, 8): dict(prakriya='neti-neti-negation',  pedagogical_role='negation-pointing',
                     note='Yac shrotreṇa — not what the ear hears; Brahman is the hearer behind hearing.'),
        (1, 9): dict(prakriya='neti-neti-negation',  pedagogical_role='negation-pointing',
                     note='Yat pranena — not what the prana lives by; Brahman animates all life-force.'),
        (2, 3): dict(prakriya='brahman-epistemology', pedagogical_stage='nididhyasana',
                     pedagogical_role='paradox-pointing',
                     note='Yasya amatam tasya matam — known by those who do not know It; not known by those who know It. The central paradox of Brahman-knowledge.'),
        (2, 4): dict(prakriya='pratibodha-viditam',  pedagogical_stage='nididhyasana',
                     ontological_scope='paramarathika', pedagogical_role='direct-pointing',
                     note='Pratibodha-viditam — Brahman known in every state of consciousness; this is true knowing leading to amrtatva.'),
        (2, 5): dict(prakriya='iha-ced-avedid',      pedagogical_stage='nididhyasana',
                     pedagogical_role='urgency-arousal',
                     note='Iha ced avedid atha satyam asti — if known here now, there is truth; if not known here, great is the loss.'),
        (3, 11): dict(prakriya='guru-upadesa', pedagogical_role='narrative-revelation',
                      note='Uma Haimavati reveals the Yaksha as Brahman — the feminine wisdom (prajña) that recognises what the cosmic forces cannot.'),
        (3, 12): dict(prakriya='advaita-culmination', pedagogical_stage='nididhyasana',
                      ontological_scope='paramarathika', pedagogical_role='direct-pointing',
                      note='Brahma ha etat — Uma declares: It is Brahman. Through Brahman\'s victory you are exalted. Indra\'s direct recognition.'),
        (4, 4): dict(prakriya='brahman-as-tadvanam', pedagogical_stage='manana',
                     pedagogical_role='meditation-instruction',
                     note='Tadvanam — meditate on Brahman as that which is longed for by all; one who knows this is longed for by all beings.'),
        (4, 6): dict(prakriya='sadhana-catustaya', pedagogical_role='method-prescription',
                     note='Tapas, dama, karma as foundation; Vedas as limbs; truth as abode — the integrated sadhana required for Brahman-knowledge.'),
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
            khanda = int(m.group(1))
            mantra = int(m.group(2))
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(self.text)
            chunk = self.text[start:end]

            unit = self._build_unit(khanda, mantra, chunk)
            if unit:
                self.units.append(unit)
                logging.info(f"Parsed Kena {unit['id']}")

        return self.units

    def _extract_file_meta(self):
        m = re.search(r'```yaml\s*\n(.*?)```', self.text, re.DOTALL)
        if not m:
            return {}
        try:
            return yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def _build_unit(self, khanda, mantra, chunk):
        translation = self._extract_section(chunk, 'Translation')
        if not translation:
            logging.warning(f"Kena {khanda}.{mantra}: missing translation — skipping")
            return None

        sanskrit = self._extract_section(chunk, 'Sanskrit')
        transliteration = self._extract_section(chunk, 'Transliteration')

        unit = {
            'id':              f"KENA_{khanda:02d}_{mantra:02d}",
            'khanda':          khanda,
            'mantra':          mantra,
            'mantra_label':    f"{khanda}.{mantra}",
            'sanskrit':        self._clean(sanskrit),
            'transliteration': self._clean(transliteration),
            'translation':     self._clean(translation),
            'status':          'VERIFIED',
        }
        return self._enrich(unit)

    def _enrich(self, unit):
        k = unit['khanda']
        defaults = self._KHANDA_DEFAULTS.get(k)
        if defaults:
            adhikara, scope, stage, cog, prakriya = defaults
            unit.setdefault('adhikara_level',    adhikara)
            unit.setdefault('ontological_scope', scope)
            unit.setdefault('pedagogical_stage', stage)
            unit.setdefault('cognitive_mode',    cog)
            unit.setdefault('prakriya',          prakriya)

        overrides = self._MANTRA_OVERRIDES.get((unit['khanda'], unit['mantra']), {})
        for key, val in overrides.items():
            unit[key] = val

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
                'text':    'kena_upanishad',
                'source':  str(self.filepath),
                'khanda':  self._file_meta.get('khanda'),
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
    p = KenaParser(args.input)
    p.parse()
    p.save(args.output)
