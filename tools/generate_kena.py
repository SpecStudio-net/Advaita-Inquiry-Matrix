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
Generate Kena Upaniṣad corpus files (4 khaṇḍas, 35 mantras total).

Source: Traditional text; translation after Swami Mādhavānanda /
Swami Gambhīrānanda (Advaita Ashrama) with minor harmonisation.

Output: corpus/upanishads/kena/kena_{khanda}.md

Usage:
  python tools/generate_kena.py
  python tools/generate_kena.py --dry-run
"""

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

OUTPUT_DIR = Path("corpus/upanishads/kena")

# ── TEXT DATA ─────────────────────────────────────────────────────────────────
# Each entry: (khanda, mantra, sanskrit, iast, translation)
# Sanskrit field: '' for prose passages where Devanagari is too long to encode inline.

KENA = [

    # ═══════════════════════════════════════════════════════
    # KHAṆḌA 1  (9 mantras — the five-fold negation section)
    # ═══════════════════════════════════════════════════════

    (1, 1,
     "केनेषितं पतति प्रेषितं मनः\nकेन प्राणः प्रथमः प्रैति युक्तः |\nकेनेषितां वाचमिमां वदन्ति\nचक्षुः श्रोत्रं क उ देवो युनक्ति || १ ||",
     "keṇeṣitaṃ patati preṣitaṃ manaḥ\nkena prāṇaḥ prathamaḥ praiti yuktaḥ |\nkeṇeṣitāṃ vācamimāṃ vadanti\ncakṣuḥ śrotraṃ ka u devo yunakti || 1 ||",
     "Willed by whom does the directed mind go towards its object? Being directed by whom does the foremost prāṇa move? By whom is this speech willed, that people speak? Who, indeed, is the god that directs the eye and the ear?"),

    (1, 2,
     "श्रोत्रस्य श्रोत्रं मनसो मनो यद्\nवाचो ह वाचं स उ प्राणस्य प्राणः |\nचक्षुषश्चक्षुरतिमुच्य धीराः\nप्रेत्यास्माल्लोकादमृता भवन्ति || २ ||",
     "śrotrasya śrotraṃ manaso mano yad\nvāco ha vācaṃ sa u prāṇasya prāṇaḥ |\ncakṣuṣaścakṣuratimucya dhīrāḥ\npretyāsmāllokādamṛtā bhavanti || 2 ||",
     "It is the ear of the ear, the mind of the mind, the speech of speech, the life of life, the eye of the eye. The wise, having freed themselves from the senses and renounced this world, become immortal."),

    (1, 3,
     "न तत्र चक्षुर्गच्छति\nन वाग्गच्छति नो मनः |\nन विद्मो न विजानीमो\nयथैतदनुशिष्यात् || ३ ||",
     "na tatra cakṣurgacchati\nna vāggacchati no manaḥ |\nna vidmo na vijānīmo\nyathaitadanuśiṣyāt || 3 ||",
     "The eye does not go there, nor speech, nor the mind. We do not know It; we do not understand how anyone can teach It."),

    (1, 4,
     "अन्यदेव तद्विदितादथो अविदितादधि |\nइति शुश्रुम पूर्वेषां\nये नस्तद्व्याचचक्षिरे || ४ ||",
     "anyadeva tadviditādatho aviditādadhi |\niti śuśruma pūrveṣāṃ\nye nastadvyācacakṣire || 4 ||",
     "It is other than the known and, moreover, It is above the unknown. Thus have we heard from the ancients who explained It to us."),

    (1, 5,
     "यद्वाचानभ्युदितं येन वागभ्युद्यते |\nतदेव ब्रह्म त्वं विद्धि\nनेदं यदिदमुपासते || ५ ||",
     "yadvācānabhyuditaṃ yena vāgabhyudyate |\ntadeva brahma tvaṃ viddhi\nnedaṃ yadidamupāsate || 5 ||",
     "That which is not expressed by speech, but by which speech is expressed — know That alone as Brahman, not this which people worship here."),

    (1, 6,
     "यन्मनसा न मनुते येनाहुर्मनो मतम् |\nतदेव ब्रह्म त्वं विद्धि\nनेदं यदिदमुपासते || ६ ||",
     "yanmanasā na manute yenāhurmano matam |\ntadeva brahma tvaṃ viddhi\nnedaṃ yadidamupāsate || 6 ||",
     "That which the mind does not think, but by which, they say, the mind is prompted to think — know That alone as Brahman, not this which people worship here."),

    (1, 7,
     "यच्चक्षुषा न पश्यति येन चक्षूंषि पश्यति |\nतदेव ब्रह्म त्वं विद्धि\nनेदं यदिदमुपासते || ७ ||",
     "yaccakṣuṣā na paśyati yena cakṣūṃṣi paśyati |\ntadeva brahma tvaṃ viddhi\nnedaṃ yadidamupāsate || 7 ||",
     "That which is not seen by the eye, but by which the eye sees — know That alone as Brahman, not this which people worship here."),

    (1, 8,
     "यच्छ्रोत्रेण न शृणोति येन श्रोत्रमिदं श्रुतम् |\nतदेव ब्रह्म त्वं विद्धि\nनेदं यदिदमुपासते || ८ ||",
     "yacchrotreṇa na śṛṇoti yena śrotramidaṃ śrutam |\ntadeva brahma tvaṃ viddhi\nnedaṃ yadidamupāsate || 8 ||",
     "That which is not heard by the ear, but by which the ear hears — know That alone as Brahman, not this which people worship here."),

    (1, 9,
     "यत्प्राणेन न प्राणिति येन प्राणः प्राणीयते |\nतदेव ब्रह्म त्वं विद्धि\nनेदं यदिदमुपासते || ९ ||",
     "yatprāṇena na prāṇiti yena prāṇaḥ prāṇīyate |\ntadeva brahma tvaṃ viddhi\nnedaṃ yadidamupāsate || 9 ||",
     "That by which the life-force does not live, but by which the life-force is animated — know That alone as Brahman, not this which people worship here."),

    # ═══════════════════════════════════════════════════════
    # KHAṆḌA 2  (5 mantras — the epistemological paradox)
    # ═══════════════════════════════════════════════════════

    (2, 1,
     "यदि मन्यसे सुवेदेति दभ्रमेवापि\nनूनं त्वं वेत्थ ब्रह्मणो रूपम् |\nयदस्य त्वं यदस्य देवेष्वथ\nनु मीमांस्यमेव ते मन्ये विदितम् || १ ||",
     "yadi manyase suvedeti dabhramevaapi\nnūnaṃ tvaṃ vettha brahmaṇo rūpam |\nyadasya tvaṃ yadasya deveṣvatha\nnu mīmāṃsyameva te manye viditam || 1 ||",
     "If you think 'I know Brahman well,' you know only a little of Its nature — you know only the form of Brahman that pertains to yourself or to the gods. Therefore Brahman must still be further inquired into by you, for I think you have not yet known It well."),

    (2, 2,
     "नाहं मन्ये सुवेदेति\nनो न वेदेति वेद च |\nयो नस्तद्वेद तद्वेद\nनो न वेदेति वेद च || २ ||",
     "nāhaṃ manye suvedeti\nno na vedeti veda ca |\nyo nastadveda tadveda\nno na vedeti veda ca || 2 ||",
     "I do not think that I know It well, nor do I think that I do not know It. He among us who knows the meaning of 'I neither know It nor do I know It' — he truly knows It."),

    (2, 3,
     "यस्यामतं तस्य मतं\nमतं यस्य न वेद सः |\nअविज्ञातं विजानतां\nविज्ञातमविजानताम् || ३ ||",
     "yasyāmataṃ tasya mataṃ\nmataṃ yasya na veda saḥ |\navijñātaṃ vijānatāṃ\nvijñātamavijānatām || 3 ||",
     "To him by whom It is not thought out (as an object), It is known; to him by whom It is thought out (as an object), he does not know It. It is not known by those who know It; It is known by those who do not know It."),

    (2, 4,
     "प्रतिबोधविदितं मतम्\nअमृतत्वं हि विन्दते |\nआत्मना विन्दते वीर्यं\nविद्यया विन्दते ऽमृतम् || ४ ||",
     "pratibodhaviditaṃ matam\namṛtatvaṃ hi vindate |\nātmanā vindate vīryaṃ\nvidyayā vindate amṛtam || 4 ||",
     "It is truly known when It is known in every state of consciousness (pratibodha); for by such knowledge one attains immortality. By one's own Self one attains strength; by knowledge one attains immortality."),

    (2, 5,
     "इह चेदवेदीदथ सत्यमस्ति\nन चेदिहावेदीन्महती विनष्टिः |\nभूतेषु भूतेषु विचित्य धीराः\nप्रेत्यास्माल्लोकादमृता भवन्ति || ५ ||",
     "iha cedavedīdatha satyamasti\nna cedihāvedīnmahatī vinaṣṭiḥ |\nbhūteṣu bhūteṣu vicitya dhīrāḥ\npretyāsmāllokādamṛtā bhavanti || 5 ||",
     "If one knows Brahman here in this life, there is truth; if one does not know It here, there is great loss. The wise, recognising Brahman in all beings, depart from this world and become immortal."),

    # ═══════════════════════════════════════════════════════
    # KHAṆḌA 3  (12 passages — the Yaksha story, part I)
    # ═══════════════════════════════════════════════════════

    (3, 1,
     '',
     "brahma ha devebhyo vijigye | tasya ha brahmaṇo vijaye devā amahīyanta || 1 ||",
     "Brahman won a victory for the gods. The gods, proud of this victory of Brahman, became conceited, thinking: 'This victory is ours alone; this glory is ours alone.'"),

    (3, 2,
     '',
     "taddhaiṣāṃ vijajñau | tebhyo ha prādurbabhūva | tannabyajānata kimidaṃ yakṣamiti || 2 ||",
     "Brahman perceived their conceit and appeared before them. But they did not recognise It, saying: 'What is this strange spirit (yakṣa)?'"),

    (3, 3,
     '',
     "te'gnimabruvan jātaveda etadvijānīhi kimidaṃ yakṣamiti | tatheti || 3 ||",
     "They said to Agni (Fire): 'O Jātaveda, go and find out what this spirit is.' Agni replied: 'So be it.'"),

    (3, 4,
     '',
     "tadabhyadravat | tamabhyavadat ko'sīti | agnirvā ahamīti bravīti jātavedā vā ahamīti | tasmin tvayi kiṃ vīryamiti | idaṃ sarvam dahed yad idaṃ pṛthivyāmiti || 4 ||",
     "Agni rushed towards it. The spirit asked: 'Who are you?' Agni replied: 'I am Agni, I am Jātaveda.' The spirit said: 'What power is in you?' Agni replied: 'I can burn everything there is on this earth.'"),

    (3, 5,
     '',
     "tasmai tṛṇaṃ nidhāya etad dahediti | tadupaprebhya sarvajavena | tannāśaknoddhartum | sa tata eva nivavṛte | naitad aśakam vijñātum yadyakṣamiti || 5 ||",
     "The spirit placed a blade of grass before Agni and said: 'Burn this.' Agni rushed at it with all his speed, but could not burn it. Then Agni returned and said to the gods: 'I was unable to find out what that spirit is.'"),

    (3, 6,
     '',
     "atha vāyumabravīt vāyo etadvijānīhi kimidaṃ yakṣamiti | tatheti || 6 ||",
     "Then they said to Vāyu (Wind): 'O Vāyu, go find out what this spirit is.' He replied: 'So be it.'"),

    (3, 7,
     '',
     "tadabhyadravat | tamabhyavadat ko'sīti | vāyurvā ahamīti bravīti mātariśvā vā ahamīti || 7 ||",
     "Vāyu rushed towards the spirit. The spirit asked: 'Who are you?' Vāyu replied: 'I am Vāyu; I am Mātariśvan (the breath of the universe).'"),

    (3, 8,
     '',
     "tasmin tvayi kiṃ vīryamiti | idaṃ sarvam ādadīya yad idaṃ pṛthivyāmiti || 8 ||",
     "'What power is in you?' the spirit asked. Vāyu replied: 'I can carry away everything there is on this earth.'"),

    (3, 9,
     '',
     "tasmai tṛṇaṃ nidhāya etad ādatsveti | tadupaprebhya sarvajavena | tannāśaknodādātum | sa tata eva nivavṛte | naitadaśakam vijñātum yadyakṣamiti || 9 ||",
     "The spirit placed a blade of grass before Vāyu and said: 'Carry this away.' Vāyu rushed at it with all his speed, but could not move it. Then Vāyu too returned and said to the gods: 'I was unable to find out what that spirit is.'"),

    (3, 10,
     '',
     "athendramabravīt maghavan etadvijānīhi kimidaṃ yakṣamīti | tatheti | tadabhyadravat | tasmāttirohitaṃ || 10 ||",
     "Then they said to Indra (the lord of the gods): 'O Maghavan, go find out what this spirit is.' He replied: 'So be it.' Indra rushed towards it, but the spirit vanished from his sight."),

    (3, 11,
     '',
     "sa tasminnevākāśe striyamājagāma bahūśobhamānām umāṃ haimavatīm | tāṃ hovāca kimidaṃ yakṣamiti || 11 ||",
     "In that very space, Indra came upon a woman, resplendently beautiful — Uma, the daughter of the Himalayas (Haimavati). He asked her: 'What is this spirit (yakṣa)?'"),

    (3, 12,
     '',
     "brahma ha etad iti hovāca | brahmaṇo vā etad vijaye mahīyadhvam iti | tato haiva vidāṃcakāra brahmeti || 12 ||",
     "Uma said: 'It is Brahman. Through Brahman's victory you are exalted.' From that alone did Indra come to know: 'It is Brahman.'"),

    # ═══════════════════════════════════════════════════════
    # KHAṆḌA 4  (9 passages — the teaching section)
    # ═══════════════════════════════════════════════════════

    (4, 1,
     '',
     "tasmādvā ete devā atitarāmivānyān devān yadagnivāyurendrāḥ | te hyenaṃ nedīṣṭhaṃ pasparśa | te hyenam prathamo vidāṃcakāra brahmeti || 1 ||",
     "Therefore these gods — Agni, Vāyu, and Indra — excel the other gods, for they touched Brahman most closely; it was they who first knew It as Brahman."),

    (4, 2,
     '',
     "tasmādvā indro'titarāmivānyān devān | sa hyenaṃ nedīṣṭhaṃ pasparśa | sa hyenaṃ prathamo vidāṃcakāra brahmeti || 2 ||",
     "Therefore Indra excels the other gods the most, for he touched It most closely and was the first to know It as Brahman."),

    (4, 3,
     '',
     "tasyaiṣa ādeśo yadetad vidyuto vyadyutadā iti nym ivaitadā iti adhi divam || 3 ||",
     "The teaching concerning Brahman is: It is like a flash of lightning that illumines and disappears, like the winking of an eye. This refers to the divine (adhi-daivam) aspect of Brahman."),

    (4, 4,
     '',
     "athadhyātmaṃ | yadesā ā itīva manasyabhisaṃkalpata enena cita hṛdayam | abhīkṣṇaṃ saṃkalpa ācetat | tadvā asyaitad brahma tad brahmetivā upāsīta tadvanam | tad dhāsyāvaṃ tadvanam iti nāmopāsīta | sa ya etadevam veda abhi haināṃ sarvāṇi bhūtāni saṃvāñchanti || 4 ||",
     "Now regarding the Self (adhyātmam): Brahman is that which is indicated by the reflection of the mind — by which the mind is repeatedly moved. Brahman is the object of desire of all beings. One should meditate on It as 'Tadvanam' (that which is to be longed for). One who knows Brahman thus — all beings long for him."),

    (4, 5,
     '',
     "upaniṣad bho brūhīti | uktā ta upaniṣad | brāhmīṃ vāva ta upaniṣadamabrūma || 5 ||",
     "The disciple said: 'Sir, teach me the Upaniṣad.' The teacher replied: 'The Upaniṣad has been taught to you. We have indeed taught you the Brahma-Upaniṣad.'"),

    (4, 6,
     '',
     "tasyai tapo damaḥ karmeti pratiṣṭhā | vedāḥ sarvāṅgāni | satyamāyatanam || 6 ||",
     "Tapas (austerity), dama (self-restraint), and karma (action) are its foundation. The Vedas are all its limbs. Truth is its abode."),

    (4, 7,
     '',
     "yo vā etāmevam vedāpahati pāpmānam | anante svarge loke jyeye pratitiṣṭhati | pratitiṣṭhati || 7 ||",
     "Whoever knows this Brahma-Upaniṣad thus destroys all sin and becomes firmly established in the infinite, supreme, and immortal world of Brahman. He is firmly established."),

    (4, 8,
     '',
     "sa ya etadevam veda | śreyaścāsmai bhavati | na hāsya tat tasmāt tadupāsīta yo brahma veda brahmaiva bhavati || 8 ||",
     "One who knows It thus attains what is greater and better. Evil does not overpower him; he overcomes all evil. He who knows Brahman becomes Brahman itself."),

    (4, 9,
     '',
     "namas te astu | tvayyeva astu | namas te brahmane | tvam eva pratyakṣaṃ brahma | tvaṃ brahma vadisyāmi | ṛtaṃ vadisyāmi | satyaṃ vadisyāmi | tan māmavatu | tad vaktāramavatu | avatu mām avatu vaktāram avatu vaktāram || 9 ||",
     "Salutation to you, O Brahman. Salutation to you. You alone are the directly perceived Brahman. I shall declare you to be Brahman. I shall speak what is right; I shall speak what is true. May that Brahman protect me; may It protect the teacher; may It protect me; may It protect the teacher — may It protect the teacher."),
]

# ── File template ─────────────────────────────────────────────────────────────

FILE_HEADER = """\
# Kena Upaniṣad — Khaṇḍa {khanda}

```yaml
text: kena_upanishad
khanda: {khanda}
source: Swami Mādhavānanda / Swami Gambhīrānanda (Advaita Ashrama tradition)
```

---
"""

MANTRA_TEMPLATE = """\
## Text {khanda}.{mantra}

{sanskrit_block}**Transliteration**

{iast}

**Translation**

{translation}

---
"""


def render_mantra(khanda, mantra, sanskrit, iast, translation):
    sanskrit_block = ''
    if sanskrit:
        sanskrit_block = f"**Sanskrit**\n\n{sanskrit}\n\n"
    return MANTRA_TEMPLATE.format(
        khanda=khanda,
        mantra=mantra,
        sanskrit_block=sanskrit_block,
        iast=iast,
        translation=translation,
    )


def generate(dry_run=False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Group mantras by khaṇḍa
    from collections import defaultdict
    by_khanda = defaultdict(list)
    for row in KENA:
        by_khanda[row[0]].append(row)

    for khanda, rows in sorted(by_khanda.items()):
        content = FILE_HEADER.format(khanda=khanda)
        content += '\n'
        for khanda_, mantra, sanskrit, iast, translation in rows:
            content += render_mantra(khanda_, mantra, sanskrit, iast, translation)

        filename = f"kena_{khanda}.md"
        path = OUTPUT_DIR / filename

        if dry_run:
            logging.info(f"DRY RUN: {filename} — {len(rows)} mantras")
        else:
            path.write_text(content, encoding='utf-8')
            logging.info(f"Wrote {path} — {len(rows)} mantras")

    total = len(KENA)
    logging.info(f"Done — {total} mantras across {len(by_khanda)} khaṇḍas")


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Generate Kena Upaniṣad corpus files')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    generate(dry_run=args.dry_run)
