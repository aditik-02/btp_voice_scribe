# MS-SNSD: Acoustic Noise Profiling & OPD Simulation EDA

**Document ID**: `eda/reports/ms_snsd_eda.md`  
**Dataset**: Microsoft Scalable Noisy Speech Dataset (MS-SNSD)  
**Source**: Microsoft Research (`https://github.com/microsoft/MS-SNSD`)  
**Storage Path**: `voice_scribe_data/ms_snsd/`  
**Figures**: `eda/figures/ms_snsd/`  

---

## 1. Dataset Overview & Purpose

The Microsoft Scalable Noisy Speech Dataset (MS-SNSD) is a standardized corpus designed for speech enhancement and robust ASR under real-world acoustic degradation. In the context of our BTP project—**Medical Voice Scribe for Indian Clinical Environments**—its primary utility is providing high-fidelity environmental noise and acoustic distractors to simulate noisy outpatient departments (OPDs).

---

## 2. Component Separation: Clean Speech vs. Noise Soundscapes

A common error in speech dataset analysis is treating MS-SNSD as a monolithic noise collection. We inspected and categorized all 24,374 audio files across the repository:

| Sub-Corpus | Subdirectory | File Count | Total Size | Duration (Hours) | Purpose in Voice Scribe |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Noise Train** | `noise_train/` | **128** | 361.5 MB | **3.29 h** | Ambient noise source for synthetic clinical acoustic augmentation. |
| **Noise Test** | `noise_test/` | **51** | 72.4 MB | **0.66 h** | Unseen evaluation noise for held-out OPD robustness benchmarking. |
| **Clean Test** | `clean_test/` | **1,100** | 399.9 MB | **3.64 h** | Baseline clean speech (LibriSpeech test splits). |
| **Clean Train** | `clean_train/` | **23,075** | 2.09 GB | **~19.21 h** | Large-scale clean speech audiobooks (not used for clinical ASR). |
| **TOTAL** | — | **24,354** | **2.86 GB** | **~26.80 h** | Complete repository. |

---

## 3. Acoustic Profiling of Noise Categories

### 3.1 Mapping to Indian Outpatient Clinic (OPD) Conditions
We analyzed all 179 noise recordings across both splits. The dataset includes 28 distinct ambient acoustic classes, of which the following directly simulate hospital OPD acoustic environments:

| Noise Class | Files | Total Duration | Typical Frequency Band | Clinical Environment Analogy |
| :--- | :---: | :---: | :---: | :--- |
| **`Babble`** | 20 | 1,237.1s | 300 Hz – 3,500 Hz | Waiting room chatter, crowded clinic corridors, adjacent patient queues. |
| **`NeighborSpeaking`**| 14 | 1,115.8s | 200 Hz – 4,000 Hz | Secondary consultation in the same room (common in multi-bed OPDs). |
| **`AirConditioner`** | 20 | 850.8s | 50 Hz – 500 Hz (Low-freq hum) | Clinic HVAC systems, ventilation fans, ceiling fans. |
| **`Typing`** | 12 | 929.3s | 1,000 Hz – 6,000 Hz (Impulsive) | Doctor/receptionist typing EHR notes during patient consultation. |
| **`ShuttingDoor`** | 18 | 499.2s | Transient burst | Frequent consultation room door openings and closures. |
| **`CopyMachine`** | 11 | 880.3s | Low-to-mid continuous | Pharmacy/clinic printer and diagnostic equipment. |
| **`Traffic` & `Bus`**| 2 | 600.0s | 80 Hz – 1,200 Hz | Street noise entering through open OPD windows. |
| **`SqueakyChair`** | 11 | 331.8s | 2,000 Hz – 8,000 Hz (Harmonic) | Patient examination stool/chair movement. |

### 3.2 Signal Metrics for Noise Assets
* **Sample Rate**: 16,000 Hz (100% uniform across all files)
* **Channels**: 1 (Mono)
* **Duration**:
  * **Mean**: 79.43 seconds (Std: 90.93s)
  * **Median**: 37.56 seconds
  * **Min**: 11.93 seconds
  * **Max**: 459.59 seconds
* **Energy Levels**:
  * **Mean RMS**: -22.65 dBFS (Median: -22.32 dBFS, Std: 6.57 dB)
  * **Peak**: Approaching 0.98 in transient categories (e.g. `ShuttingDoor`), while continuous categories (e.g. `AirConditioner`) maintain steady RMS around -28 dBFS.

---

## 4. Technical Protocol: Controlled Clinical Acoustic Simulation

Per project guidelines, no audio preprocessing or mixing was performed during EDA. However, we evaluated MS-SNSD's built-in synthesis toolchain (`audiolib.py`, `noisyspeech_synthesizer.py`) and formulated the exact mathematical protocol for subsequent controlled noise benchmarking.

### 4.1 Signal-to-Noise Ratio (SNR) Formulation
To evaluate ASR robustness under varying OPD noise levels without destroying speech intelligibility, clinical consultation audio $s(t)$ and background noise $n(t)$ must be mixed at calibrated SNR levels:

$$\text{SNR}_{\text{dB}} = 10 \log_{10} \left( \frac{P_{\text{speech}}}{P_{\text{noise}}} \right)$$

where $P_{\text{speech}}$ is calculated strictly over **active speech frames** (excluding the 72.9% silent gaps in PriMock57) to avoid artificial amplification:

$$P_{\text{speech}} = \frac{1}{|T_{\text{active}}|} \sum_{t \in T_{\text{active}}} s^2(t)$$

### 4.2 Signal-to-Interference Ratio (SIR) for Competing Secondary Speech
In Indian OPDs, the primary failure mode of ASR scribes is transcribing a bystander or adjacent conversation rather than the doctor or patient (causing catastrophic insertion errors). By using MS-SNSD `Babble` or `NeighborSpeaking` as an interference signal $i(t)$, we can establish controlled SIR benchmarks:

$$y(t) = s(t) + \alpha \cdot i(t) + \beta \cdot n_{\text{ambient}}(t)$$

* **Target Evaluation Grid**:
  * **Clean Baseline**: $\infty$ dB SNR / $\infty$ dB SIR
  * **Moderate OPD Noise**: 15 dB SNR (Ceiling fan + distant corridor hum)
  * **Challenging OPD Noise**: 5 dB SNR (Loud HVAC + nearby keyboard typing)
  * **Severe Multi-Speaker Interference**: 10 dB SIR (Nearby nurse/family conversation)

---

## 5. Visualizations & Acoustic Evidence

1. **RMS Energy by Noise Category**: `eda/figures/ms_snsd/ms_snsd_noise_rms_by_category.png`  
   *Contrasts high-energy impulsive soundscapes (Babble, Neighbor, Cafe) with stationary low-frequency HVAC noise.*
2. **Clinical Distractor Spectrograms**: `eda/figures/ms_snsd/ms_snsd_distractor_spectrograms.png`  
   *4-panel spectrogram comparison of 5-second snapshots of Babble, AirConditioner, Typing, and NeighborSpeaking.*

---

## 6. Strengths & Limitations for Medical Voice Scribe

### 6.1 Project Strengths
1. **Diverse Acoustic Distractors**: Provides standard, validated recordings of office, babble, appliance, and HVAC noise that match clinical room physics.
2. **Sample-Rate Consistency**: 16 kHz mono format natively matches PriMock57 and Svarah, allowing zero-resampling simulation.
3. **Turnkey Mixing Engine**: The presence of `audiolib.py` and `noisyspeech_synthesizer.py` provides verified math for calibrated SNR scaling.

### 6.2 Critical Project Limitations
1. **Non-Clinical Noise Origins**: Noise was collected in standard commercial environments (cafes, offices, homes), not in active Indian government hospital OPDs.
2. **Missing Specific Medical Soundscapes**: Lacks authentic Indian hospital intercom announcements, diagnostic equipment telemetry (vital monitor beeps), and metal trolley rattles.
3. **Clean Audio Redundancy**: 2.09 GB of the dataset is clean audiobook narration (`clean_train`), which has no utility for clinical scribe benchmarking and should be excluded from future processing.
