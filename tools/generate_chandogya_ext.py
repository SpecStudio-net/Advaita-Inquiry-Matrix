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
Generate Chandogya Upanishad extension corpus files:
  - corpus/upanishads/chandogya/chandogya_3_14.md  (3.14.1-4)
  - corpus/upanishads/chandogya/chandogya_8.md     (8.1-12, key passages)
"""
import os

OUT_DIR = os.path.join("corpus", "upanishads", "chandogya")

# ---------------------------------------------------------------------------
# 3.14 — Sarvam khalv idam brahma
# ---------------------------------------------------------------------------

CHANDOGYA_3_14 = [
    (
        "3.14.1",
        "सर्वं खल्विदं ब्रह्म तज्जलानिति शान्त उपासीत ।\nअथ खलु क्रतुमयः पुरुषो यथाक्रतुरस्मिँल्लोके पुरुषो भवति\nतथेतः प्रेत्य भवति स क्रतुं कुर्वीत ॥ ३.१४.१ ॥",
        "sarvam khalv idaṃ brahma tajjalāniti śānta upāsīta |\natha khalu kratumayaḥ puruṣo yathākratur asmiṃl loke puruṣo bhavati\ntathetaḥ pretya bhavati; sa kratum kurvīta ||",
        "All this is indeed Brahman. From it all things are born, in it all things live, and "
        "into it all things dissolve. Therefore one should worship with tranquillity. "
        "Now, man is constituted of will. As is his will in this world, so does he become "
        "after leaving it. Let him therefore form his will accordingly.",
        "sarvam-khalv-idam",
        "mahavakya-direct-pointing",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The opening mahāvākya of this section. All is Brahman — tajjalān: from Brahman (taj) "
        "all is born (ja), in Brahman all lives (la), into Brahman all dissolves (an). "
        "The will-teaching that follows links cosmology to rebirth logic.",
    ),
    (
        "3.14.2",
        "मनोमयः प्राणशरीरो भारूपः सत्यसङ्कल्प आकाशात्मा\nसर्वकर्मा सर्वकामः सर्वगन्धः सर्वरसः\nसर्वमिदमभ्यात्तोऽवाक्यनादर एष म आत्माऽन्तर्हृदये ।\nएतद्ब्रह्मैतमितः प्रेत्याभिसंभवितास्मीति\nयस्य स्यादद्धा न विचिकित्सास्तीति ।\nहारुणिरुवाच ॥ ३.१४.२ ॥",
        "manomayaḥ prāṇaśarīro bhārūpaḥ satyasaṃkalpa ākāśātmā\nsarvakarmā sarvakāmaḥ sarvagandhaḥ sarvarasaḥ\nsarvam idam abhyātto 'vākyam ānadaraḥ eṣa ma ātmā 'ntarhṛdaye |\netad brahmaitam itaḥ pretya abhisambhavitāsmi iti\nyasya syād addhā na vicikitsāsti iti |\nhāruṇir uvāca ||",
        "He is constituted of mind, his body is life, his form is light, his intention is "
        "truth, his self is space. He performs all actions, has all desires, has all smells, "
        "has all tastes. He pervades all this, is without speech and without concern. "
        "This is my Self within the heart — this is Brahman. When I depart this life "
        "I shall merge into him. He who has no doubt about this — so said Āruṇi.",
        "dahara-vidya",
        "atman-in-heart-meditation",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The full description of the ātman in the heart — manomayaḥ prāṇaśarīraḥ. "
        "The ātman pervades everything (sarvam idam abhyātto) yet is subtler than space. "
        "The passage ends with the guru's direct identification: 'This is Brahman; "
        "when I die I shall merge into it.'",
    ),
    (
        "3.14.3",
        "एष म आत्माऽन्तर्हृदयेऽणीयान् व्रीहेर्वा यवाद्वा\nसर्षपाद्वा श्यामाकाद्वा श्यामाकतण्डुलाद्वाप्येष म\nआत्माऽन्तर्हृदये जयायान् पृथिव्या जयायानन्तरिक्षाज्\nजयायान् दिवो जयायानेभ्यो लोकेभ्यः ॥ ३.१४.३ ॥",
        "eṣa ma ātmā 'ntarhṛdaye 'ṇīyān vrīher vā yavād vā\nsarṣapād vā śyāmākād vā śyāmākataṇḍulād vā;\napy eṣa ma ātmā 'ntarhṛdaye jyāyān pṛthivyā jyāyān antarikṣāj\njyāyān divo jyāyān ebhyo lokebhyaḥ ||",
        "This Self within my heart is smaller than a grain of rice, smaller than a barleycorn, "
        "smaller than a mustard seed, smaller than a grain of millet, smaller than the kernel "
        "of a grain of millet. And this Self within my heart is greater than the earth, "
        "greater than the atmosphere, greater than the sky, greater than all these worlds.",
        "anor-aniyan",
        "scale-paradox-pointing",
        "paramarathika",
        "manana",
        "analytic_inquiry",
        "uttama",
        "The classic 'smaller than the smallest, greater than the greatest' description — "
        "aṇor aṇīyān mahato mahīyān in this Chāndogya form. Points to the ātman as beyond "
        "spatial categories while being the very ground of space.",
    ),
    (
        "3.14.4",
        "सर्वकर्मा सर्वकामः सर्वगन्धः सर्वरसः सर्वमिदमभ्यात्तोऽवाक्यनादर\nएष म आत्माऽन्तर्हृदयेतद्ब्रह्म\nतमितः प्रेत्याभिसंभवितास्मीति\nयस्य स्यादद्धा न विचिकित्सास्तीति\nहारुणिरुवाच ॥ ३.१४.४ ॥",
        "sarvakarmā sarvakāmaḥ sarvagandhaḥ sarvarasaḥ sarvam idam abhyātto 'vākyam ānadaraḥ\neṣa ma ātmā 'ntarhṛdaye etad brahma\ntam itaḥ pretya abhisambhavitāsmi iti\nyasya syād addhā na vicikitsāsti iti\nhāruṇir uvāca ||",
        "Performing all actions, having all desires, having all smells, having all tastes, "
        "pervading all this, without speech and without concern — this is my Self within "
        "the heart, this is Brahman. After leaving this life I shall merge into that. "
        "He who has no doubt about this — so said Āruṇi.",
        "atman-as-brahman",
        "mahavakya-culmination",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The culminating declaration: eṣa ma ātmāntarhṛdaye etad brahma — "
        "this Self in the heart is Brahman. The phrase yasya syād addhā na vicikitsāsti "
        "('he who has no doubt') marks the goal: the doubt-free recognition of identity.",
    ),
]

# ---------------------------------------------------------------------------
# 8.1-12 — Daharākāśa and Prajāpati-Indra dialogue (key passages)
# ---------------------------------------------------------------------------

CHANDOGYA_8 = [
    # --- 8.1: The City of Brahman (daharākāśa) ---
    (
        "8.1.1",
        "ब्रह्म पुरमिदं शरीरं ब्रह्म च वाव पुरं\nयो ब्रह्मपुरे वसति स क्षेत्रज्ञः ॥",
        "brahma puram idaṃ śarīraṃ brahma ca vāva puraṃ\nyo brahmapure vasati sa kṣetrajñaḥ ||",
        "This body is the city of Brahman, and within it dwells the city of Brahman. "
        "He who dwells in the city of Brahman is the knower of the field.",
        "brahma-pura",
        "city-of-brahman-entry",
        "dual-register",
        "sravana",
        "analytic_contemplative",
        "madhyama",
        "The brahmapura framing — the body is the city of Brahman, preparing the listener "
        "for the dahara teaching. The kṣetrajña (knower of the field) language connects to "
        "the ātman-as-witness teaching.",
    ),
    (
        "8.1.2",
        "अथ यदिदमस्मिन् ब्रह्मपुरे दहरं पुण्डरीकं वेश्म\nदहरोऽस्मिन्नन्तराकाशस्तस्मिन् यदन्तस्तदन्वेष्टव्यं\nतद्वाव विजिज्ञासितव्यमिति ॥ ८.१.२ ॥",
        "atha yad idam asmin brahmapure daharaṃ puṇḍarīkaṃ veśma\ndaharo 'smin antarākāśas tasmin yad antas tad anveṣṭavyaṃ\ntad vāva vijijñāsitavyam iti ||",
        "Now, within this city of Brahman there is a small lotus, a dwelling place. "
        "Within it is a small space. What is inside that is to be sought, "
        "that is indeed to be known.",
        "dahara-vidya",
        "dahara-akasha-pointing",
        "paramarathika",
        "manana",
        "analytic_inquiry",
        "uttama",
        "The opening of the daharākāśa (small-space) teaching. The 'small lotus' is the "
        "hṛdaya (heart). The small space within it is said to be Brahman. 'Small' (dahara) "
        "is itself part of the apophatic strategy — the infinite is pointed to through "
        "the intimate and interior.",
    ),
    (
        "8.1.3",
        "तं चेद् ब्रूयुः यदिदमस्मिन् ब्रह्मपुरे दहरं पुण्डरीकं वेश्म\nदहरोऽस्मिन्नन्तराकाशः किमेतत्र विद्यत इति\nस ब्रूयात् — यावान् वा अयमाकाशस्तावानेषोऽन्तर्हृदय आकाशः\nउभे अस्मिन्द्यावापृथिवी अन्तरेव समाहिते\nउभावग्निश्च वायुश्च सूर्याचन्द्रमसावुभौ\nविद्युन्नक्षत्राणि यच्चास्येहास्ति यच्च नास्ति\nसर्वं तदस्मिन् समाहितमिति ॥ ८.१.३ ॥",
        "taṃ ced brūyuḥ yad idam asmin brahmapure daharaṃ puṇḍarīkaṃ veśma\ndaharo 'smin antarākāśaḥ kim etat ra vidyata iti\nsa brūyāt — yāvān vā ayam ākāśas tāvān eṣo 'ntarhṛdaya ākāśaḥ\nubhe asmin dyāvāpṛthivī antareva samāhite\nubhāv agniś ca vāyuś ca sūryācandramasāv ubhau\nvidyun nakṣatrāṇi yac cāsyehāsti yac ca nāsti\nsarvaṃ tad asmin samāhitam iti ||",
        "If they were to say to him: 'In this city of Brahman there is a small lotus, "
        "a dwelling, and within it a small space — what is there within it to be found?' "
        "He should say: 'As large as this space (of the universe) is, so large is this "
        "space within the heart. Within it both heaven and earth are contained, "
        "both fire and wind, both sun and moon, lightning and the stars — "
        "what is here and what is not here — all that is gathered within it.'",
        "dahara-vidya",
        "infinite-in-the-intimate",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The paradox of the dahara teaching: the small space in the heart (antarākāśa) "
        "contains the entire universe. This is the non-dual teaching in spatial form — "
        "the ātman (as Brahman) is not 'somewhere small' but is the ground of all space.",
    ),
    (
        "8.1.5",
        "सर्वे च कामाः सर्वे च गन्धाः सर्वे च रसाः सर्वमिदमभ्यात्तो\n'वाक्यनादर एष म आत्मान्तर्हृदय एतद् ब्रह्म एतमितः प्रेत्याभिसंभवितास्मि ॥ ८.१.५ ॥",
        "sarve ca kāmāḥ sarve ca gandhāḥ sarve ca rasāḥ sarvam idam abhyātto\n'vākyam ānadaraḥ eṣa ma ātmān tarhṛdaya etad brahma\netam itaḥ pretya abhisambhavitāsmi ||",
        "All desires, all smells, all tastes — he pervades all this, without speech, "
        "without concern. This is my Self within the heart; this is Brahman. "
        "When I depart from here I shall merge into him.",
        "atman-as-brahman",
        "mahavakya-reiteration",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The declaration of identity restated within the dahara context — "
        "eṣa ma ātmāntarhṛdaye etad brahma. The same formula as 3.14.4, "
        "linking both sections as a pedagogical doublet.",
    ),
    (
        "8.3.2",
        "तद् ब्रह्म तद् अमृतम् तद् ब्रह्म सर्वाः प्रजाः\nब्रह्माण्यन्तर्भवन्ति ब्रह्माणि चोत्क्रामन्ति ॥ ८.३.२ ॥",
        "tad brahma tad amṛtam tad brahma sarvāḥ prajāḥ\nbrahmāṇy antarbhavanti brahmāṇi cotkrāmanti ||",
        "That is Brahman, that is the immortal. In Brahman all beings are born, "
        "and into Brahman they depart.",
        "brahman-as-ground",
        "immortality-pointing",
        "paramarathika",
        "manana",
        "analytic_inquiry",
        "uttama",
        "The bridge passage within chapter 8 connecting the daharākāśa to the Prajāpati "
        "dialogue. Brahman is the immortal ground from which all emerge and to which all return.",
    ),
    # --- 8.7: Prajāpati's declaration; Indra and Virocana come ---
    (
        "8.7.1",
        "य आत्मा अपहतपाप्मा विजरो विमृत्युर् विशोको\nविजिघत्सोऽपिपासः सत्यकामः सत्यसङ्कल्पः\nसोऽन्वेष्टव्यः स विजिज्ञासितव्यः ॥ ८.७.१ ॥",
        "ya ātmā apahatapāpmā vijaro vimṛtyur viśoko\nvijighatsaḥ apipāsaḥ satyakāmaḥ satyasaṃkalpaḥ\nso 'nveṣṭavyaḥ sa vijijñāsitavyaḥ ||",
        "The Self that is free from evil, free from old age, free from death, free from grief, "
        "free from hunger and thirst — whose desire is truth, whose will is truth — "
        "that is to be sought, that is to be known.",
        "atman-definition",
        "inquiry-arousal",
        "paramarathika",
        "sravana",
        "analytic_contemplative",
        "madhyama",
        "Prajāpati's opening proclamation that draws Indra and Virocana from the gods and "
        "demons respectively. The eight negations (apahatapāpmā etc.) define the ātman "
        "apophatically — what it is NOT — before any positive teaching is given.",
    ),
    (
        "8.7.4",
        "य एषोऽक्षिणि पुरुषो दृश्यत एष आत्मेति होवाच\nएतदमृतमभयमेतद् ब्रह्म ॥ ८.७.४ ॥",
        "ya eṣo 'kṣiṇi puruṣo dṛśyata eṣa ātmeti hovāca\netad amṛtam abhayam etad brahma ||",
        "The person seen in the eye — he is the Self, said Prajāpati. "
        "He is the immortal, the fearless; he is Brahman.",
        "prajapati-upadesa",
        "first-teaching-reflection",
        "dual-register",
        "sravana",
        "analytic_contemplative",
        "madhyama",
        "Prajāpati's first teaching: the ātman is the person seen in the eye (or in water). "
        "Virocana is satisfied and leaves — taking body-identification as the final answer. "
        "Indra is troubled and stays. This sets up the progressive dismantling.",
    ),
    (
        "8.8.4",
        "यद्येवमेतन्मन्यसे मनस्येवाहं तदा सुपर्णो\nभवाम्यो वा असो मन्यस एवं मन्यस्व ॥ ८.८.४ ॥",
        "yady evam etan manyase manasy evāham tadā suparṇo\nbhavāmy o vā aso manyase evaṃ manyasva ||",
        "If you think thus, then you may think: 'I am a beautiful being in a dream' — "
        "think of yourself thus.",
        "prajapati-upadesa",
        "second-teaching-dream",
        "dual-register",
        "manana",
        "analytic_inquiry",
        "uttama",
        "Prajāpati's second teaching: the ātman is the self in the dream state. "
        "Indra recognizes this as insufficient — in dream one can still be harmed. "
        "Each stage of the teaching strips away a grosser identification.",
    ),
    (
        "8.9.1",
        "स ह प्राजापत्यं पञ्चाशतं वर्षाणि ब्रह्मचर्यमुवास\nतस्मै होवाच प्रजापतिः ॥ ८.९.१ ॥",
        "sa ha prājāpatyaṃ pañcāśataṃ varṣāṇi brahmacaryam uvāsa\ntasmai hovāca prajāpatiḥ ||",
        "He lived as a student with Prajāpati for another fifty years. "
        "Then Prajāpati said to him:",
        "prajapati-upadesa",
        "progressive-dismantling",
        "dual-register",
        "sravana",
        "analytic_contemplative",
        "madhyama",
        "The repeated discipleship — Indra returns for 50 more years for the third teaching. "
        "The structure of the dialogue enacts the teaching: genuine inquiry requires repeated "
        "return, patience, and willingness to go beyond the first satisfying answer.",
    ),
    (
        "8.9.3",
        "मघवन् मर्त्यं वा इदं शरीरमात्तं मृत्युना\nतदस्यामृतस्याशरीरस्यात्मनोऽधिष्ठानमात्तो वै सशरीरः\nप्रियाप्रियाभ्यां न वै सशरीरस्य सतः\nप्रियाप्रियाभ्यामपहतिरस्ति ॥ ८.९.३ ॥",
        "maghavan martyan vā idaṃ śarīram āttaṃ mṛtyunā\ntad asyāmṛtasyāśarīrasyātmano 'dhiṣṭhānam\nātto vai saśarīraḥ priyāpriyābhyāṃ\nna vai saśarīrasya sataḥ priyāpriyābhyām apatir asti ||",
        "O Maghavan, this body is indeed mortal, seized by death. Yet it is the abode of "
        "that immortal, bodiless Self. One who is embodied is subject to pleasure and pain. "
        "There is no freedom from pleasure and pain for the embodied one.",
        "prajapati-upadesa",
        "body-limitation-pointing",
        "paramarathika",
        "manana",
        "analytic_inquiry",
        "uttama",
        "The pivot point: Prajāpati reveals why the body-based teaching is insufficient. "
        "The ātman is described as aśarīra (bodiless) and amṛta (immortal). "
        "The body is mortal (mṛtyu-seized); as long as the ātman is conflated with the body, "
        "bondage to pleasure/pain persists.",
    ),
    (
        "8.10.1",
        "स ह पुनरेव प्राजापत्यमेकशतं वर्षाणि ब्रह्मचर्यमुवास ।\nतस्मै होवाच प्रजापतिः ॥ ८.१०.१ ॥",
        "sa ha punar eva prājāpatyam ekaśataṃ varṣāṇi brahmacaryam uvāsa |\ntasmai hovāca prajāpatiḥ ||",
        "He again lived as a student with Prajāpati for yet another hundred years. "
        "Then Prajāpati said to him:",
        "prajapati-upadesa",
        "progressive-dismantling",
        "dual-register",
        "sravana",
        "analytic_contemplative",
        "madhyama",
        "Indra returns for a fourth time — 101 + 32 + 5 = 101 total years of study. "
        "The structure dramatizes uttama adhikāra: the qualified student does not settle "
        "for proximate answers but persists until the final teaching is given.",
    ),
    (
        "8.11.2",
        "य एवमेते ब्रह्मपुरे धाराः स्युः\nएवमेव ब्रह्मणि यानि चेमानि भूतानि जीवन्ति\nब्रह्मण्येव विलीयन्ते ॥ ८.११.२ ॥",
        "ya evam ete brahmapure dhārāḥ syuḥ\nevam eva brahmaṇi yāni cemāni bhūtāni jīvanti\nbrahmaṇy eva vilīyante ||",
        "Just as these streams in the city of Brahman — so all these beings, "
        "living in Brahman, dissolve back into Brahman alone.",
        "brahman-as-ground",
        "dissolution-pointing",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The return-to-source teaching within Prajāpati's final instruction. "
        "All beings arise from Brahman and dissolve back into Brahman — "
        "the tajjalān formula of 3.14.1 made explicit in narrative form.",
    ),
    (
        "8.11.3",
        "एवं वा अरेऽयमात्मा अजरामर ब्रह्मैव संविशति\nनैनं केन चन कर्मणा लिप्यते ॥ ८.११.३ ॥",
        "evam vā are 'yam ātmā ajarāmara brahmaiva saṃviśati\nnainaṃ kena cana karmaṇā lipyate ||",
        "In this way, this Self — undecaying, immortal — enters into Brahman itself. "
        "No action of any kind touches it.",
        "prajapati-upadesa",
        "atman-as-brahman",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The climactic teaching of the Prajāpati-Indra dialogue. The ātman is ajarā (undecaying) "
        "and amara (immortal) — it enters (is) Brahman itself. Karma cannot touch it. "
        "This passage directly addresses the sublation of the deep-sleep teaching: "
        "the ātman is not 'unconscious' in suṣupti but is pure consciousness beyond modification.",
    ),
    (
        "8.12.1",
        "अशरीरं वाव सन्तं न प्रियाप्रिये स्पृशतः ।\nअशरीरं वाव सन्तमाभिसम्पद्यते ॥ ८.१२.१ ॥",
        "aśarīraṃ vāva santaṃ na priyāpriye spṛśataḥ |\naśarīraṃ vāva santaṃ ābhisampadyate ||",
        "The bodiless one is not touched by pleasure or pain. "
        "The bodiless one is indeed attained.",
        "prajapati-upadesa",
        "final-liberation-pointing",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The resolution of the dialogue. Aśarīra (bodiless): the ātman is intrinsically "
        "beyond the body and thus untouched by pleasure/pain. Liberation is not something "
        "to be gained but the recognition of what one already is — the bodiless witnessing Self.",
    ),
    (
        "8.12.3",
        "सोऽहमत्र कृत्वा क्रतुः संस्कारात् संसारं मन्यामहे\nतस्माद् य एवमेतद् विद्याद् यावन्मात्रं हि तावत् संसारं मन्यते\nपरं तु ब्रह्म पश्यति ॥ ८.१२.३ ॥",
        "so 'ham atra kṛtvā kratuḥ saṃskārāt saṃsāraṃ manyāmahe\ntasmād ya evam etad vidyād yāvan mātraṃ hi tāvat saṃsāraṃ manyate\nparaṃ tu brahma paśyati ||",
        "Acting here with will shaped by latent impressions, we take ourselves to be "
        "in transmigration. Therefore, one who knows this thus — only to that extent does "
        "he take himself to be in transmigration; beyond that he sees Brahman.",
        "prajapati-upadesa",
        "liberation-through-knowledge",
        "paramarathika",
        "nididhyasana",
        "direct_insight",
        "uttama",
        "The final teaching: saṃsāra is a misidentification sustained by saṃskāras (latent impressions). "
        "Knowledge (vidyā) breaks this. The one who knows sees Brahman directly (paśyati) "
        "beyond the appearance of transmigration — jñāna as the sole means to liberation.",
    ),
]


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

def build_unit_block(ref, sanskrit, iast, translation,
                     prakriya, pedagogical_role, ontological_scope,
                     pedagogical_stage, cognitive_mode, adhikara_level, note):
    lines = []
    lines.append(f"## Text {ref}")
    lines.append("")
    if sanskrit:
        lines.append("**Sanskrit**")
        lines.append("")
        lines.append(sanskrit)
        lines.append("")
    lines.append("**Transliteration**")
    lines.append("")
    lines.append(iast)
    lines.append("")
    lines.append("**Translation**")
    lines.append("")
    lines.append(translation)
    lines.append("")
    lines.append("```yaml")
    lines.append(f"prakriya: '{prakriya}'")
    lines.append(f"pedagogical_role: '{pedagogical_role}'")
    lines.append(f"ontological_scope: '{ontological_scope}'")
    lines.append(f"pedagogical_stage: '{pedagogical_stage}'")
    lines.append(f"cognitive_mode: '{cognitive_mode}'")
    lines.append(f"adhikara_level: '{adhikara_level}'")
    safe_note = note.replace('"', '\\"')
    lines.append(f'note: "{safe_note}"')
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_file(title, section_title, chapter_ref, canonical_ref, primary_themes, units):
    parts = []
    parts.append(f"# Chāndogya Upaniṣad {title}")
    parts.append("")
    parts.append(f"## {section_title}")
    parts.append("")
    parts.append("---")
    parts.append("```yaml")
    parts.append(f"title: Chāndogya Upaniṣad — {title}")
    parts.append(f"section_title: {section_title}")
    parts.append("tradition: Sāmaveda")
    parts.append("text_type: Upaniṣad")
    parts.append(f"chapter: '{chapter_ref}'")
    parts.append("knowledge_tier: para_vidyā")
    parts.append("macro_function: identity_revelation")
    parts.append("teaching_method: direct_pointing")
    parts.append("dialogue_type: guru_student_dialogue")
    parts.append("primary_themes:")
    for t in primary_themes:
        parts.append(f"  - {t}")
    parts.append(f"canonical_reference: Chāndogya Upaniṣad {canonical_ref}")
    parts.append("```")
    parts.append("---")
    parts.append("")

    for u in units:
        parts.append(build_unit_block(*u))

    return "\n".join(parts)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # --- chandogya_3_14.md ---
    content_3_14 = build_file(
        title="Chapter 3.14",
        section_title="Sarvam Khalv Idam Brahma — The Teaching of Āruṇi",
        chapter_ref="3.14",
        canonical_ref="3.14.1–3.14.4",
        primary_themes=[
            "sarvam_khalv_idam_brahma",
            "atman_in_heart",
            "brahman_as_ground",
            "will_and_rebirth",
            "dahara_vidya",
        ],
        units=CHANDOGYA_3_14,
    )
    path_3_14 = os.path.join(OUT_DIR, "chandogya_3_14.md")
    with open(path_3_14, "w", encoding="utf-8") as f:
        f.write(content_3_14)
    print(f"Written: {path_3_14} ({len(CHANDOGYA_3_14)} units)")

    # --- chandogya_8.md ---
    content_8 = build_file(
        title="Chapter 8 (Key Passages)",
        section_title="Daharākāśa and Prajāpati-Indra Dialogue",
        chapter_ref="8",
        canonical_ref="8.1–8.12 (selected)",
        primary_themes=[
            "dahara_vidya",
            "atman_in_heart",
            "brahman_as_ground",
            "prajapati_upadesa",
            "progressive_dismantling_of_body_identification",
            "liberation_through_knowledge",
        ],
        units=CHANDOGYA_8,
    )
    path_8 = os.path.join(OUT_DIR, "chandogya_8.md")
    with open(path_8, "w", encoding="utf-8") as f:
        f.write(content_8)
    print(f"Written: {path_8} ({len(CHANDOGYA_8)} units)")


if __name__ == "__main__":
    main()
