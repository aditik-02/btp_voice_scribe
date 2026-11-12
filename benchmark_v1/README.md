# Voice Scribe — English benchmark set, v1.1 (built 2026-10-26)

Fixed test set for comparing speech-to-text models. Score every model on these manifests, with
`scripts/normalize.py` applied to BOTH reference and model output.

## What's in it

| Part | Files | Use |
|---|---|---|
| PriMock57 clean consultations | 57 × doctor+patient mixed into one track (`primock57/mixed/*.wav`), 8.6 h | Long-form consultation WER |
| PriMock57 utterances | 6,551 utterances on the separate doctor / patient tracks (start/end offsets, no cutting) | WER per role (doctor vs patient), short-form models |
| PriMock57 noisy variants | 399 files = 57 consultations × 7 conditions (`primock57/noisy/*.flac`) | Robustness and background-speech leakage |
| Clinician notes | `primock57/notes/*.json` | Later: note generation |
| **Eka Medical ASR (en)** | 3,619 clips, 8.4 h, 57 speaker groups (`eka_en/`) | Indian doctors; drug / dosage / finding accuracy via `medical_entities` |
| **Svarah** | 6,656 clips, 9.6 h, ~117 speakers from 19 states (`svarah/`) | Indian-English accent control (non-medical) |

Splits (dev for tuning, test for reporting):
| Dataset | dev | test | Split unit |
|---|---|---|---|
| PriMock57 | 11 consultations, 1.7 h | 46, 7.0 h | consultation (stratified by day) |
| Eka en | 735 clips, 1.6 h | 2,884 clips, 6.8 h | speaker (narration); session (conversation clips have no speaker id) |
| Svarah | 1,351 clips, 2.2 h | 5,305 clips, 7.4 h | speaker (demographic profile as proxy: no speaker id released) |
No speaker appears in both dev and test within Eka or Svarah.
All variants of a consultation stay in its split. Use dev for tuning settings/prompts; report test only.

## Noise conditions (ClinicalMix v1)
The reference is always the original consultation transcript only.

| Condition | Background talker (SIR) | Noise (SNR) |
|---|---|---|
| noise_snr20 / 10 / 5 | – | 20 / 10 / 5 dB |
| talker_sir10 / 5 / 0 | 10 / 5 / 0 dB | – |
| opd_sir5_snr10 | 5 dB | 10 dB |
| talker_in_sir10 / 5 / 0 | 10 / 5 / 0 dB, **Indian-accented** | – |

- **Background talker** = a *different* PriMock57 consultation from the same split, random start, looped (like the next desk in an OPD). Its ID is in `distractor_consultation`, so leakage can be measured as words from that consultation appearing in the output.
- **Indian background talker** (`talker_in_*`) = two Svarah speakers from the same split taking turns with short pauses, looped. Measured SIR within 0.1 dB of target.
- **Noise bed** = air-conditioner hum + ambient (babble / cafeteria / hallway / neighbour talking) + sparse events every 15–45 s (doors, typing, PA announcements, copier), from MS-SNSD (MIT licence). Dev uses MS-SNSD's train clips, test its test clips, so no noise clip is shared.
- Levels are measured against the target's annotated speech regions. Checked: noise conditions hit target exactly; talker conditions within 0.3 dB.
- All gains, offsets and noise clips per file are in the `mix_meta` column (fully reproducible).

## Reference transcripts (`primock57/references/<id>.json`)
`segments` (speaker, start, end, raw text with tags, flags), `reference` (time-ordered, tags removed), `reference_norm`.
Transcriber tags: `<UNSURE>` (words kept), `<UNIN/>` (unintelligible, removed). 15% of utterances contain an unsure span and 17% an unintelligible one — flagged per utterance so they can be excluded in a strict score.

## Eka Medical ASR — what it really contains
Checked against the full metadata (correcting what I said earlier from the preview rows): it is **mostly narration, not conversation**.
| recording_context | clips | hours |
|---|---|---|
| narration_entity (a single drug / finding / test name) | 2,206 | 2.4 |
| narration_sentence (a dictated clinical sentence) | 1,303 | 5.5 |
| conversation (doctor–patient snippets) | 110 | 0.45 |
Report WER separately per `recording_context`: single-entity clips are 1–4 words, so they behave like a keyword test, not like dialogue.
Eka's own published test-set results (whole English set, not our split): Whisper large-v3 15.7% WER, Gemini 2.5 Flash 14.8%, AWS Transcribe 18.3%, Eka's Parrotlet-a-en-5b 10.9%.
Speaker e-mail addresses in the source are replaced by `eka_spk_NN`.

## Normalisation v1 (`scripts/normalize.py`)
lowercase · strip punctuation · hyphen → space · drop fillers (um, uh, erm, hmm, mm…) · **numbers left as written** (to revisit before scoring Eka dosages).

## Known limitations
- British accents, clean remote-call audio: tests long-form + noise robustness, **not** Indian accents (Eka/Svarah will cover that).
- 7 clinicians across 57 consultations with no IDs released, so doctors repeat across dev/test (patients don't). Fine for comparing pretrained models; not for training.
- Svarah has no speaker ids; demographic profile is used as a proxy (115 profiles for 117 speakers).
- Eka references contain uppercase, digits and units as typed ("1000 Tablet", "3RD DAY"); number/unit handling must be settled before Eka WER is final.
- Synthetic mixing: no room reverberation yet.

## Build / rebuild
From the `voice_scribe_data` folder:
```
python -m pip install numpy soundfile pyarrow pandas
python benchmark_v1\scripts\run_all.py
```
It downloads the PriMock57 audio, builds everything into `benchmark_v1/data/`, skips steps already done, and checks the
result against `scripts/reference_md5.txt` (the build is deterministic: same seeds give byte-identical manifests and audio).
All manifest paths are relative to `benchmark_v1/data/`.

Sources: PriMock57 (github.com/babylonhealth/primock57), MS-SNSD noise (github.com/microsoft/MS-SNSD),
Eka (`hf download ekacare/eka-medical-asr-evaluation-dataset --repo-type dataset`), Svarah (`hf download ai4bharat/Svarah --repo-type dataset`).

## Licences
PriMock57: CC-BY-4.0 (Papadopoulos Korfiatis et al., ACL 2022). MS-SNSD: MIT (Reddy et al., 2019).
Eka Medical ASR: MIT (Eka Care, 2025). Svarah: CC-BY-4.0 (Javed et al., Interspeech 2023).
