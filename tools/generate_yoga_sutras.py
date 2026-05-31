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
Generate Yoga Sutra corpus files (key sūtras for AIM counseling entry points):
  - corpus/yoga_sutras/yoga_sutra_1.md  (Samadhi Pada, selected)
  - corpus/yoga_sutras/yoga_sutra_2.md  (Sadhana Pada, selected)
  - corpus/yoga_sutras/yoga_sutra_4.md  (Kaivalya Pada, selected)

Pāda 3 (Vibhūti) omitted — siddhis are outside AIM's counseling scope.
"""
import os

OUT_DIR = os.path.join("corpus", "yoga_sutras")

# Each entry: (pada, sutra, sanskrit, iast, translation, prakriya,
#              pedagogical_role, ontological_scope, pedagogical_stage,
#              cognitive_mode, adhikara_level, note)

SUTRAS_1 = [
    (1, 1,
     "अथ योगानुशासनम् ॥ १.१ ॥",
     "atha yogānuśāsanam ||",
     "Now begins the teaching of yoga.",
     "inquiry-opening",
     "inquiry-arousal",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "Atha marks an auspicious beginning and signals readiness (adhikāra). "
     "The text opens not with a definition but with the declaration that teaching is now occurring — "
     "pointing to the living transmission rather than mere doctrine."),

    (1, 2,
     "योगश्चित्तवृत्तिनिरोधः ॥ १.२ ॥",
     "yogaś citta-vṛtti-nirodhaḥ ||",
     "Yoga is the cessation of the modifications of the mind.",
     "vritti-definition",
     "definition-of-yoga",
     "paramarathika",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The foundational definition. Citta = mind-field; vṛtti = modifications/fluctuations; "
     "nirodha = cessation. This sūtra is the diagnostic basis for all AIM counseling: "
     "the presenting problem is always a vṛtti that obscures the seer."),

    (1, 3,
     "तदा द्रष्टुः स्वरूपेऽवस्थानम् ॥ १.३ ॥",
     "tadā draṣṭuḥ svarūpe 'vasthānam ||",
     "Then the seer abides in its own nature.",
     "drashtr-svarupa",
     "direct-pointing",
     "paramarathika",
     "nididhyasana",
     "direct_insight",
     "uttama",
     "The positive counterpart to 1.2. When vṛttis cease, the seer (draṣṭṛ/Puruṣa) abides "
     "as what it always already is. Svarūpa = own nature. This is not a state to be attained "
     "but a recognition of what was obscured."),

    (1, 4,
     "वृत्तिसारूप्यमितरत्र ॥ १.४ ॥",
     "vṛtti-sārūpyam itaratra ||",
     "At other times, it [the seer] is identified with the modifications.",
     "vritti-identification",
     "bondage-diagnosis",
     "dual-register",
     "manana",
     "analytic_inquiry",
     "madhyama",
     "The bondage mechanism: sārūpya = assuming the form of. The seer appears to take the "
     "shape of whatever vṛtti arises. This is the root of misidentification — asmitā "
     "expressed in functional terms. Key counseling entry: which vṛtti is the student "
     "currently identified with?"),

    (1, 5,
     "वृत्तयः पञ्चतय्यः क्लिष्टाक्लिष्टाः ॥ १.५ ॥",
     "vṛttayaḥ pañcatayyaḥ kliṣṭā-akliṣṭāḥ ||",
     "The modifications are fivefold; they are either afflicted or non-afflicted.",
     "vritti-classification",
     "diagnostic-taxonomy",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The five vṛttis are kliṣṭa (producing kleśas/bondage) or akliṣṭa (not doing so). "
     "The kliṣṭa/akliṣṭa distinction is the first diagnostic axis — even apparently 'good' "
     "cognitions can be kliṣṭa if they reinforce body-identification."),

    (1, 6,
     "प्रमाणविपर्ययविकल्पनिद्रास्मृतयः ॥ १.६ ॥",
     "pramāṇa-viparyaya-vikalpa-nidrā-smṛtayaḥ ||",
     "They are: right cognition, error, imagination, sleep, and memory.",
     "vritti-five-types",
     "diagnostic-taxonomy",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The five named: (1) pramāṇa (valid cognition), (2) viparyaya (wrong cognition/error), "
     "(3) vikalpa (imagination/conceptual construction), (4) nidrā (sleep/absence), "
     "(5) smṛti (memory). Most counseling situations involve predominance of viparyaya "
     "or vikalpa — misperception or conceptual superimposition."),

    (1, 7,
     "प्रत्यक्षानुमानागमाः प्रमाणानि ॥ १.७ ॥",
     "pratyakṣānumānāgamāḥ pramāṇāni ||",
     "Right cognition arises from perception, inference, and testimony.",
     "pramana-definition",
     "epistemological-grounding",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The three pramāṇas of Yoga. Āgama (scripture/testimony) is the third — "
     "establishing the guru's teaching as a valid pramāṇa alongside perception and inference. "
     "This grounds śravaṇa as epistemically legitimate."),

    (1, 8,
     "विपर्ययो मिथ्याज्ञानमतद्रूपप्रतिष्ठम् ॥ १.८ ॥",
     "viparyayo mithyā-jñānam atad-rūpa-pratiṣṭham ||",
     "Error is false knowledge, established in a form that is not its own.",
     "viparyaya-definition",
     "misidentification-diagnosis",
     "dual-register",
     "manana",
     "analytic_inquiry",
     "madhyama",
     "Viparyaya is the Yoga system's analog of avidyā. Atad-rūpa = a form not its own. "
     "The seer takes itself to be the body, mind, or vṛtti — established in a form that is "
     "not its own nature. This is the primary target of AIM's inquiry."),

    (1, 9,
     "शब्दज्ञानानुपाती वस्तुशून्यो विकल्पः ॥ १.९ ॥",
     "śabda-jñānānupātī vastu-śūnyo vikalpaḥ ||",
     "Imagination follows verbal knowledge without a corresponding object.",
     "vikalpa-definition",
     "conceptual-superimposition",
     "dual-register",
     "manana",
     "analytic_inquiry",
     "madhyama",
     "Vikalpa is conceptual construction: knowing through words that have no referent "
     "in direct experience. The word 'I' generates an apparent subject without a real object. "
     "Much of samsaric suffering is sustained by vikalpa — linguistic reification of 'me.'"),

    (1, 12,
     "अभ्यासवैराग्याभ्यां तन्निरोधः ॥ १.१२ ॥",
     "abhyāsa-vairāgyābhyāṃ tan-nirodhaḥ ||",
     "Their cessation comes through practice and dispassion.",
     "abhyasa-vairagya",
     "method-prescription",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The two-wing method: abhyāsa (sustained practice toward stillness) and vairāgya "
     "(dispassion/non-clinging). These are not sequential but simultaneous. Vairāgya "
     "prevents re-attachment to whatever the practice temporarily transcends."),

    (1, 13,
     "तत्र स्थितौ यत्नोऽभ्यासः ॥ १.१३ ॥",
     "tatra sthitau yatno 'bhyāsaḥ ||",
     "Of these, practice is the effort toward steadiness.",
     "abhyasa-definition",
     "method-definition",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "Abhyāsa is not any practice but specifically the effort (yatna) toward sthiti "
     "(steadiness). The target of practice is the cessation of oscillation — "
     "not the production of experiences."),

    (1, 14,
     "स तु दीर्घकालनैरन्तर्यसत्कारासेवितो दृढभूमिः ॥ १.१४ ॥",
     "sa tu dīrgha-kāla-nairantarya-satkārāsevito dṛḍha-bhūmiḥ ||",
     "But that practice becomes firmly grounded when cultivated for a long time, "
     "without interruption, and with devoted care.",
     "abhyasa-conditions",
     "method-qualification",
     "dual-register",
     "manana",
     "analytic_inquiry",
     "madhyama",
     "Three conditions for dṛḍha-bhūmi (firm ground): dīrgha-kāla (long time), "
     "nairantarya (without interruption), satkāra (with devotion/respect). "
     "The satkāra condition distinguishes mechanical repetition from genuine sādhana."),

    (1, 15,
     "दृष्टानुश्रविकविषयवितृष्णस्य वशीकारसंज्ञा वैराग्यम् ॥ १.१५ ॥",
     "dṛṣṭānuśravika-viṣaya-vitṛṣṇasya vaśīkāra-saṃjñā vairāgyam ||",
     "Dispassion is the mastery of one who has no thirst for objects that are seen "
     "or heard about.",
     "vairagya-definition",
     "method-definition",
     "dual-register",
     "manana",
     "analytic_inquiry",
     "madhyama",
     "Vairāgya is not suppression but vaśīkāra — mastery, the mind no longer pulled. "
     "It covers both dṛṣṭa (directly experienced) and anuśravika (objects promised by "
     "scripture, i.e., heavenly rewards). Complete vairāgya extends to subtle spiritual goals."),

    (1, 16,
     "तत्परं पुरुषख्यातेर्गुणवैतृष्ण्यम् ॥ १.१६ ॥",
     "tat-paraṃ puruṣa-khyāter guṇa-vaitṛṣṇyam ||",
     "The highest dispassion is non-thirst for the guṇas, arising from the vision of Puruṣa.",
     "para-vairagya",
     "direct-pointing",
     "paramarathika",
     "nididhyasana",
     "direct_insight",
     "uttama",
     "Para-vairāgya: the highest dispassion arises not from will but from puruṣa-khyāti "
     "(the vision of Puruṣa as pure witnessing consciousness). When the Self is recognized, "
     "the guṇas lose their pull automatically — not suppressed but transcended through knowledge."),

    (1, 30,
     "व्याधिस्त्यानसंशयप्रमादालस्याविरतिभ्रान्तिदर्शनालब्धभूमिकत्वानवस्थितत्वानि "
     "चित्तविक्षेपास्तेऽन्तरायाः ॥ १.३० ॥",
     "vyādhi-styāna-saṃśaya-pramāda-ālasya-avirati-bhrāntidarśana-"
     "alabdha-bhūmikatva-anavasthitatvāni citta-vikṣepās te 'ntarāyāḥ ||",
     "Illness, apathy, doubt, carelessness, laziness, sensuality, false perception, "
     "failure to attain firm ground, and inability to sustain it — these are the "
     "distractions of the mind; they are the obstacles.",
     "viksepa-obstacles",
     "diagnostic-obstacles",
     "dual-register",
     "manana",
     "analytic_inquiry",
     "madhyama",
     "Nine obstacles (antarāya) mapped as vikṣepa (distraction/scattering) of citta. "
     "AIM counseling diagnostic: which antarāya is operative? Saṃśaya (doubt) and "
     "bhrāntidarśana (false perception) are the most common presenting obstacles. "
     "Alabdha-bhūmikatva (not attaining firm ground) describes the stuck student."),

    (1, 31,
     "दुःखदौर्मनस्याङ्गमेजयत्वश्वासप्रश्वासा विक्षेपसहभुवः ॥ १.३१ ॥",
     "duḥkha-daurmanasya-aṅgamejayatva-śvāsapraśvāsā vikṣepa-sahabhuvaḥ ||",
     "Pain, despondency, trembling of the limbs, and disturbed breathing "
     "accompany the distractions.",
     "viksepa-symptoms",
     "somatic-diagnostic",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The embodied symptoms that accompany the mental obstacles: duḥkha (pain), "
     "daurmanasya (depression/despondency), aṅgamejayatva (bodily trembling), "
     "śvāsapraśvāsa (disturbed breath). These are the somatic markers of a mind "
     "in vikṣepa — direct counseling entry points through the body."),

    (1, 32,
     "तत्प्रतिषेधार्थमेकतत्त्वाभ्यासः ॥ १.३२ ॥",
     "tat-pratiṣedhārtham eka-tattvābhyāsaḥ ||",
     "For their prevention, the practice of one principle.",
     "eka-tattva-abhyasa",
     "method-prescription",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The remedy for all nine obstacles is eka-tattva-abhyāsa — practice of one principle. "
     "The 'one principle' is deliberate: Patañjali does not specify which, allowing for "
     "the guru to prescribe the appropriate single focus based on the student's adhikāra."),
]

SUTRAS_2 = [
    (2, 1,
     "तपःस्वाध्यायेश्वरप्रणिधानानि क्रियायोगः ॥ २.१ ॥",
     "tapaḥ-svādhyāya-Īśvara-praṇidhānāni kriyā-yogaḥ ||",
     "Tapas, self-study, and surrender to Īśvara constitute kriyā yoga.",
     "kriya-yoga",
     "sadhana-prescription",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The practical triad: tapas (discipline/heat), svādhyāya (self-study/scripture study), "
     "Īśvara-praṇidhāna (surrender to the Lord). Together they constitute kriyā yoga — "
     "yoga of action, the foundation before formal meditation. Svādhyāya bridges tapas "
     "and surrender: it is both study of texts and inquiry into the self."),

    (2, 2,
     "समाधिभावनार्थः क्लेशतनूकरणार्थश्च ॥ २.२ ॥",
     "samādhi-bhāvanārthaḥ kleśa-tanūkaraṇārthaś ca ||",
     "It is practiced for cultivating samādhi and for attenuating the afflictions.",
     "kriya-yoga-purpose",
     "method-clarification",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "Two purposes of kriyā yoga: samādhi-bhāvana (cultivating absorption) and "
     "kleśa-tanūkaraṇa (thinning/attenuating the kleśas). Tanūkaraṇa means reducing "
     "their force, not eliminating them — they are eventually destroyed only by viveka-khyāti."),

    (2, 3,
     "अविद्यास्मितारागद्वेषाभिनिवेशाः क्लेशाः ॥ २.३ ॥",
     "avidyāsmitā-rāga-dveṣa-abhiniveśāḥ kleśāḥ ||",
     "Avidyā, asmitā, rāga, dveṣa, and abhiniveśa are the five afflictions.",
     "klesa-five",
     "diagnostic-taxonomy",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The five kleśas: (1) avidyā (ignorance), (2) asmitā (I-am-ness/ego), "
     "(3) rāga (attraction), (4) dveṣa (aversion), (5) abhiniveśa (fear of death/clinging to life). "
     "All five are derivatives of avidyā (see 2.4). The central AIM diagnostic framework."),

    (2, 4,
     "अविद्या क्षेत्रमुत्तरेषां प्रसुप्ततनुविच्छिन्नोदाराणाम् ॥ २.४ ॥",
     "avidyā kṣetram uttareṣāṃ prasuptatanu-vicchinnodārāṇām ||",
     "Avidyā is the field for the others, whether they be dormant, attenuated, "
     "intercepted, or active.",
     "avidya-as-root",
     "root-cause-identification",
     "paramarathika",
     "manana",
     "analytic_inquiry",
     "uttama",
     "Avidyā is the kṣetra (field/soil) in which the other four kleśas grow. "
     "The four states of a kleśa — prasupta (dormant), tanu (thin), vicchinna (intercepted), "
     "udāra (active) — map a progression. Dormant kleśas are the most dangerous: "
     "they appear absent but remain as seeds (saṃskāras)."),

    (2, 5,
     "अनित्याशुचिदुःखानात्मसु नित्यशुचिसुखात्मख्यातिरविद्या ॥ २.५ ॥",
     "anityāśuci-duḥkhānātmasu nitya-śuci-sukha-ātmakhyātir avidyā ||",
     "Avidyā is taking the impermanent to be permanent, the impure to be pure, "
     "the painful to be pleasurable, and the non-self to be the Self.",
     "avidya-definition",
     "root-ignorance-analysis",
     "paramarathika",
     "manana",
     "analytic_inquiry",
     "uttama",
     "The fourfold error of avidyā: (1) nitya/anitya confusion (permanence), "
     "(2) śuci/aśuci confusion (purity), (3) sukha/duḥkha confusion (pleasure), "
     "(4) ātman/anātman confusion (selfhood). The fourth is the root — "
     "misidentification with the non-self. The first three are its expressions."),

    (2, 6,
     "दृग्दर्शनशक्त्योरेकात्मतेवास्मिता ॥ २.६ ॥",
     "dṛg-darśana-śaktyor ekātmatevāsmitā ||",
     "Asmitā is as if the powers of the seer and the instrument of seeing were one.",
     "asmita-definition",
     "ego-mechanism",
     "dual-register",
     "manana",
     "analytic_inquiry",
     "madhyama",
     "Asmitā is the confusion of dṛk (seer/Puruṣa) and darśana-śakti (power of seeing/buddhi). "
     "The 'iva' (as if) is crucial — they are not actually one, only appear so. "
     "This is the precise mechanism of ego: the witness is mistaken for the instrument."),

    (2, 7,
     "सुखानुशयी रागः ॥ २.७ ॥",
     "sukhānuśayī rāgaḥ ||",
     "Rāga is that which follows in the wake of pleasure.",
     "raga-definition",
     "affliction-analysis",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "Anuśayī = that which follows as a residue. Rāga is not the pleasure itself "
     "but the latent tendency (saṃskāra) that follows the experience of pleasure — "
     "the pull toward its repetition. This is the addictive mechanism in Yoga terms."),

    (2, 8,
     "दुःखानुशयी द्वेषः ॥ २.८ ॥",
     "duḥkhānuśayī dveṣaḥ ||",
     "Dveṣa is that which follows in the wake of pain.",
     "dvesa-definition",
     "affliction-analysis",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The paired affliction to rāga. Dveṣa is the latent aversion-tendency left by the "
     "experience of pain — the impulse to avoid its repetition. Rāga and dveṣa together "
     "drive the pleasure-pain oscillation that sustains saṃsāra."),

    (2, 9,
     "स्वरसवाही विदुषोऽपि तथारूढोऽभिनिवेशः ॥ २.९ ॥",
     "svarasavāhī viduṣo 'pi tathārūḍho 'bhiniveśaḥ ||",
     "Abhiniveśa, flowing by its own momentum, is established even in the learned.",
     "abhinivesa-definition",
     "fear-of-death-analysis",
     "dual-register",
     "manana",
     "analytic_inquiry",
     "uttama",
     "Abhiniveśa = clinging to life, fear of annihilation. Svarasavāhī = flows by its own "
     "current (without external cause). The crucial qualification: viduṣo 'pi — even in the "
     "learned/scholars. Intellectual understanding does not dissolve this kleśa. "
     "Only the direct recognition of the deathless nature of Puruṣa removes it."),

    (2, 10,
     "ते प्रतिप्रसवहेयाः सूक्ष्माः ॥ २.१० ॥",
     "te pratiprasava-heyāḥ sūkṣmāḥ ||",
     "When subtle, those [kleśas] are to be dissolved by involution into their cause.",
     "klesa-subtle-remedy",
     "method-prescription",
     "paramarathika",
     "manana",
     "analytic_inquiry",
     "uttama",
     "Pratiprasava = counter-evolution, return to the source. When kleśas are in their "
     "subtle (tanu) form — reduced by practice but not eliminated — they are dissolved "
     "by tracing them back to their root in avidyā and thence to citta, to Puruṣa."),

    (2, 11,
     "ध्यानहेयास्तद्वृत्तयः ॥ २.११ ॥",
     "dhyāna-heyās tad-vṛttayaḥ ||",
     "Their gross modifications are to be removed by meditation.",
     "klesa-gross-remedy",
     "method-prescription",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The gross (udāra) forms of kleśas — when they are active as vṛttis — are addressed "
     "by dhyāna (meditation), not inquiry alone. Two levels of treatment: gross forms "
     "by meditation, subtle roots by pratiprasava/viveka."),

    (2, 16,
     "हेयं दुःखमनागतम् ॥ २.१६ ॥",
     "heyaṃ duḥkham anāgatam ||",
     "The pain that has not yet come is to be avoided.",
     "future-suffering",
     "urgency-arousal",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The most compact statement of the purpose of sādhana. Past pain cannot be undone; "
     "present pain must be endured; but future pain — rooted in the conjunction of seer "
     "and seen — can be forestalled by knowledge. This creates urgency for inquiry now."),

    (2, 17,
     "द्रष्टृदृश्ययोः संयोगो हेयहेतुः ॥ २.१७ ॥",
     "draṣṭṛ-dṛśyayoḥ saṃyogo heya-hetuḥ ||",
     "The conjunction of the seer and the seen is the cause of what is to be avoided.",
     "samyoga-as-bondage",
     "root-cause-identification",
     "paramarathika",
     "manana",
     "analytic_inquiry",
     "uttama",
     "Saṃyoga = conjunction, apparent union of draṣṭṛ (seer/Puruṣa) and dṛśya "
     "(seen/Prakṛti). This apparent union — not their actual mixing — is the causal root "
     "of all suffering. Viveka-khyāti dissolves the saṃyoga by revealing it as apparent only."),

    (2, 20,
     "द्रष्टा दृशिमात्रः शुद्धोऽपि प्रत्ययानुपश्यः ॥ २.२० ॥",
     "draṣṭā dṛśimātraḥ śuddho 'pi pratyayānupaśyaḥ ||",
     "The seer is nothing but pure seeing; though pure, it appears to look "
     "through the cognitions of the mind.",
     "drashtr-as-pure-consciousness",
     "atman-as-witness-pointing",
     "paramarathika",
     "nididhyasana",
     "direct_insight",
     "uttama",
     "The Yoga Sūtra's closest approach to the Advaita witness-pointing. The draṣṭṛ "
     "is dṛśimātra — pure seeing alone. Śuddha (pure) yet appears (iva) to look through "
     "pratyaya (cognitions/mental content). The impurity is apparent, not real."),

    (2, 25,
     "तदभावात् संयोगाभावो हानं तद् दृशेः कैवल्यम् ॥ २.२५ ॥",
     "tad-abhāvāt saṃyogābhāvo hānaṃ tad dṛśeḥ kaivalyam ||",
     "From the absence of avidyā, there is no conjunction; "
     "that is the freedom of the seer — kaivalya.",
     "kaivalya-through-viveka",
     "liberation-pointing",
     "paramarathika",
     "nididhyasana",
     "direct_insight",
     "uttama",
     "Kaivalya = aloneness/independence of the seer. When avidyā dissolves, saṃyoga "
     "dissolves, and the seer stands in its own nature. The causal chain: "
     "avidyā → saṃyoga → duḥkha; its reversal: viveka → no saṃyoga → kaivalya."),

    (2, 26,
     "विवेकख्यातिरविप्लवा हानोपायः ॥ २.२६ ॥",
     "viveka-khyātir aviplavā hānopāyaḥ ||",
     "Uninterrupted discriminative awareness is the means of liberation.",
     "viveka-khyati",
     "direct-means-identification",
     "paramarathika",
     "nididhyasana",
     "direct_insight",
     "uttama",
     "Viveka-khyāti = discriminative knowledge (of Puruṣa from Prakṛti). Aviplavā = "
     "without interruption, unwaveringly. This is the sole means (upāya) of liberation "
     "in Sāṃkhya-Yoga. The Advaita parallel is jñāna/nididhyāsana. The qualification "
     "aviplavā is key — intermittent discrimination does not liberate."),

    (2, 29,
     "यमनियमासनप्राणायामप्रत्याहारधारणाध्यानसमाधयोऽष्टावङ्गानि ॥ २.२९ ॥",
     "yama-niyamāsana-prāṇāyāma-pratyāhāra-dhāraṇā-dhyāna-samādhayo 'ṣṭāv aṅgāni ||",
     "Restraint, observance, posture, breath-control, withdrawal, concentration, "
     "meditation, and absorption are the eight limbs.",
     "ashtanga-yoga",
     "sadhana-framework",
     "dual-register",
     "sravana",
     "analytic_contemplative",
     "madhyama",
     "The eight-limbed path. For AIM counseling purposes, the first two limbs "
     "(yama/niyama) address ethical/behavioral obstacles, prāṇāyāma/pratyāhāra address "
     "somatic/sensory obstacles, and dhāraṇā/dhyāna/samādhi address the cognitive. "
     "Entry point selection depends on the presenting obstacle."),
]

SUTRAS_4 = [
    (4, 18,
     "सदा ज्ञाताश्चित्तवृत्तयस्तत्प्रभोः पुरुषस्यापरिणामित्वात् ॥ ४.१८ ॥",
     "sadā jñātāś citta-vṛttayas tat-prabhoḥ puruṣasyāpariṇāmitvāt ||",
     "The modifications of the mind are always known to their master, Puruṣa, "
     "because of his unchanging nature.",
     "purusa-as-witness",
     "atman-as-witness-pointing",
     "paramarathika",
     "nididhyasana",
     "direct_insight",
     "uttama",
     "The final pāda's direct statement of Puruṣa as the eternal witness. "
     "Sadā jñāta = always known. Apariṇāmitva = unchanging nature. The witness never "
     "changes — only the vṛttis change. This unchanging witness is the ground that makes "
     "all change perceptible. Key for the atman-as-witness prakriyā in AIM."),

    (4, 25,
     "विशेषदर्शिन आत्मभावभावनाविनिवृत्तिः ॥ ४.२५ ॥",
     "viśeṣa-darśina ātmabhāva-bhāvanā-vinivṛttiḥ ||",
     "For one who sees the distinction, the continuous imagining of 'I am' ceases.",
     "asmita-dissolution",
     "ego-dissolution-pointing",
     "paramarathika",
     "nididhyasana",
     "direct_insight",
     "uttama",
     "Viśeṣa-darśin = one who sees the distinction (between Puruṣa and Prakṛti/citta). "
     "Ātmabhāva-bhāvanā = the repeated imagining of selfhood/I-am-ness. When viveka is "
     "firmly established, the compulsive construction of ego ceases. Not suppressed — "
     "seen through."),

    (4, 34,
     "पुरुषार्थशून्यानां गुणानां प्रतिप्रसवः कैवल्यं\nस्वरूपप्रतिष्ठा वा चितिशक्तिरिति ॥ ४.३४ ॥",
     "puruṣārtha-śūnyānāṃ guṇānāṃ pratiprasavaḥ kaivalyaṃ\nsvarūpa-pratiṣṭhā vā citiśaktir iti ||",
     "Liberation is the involution of the guṇas, emptied of their purpose for Puruṣa; "
     "or the establishment of consciousness in its own nature.",
     "kaivalya-definition",
     "liberation-definition",
     "paramarathika",
     "nididhyasana",
     "direct_insight",
     "uttama",
     "The final sūtra's double definition of kaivalya: (1) the guṇas return to their "
     "source (pratiprasava) having fulfilled their purpose, (2) citiśakti (power of "
     "consciousness) stands established in its own nature (svarūpa-pratiṣṭhā). "
     "The 'iti' closes the text — 'thus ends [the teaching].' The second definition "
     "directly parallels Advaita's svarūpāvasthāna (1.3 in CU)."),
]

# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

PADA_META = {
    1: ("Samādhi Pāda", "The Nature of Samādhi — Vṛttis and Their Cessation",
        ["citta_vritti_nirodha", "drashtr_svarupa", "vritti_classification",
         "abhyasa_vairagya", "viksepa_obstacles"]),
    2: ("Sādhana Pāda", "The Means of Practice — Kleśas and Liberation",
        ["klesa_framework", "avidya_as_root", "kriya_yoga",
         "viveka_khyati", "kaivalya"]),
    4: ("Kaivalya Pāda", "Liberation — Puruṣa as Witness and Kaivalya",
        ["purusa_as_witness", "asmita_dissolution", "kaivalya_definition"]),
}


def build_sutra_block(pada, sutra, sanskrit, iast, translation,
                      prakriya, pedagogical_role, ontological_scope,
                      pedagogical_stage, cognitive_mode, adhikara_level, note):
    ref = f"{pada}.{sutra}"
    lines = [f"## Text {ref}", ""]
    if sanskrit:
        lines += ["**Sanskrit**", "", sanskrit, ""]
    lines += ["**Transliteration**", "", iast, "",
              "**Translation**", "", translation, ""]
    lines += ["```yaml",
              f"prakriya: '{prakriya}'",
              f"pedagogical_role: '{pedagogical_role}'",
              f"ontological_scope: '{ontological_scope}'",
              f"pedagogical_stage: '{pedagogical_stage}'",
              f"cognitive_mode: '{cognitive_mode}'",
              f"adhikara_level: '{adhikara_level}'",
              f'note: "{note.replace(chr(34), chr(92)+chr(34))}"',
              "```", "", "---", ""]
    return "\n".join(lines)


def build_pada_file(pada, sutras):
    pada_name, section_title, themes = PADA_META[pada]
    canonical = f"{pada}.1–{sutras[-1][1]} (selected)"

    parts = [
        f"# Yoga Sūtras of Patañjali — {pada_name}",
        "",
        f"## {section_title}",
        "",
        "---",
        "```yaml",
        f"title: Yoga Sūtras — {pada_name}",
        f"section_title: {section_title}",
        "tradition: Yoga / Sāṃkhya",
        "text_type: Sūtra",
        f"pada: {pada}",
        "knowledge_tier: para_vidyā",
        "macro_function: diagnosis_and_method",
        "teaching_method: analytic_enumeration",
        "dialogue_type: systematic_teaching",
        "primary_themes:",
    ]
    for t in themes:
        parts.append(f"  - {t}")
    parts += [
        f"canonical_reference: Yoga Sūtras {canonical}",
        "```",
        "---",
        "",
    ]
    for entry in sutras:
        parts.append(build_sutra_block(*entry))
    return "\n".join(parts)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    for pada, sutras in [(1, SUTRAS_1), (2, SUTRAS_2), (4, SUTRAS_4)]:
        content = build_pada_file(pada, sutras)
        path = os.path.join(OUT_DIR, f"yoga_sutra_{pada}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Written: {path} ({len(sutras)} sūtras)")


if __name__ == "__main__":
    main()
