# BTP Voice Scribe: Dataset Downloads & Storage Ledger

## 1. Local Storage Policy & Hard Rules
1. **Zero Raw Audio in Git**: Per Hard Rule 6, no `.wav`, `.mp3`, `.flac`, `.opus`, archives, or raw audio datasets are stored in the git repository. All media files are blocked by `.gitignore`.
2. **External Storage Staging**: Audio datasets and evaluation splits are downloaded to an isolated external storage path (e.g. `/tmp/voice_scribe_eval_cache` or `~/.gemini/antigravity-cli/brain/b521fed2-8002-4db2-97cd-97ca13377766/scratch/`).
3. **Integrity Verification**: Every downloaded asset is verified against its published SHA-256 / MD5 checksum before being admitted to the benchmark pipeline.

---

## 2. Verified Download Log & Integrity Ledger

The following table records all audio assets physically downloaded, inspected, and checksummed outside the Git repository during our empirical feasibility audit:

| Dataset ID | Asset Name | Storage Location | Size (Bytes) | SHA-256 Checksum | Verified Audio Properties |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `primock57` | `day1_consultation01_doctor.wav` | `scratch/primock57/day1_consultation01_doctor.wav` | 14,653,484 | `a93ca69f49da821b2d10b03f3189fd0d82200a697805c18f316719ba328ff96b` | 457.92s, 16kHz, 1ch, RMS 0.0996, Peak 0.9788, Noise floor -92.8 dBFS |
| `primock57` | `day1_consultation01_patient.wav` | `scratch/primock57/day1_consultation01_patient.wav` | 14,651,564 | `12b0c5c12018cff8466bba78c930419fcda6dc0a53b5869d80d19f864190ba33` | 457.86s, 16kHz, 1ch, RMS 0.0815, Peak 0.9944, Bleed during doc speech -84.5 dBFS |
| `primock57` | `day1_consultation01_doctor.TextGrid` | `scratch/primock57/day1_consultation01_doctor.TextGrid` | 18,434 | `a727b4f53fd0c217469a4892c90c7667d40dd1e31d4e41416805178129759494` | Utterance intervals and text for doctor channel |
| `primock57` | `day1_consultation01_patient.TextGrid` | `scratch/primock57/day1_consultation01_patient.TextGrid` | 17,513 | `7082e1abf185b30a525fdf21ae43b9df0ee65013beaf9c9bb7630739c948e9d9` | Utterance intervals and text for patient channel |
| `medial_speech` | `DR1_16v_RoboDr Meeting - 16.wav` | `scratch/medial_speech/DR1_16v_RoboDr Meeting - 16.wav` | 19,265,614 | `51039713a4991addc2c2f689f76a6d66e746522c0032fcfb297ea07a3c316a7f` | 602.05s, 16kHz, 1ch, RMS 0.0681, Peak 0.9997, Inter-turn floor -53.1 dBFS |
| `medial_speech` | `output-16r-1700227158.1632931.wav` | `scratch/medial_speech/output-16r-1700227158.1632931.wav` | 15,920,044 | `419892c3b2c5e8cc871feea60fa64c2ec51d02f7481c5be04584e037707e7b68` | 497.50s, 16kHz, 1ch, RMS 0.0265, Peak 0.7791 |
| `eka_medical_asr` | `sample_0.wav` (Clinical Advice) | `scratch/eka_medical_asr/sample_0.wav` | 335,916 | `7b05b870518bbdb6a978ca51be1e7da9e17b8f041285dbaf86b16d1f97c41372` | 10.50s, 16kHz, 1ch, RMS 0.0268, Peak 0.3626, Single doctor dictation |
| `eka_medical_asr` | `sample_1.wav` (Azithromycin) | `scratch/eka_medical_asr/sample_1.wav` | 326,444 | `002e575a397c62d8ea2e88a38dbcb0baee8300eb2305aa314eb4ff12814b600d` | 10.20s, 16kHz, 1ch, RMS 0.0095, Peak 0.1057, Single doctor dictation |
| `eka_medical_asr` | `sample_2.wav` (Zincovit) | `scratch/eka_medical_asr/sample_2.wav` | 352,044 | `30c79853a603f329972cbbdf9908cf570ca73891461fbfd2547b7dd5351a44c9` | 11.00s, 16kHz, 1ch, RMS 0.0092, Peak 0.0941, Single doctor dictation |
| `synth_dopaco` | `dialog_0060_0120.opus` | `scratch/synth_dopaco/dialog_0060_0120.opus` | 731,108 | `021a0de2efb4dd631a0a52df271d4766fbf4ae1f173ce8dc215cb8289874a727` | 343.65s, 48kHz, 1ch, Kokoro-82M synthetic TTS, Foley sound events |
| `synth_dopaco` | `dialog_0060_0120.transcript.txt` | `scratch/synth_dopaco/dialog_0060_0120.transcript.txt` | 6,186 | `8abea3d54b06d9735d9703666b6c039fb2b0dae6a9f6d74102927236d62a420b` | Paired transcript text with Foley markup |
| `ami_corpus` | `EN2001a_sample_30s.wav` | `scratch/ami_corpus/EN2001a_sample_30s.wav` | 960,044 | `edb053ca9b2f06fca6e54881775f0a072483861c8eeaf33cba7339712792da85` | 30.00s, 16kHz, 1ch, RMS 0.0085, Peak 0.2521, Conference meeting table audio |

---

## 3. Storage Footprint Estimates for Full Corpus Ingestion

| Dataset ID | Target Split | Format | Est. Uncompressed Storage | Est. Compressed Download | Recommended Action |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `primock57` | Complete (57 visits) | WAV 16kHz 16-bit | 1.8 GB | 1.2 GB | **Full local clone** via `git lfs` |
| `medial_speech` | Complete (Part 1 + 2) | WAV 16kHz | 15.0 GB | 9.26 GB | **Full download** to external drive |
| `eka_medical_asr` | English Test (`en`) | Parquet (embedded WAV) | 1.81 GB | 1.54 GB | **Cache locally** via `datasets` |
| `synth_dopaco` | Dev split (400 visits) | Opus TAR shard | 0.5 GB | 0.47 GB | **Download dev shard**; stream train |
| `modulate_synthetic_dictation`| Quick subset (120 notes) | WAV 16kHz | 0.4 GB | 0.25 GB | **Download quick subset** |
| `ami_corpus` | Headset audio subset | WAV 16kHz | 12.0 GB | 8.5 GB | **Download core test set** (16 meetings) |
| `voxconverse` | Dev split audio | WAV 16kHz | 10.0 GB | 8.0 GB | **Download dev split** |
| `displace_2026` | Dev Track 1 & 2 | Zip (WAV 16kHz) | 4.5 GB | 3.2 GB | **Pending DUA decryption password** |

---

## 4. Failed Downloads, Blockers & Access Restrictions

| Dataset ID | Action Attempted | Result / Status | Official Remedy / Next Step |
| :--- | :--- | :--- | :--- |
| `displace_2026` | Extract `Track_1_SD_DevData_1.zip` | **Zip Password Encrypted** | Register at `https://forms.office.com/r/U5zLg8nihB` and sign Terms & Conditions with LEAP Lab, IISc Bangalore to receive password. |
| `whissleai_simulated_exams` | Download README / Parquet | **HTTP 401 Restricted** | Gated on Hugging Face; request organizational access via Hugging Face UI. |
| `physionet_egd_cxr` | Direct Wget of audio files | **Gated (Credentialed)** | Requires human research training (CITI certificate) and signed DUA on PhysioNet. |
| `dihard3_clinical` | LDC direct download | **Gated (LDC Membership)** | Requires university institutional membership or license purchase from LDC catalog (`LDC2022S12`). |
| `defined_ai_doctor_patient`| Commercial catalog access | **Commercial Purchase** | Requires commercial contract with Defined.ai enterprise sales ($10k+ quote). |
| `paultimothymooney_kaggle`| Direct Kaggle URL fetch | **HTTP 404 (Auth Needed)** | Resolved via verified open Hugging Face mirror (`Shamus/Medical_Speech_Transcription_and_Intent`). |
