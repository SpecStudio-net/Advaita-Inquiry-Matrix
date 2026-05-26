# AIM — Advaita Inquiry Matrix

## Project Overview

The **Advaita Inquiry Matrix (AIM)** is a structured knowledge system designed to model and reproduce the pedagogical logic of the Advaita Vedānta teaching tradition.

Rather than acting as a general-purpose chatbot, AIM is intended to function as a **pedagogical engine** that can diagnose misunderstanding, select appropriate teaching methods (*prakriyā-s*), and guide a student through the classical Advaita inquiry process.

The architecture separates **scriptural sources**, **pedagogical knowledge**, and **system logic** so that the teaching tradition itself becomes the primary teacher.

## Project Status

Basic development is complete. The project is currently in the **tuning stage** — verifying correct functionality according to Advaita scriptural pedagogy.

---

## Top-Level Architecture

```
AIM/
├── archive/
├── corpus/
├── pedagogy/
├── system/
├── teaching_engine/
└── tools/
```

Each directory serves a distinct purpose in the overall system.

---

## archive/

Contains deprecated specifications, experimental materials, or historical project artifacts that are no longer active components of the system. Examples include early specifications, retired design documents, and branding assets.

Nothing inside `archive/` should be referenced by the runtime system.

---

## corpus/

The **primary textual knowledge base** of the project. This folder contains source texts used by the AIM engine, organized by genre.

```
corpus/
├── upanishads/
├── prakaranas/
└── commentaries/
```

Included materials:

- Upaniṣads
- Prakaraṇa texts (Ātma-bodha, Upadeśa-sāhasrī)
- Traditional commentaries

Files in this directory contain **only textual material and structured tags** — never system logic.

---

## pedagogy/

This layer extracts and organizes the **teaching structure** present in Advaita scripture.

```
pedagogy/
├── advaita_framework/
├── corpus_index/
└── text_maps/
```

### advaita_framework/

Defines the general principles of Advaita pedagogy, including teaching methods (*prakriyā-s*), student cognition models, error patterns, recognition processes, and dialogue protocols. This folder describes **how Advaita teaching works**.

### corpus_index/

Cross-text indexes linking philosophical concepts to specific textual passages — pedagogical coverage maps, cross-Upaniṣadic teaching patterns, and concept indexes.

### text_maps/

Pedagogical analyses of individual texts or sections of texts, such as the Kaṭha Upaniṣad teaching graph, Chāndogya 6 teaching loop, and Taittirīya pedagogical map. These maps describe **how a specific scripture conducts the teaching process**.

---

## system/

Defines the **internal architecture of AIM**.

```
system/
├── architecture/
├── schemas/
├── state_machine/
├── dialogue_protocols/
└── ingestion/
```

This layer defines data schemas, system specifications, ingestion rules, cognitive state models, and dialogue protocols. The files here function as the **operating system of AIM**.

---

## teaching_engine/

Contains runtime teaching logic used to guide inquiry, including the prakriyā selection engine, dialogue strategy modules, and scripture routing logic.

The decision process follows this flow:

```
student input
→ error detection
→ student state
→ prakriyā selection
→ scripture reference
→ dialogue generation
```

---

## tools/

Developer utilities used to maintain and expand the system — ingestion templates, validation scripts, and corpus analysis tools. These assist development but are **not part of the runtime teaching engine**.

---

## Conceptual Model

The AIM architecture mirrors the traditional Advaita teaching structure:

| Traditional System | AIM Layer          |
|--------------------|--------------------|
| Śruti              | corpus             |
| Prakriyā           | pedagogy           |
| Guru reasoning     | teaching_engine    |
| Śiṣya cognition    | state_machine      |
| Teaching dialogue  | dialogue_protocols |

This separation allows the system to reproduce the **guru–śiṣya pedagogical process** in a structured way.

---

## Project Goal

The long-term aim of the project is to construct a system capable of:

1. Diagnosing conceptual error
2. Selecting the appropriate Advaita teaching method
3. Routing to relevant scriptural passages
4. Conducting structured philosophical dialogue

The ultimate objective is to model the **Advaita teaching tradition as an adaptive inquiry system**.
