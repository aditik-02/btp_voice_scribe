# Medical Voice Scribe: Cross-Dataset Comparative Analysis

**Document ID**: `eda/reports/cross_dataset_comparison.md`  
**Datasets Analyzed**: PriMock57, Eka Medical ASR, Svarah, MS-SNSD  
**Figures**: `eda/figures/comparison/`  

---

## 1. Comprehensive Cross-Dataset Comparison Matrix

The table below provides a rigorous side-by-side comparison across the 12 evaluation parameters specified in the research protocol.

| Parameter | PriMock57 | Eka Medical ASR | Svarah | MS-SNSD |
| :--- | :--- | :--- | :--- | :--- |
| **1. Primary Purpose** | Primary care consultation dialogue & clinical note generation. | Medical speech recognition for Indian clinical terms & dictation. | Indian-accented English speech recognition evaluation. | Acoustic noise synthesis & speech enhancement benchmarking. |
| **2. Speech Type** | Continuous 2-party conversational dialogue (unscripted turns). | Isolated medical terms (61%) & scripted clinical sentences (36%). | Single-speaker read prompts and spontaneous monologues. | Environmental ambient noise (179 files) & clean audiobook speech. |
| **3. Medical Vocabulary** | General practice symptoms, common complaints, UK medications. | **Extensive Indian pharmaceutical brands, dosages, clinical entities.** | **Zero clinical terms** (general Indian history, geography, civics). | N/A (Non-speech acoustic noise / audiobook literature). |
| **4. Indian Accents** | **None** (Exclusively British English / UK RP). | **Authentic Indian clinicians** (accent phonology present; state unannotated). | **Extensive & systematic** (117 speakers across 19 native L1 languages). | N/A (Noise soundscapes / US English clean audio). |
| **5. Doctor-Patient Dialogue**| **Yes (100%)** — 57 complete consultations. | **Minimal (3%)** — 110 dialogue clips; 97% are single-speaker dictations. | **None (0%)** — Monologue utterances only. | **None (0%)** — Ambient noise / audiobooks. |
| **6. Speaker Labels & Roles** | **Physical channel separation**: Channel 1 = Doctor, Channel 2 = Patient. | Speaker IDs provided (57 clinicians); **no doctor vs patient roles**. | Speaker IDs, gender, age, state, and primary language annotated. | N/A |
| **7. Transcript Availability** | Time-aligned TextGrids (7,109 turns) + GP consultation notes. | Full ground-truth text + character-level entity boundary spans. | Full ground-truth English text for all 6,656 utterances. | Text available for clean speech only (not for noise). |
| **8. Audio Duration** | **17.27 hours** total (8.64 h Doctor + 8.63 h Patient; 57 visits). | **~8.47 hours** total (3,619 English clips + 320 Hindi clips). | **9.61 hours** total (6,656 test utterances). | **3.95 hours noise** (179 files) + 22.85 h clean audio. |
| **9. Sample Rates & Channels**| **16,000 Hz, 1-ch (Mono)**, 16-bit PCM. | **16,000 Hz, 1-ch (Mono)**, embedded byte buffers. | **16,000 Hz, 1-ch (Mono)**, embedded byte buffers. | **16,000 Hz, 1-ch (Mono)**, 16-bit PCM. |
| **10. Noise Characteristics** | Studio-quiet rooms (RMS noise floor: -72 dBFS); faint mic bleed. | Clean mobile/headset dictation with minimal background noise. | Standard clean room recordings with minor acoustic room reverberation. | **Controlled ambient noise**: Babble, HVAC, typing, traffic, doors. |
| **11. Main Project Use** | **Conversational structure, diarization, turn-taking, EHR note generation.** | **Medical entity extraction, Indian drug name WER, dosage ASR.** | **Indian English accent robustness across 19 regional mother tongues.** | **Controlled OPD acoustic corruption via calibrated SNR/SIR mixing.** |
| **12. Main Limitations** | Lacks Indian accents; clean acoustic conditions unrepresentative of OPDs. | Dominated by isolated terms; lacks doctor-patient conversational flow. | Lacks medical terminology; lacks conversational multi-speaker turns. | Lacks hospital-specific telemetry noise; clean speech is audiobooks. |

---

## 2. Comparative Audio Signal Metrics

From the programmatic measurements compiled in `eda/reports/audio_signal_summary.json`:

```
Metric                 PriMock57      Eka Medical       Svarah         MS-SNSD (Noise)
--------------------------------------------------------------------------------------
Total Audio Hours       17.27 h         8.47 h          9.61 h             3.95 h
Mean Duration          545.36 s         8.43 s          5.20 s            79.43 s
Median Duration        559.20 s         5.01 s          4.21 s            37.56 s
Min Duration           228.60 s         1.68 s          0.10 s            11.93 s
Max Duration           858.24 s        28.32 s         29.87 s           459.59 s
Mean RMS (dBFS)        -23.28 dB       -25.01 dB       -24.47 dB         -22.65 dB
Silence Percentage      72.94%          41.94%          23.05%            25.42%
Uniform Sample Rate     16 kHz          16 kHz          16 kHz            16 kHz
Uniform Channels         Mono            Mono            Mono              Mono
```

### 2.1 Acoustic Observations
1. **Duration Disparity**: PriMock57 recordings are orders of magnitude longer (mean 9.1 minutes) than Eka (8.4s) and Svarah (5.2s), reflecting continuous consultation encounters versus segmented utterance prompts.
2. **Silence Ratio Differences**:
   * PriMock57's high silence ratio (72.9%) reflects dual-channel isolation: one channel is idle while the other party speaks.
   * Eka's silence ratio (41.9%) reflects pause gaps between dictated medication names.
   * Svarah's silence ratio (23.1%) represents continuous read speech.
3. **Signal Calibration Consistency**: Mean RMS energy across all four datasets sits between **-22.6 dBFS and -25.0 dBFS**. This tight 2.4 dB range means speech and noise can be mixed realistically without requiring artificial level scaling.

---

## 3. Project Requirement Suitability Matrix

We mapped our four benchmark datasets against the 9 primary functional requirements of the Medical Voice Scribe project:

| Project Requirement | PriMock57 | Eka Medical | Svarah | MS-SNSD | Joint Testbed Strategy |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Accept WAV audio** | **Fully Met** | **Fully Met** (Decode) | **Fully Met** (Decode) | **Fully Met** | All audio is 16 kHz mono compatible. |
| **2. Accurate speech-to-text** | **Fully Met** (Conversational) | **Fully Met** (Dictation) | **Fully Met** (Utterance) | N/A | Evaluates baseline English ASR WER. |
| **3. Distinguish Doctor vs Patient** | **Fully Met** (Isolated channels) | **Unusable** | **Unusable** | N/A | PriMock57 is the sole ground truth for diarization & role assignment. |
| **4. Handle Indian English accents** | **Unusable** (British only) | **Partially Met** | **Fully Met** (19 L1s) | N/A | Svarah evaluates accent robustness; Eka evaluates accented medical terms. |
| **5. Medical terms, drugs, dosages** | **Partially Met** (General GP) | **Fully Met** (Indian Pharma) | **Unusable** (General) | N/A | Eka provides Indian drug brand names and dosage entity spans. |
| **6. Support Hindi & Kannada** | **Unusable** | **Partially Met** (320 Hindi clips) | **Partially Met** (L1 only) | N/A | Existing data lacks conversational Hindi/Kannada doctor visits. |
| **7. Handle background noise (OPD)** | **Unusable** (Clean studio) | **Unusable** (Clean mic) | **Unusable** (Clean mic) | **Fully Met** | MS-SNSD provides the acoustic noise source for simulated OPD noise. |
| **8. Avoid transcribing background speech** | **Partially Met** (Channel bleed) | **Unusable** | **Unusable** | **Fully Met** (Babble) | MS-SNSD Babble & NeighborSpeaking serve as distractor speech. |
| **9. Speaker-labelled transcript output**| **Fully Met** (TextGrids) | **Unusable** | **Unusable** | N/A | TextGrid intervals provide exact ground-truth speaker turns. |

---

## 4. Visualizations & Comparative Figures

1. **Duration Boxplot (Cross-Dataset)**: `eda/figures/comparison/cross_dataset_duration_comparison.png`  
   *Visually contrasts the long continuous consultation scale of PriMock57 with the short utterance scale of Svarah and Eka.*
2. **RMS Signal Energy Violins**: `eda/figures/comparison/cross_dataset_rms_comparison.png`  
   *Demonstrates the close acoustic energy alignment between clinical speech and environmental noise soundscapes.*
