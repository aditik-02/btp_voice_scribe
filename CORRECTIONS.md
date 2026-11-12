# Corrections to earlier documents

Facts in `research/` and `eda/` that were checked against the data or the source pages and turned out to be wrong or unsupported. The documents themselves are left unchanged as a record; use the values below.

| Where | Claim | Correct value | How checked |
|---|---|---|---|
| research: feasibility report / shortlist | Eka Medical ASR is single-speaker dictation | 2,206 single-term clips, 1,303 dictated sentences and 110 doctor–patient conversation clips (0.45 h) | full Eka metadata (`recording_context`) |
| research: shortlist | DISPLACE-M covers Kannada | Phase I is Hindi with English code-switching; no Kannada | DISPLACE-M challenge paper (arXiv 2603.02813) |
| research | the project plan's Doctor–Patient Indic Speech dataset (bala-ceg) was not catalogued | it holds one ~1-minute scripted conversation per language: usable only as a pipeline check | cloned the repository |
| research | model testing must wait for gated data | PriMock57, Eka and Svarah are open; the benchmark is built from them | — |
| eda: dataset inventory, recommendations | PriMock57 was recorded with lapel or directional microphones worn by doctor and patient | not stated in the dataset's README; check the PriMock57 paper before repeating it | PriMock57 README |
| eda: recommendations | Eka was spoken by 57 Indian clinicians | 56 identified speakers, plus 110 conversation clips with no speaker id | Eka `speaker` field |
| eda: recommendations | "1,766 drug clips" | correct as clips whose main label is `drugs`; there are 2,504 drug mentions in total across all clips. Say which one is meant | Eka `type_concept` and `medical_entities` |
| experiments: results summary | Amazon Transcribe Medical as a candidate | likely US English only; confirm before use | — |
| model list | Gemini 2.5 Pro / Flash | shut down in October 2026; use Gemini 3.5 Transcribe / 3.8 Flash | Google notice, Nov 2026 |
| model list | Sarvam Saarika | deprecated; current models are Saaras v4 (default) and v3 | Sarvam docs, Nov 2026 |
| benchmark EDA (first version) | British background-talker levels measured 0.3–0.8 dB louder than labelled | on target within 0.2 dB when measured the way the levels were set (over the background talker's own speech) | re-measured all 30 dev files |
| benchmark EDA (first version) | 19.6% of Eka dev clips have digits in a drug name | 33.2% (the first figure came from a loose text pattern; the corrected one uses the drug tags) | Eka `medical_entities` |
