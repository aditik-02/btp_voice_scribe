# Medical Voice Scribe: Data Quality & Critical Limitations Assessment

**Document ID**: `eda/reports/data_quality_report.md`  
**Role**: Senior Speech Data Scientist & Data Quality Auditor  
**Project**: Medical Voice Scribe for Indian Clinical Environments  
**Date**: November 2, 2026  

---

## 1. Executive Quality Audit

A data quality audit must prioritize empirical truth over optimism. This audit exposes the structural vulnerabilities, dataset imbalances, domain mismatches, and confounding variables present across the four benchmark datasets.

Every identified issue is documented with its observed frequency, practical impact on the Voice Scribe pipeline, and mandatory pre-benchmarking remediation protocol.

---

## 2. Itemized Quality Issues & Risk Matrix

### Issue 1: Dictation Dominance & Lack of Conversational Flow
* **Dataset**: `eka_medical_asr`
* **Observed Frequency**: **97.0% of all English clips** (61.0% single terms, 36.0% scripted sentences). Only 3.0% (110 clips) represent interactive dialogue.
* **Why It Matters**: Standard ASR models (e.g. Whisper) perform significantly better on isolated words and clear dictations than on natural conversational speech where speech rate varies, words are slurred, and interruptions occur. Benchmarking solely on Eka would yield unrealistically low Word Error Rates (WER) that collapse when deployed in live consultations.
* **Pre-Benchmarking Action**: **Mandatory Partitioning**. Split Eka evaluation into two distinct benchmark tracks:
  1. *Track A (Lexical & Drug Name Recall)*: Evaluated on `narration_entity` and `narration_sentence`.
  2. *Track B (Dialogue ASR)*: Restrict conversational benchmarking strictly to PriMock57 or Eka's 110 conversation clips.

---

### Issue 2: Geographic & Phonological Accent Mismatch
* **Dataset**: `primock57`
* **Observed Frequency**: **100% of the dataset** (All 57 consultations, 64 speakers).
* **Why It Matters**: PriMock57 is the only dataset providing multi-speaker conversational doctor-patient dialogue, but every speaker speaks with a British English accent. In Indian OPDs, doctors and patients speak Indian English characterized by retroflex stops ($/ʈ/, /ɖ/$), unaspirated voiceless plosives, distinct syllable-timed prosody, and regional phoneme substitutions.
* **Pre-Benchmarking Action**: **Do not report PriMock57 ASR WER as an indicator of Indian deployment accuracy.** Use PriMock57 strictly for evaluating:
  1. Speaker diarization error rate (DER).
  2. Speaker role attribution (Doctor vs. Patient classification).
  3. Clinical note summarization.
  Evaluate Indian English acoustic transcription accuracy separately on Svarah and Eka.

---

### Issue 3: Zero Clinical Terminology in Regional Accent Benchmark
* **Dataset**: `svarah`
* **Observed Frequency**: **100% of the dataset** (All 6,656 test records).
* **Why It Matters**: Svarah provides the essential Indian English regional accent diversity (covering 19 mother tongues including Kannada and Hindi), but its transcripts are entirely general English (geography, monuments, civic history). A search across all 69,593 words revealed zero Indian pharmaceutical brand names (0 mentions of Dolo, Paracetamol, Azithromycin, Metformin) and fewer than 10 mentions of basic medical words ('hospital': 10, 'medicine': 6, 'doctor': 3, 'patient': 1).
* **Pre-Benchmarking Action**: Svarah must be treated as an **acoustic robustness benchmark**, NOT a medical entity benchmark. Models must be evaluated on Svarah for general Word Error Rate (WER) and Character Error Rate (CER) across L1 accents, but entity extraction benchmarking must be confined to Eka.

---

### Issue 4: Speaker Concentration Imbalance
* **Dataset**: `eka_medical_asr`
* **Observed Frequency**: **39.6% of all English clips originate from just 3 speakers** (Top speaker: 15.4%, Top 2: 14.3%, Top 3: 9.9%). The top 4 speakers contribute **47.9%** of the entire dataset.
* **Why It Matters**: If an ASR model happens to overfit or adapt well to the vocal tracts and speaking rates of these 3 specific individuals, overall benchmark accuracy will appear artificially inflated.
* **Pre-Benchmarking Action**: Report **macro-averaged WER across speakers** alongside aggregate micro-averaged WER to ensure high accuracy is not skewed by the top 3 dominant speakers.

---

### Issue 5: Artificial Acoustic Cleanliness Across All Speech Datasets
* **Datasets**: `primock57`, `eka_medical_asr`, `svarah`
* **Observed Frequency**: **100% of speech recordings**.
* **Why It Matters**: All three speech datasets were recorded in quiet rooms with high-quality microphones (headsets, lapel mics, or close-range smartphones). None were recorded in the reverberant, chaotic acoustic environment of an Indian government or private hospital Outpatient Department (OPD), where ceiling fans, corridor chatter, door slams, and street traffic produce continuous noise (-15 to 0 dB SNR).
* **Pre-Benchmarking Action**: **Mandatory Acoustic Corruption via MS-SNSD**. Before evaluating models for deployment readiness, clean consultation audio must be synthetically augmented with controlled background noise (MS-SNSD Babble, HVAC, Typing) at calibrated SNR levels (15 dB, 10 dB, 5 dB).

---

### Issue 6: Language Inequity in Non-English Targets (Hindi & Kannada)
* **Datasets**: All four datasets
* **Observed Frequency**: **91.9% English overall**.
* **Specific Deficits**:
  * **Hindi**: Present only as 320 short dictation clips in Eka Medical ASR. Zero Hindi doctor-patient dialogues exist.
  * **Kannada**: **Zero Kannada language audio exists** in the current inventory. Svarah contains 577 clips spoken by native Kannada speakers, but they are speaking *English*, not Kannada.
* **Why It Matters**: Project Requirement 6 states: *"Eventually support Hindi, Kannada and code-switched speech."* The current data inventory cannot support or validate Kannada speech recognition or clinical code-switching (Hinglish / Kanglish).
* **Pre-Benchmarking Action**: Clearly document this limitation in project milestones. ASR benchmarking must be restricted to English, while recommending targeted collection of Hindi and Kannada clinical audio.

---

### Issue 7: Unnecessary Storage Footprint from Clean Audiobooks
* **Dataset**: `ms_snsd`
* **Observed Frequency**: **23,075 files (2.09 GB)** in `clean_train/`.
* **Why It Matters**: These files are public domain LibriSpeech audiobooks (narrated literature) provided by Microsoft solely as clean source audio for synthetic speech enhancement training. They have zero clinical relevance, consume 2+ GB of local disk space, and slow down filesystem indexing.
* **Pre-Benchmarking Action**: Exclude `clean_train/` from all Voice Scribe benchmarking pipelines. Keep only `noise_train/` (128 files, 361.5 MB) and `noise_test/` (51 files, 72.4 MB).

---

### Issue 8: Microphone Bleed in PriMock57 Dual Channels
* **Dataset**: `primock57`
* **Observed Frequency**: Present across **all 57 consultation pairs**.
* **Why It Matters**: In physical doctor-patient consultations, when the doctor speaks loudly, their voice travels across the examination desk and is captured at low amplitude by the patient's microphone (and vice versa). In PriMock57, acoustic room bleed on the idle channel averages -45 to -55 dBFS. If an energy-based Voice Activity Detector (VAD) has a threshold set too sensitively, it incorrectly classifies microphone bleed as active speech, leading to false overlap detection and transcript duplication.
* **Pre-Benchmarking Action**: Calibrate VAD energy thresholds using relative frame RMS (active speech threshold set at $\ge 0.05 \times \text{peak RMS}$) rather than static decibel cutoffs.

---

## 3. Summary of Data Hygiene Verification

| Verification Check | Target | Result | Status |
| :--- | :--- | :---: | :---: |
| **Corrupted Audio Headers** | 0 corrupted files | **0 detected** | **PASSED** |
| **Empty Audio Files (0 bytes)** | 0 empty files | **0 detected** | **PASSED** |
| **Missing Parquet Shards** | 0 missing shards | **0 detected** | **PASSED** |
| **Missing TextGrid Alignments** | 0 missing TextGrids | **0 detected** | **PASSED** |
| **Sample Rate Inconsistency** | 100% 16,000 Hz | **100% 16,000 Hz** | **PASSED** |
| **Channel Inconsistency** | 100% Mono | **100% Mono** | **PASSED** |
| **Parquet Null Values** | 0 null texts / audios | **0 detected** | **PASSED** |
