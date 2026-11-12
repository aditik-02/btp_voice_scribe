# Eka Medical ASR: Indian Clinical Vocabulary & Entity EDA

**Document ID**: `eda/reports/eka_medical_asr_eda.md`  
**Dataset**: Eka Medical ASR Evaluation Dataset  
**Source**: Eka Care AI Research (`https://huggingface.co/datasets/ekacare/eka-medical-asr-evaluation-dataset`)  
**Storage Path**: `voice_scribe_data/eka_medical_asr/`  
**Figures**: `eda/figures/eka_medical_asr/`  

---

## 1. Dataset Overview & Clinical Context

Eka Medical ASR is an evaluation benchmark developed specifically to test medical speech recognition in Indian healthcare contexts. Recorded by Indian clinicians and medical professionals, it contains medical terminology, pharmaceutical brand names, clinical dosages, and medical advice commonly encountered in Indian clinics.

---

## 2. Investigation of Verified Counts & the 3,619 Discrepancy

A primary task in our research protocol was to resolve the apparent contradiction between published benchmark figures (3,619 English clips) and the downloaded inventory (reportedly 3,019 English and 920 Hindi clips).

### 2.1 Empirical Shard Verification
We programmatically inspected the row headers of all 9 Apache Parquet shards:

| Shard Path | Language Split | Row Count | Shard Size (MB) |
| :--- | :---: | :---: | :---: |
| `en/test-00000.parquet` | English (`en`) | **500** | 21.97 MB |
| `en/test-00001.parquet` | English (`en`) | **500** | 13.50 MB |
| `en/test-00002.parquet` | English (`en`) | **500** | 13.69 MB |
| `en/test-00003.parquet` | English (`en`) | **500** | 13.40 MB |
| `en/test-00004.parquet` | English (`en`) | **500** | 30.57 MB |
| `en/test-00005.parquet` | English (`en`) | **500** | 57.41 MB |
| `en/test-00006.parquet` | English (`en`) | **500** | 60.18 MB |
| `en/test-00007.parquet` | English (`en`) | **119** | 15.09 MB |
| **English Subtotal** | **en** | **3,619** | **225.80 MB** |
| `hi/test-00000.parquet` | Hindi (`hi`) | **320** | 42.56 MB |
| **GRAND TOTAL** | **en + hi** | **3,939** | **268.37 MB** |

### 2.2 Finding & Resolution
* **The benchmark document's count of 3,619 English evaluation clips is 100% verified and mathematically exact.**
* The figure of "3,019 English and 920 Hindi clips" arose from an arithmetic transposition: $3,939 - 920 = 3,019$. In reality, the Hindi split contains 320 records, not 920.
* Zero records were lost or corrupted; all 3,619 English evaluation clips are present and verified in `voice_scribe_data/eka_medical_asr/en/`.

---

## 3. Dissecting Recording Contexts: Entity Dictation vs. Conversation

A critical danger in clinical ASR research is treating isolated term recordings as conversational speech. We investigated the `recording_context` field across all 3,619 English records:

| Recording Context | Clip Count | Percentage | Description |
| :--- | :---: | :---: | :--- |
| **`narration_entity`** | **2,206** | **61.0%** | Isolated dictation of a single drug name, diagnostic test, or clinical finding. |
| **`narration_sentence`** | **1,303** | **36.0%** | Dictated clinical sentence or prescription instruction. |
| **`conversation`** | **110** | **3.0%** | Multi-speaker dialogue interaction. |

### Key Research Insight
**Over 61% of this dataset consists of isolated individual medical words.** Only 3.0% represents natural doctor-patient conversation. Consequently, Eka Medical ASR must be utilized as a **lexical and entity recognition benchmark**, NOT as a doctor-patient conversational turn benchmark.

---

## 4. Clinical Concept & Entity Analysis

### 4.1 Concept Distribution (`type_concept`)
* **`drugs`**: **1,766 clips** (48.8%) — Branded and generic pharmaceutical formulations.
* **`clinical_findings`**: **962 clips** (26.6%) — Symptoms, signs, examination findings.
* **`misc_medical`**: **396 clips** (10.9%) — Clinical abbreviations, anatomical terms.
* **`diagnostics`**: **294 clips** (8.1%) — Laboratory tests, imaging modalities.
* **`advices`**: **201 clips** (5.6%) — Dietary and lifestyle recommendations.

### 4.2 Most Frequent Indian Drug Names & Entities
From programmatic parsing of the `medical_entities` annotation spans:
* **Top Medications**: `antibiotic` (78), `statins` (28), `penicillin` (23), `antifungals` (19), `anti-diabetic drugs` (18), `amlodipine` (16), `dolo 650` (15), `antihistamines` (13), `thyroxine` (12), `metformin` (12), `azithromycin` (11), `zincovit` (9), `augmentin` (8), `pantocid` (8).
* **Top Clinical Findings**: `fever` (44), `cough` (38), `headache` (29), `chest pain` (26), `hypertension` (24), `diabetes mellitus` (22), `vomiting` (18), `sore throat` (15).
* **Dosage Forms & Regimens**:
  * `tablet`: 1,002 occurrences
  * `mg`: 140 occurrences
  * `capsule`: 114 occurrences
  * `syrup`: 15 occurrences
  * `od` (once daily): 14 occurrences
  * `bd` (twice daily): 3 occurrences
  * `sos` (as needed): 4 occurrences

---

## 5. Audio Signal Characteristics

* **Sample Rate**: 16,000 Hz (100% uniform)
* **Audio Encoding**: Embedded compressed audio bytes (`bytes` column), decoded as 16 kHz mono float32.
* **Clip Duration**:
  * **Mean**: 8.43 seconds (Std: 6.08s)
  * **Median**: 5.01 seconds
  * **Min**: 1.68 seconds (single entity dictation)
  * **Max**: 28.32 seconds (extended clinical advice)
  * **Clips under 3.0 seconds**: 1,288 clips (35.6% of dataset)
* **Signal Levels**:
  * **Mean RMS Energy**: -25.01 dBFS (Median: -24.96 dBFS, Std: 4.66 dB)
  * **Silence Ratio**: **41.94%** (significantly lower than PriMock57 because clips are continuous dictations rather than two-party turn-taking).

---

## 6. Speaker Concentration & Diversity

Parsing the `speaker` metadata field across all 3,619 clips revealed **57 distinct speaker identifiers**:
* Top Speaker 1 (`anushree.rana@...`): 557 clips (**15.4%** of dataset)
* Top Speaker 2 (`rajshree.badami@...`): 518 clips (**14.3%** of dataset)
* Top Speaker 3 (`neha.ramesh@...`): 358 clips (**9.9%** of dataset)
* Top Speaker 4 (`sanjana.sn@...`): 299 clips (**8.3%** of dataset)
* **Speaker Concentration**: The top 4 speakers contribute **47.9% of all audio clips**.
* **Limitation**: While all speakers possess authentic Indian English phonology, demographic attributes (native regional state, first language) are not annotated.

---

## 7. Visualizations & Acoustic Evidence

The following figures illustrate Eka's acoustic and lexical properties:
1. **Duration by Context**: `eda/figures/eka_medical_asr/eka_duration_by_context.png`  
   *Contrasts short entity dictations (median 3.2s) with longer clinical sentences (median 12.1s).*
2. **RMS Energy Distribution**: `eda/figures/eka_medical_asr/eka_rms_energy_distribution.png`  
   *Displays consistent -25 dBFS clinician recording levels across all context categories.*
3. **Waveforms & Spectrograms**: `eda/figures/eka_medical_asr/eka_sample_waveforms_spectrograms.png`  
   *Provides visual comparison between an isolated drug name ("Zincovit", narration_entity) and a complete clinical sentence ("Tablet Dolo 650 mg to be taken twice daily after food").*

---

## 8. Strengths & Limitations for Medical Voice Scribe

### 8.1 Project Strengths
1. **Authentic Indian Medical Lexicon**: Captures Indian pharmaceutical brand names (Dolo 650, Pantocid, Zincovit) that are absent from Western medical benchmarks like PriMock57.
2. **Gold-Standard Entity Annotations**: Character-level offset spans for drug names, dosages, and clinical findings provide ground truth for extracting structured clinical EHR entities.
3. **Indian Clinician Accents**: Recorded by Indian doctors, providing phonetic training data for Indian medical pronunciation.

### 8.2 Critical Project Limitations
1. **Dictation Bias**: 97% of clips are monologue dictations (either single terms or scripted sentences); it cannot evaluate conversational diarization or turn-taking.
2. **Speaker Imbalance**: Heavy concentration on 4 primary speakers.
3. **Acoustic Cleanliness**: Recorded via mobile/headset dictation apps with low background noise.
