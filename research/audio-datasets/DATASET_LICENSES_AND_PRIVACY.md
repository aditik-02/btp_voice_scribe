# BTP Voice Scribe: Dataset Licenses, Legal Compliance & Privacy Analysis

## 1. Legal & Licensing Overview

The legal viability of speech and dialogue datasets for developing clinical artificial intelligence hinges on two interrelated regimes: intellectual property / copyright licensing, and patient privacy / data protection regulations.

### 1.1 License Taxonomy Across Catalog Corpora

| License Type | Permitted Uses | Commercial Rights | Redistribution | Datasets in Catalog |
| :--- | :--- | :---: | :---: | :--- |
| **MIT** | Unrestricted research & commercial | **Yes** | Permitted with notice | `eka_medical_asr` |
| **CC-BY-4.0** | Unrestricted research & commercial | **Yes** | Permitted with attribution | `primock57`, `synth_dopaco`, `modulate_synthetic_dictation`, `ami_corpus`, `voxconverse`, `svarah`, `indicvoices`, `librispeech`, `aci_bench` |
| **CC BY-SA 4.0** | Unrestricted research & commercial | **Yes** (ShareAlike) | Permitted under same license | `openslr_mucs2021` |
| **CC0 (Public Domain)** | Unrestricted | **Yes** | Unrestricted | `common_voice` |
| **CC-BY-NC-4.0** | Academic & non-commercial research | **No** | Permitted for non-commercial | `medial_speech` |
| **PhysioNet License 1.5.0** | Credentialed scientific research | **No** | Prohibited (DUA bound) | `physionet_egd_cxr`, `physionet_b2ai_voice` |
| **LDC User Agreement** | Academic member / licensed research | **No** | Prohibited (Strict DUA) | `dihard3_clinical` |
| **Commercial Enterprise** | Commercial deployment per contract | **Yes** (Per fee) | Restricted by contract | `defined_ai_doctor_patient` |

---

## 2. Regulatory Compliance & Patient Privacy

### 2.1 The Inherent Privacy Barrier in Clinical Audio
Unlike text transcripts, which can be de-identified by masking or replacing Protected Health Information (PHI) like names, dates, locations, and MRNs, **raw human voice recordings are inherently biometric identifiers**.

Under major global privacy frameworks:
1. **HIPAA (United States - 45 CFR § 164.514)**:
   - Voice recordings are classified as biometric identifiers (§ 164.514(b)(2)(i)(P)). An audio recording of a real patient cannot be de-identified via the standard Safe Harbor method simply by removing names; the acoustic waveform itself can theoretically identify the speaker.
   - Releasing real clinical audio publicly requires full patient waiver or rigorous institutional certification by an expert statistician (§ 164.514(b)(1)).
2. **GDPR (European Union - Regulation (EU) 2016/679)**:
   - Voice recordings that allow biometric identification constitute "special category personal data" under Article 9. Processing requires explicit, informed, revocable patient consent.
3. **Digital Personal Data Protection (DPDP) Act 2023 (India)**:
   - Audio recordings captured during outpatient or hospital visits constitute personal data. Ambient scribes in Indian clinics must operate under clear notice, explicit consent from both patient and clinician, purpose limitation, and mandatory erasure obligations once clinical notes are generated.

---

## 3. Ethics & Sourcing Analysis of Catalog Corpora

### 3.1 Simulated & Mock Consultations (Zero PHI Risk)
* **PriMock57**:
  - *Sourcing*: Conducted by 7 licensed Babylon Health clinicians and 57 employee volunteers acting as patients using synthetic clinical case cards (pre-scripted complaints, histories, symptoms).
  - *IRB / Ethics Statement*: Babylon Health clinical research committee approved the protocol. Written informed consent was obtained from all clinician and employee participants allowing open public release under CC-BY-4.0.
  - *PHI Exposure*: **Zero**. No real patient data or actual medical histories are present in the audio.
* **Synth-DoPaCo**:
  - *Sourcing*: Fully synthetic dialogues generated during the JSALT 2025 workshop (Johns Hopkins CLSP / Brno University of Technology) using large language models and speech synthesis (Kokoro-82M).
  - *PHI Exposure*: **Zero**. Clinically verified term banks used for random slot filling; no human vocal cords involved.
* **Modulate Synthetic Medical Dictation**:
  - *Sourcing*: Text synthesized from structured clinical term banks across 20 specialties, rendered via Apache 2.0 Kokoro-82M voices.
  - *PHI Exposure*: **Zero**. Completely synthetic.

### 3.2 Real Human Medical Recordings (With Ethical Protections)
* **Eka Medical ASR Evaluation Dataset**:
  - *Sourcing*: Recordings contributed by practicing clinicians and students from Indian medical colleges. Recordings consist of medical terminology, drug brand names, and simulated sentence reads.
  - *Consent*: Voluntary participant contribution for open-source AI benchmarking under MIT license.
  - *PHI Exposure*: **Zero**. No real patient encounters or patient records recorded.
* **MeDial-Speech (ICASSP 2026)**:
  - *Sourcing*: Controlled experimental environment with medical professionals, student participants, and virtual robot patient avatars across 4 defined health conditions.
  - *Ethics Approval*: Approved by Institutional Ethics Review Board (IRB); participant consent granted for open academic release under CC-BY-NC-4.0.
* **PhysioNet Eye Gaze Data for Chest X-rays (`egd-cxr`)**:
  - *Sourcing*: Five board-certified radiologists reading anonymized chest X-rays from MIMIC-CXR.
  - *Protections*: PhysioNet Credentialed Health Data License requires human subjects research training (CITI), strict prohibition against re-identification, and secure compute environment.

---

## 4. Policy Recommendations for Voice Scribe Deployment

1. **Benchmarking & Development Phase**:
   - Utilize open simulated corpora (**`primock57`**, **`medial_speech`**, **`synth_dopaco`**, **`eka_medical_asr`**). These provide total legal security with zero risk of HIPAA, GDPR, or DPDP violations.
2. **Production Pipeline Architecture**:
   - Audio must be processed in real-time in memory and never persisted unencrypted to disk.
   - Once the ASR transcript is generated and diarized, raw audio waveforms must be immediately purged from temporary buffers unless explicit long-term storage consent is granted by the patient and provider.
   - Model fine-tuning must be conducted using synthetic or fully consented speech data to prevent voiceprint leakage.
