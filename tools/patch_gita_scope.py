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
Assign ontological_scope to Gita verse YAML blocks.
Uses cluster field (primary) for mapping.
Skips units that already have ontological_scope.
"""
import re
import yaml
from pathlib import Path

GITA_DIR = Path("corpus/smriti/gita")

# cluster → ontological_scope
CLUSTER_SCOPE = {
    # ── pāramārthika ──
    "nature_of_self": "pāramārthika",
    "liberation_through_knowledge": "pāramārthika",
    "knowledge_liberation": "pāramārthika",
    "contemplative_realization": "pāramārthika",
    "enlightened_person": "pāramārthika",
    "universal_self_vision": "pāramārthika",
    "brahman_revelation": "pāramārthika",
    "omnipresent_brahman": "pāramārthika",
    "nonlocal_presence": "pāramārthika",
    "inner_witness": "pāramārthika",
    "witness_discrimination": "pāramārthika",
    "universal_witness": "pāramārthika",
    "witness_consciousness": "pāramārthika",
    "supreme_self": "pāramārthika",
    "puruṣottama_identity": "pāramārthika",
    "puruṣottama_realization": "pāramārthika",
    "guṇātīta_liberation": "pāramārthika",
    "guṇātīta_equanimity": "pāramārthika",
    "guṇātīta_equanimity_traits": "pāramārthika",
    "guṇātīta_detachment": "pāramārthika",
    "guṇātīta_question": "pāramārthika",
    "bhakti_transcends_guṇas": "pāramārthika",
    "nondual_vision": "pāramārthika",
    "nondual_ground": "pāramārthika",
    "nondual_identity": "pāramārthika",
    "liberation_result": "pāramārthika",
    "transcendental_state": "pāramārthika",
    "knowledge_liberation_frame": "pāramārthika",
    "culmination_of_knowledge": "pāramārthika",
    "brahman_foundation": "pāramārthika",
    "maya_transcendence": "pāramārthika",
    "consciousness_principle": "pāramārthika",
    "consciousness_as_light": "pāramārthika",
    "unity_of_beings": "pāramārthika",
    "universal_self": "pāramārthika",
    "unity_within_diversity": "pāramārthika",
    "cosmic_illumination": "pāramārthika",
    "final_discrimination": "pāramārthika",
    "knowledge_supremacy": "pāramārthika",
    "realization_by_hearing": "pāramārthika",
    "liberation_seeking": "pāramārthika",

    # ── vyavahārika ──
    "crisis_of_identity": "vyavahārika",
    "dharma_confusion": "vyavahārika",
    "action_confusion": "vyavahārika",
    "desire_psychology": "vyavahārika",
    "impermanence_of_body": "vyavahārika",
    "desire_motivated_religion": "vyavahārika",
    "conditional_devotion": "vyavahārika",
    "limited_spiritual_results": "vyavahārika",
    "limitation_of_ritual": "vyavahārika",
    "duality_delusion": "vyavahārika",
    "misunderstanding_of_absolute": "vyavahārika",
    "svadharma": "vyavahārika",
    "pseudo_renunciation": "vyavahārika",
    "ignorance_resistance": "vyavahārika",
    "nature_conditioning": "vyavahārika",
    "ignorance_covering": "vyavahārika",
    "ignorance_types": "vyavahārika",
    "sensory_impermanence": "vyavahārika",
    "karmic_consequence": "vyavahārika",
    "social_dynamics": "vyavahārika",
    "social_integration": "vyavahārika",
    "ignorance_of_self": "vyavahārika",
    "scriptural_validation": "vyavahārika",
    "maya_delusion": "vyavahārika",
    "desire_driven_action": "vyavahārika",

    # ── dual-register ──
    "karma_yoga": "dual-register",
    "dharma_action_framework": "dual-register",
    "action_analysis": "dual-register",
    "sacrifice_reinterpretation": "dual-register",
    "enlightened_action": "dual-register",
    "inner_sannyāsa": "dual-register",
    "renunciation_vs_action": "dual-register",
    "cosmic_order": "dual-register",
    "doership_deconstruction": "dual-register",
    "non_doership": "dual-register",
    "mind_mastery": "dual-register",
    "serenity_of_mind": "dual-register",
    "equanimity_of_mind": "dual-register",
    "meditation_discipline": "dual-register",
    "sense_control": "dual-register",
    "self_vs_body_discrimination": "dual-register",
    "divine_immanence": "dual-register",
    "divine_manifestation": "dual-register",
    "transmission_of_teaching": "dual-register",
    "spiritual_progression": "dual-register",
    "knowledge_qualifications": "dual-register",
    "teaching_framework": "dual-register",
    "transcendence_within_immanence": "dual-register",
    "field_inventory": "dual-register",
    "prakriti_purusha_framework": "dual-register",
    "prakriti_puruṣa_framework": "dual-register",
    "guṇa_dynamics": "dual-register",
    "guṇa_metaphysics": "dual-register",
    "sattva_psychology": "dual-register",
    "rajas_psychology": "dual-register",
    "tamas_psychology": "dual-register",
    "sattva_diagnostics": "dual-register",
    "rajas_diagnostics": "dual-register",
    "tamas_diagnostics": "dual-register",
    "sattva_destiny": "dual-register",
    "rajas_tamas_destiny": "dual-register",
    "guṇa_action_results": "dual-register",
    "guṇa_psychological_effects": "dual-register",
    "guṇa_cosmic_hierarchy": "dual-register",
    "guṇa_transcendence": "dual-register",
    "saṁsāra_tree_metaphor": "dual-register",
    "saṁsāra_tree_structure": "dual-register",
    "saṁsāra_indeterminacy": "dual-register",
    "liberation_path": "dual-register",
    "liberation_qualifications": "dual-register",
    "liberation_process": "dual-register",
    "jīva_manifestation": "dual-register",
    "subtle_body_transmigration": "dual-register",
    "sensory_experience_model": "dual-register",
    "yogic_perception": "dual-register",
    "cosmic_sustenance": "dual-register",
    "biological_immanence": "dual-register",
    "cognitive_source": "dual-register",
    "ontological_duality": "dual-register",
    "ontological_discrimination": "dual-register",
    "field_knower_interaction": "dual-register",
    "realization_methods": "dual-register",
    "experience_mechanism": "dual-register",
    "bondage_mechanism": "dual-register",
    "knowledge_definition": "dual-register",
    "knowledge_transmission": "dual-register",
    "rarity_of_realization": "dual-register",
    "cosmological_framework": "dual-register",
    "cosmic_origin": "dual-register",
    "seeker_typology": "dual-register",
    "analytical_framework": "dual-register",
    "ritual_transcendence": "dual-register",
    "path_differentiation": "dual-register",
    "purification_of_mind": "dual-register",
    "purification_through_knowledge": "dual-register",
    "hidden_divinity": "dual-register",
    "transcendental_knowledge": "dual-register",
    "comprehensive_knowledge": "dual-register",
    "teaching_conclusion": "dual-register",
    "surrender_to_teaching": "dual-register",
    "teaching_initiation": "dual-register",
    "teaching_summary": "dual-register",
    "inner_hierarchy": "dual-register",
    "contemplative_practice": "dual-register",
    "contemplative_environment": "dual-register",
    "entry_to_higher_knowledge": "dual-register",
    "divine_relationship": "dual-register",
    "hierarchy_of_devotion": "dual-register",
    "prakṛti_cosmology": "dual-register",
    "prakṛti_puruṣa_creation": "dual-register",
    "experience_structure": "dual-register",
    "bondage_explanation": "dual-register",
    "explanation_of_individuality": "dual-register",
    "cosmological_clarification": "dual-register",
    "cosmological_expansion": "dual-register",
    "self_immutability": "pāramārthika",
    "space_metaphor": "dual-register",
    "illumination_metaphor": "dual-register",
    "witness_perspective": "pāramārthika",
}

YAML_BLOCK_RE = re.compile(r'(```yaml\s*\n)(.*?)(```)', re.DOTALL)

def process_file(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    blocks = list(YAML_BLOCK_RE.finditer(text))
    if not blocks:
        return 0

    patches = []
    for match in blocks:
        body = match.group(2)
        try:
            data = yaml.safe_load(body)
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        # Skip document-level header blocks
        if any(k in data for k in ('title', 'text_type', 'schema_version', 'macro_prakriyā')):
            continue
        # Skip if already has scope
        if 'ontological_scope' in data:
            continue

        cluster = data.get('cluster', '')
        scope = CLUSTER_SCOPE.get(cluster)
        if not scope:
            print(f"  UNMAPPED cluster: '{cluster}' in {filepath.name}")
            continue

        # Insert ontological_scope after 'cluster' line
        lines = body.split('\n')
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if not inserted and re.match(r'cluster\s*:', line):
                new_lines.append(f'ontological_scope: {scope}')
                inserted = True
        if not inserted:
            # fallback: insert at top
            new_lines.insert(0, f'ontological_scope: {scope}')

        new_body = '\n'.join(new_lines)
        patches.append((match.start(2), match.end(2), new_body))

    if not patches:
        return 0

    # Apply patches in reverse order
    result = text
    for start, end, new_body in reversed(patches):
        result = result[:start] + new_body + result[end:]

    filepath.write_text(result, encoding="utf-8")
    return len(patches)


if __name__ == "__main__":
    total = 0
    for filepath in sorted(GITA_DIR.glob("gita_*.md")):
        count = process_file(filepath)
        print(f"{filepath.name}: {count} units patched")
        total += count
    print(f"\nTotal: {total} units patched")
