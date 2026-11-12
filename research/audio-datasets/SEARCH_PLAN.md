# BTP Voice Scribe: Advanced Audio Dataset Discovery Search Plan

## 1. Project Context & Pipeline Scope
The BTP Voice Scribe project targets an automated end-to-end clinical ambient scribe:
$$\text{Audio} \longrightarrow \text{Speech-to-Text (ASR)} \longrightarrow \text{Speaker Diarization} \longrightarrow \text{Doctor/Patient Attribution} \longrightarrow \text{Transcript} \longrightarrow \text{Clinical Note (SOAP)}$$

This search plan details the exhaustive, evidence-first discovery methodology used to locate, verify, catalog, and rank every downloadable audio dataset capable of evaluating or training any stage of this pipeline.

---

## 2. Evidence Rules & Verification Rigor
1. **Zero Hallucination / Zero Assumption**: No dataset name, sample count, license, duration, or annotation is accepted on memory or hearsay. Every single claim in the catalog must be validated directly from official repository pages, official APIs, raw manifests, or published peer-reviewed papers inspected during this session.
2. **Traceability**: Every datum must point to an explicit row in `research/audio-datasets/EVIDENCE_LEDGER.csv` with source URL, timestamp, retrieval method, and confidence score.
3. **Strict Modality Verification**: Transcripts without audio are tagged as `Text-only`. Speech without medical domain context is tagged as `General Speech`. Unlabeled multi-speaker audio is tagged as `Diarization-only` (lacking doctor/patient role labels).
4. **Legal & Ethical Compliance**: Strictly open, permissible, or credentialed official channels only. No scraping behind login gates, no bypassing DUAs, no unauthorized mirrors, and zero exposure of PHI or raw audio in the Git repository.

---

## 3. The 166-Keyword Universe (Categorized)

### Family 1: Clinical Conversation & Healthcare Dialogue (45 Terms)
1. `doctor-patient`
2. `physician-patient`
3. `clinician-patient`
4. `medical consultation`
5. `clinical conversation`
6. `outpatient visit`
7. `primary care consultation`
8. `telemedicine consultation`
9. `telehealth dialogue`
10. `triage call`
11. `nurse-patient interaction`
12. `patient interview`
13. `history taking`
14. `OSCE` (Objective Structured Clinical Examination)
15. `objective structured clinical examination`
16. `standardized patient`
17. `simulated patient`
18. `mock consultation`
19. `role-play medical consultation`
20. `ambient clinical intelligence`
21. `AI scribe`
22. `medical scribe`
23. `clinical documentation`
24. `doctor patient conversation audio`
25. `clinical encounter`
26. `doctor patient dialogue`
27. `anamnesis`
28. `general practice consultation`
29. `ambulatory care encounter`
30. `emergency department triage audio`
31. `hospital round recording`
32. `psychiatry intake interview`
33. `clinical intake session`
34. `clinical handover`
35. `medical discharge discussion`
36. `bedside consultation`
37. `multi-party clinical meeting`
38. `palliative care conversation`
39. `pediatric clinical consultation`
40. `patient counseling audio`
41. `consultation recording`
42. `medical roleplay audio`
43. `medical interview recording`
44. `consultation audio transcript`
45. `clinical conversational corpus`

### Family 2: Speech Tasks, ASR, Diarization & Audio Processing (45 Terms)
46. `medical ASR`
47. `clinical speech recognition`
48. `medical speech-to-text`
49. `medical dictation`
50. `radiology dictation`
51. `pathology audio dictation`
52. `speech-to-note`
53. `conversation-to-note`
54. `clinical note generation from audio`
55. `dialogue summarization with audio`
56. `clinical diarization`
57. `speaker diarization`
58. `speaker role attribution`
59. `who-spoke-when`
60. `doctor patient diarization`
61. `overlapping speech in medical dialogue`
62. `turn-taking in medical conversation`
63. `multi-speaker clinical audio`
64. `meeting corpus diarization`
65. `acoustic modeling clinical speech`
66. `spontaneous clinical speech`
67. `conversational ASR`
68. `clinical domain adaptation ASR`
69. `word error rate clinical audio`
70. `diarization error rate medical`
71. `far-field medical audio`
72. `ambient mic clinical recording`
73. `lapel microphone clinical speech`
74. `close-talking vs far-field speech`
75. `multi-channel audio consultation`
76. `medical phoneme recognition`
77. `clinical conversational benchmark`
78. `voice activity detection clinical`
79. `medical entity recognition from speech`
80. `clinical speech segmentation`
81. `medical terminology ASR benchmark`
82. `medical acronym speech recognition`
83. `clinical audio transcription`
84. `clinician voice recognition`
85. `patient voice identification`
86. `speaker verification clinical`
87. `medical audio corpus`
88. `clinical NLP audio pipeline`
89. `doctor dictation wav`
90. `clinical dialogue recording`

### Family 3: Languages, Dialects, Accents & Indian Context (40 Terms)
91. `Indian English`
92. `Hinglish`
93. `code-switching clinical speech`
94. `Hindi-English medical speech`
95. `Hindi medical consultation`
96. `Tamil clinical audio`
97. `Telugu medical speech`
98. `Bengali clinical consultation`
99. `Marathi doctor patient speech`
100. `Gujarati medical dialogue`
101. `Kannada clinical speech`
102. `Malayalam medical conversation`
103. `Punjabi clinical audio`
104. `accented English clinical speech`
105. `L2 English medical ASR`
106. `non-native English doctor patient`
107. `South Asian accented English ASR`
108. `multilingual clinical speech`
109. `Indic speech corpus`
110. `IndicVoices`
111. `Svarah`
112. `Vistaar`
113. `Kathbath`
114. `Shrutilipi`
115. `Lahaja`
116. `AI4Bharat speech`
117. `respire medical audio India`
118. `Indian hospital consultation audio`
119. `multilingual Indian medical dictation`
120. `code-mixed Hindi English doctor consultation`
121. `rural healthcare audio India`
122. `community health worker audio`
123. `ASHA worker audio interaction`
124. `ANM consultation audio`
125. `Tele-MANAS audio`
126. `eSanjeevani consultation audio`
127. `104 triage audio India`
128. `108 emergency call audio`
129. `regional Indian accent ASR`
130. `Indic medical voice scribe`

### Family 4: Repositories, Registries & Discovery Keywords (36 Terms)
131. `corpus`
132. `dataset`
133. `benchmark`
134. `release`
135. `supplementary material`
136. `"data availability"`
137. `Zenodo`
138. `figshare`
139. `OSF`
140. `Open Science Framework`
141. `Dataverse`
142. `Harvard Dataverse`
143. `Mendeley Data`
144. `Dryad`
145. `PhysioNet`
146. `OpenSLR`
147. `LDC` (Linguistic Data Consortium)
148. `ELRA` (European Language Resources Association)
149. `Kaggle`
150. `Hugging Face`
151. `Hugging Face Datasets`
152. `Academic Torrents`
153. `GitHub`
154. `Papers with Code`
155. `Interspeech challenge dataset`
156. `ICASSP speech benchmark`
157. `DIHARD diarization corpus`
158. `CHiME speech dataset`
159. `VoxSRC`
160. `VoxConverse`
161. `AMI meeting corpus`
162. `ICSI meeting corpus`
163. `LibriSpeech`
164. `Common Voice`
165. `re3data`
166. `OpenAIRE`

---

## 4. Query Matrix & Tooling Strategy

| Source Family | Target Platforms | Query Mechanism | Verification Script / Method |
| :--- | :--- | :--- | :--- |
| **Hugging Face Hub** | datasets & models | `HfApi().list_datasets()`, tags: `audio`, `automatic-speech-recognition`, `medical`, `healthcare` | `scripts/discover_hf.py` |
| **Zenodo** | zenodo.org | REST API `https://zenodo.org/api/records?q=...` | `scripts/discover_zenodo.py` |
| **Scientific Literature** | arXiv, PubMed, Nature, Springer, Interspeech, ACL | Web search, DOI lookup, Crossref / OpenAlex API | Direct URL fetch & citation extraction |
| **Audio Registries** | OpenSLR, LDC, ELRA, PhysioNet | Catalogue queries & direct URL inspection | Manual / programmatic scraping & HEAD verification |
| **Benchmark Repos** | Papers with Code, GitHub, Hugging Face models | Model card training corpora mining | `scripts/check_links.py` & card inspection |

---

## 5. Execution Protocol
1. Run programmatic discovery scripts (`discover_hf.py`, `discover_zenodo.py`).
2. Execute search engine queries across targeted domains.
3. Conduct backward/forward citation snowballing on high-relevance clinical speech literature.
4. Log every hit and candidate into `EVIDENCE_LEDGER.csv`.
5. Verify candidates against the 10-step protocol: URL accessibility, real audio presence, open licensing, doctor/patient role labels, diarization timestamps, split isolation, and storage footprints.
6. Assemble catalog and ranking reports.
