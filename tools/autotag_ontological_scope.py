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
autotag_ontological_scope.py

Scans corpus markdown files for units missing `ontological_scope`.
Applies deterministic rules based on `prakriyā` value.

Outputs:
  - A review report showing auto-tagged and flagged units
  - With --apply: writes auto-tagged values back to the markdown files

Usage:
  python tools/autotag_ontological_scope.py              # report only
  python tools/autotag_ontological_scope.py --apply      # write to files
  python tools/autotag_ontological_scope.py --text katha # single text
"""

import re
import sys
import os
from pathlib import Path
from collections import defaultdict

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Rules: prakriyā → ontological_scope
# HIGH = write automatically; LOW = flag for review
# ---------------------------------------------------------------------------

RULES = {
    # --- pāramārthika ---
    "identity":                         ("pāramārthika",  "HIGH"),
    "identity-recognition":             ("pāramārthika",  "HIGH"),
    "apavāda":                          ("pāramārthika",  "HIGH"),
    "negation":                         ("pāramārthika",  "HIGH"),
    "negation-through-description":     ("pāramārthika",  "HIGH"),
    "negation-of-attributes":           ("pāramārthika",  "HIGH"),
    "epistemic-negation":               ("pāramārthika",  "HIGH"),
    "linguistic-collapse":              ("pāramārthika",  "HIGH"),
    "nondual-assertion":                ("pāramārthika",  "HIGH"),
    "difference-negation":              ("pāramārthika",  "HIGH"),
    "brahman-identity-statement":       ("pāramārthika",  "HIGH"),
    "brahmaiva-bhavati":                ("pāramārthika",  "HIGH"),
    "supreme-identity-attainment":      ("pāramārthika",  "HIGH"),
    "mahāvākya_revelation":             ("pāramārthika",  "HIGH"),
    "mahāvākya_prakriyā":               ("pāramārthika",  "HIGH"),
    "de-objectification":               ("pāramārthika",  "HIGH"),
    "hierarchy-termination":            ("pāramārthika",  "HIGH"),
    "vāsanā-collapse":                  ("pāramārthika",  "HIGH"),
    "bondage-severance":                ("pāramārthika",  "HIGH"),
    "transcendental-conclusion":        ("pāramārthika",  "HIGH"),
    "apophatic-clarification":          ("pāramārthika",  "HIGH"),
    "direct-realization-description":   ("pāramārthika",  "HIGH"),
    "realization_statement":            ("pāramārthika",  "HIGH"),
    "realization_expression":           ("pāramārthika",  "HIGH"),
    "kosha_transcendence":              ("pāramārthika",  "HIGH"),
    "self-delighting-sage":             ("pāramārthika",  "HIGH"),
    "vedānta-certainty-and-saṃnyāsa":  ("pāramārthika",  "HIGH"),
    "two-birds-resolution":             ("pāramārthika",  "HIGH"),
    "ātma_vicāra_seed":                 ("pāramārthika",  "HIGH"),
    "heart_space_contemplation":        ("pāramārthika",  "HIGH"),
    "direct-seeing-of-self":            ("pāramārthika",  "HIGH"),
    "direct_path_instruction":          ("pāramārthika",  "HIGH"),
    "ontological_definition":           ("pāramārthika",  "HIGH"),
    "rivers-merging-in-ocean":          ("pāramārthika",  "HIGH"),
    "parts-returning-to-source":        ("pāramārthika",  "HIGH"),

    # --- vyavahārika ---
    "avasthā-analysis":                 ("vyavahārika",   "HIGH"),
    "kosha_examination":                ("vyavahārika",   "HIGH"),
    "indriya_function_analysis":        ("vyavahārika",   "HIGH"),
    "element_to_function_mapping":      ("vyavahārika",   "HIGH"),
    "ritual-frame-invocation":          ("vyavahārika",   "HIGH"),
    "ritual-procedure-description":     ("vyavahārika",   "HIGH"),
    "ritual-technical-detail":          ("vyavahārika",   "HIGH"),
    "ritual-merit-structure":           ("vyavahārika",   "HIGH"),
    "ritual-dependence-analysis":       ("vyavahārika",   "HIGH"),
    "karmic-result-description":        ("vyavahārika",   "HIGH"),
    "karmic-return-cycle":              ("vyavahārika",   "HIGH"),
    "karmic-differentiation":           ("vyavahārika",   "HIGH"),
    "heaven-impermanence":              ("vyavahārika",   "HIGH"),
    "virāṭ_projection":                 ("vyavahārika",   "HIGH"),
    "virāṭ-expansion-sequence":         ("vyavahārika",   "HIGH"),
    "three_births_doctrine":            ("vyavahārika",   "HIGH"),
    "embodiment_process":               ("vyavahārika",   "HIGH"),
    "structural-instrument-analysis":   ("vyavahārika",   "HIGH"),
    "phonetic_discipline":              ("vyavahārika",   "HIGH"),
    "ethical_life_discipline":          ("vyavahārika",   "HIGH"),
    "relational_dharma_instruction":    ("vyavahārika",   "HIGH"),
    "sacred_generosity_practice":       ("vyavahārika",   "HIGH"),
    "integrated_discipline_of_study_and_conduct": ("vyavahārika", "HIGH"),
    "paramparā-establishment":          ("vyavahārika",   "HIGH"),
    "paramparā-continuity":             ("vyavahārika",   "HIGH"),
    "explicit-apara-listing":           ("vyavahārika",   "HIGH"),
    "laya_analysis":                    ("vyavahārika",   "HIGH"),
    "consciousness_analysis":           ("vyavahārika",   "HIGH"),
    "invocation_alignment":             ("vyavahārika",   "HIGH"),
    "contemplative_self_affirmation":   ("dual-register", "HIGH"),
    "ethical_discernment_method":       ("vyavahārika",   "HIGH"),
    "closing_benediction_invocation":   ("vyavahārika",   "HIGH"),
    "learning_community_invocation":    ("vyavahārika",   "HIGH"),
    "aspirational_alignment":           ("dual-register", "HIGH"),
    "omkara_contemplation":             ("dual-register", "HIGH"),
    "śānti_mantra_invocation":          ("vyavahārika",   "HIGH"),
    "brahman_inquiry_instruction":      ("dual-register", "HIGH"),
    "contemplative_inquiry":            ("dual-register", "HIGH"),
    "experiential_definition":          ("vyavahārika",   "HIGH"),
    "experiential_verification":        ("vyavahārika",   "HIGH"),
    "experiential_reduction":           ("vyavahārika",   "HIGH"),
    "experiential_comparison":          ("vyavahārika",   "HIGH"),
    "experiential_inquiry":             ("vyavahārika",   "HIGH"),
    "grief-transcendence":              ("vyavahārika",   "HIGH"),
    "instrument-disidentification":     ("vyavahārika",   "LOW"),
    "instrument-negation":              ("vyavahārika",   "LOW"),
    "progressive-disidentification":    ("vyavahārika",   "LOW"),
    "progressive-disidentification-reprise": ("vyavahārika", "LOW"),

    # --- dual-register ---
    "sṛṣṭi_prakriyā":                  ("dual-register", "HIGH"),
    "adhyāropa-apavāda":               ("dual-register", "HIGH"),
    "adhidaiva_adhyātma_mapping":      ("dual-register", "HIGH"),
    "microcosm_macrocosm_mapping":     ("dual-register", "HIGH"),
    "analogical_identity_revelation":  ("dual-register", "HIGH"),
    "kārya-kāraṇa-ananyatva":          ("dual-register", "HIGH"),
    "satkāryavāda":                    ("dual-register", "HIGH"),
    "symbolic-universalization":       ("dual-register", "HIGH"),
    "symbolic-interiorization":        ("dual-register", "HIGH"),
    "symbolic-condensation":           ("dual-register", "HIGH"),
    "symbolic_correspondence":         ("dual-register", "HIGH"),
    "symbolic-correlation":            ("dual-register", "HIGH"),
    "cosmic_correspondence_meditation":("dual-register", "HIGH"),
    "contemplative_correspondence":    ("dual-register", "HIGH"),
    "contemplative_identification":    ("dual-register", "HIGH"),
    "contemplative_hypothesis":        ("dual-register", "HIGH"),
    "contemplative_upasana":           ("dual-register", "HIGH"),
    "meditative-focus-and-penetration":("dual-register", "HIGH"),
    "medha_invocation":                ("dual-register", "HIGH"),
    "upāsanā-elevation":               ("dual-register", "HIGH"),
    "ethical_expression_of_realization":("dual-register","HIGH"),
    "existential-intensification":     ("dual-register", "HIGH"),
    "existential-axis-establishment":  ("dual-register", "HIGH"),
    "existential-contrast-clarification":("dual-register","HIGH"),
    "dual-mode-relationality":         ("dual-register", "HIGH"),
    "participatory-integration":       ("dual-register", "HIGH"),
    "inner-outer-unification":         ("dual-register", "HIGH"),
    "subtle-causal-expansion":         ("dual-register", "HIGH"),
    "cosmic-expansion-sequence":       ("dual-register", "HIGH"),
    "cosmic-metaphor-expansion":       ("dual-register", "HIGH"),
    "cosmological-integration":        ("dual-register", "HIGH"),
    "cosmological_explanation":        ("dual-register", "HIGH"),
    "vyahriti_cosmic_expansion":       ("dual-register", "HIGH"),
    "pentadic_cosmic_contemplation":   ("dual-register", "HIGH"),
    "relational_meditation":           ("dual-register", "HIGH"),
    "generative_order_meditation":     ("dual-register", "HIGH"),
    "embodied_contemplation":          ("dual-register", "HIGH"),
    "misidentification-exposure":      ("dual-register", "HIGH"),
    "superimposition-correction":      ("dual-register", "HIGH"),
    "miscontextualization-warning":    ("dual-register", "HIGH"),
    "assimilation-illustration":       ("dual-register", "HIGH"),
    "limitation-critique":             ("dual-register", "HIGH"),
    "ritual-limitation-description":   ("dual-register", "HIGH"),
    "non-binding-action":              ("dual-register", "HIGH"),
    "non-adhesion-clarification":      ("dual-register", "HIGH"),
    "unity-within-diversity-clarification":("dual-register","HIGH"),
    "contextual-diagnosis-and-reversal":("dual-register","HIGH"),
    "ontological-intimation":          ("dual-register", "HIGH"),
    "ontological-threshold":           ("dual-register", "HIGH"),
    "ontological-contrast":            ("dual-register", "HIGH"),
    "guru_guidance":                   ("dual-register", "HIGH"),
    "guru-upasatti-and-brahmavidyā":   ("dual-register", "HIGH"),
    "jñāna_prakriyā":                  ("dual-register", "HIGH"),
    "fire-sparks-metaphor":            ("dual-register", "HIGH"),
    "knot-cutting-metaphor":           ("dual-register", "HIGH"),
    "two-birds-metaphor":              ("dual-register", "HIGH"),
    "akṣara-definition":               ("dual-register", "HIGH"),
    "source-universe-derivation":      ("dual-register", "HIGH"),
    "satya_principle":                 ("dual-register", "HIGH"),
    "luminosity-assertion":            ("dual-register", "HIGH"),
    "doctrinal-explication":           ("dual-register", "HIGH"),
    "recognition-confirmation":        ("dual-register", "HIGH"),
    "ontological-compression":         ("dual-register", "LOW"),
    "hierarchy-exhaustion":            ("pāramārthika",  "HIGH"),
    "prāṇa-subordination":             ("vyavahārika",   "HIGH"),
    "identity-separation":             ("dual-register", "HIGH"),
    "experiential-universalization":   ("dual-register", "HIGH"),
    "metaphorical-universalization":   ("dual-register", "HIGH"),
    "meditative-definition":           ("dual-register", "HIGH"),
    "stabilization-warning":           ("vyavahārika",   "HIGH"),
    "affirmation-stabilization":       ("pāramārthika",  "HIGH"),
    "symbolic-departure-clarification":("vyavahārika",   "HIGH"),
    "interiorization-intensification": ("dual-register", "HIGH"),
    "narrative-closure":               ("dual-register", "HIGH"),
    "transmission-sealing":            ("dual-register", "HIGH"),
    "sovereignty-assertion":           ("dual-register", "HIGH"),
    "existential-urgency":             ("dual-register", "HIGH"),
    "identity_reintegration":          ("pāramārthika",  "LOW"),
    "universalization-of-self":        ("pāramārthika",  "LOW"),

    # --- scope-clarification ---
    "scope-clarification":             ("scope-clarification", "HIGH"),
    "para-apara-differentiation":      ("scope-clarification", "HIGH"),
    "adhikāra-confirmation":           ("scope-clarification", "HIGH"),
    "ontological-clarification":       ("scope-clarification", "HIGH"),
    "epistemic-limitation":            ("scope-clarification", "HIGH"),
    "epistemic-compression-inquiry":   ("scope-clarification", "HIGH"),
    "subtle-qualification":            ("scope-clarification", "HIGH"),
    "clarity-gradation":               ("scope-clarification", "HIGH"),
    "contextual-refinement":           ("scope-clarification", "HIGH"),
    "contextual-reorientation":        ("scope-clarification", "HIGH"),
    "epistemic-deconstruction":        ("scope-clarification", "LOW"),
    "apophatic-humility":              ("scope-clarification", "LOW"),
    "body-negation":                   ("scope-clarification", "LOW"),
}

FIELD = "ontological_scope"

# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

YAML_BLOCK_RE = re.compile(r'(```yaml\s*\n)(.*?)(```)', re.DOTALL)


def extract_yaml(block_content):
    try:
        return yaml.safe_load(block_content) or {}
    except Exception:
        return {}


def insert_field(block_content, value):
    """Insert ontological_scope after prakriyā line."""
    lines = block_content.split('\n')
    result = []
    inserted = False
    for line in lines:
        result.append(line)
        if not inserted and line.strip().startswith('prakriyā:'):
            result.append(f'{FIELD}: {value}')
            inserted = True
    if not inserted:
        result.insert(0, f'{FIELD}: {value}')
    return '\n'.join(result)


def process_file(filepath, apply=False):
    text = Path(filepath).read_text(encoding='utf-8')
    tagged = []
    flagged = []
    new_text = text
    offset = 0

    for m in YAML_BLOCK_RE.finditer(text):
        open_tag, content, close_tag = m.group(1), m.group(2), m.group(3)
        parsed = extract_yaml(content)

        if FIELD in parsed:
            continue  # already has it

        # Skip document-level metadata blocks (chapter headers, etc.)
        if any(k in parsed for k in ('title', 'text_type', 'schema_version', 'macro_prakriyā')):
            continue

        prakriya = parsed.get('prakriyā', '')
        unit_id = parsed.get('id', parsed.get('id', '?'))

        if prakriya in RULES:
            scope, confidence = RULES[prakriya]
            entry = {
                'id': unit_id,
                'prakriyā': prakriya,
                'scope': scope,
                'confidence': confidence,
                'file': str(filepath),
            }
            if confidence == 'HIGH':
                tagged.append(entry)
                if apply:
                    new_content = insert_field(content, scope)
                    replacement = open_tag + new_content + close_tag
                    start = m.start() + offset
                    end = m.end() + offset
                    new_text = new_text[:start] + replacement + new_text[end:]
                    offset += len(replacement) - (m.end() - m.start())
            else:
                flagged.append(entry)
        else:
            flagged.append({
                'id': unit_id,
                'prakriyā': prakriya or '(none)',
                'scope': '?',
                'confidence': 'UNKNOWN',
                'file': str(filepath),
            })

    if apply and new_text != text:
        Path(filepath).write_text(new_text, encoding='utf-8')

    return tagged, flagged


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    apply = '--apply' in sys.argv
    text_filter = None
    if '--text' in sys.argv:
        idx = sys.argv.index('--text')
        if idx + 1 < len(sys.argv):
            text_filter = sys.argv[idx + 1]

    corpus_root = Path('corpus')
    md_files = sorted([
        f for f in corpus_root.rglob('*.md')
        if 'metadata' not in f.parts
    ])

    if text_filter:
        md_files = [f for f in md_files if text_filter in str(f)]

    all_tagged = []
    all_flagged = []

    for filepath in md_files:
        tagged, flagged = process_file(filepath, apply=apply)
        all_tagged.extend(tagged)
        all_flagged.extend(flagged)

    # --- Report ---
    print(f'\n{"="*60}')
    print(f'  AIM Ontological Scope Auto-tagger')
    print(f'  Mode: {"APPLY (writing to files)" if apply else "REPORT ONLY (dry run)"}')
    print(f'{"="*60}\n')

    print(f'AUTO-TAGGED ({len(all_tagged)} units — high confidence):')
    by_scope = defaultdict(list)
    for e in all_tagged:
        by_scope[e['scope']].append(e)
    for scope in sorted(by_scope):
        print(f'\n  {scope} ({len(by_scope[scope])} units):')
        for e in by_scope[scope]:
            print(f'    {e["id"] or Path(e["file"]).name:<40}  prakriyā: {e["prakriyā"]}')

    print(f'\n{"─"*60}')
    print(f'FLAGGED FOR REVIEW ({len(all_flagged)} units):')
    for e in all_flagged:
        label = f'[{e["confidence"]}]'
        print(f'  {label:<10} {e["id"] or Path(e["file"]).name:<35}  prakriyā: {e["prakriyā"]}')

    print(f'\n{"─"*60}')
    print(f'SUMMARY')
    print(f'  Auto-tagged (HIGH):   {len(all_tagged)}')
    print(f'  Flagged for review:   {len(all_flagged)}')
    print(f'  Total processed:      {len(all_tagged) + len(all_flagged)}')
    if not apply:
        print(f'\n  Run with --apply to write auto-tagged values to files.')
    print()


if __name__ == '__main__':
    main()
