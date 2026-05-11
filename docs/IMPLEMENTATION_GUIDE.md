# Implementation Guide

Tai lieu nay giai thich cach thay tung phan gia lap bang he thong that.

## 1. Text preprocessing

File lien quan:

- `src/preprocess.py`

Ban co the nang cap theo huong:

- tach cau tieng Viet tot hon
- gom cau thanh segment theo do dai toi uu
- them nhan cho tung segment: narrator, emphasis, transition

## 2. Script analysis

File lien quan:

- `src/analyze.py`
- `data/outputs/analysis_prompts.json`

Ban co hai cach:

1. Rule-based:
   - nhanh
   - de demo
2. LLM-based:
   - cho ket qua tu nhien hon
   - de mo rong scene, tone, visual idea

Neu ban muon dung Qwen3, repo da co san file `data/outputs/analysis_requests.json`.
Ban co the giu `analyze.py` o che do rule-based de co baseline on dinh, sau do gui cac request nay sang Qwen3 va merge ket qua tra ve.

## 3. TTS

File lien quan:

- `src/tts_engine.py`

Hien tai file nay chi tao manifest.

Khi thay bang TTS that, ban nen:

- tao file wav hoac mp3 that
- do do dai audio that
- gan `status="generated"`

## 4. Image retrieval

File lien quan:

- `src/retrieve_images.py`
- `data/images/metadata.json`

Ban co the bat dau bang metadata nhu hien tai, sau do nang cap:

- CLIP text-image embedding
- FAISS de tim anh top-k
- them confidence score

## 5. Timeline building

File lien quan:

- `src/build_timeline.py`

No da co san:

- start time
- end time
- duration
- image path
- audio path

Ban chi can thay audio duration gia lap bang duration that.

## 6. DaVinci Resolve

File lien quan:

- `src/resolve_integration.py`
- `data/outputs/resolve_import_plan.json`

Buoc tiep theo la dung plan nay de goi scripting API that.
