# AI Video Assistant Prototype

Du an nay la bo khung cho de tai:

`script text -> phan tich noi dung -> tao narration -> tim anh -> xuat timeline cho DaVinci Resolve`

Muc tieu cua bo khung:

- tu dong phan tich noi dung script de lay scene, action, context, tone
- tu dong sinh voice narration bang TTS Qwen3/CosyVoice
- tu dong tim anh phu hop bang CLIP + FAISS neu du lieu metadata duoc cung cap
- xuat ke hoach timeline de nhap vao DaVinci Resolve
- co cau truc de viet bao cao va demo end-to-end

## 1. Kien truc tong quan

```text
script.txt
  -> preprocess
  -> analyze
  -> tts
  -> image retrieval
  -> timeline builder
  -> resolve export
```

## 2. Cau truc thu muc

```text
.
|-- config/
|   |-- project_config.json
|   |-- training_prep_config.json
|-- data/
|   |-- images/
|   |   |-- metadata.json
|   |-- outputs/
|   |-- reports/
|   |-- scripts/
|   |   |-- sample_script.txt
|   |-- training_workspace/
|-- docs/
|   |-- DATA_SCHEMA.md
|   |-- IMPLEMENTATION_GUIDE.md
|   |-- NEXT_STEPS.md
|   |-- REPORT_TEMPLATE.md
|   |-- TEST_CHECKLIST.md
|   |-- TRAINING_GUIDE.md
|-- src/
|   |-- __init__.py
|   |-- analyze.py
|   |-- build_timeline.py
|   |-- config.py
|   |-- models.py
|   |-- preprocess.py
|   |-- resolve_integration.py
|   |-- retrieve_images.py
|   |-- training_config.py
|   |-- training_prep.py
|   |-- tts_engine.py
|   |-- utils.py
|-- main.py
|-- prepare_training_data.py
|-- requirements.txt
```

## 3. Cach chay

Can cai Python 3.10+.

```bash
pip install -r requirements.txt
python main.py
```

Neu muon xay dung FAISS image index truoc khi chay pipeline:

```bash
python src/build_image_index.py
```

Neu co the chi dinh thu muc anh voi tu khoa `--image-dir`:

```bash
python src/build_image_index.py --image-dir data/images
```

Neu may chua co Python, cai Python truoc roi chay lai hai lenh tren.

Neu muon dung file cau hinh rieng:

```bash
python main.py --config config/project_config.json
```
Neu `analysis_mode` duoc dat la `external_llm`, pipeline se co gang goi nha cung cap LLM neu co the.
Hien tai repo ho tro OpenAI khi cài `openai` va dat `OPENAI_API_KEY` trong môi truong.
Neu muon dung Qwen remote, dat `QWEN_API_URL` va `QWEN_API_KEY`.
The config key `image_strategy` can be set to `metadata_keyword_match` for metadata-based retrieval or `auto`/`faiss` to enable FAISS + CLIP search when an index is available.
De chuan bi dataset train:

```bash
python prepare_training_data.py
```

## 4.1 Dung Flickr8k lam image data

Neu ban muon su dung Flickr8k lam du lieu anh, lam theo cac buoc:

1. Download dataset tu Kaggle: `https://www.kaggle.com/datasets/adityajn105/flickr8k`
2. Giai nen va dat vao mot thu muc local, vi du:
   `data/images/flickr8k_raw/`
3. Chay script de tao metadata va copy anh:

```bash
python src/build_flickr8k_metadata.py --source-dir data/images/flickr8k_raw
```

4. Sau do co the chay pipeline chinh:

```bash
python main.py
```

Neu muon xoa bo 100 anh mau cu, thu muc `data/images/` da bi cap nhat de khong su dung sample anh nua.

## 4.2 Dung audio sinh tu Kaggle (khong gia lap)

Neu ban da tai `generated_audio.zip` tu Kaggle, giai nen vao mot thu muc local, vi du:

`data/external_audio/generated_audio/`

Thu muc nay can co:

- `segment_01.wav`
- `segment_02.wav`
- ...
- `manifest.json`

Sau do sua `config/project_config.json`:

```json
{
  "tts_engine_name": "kaggle_generated",
  "external_audio_manifest_path": "data/external_audio/generated_audio/manifest.json"
}
```

Khi chay `python main.py`, pipeline se uu tien doc `manifest.json`, copy audio that vao `data/outputs/audio/` va tao timeline dua tren audio do.

## 4. Dau ra

Sau khi chay, he thong se tao:

- `data/outputs/segments.json`
- `data/outputs/analysis.json`
- `data/outputs/audio_manifest.json`
- `data/outputs/image_matches.json`
- `data/outputs/timeline_plan.json`
- `data/outputs/resolve_import_plan.json`
- `data/outputs/resolve_import_template.py`
- `data/outputs/analysis_prompts.json`
- `data/reports/project_summary.json`

## 5. Trang thai hien tai

Day la prototype MVP de lam do an trong 2 thang:

- Co xu ly script
- Co phan tich tu khoa, boi canh, cam xuc o muc co ban
- Co mo phong TTS bang audio manifest
- Co tim anh dua tren metadata
- Co xuat timeline plan
- Co san cho tich hop DaVinci Resolve API

## 6. Cach nang cap tiep

### TTS that

Thay `src/tts_engine.py` bang mot trong cac huong:

- OpenAI TTS
- Qwen TTS
- Coqui TTS
- Model fine-tune rieng

### LLM analysis voi Qwen3

Repo hien co them cau hinh de ban chuan hoa buoc phan tich script neu muon dung Qwen3:

- `analysis_mode`: che do phan tich, hien tai van de `rule_based` de chay on dinh
- `analysis_provider`: nha cung cap prompt, vi du `qwen`
- `analysis_model`: ten model cu the, vi du `Qwen3-8B`

Sau khi chay `python main.py`, ngoai `analysis_prompts.json` he thong se tao them:

- `data/outputs/analysis_requests.json`

File nay chua san message + schema de ban dem sang notebook, API client, hoac server Qwen3 ma khong can tu viet lai prompt.

### Image retrieval that

Thay `src/retrieve_images.py` bang:

- CLIP embedding + FAISS
- ChromaDB
- Elasticsearch

### DaVinci Resolve that

Bo sung API trong `src/resolve_integration.py` de:

- import media vao media pool
- tao timeline moi
- chen audio va image theo thu tu

## 7. Huong lam do an

Thu tu nen lam:

1. Chay prototype nay de hieu pipeline.
2. Thay TTS gia lap bang TTS that.
3. Them bo anh va nang cap image retrieval.
4. Ket noi DaVinci Resolve that.
5. Danh gia ket qua va viet bao cao.

## 8. Cac file ban nen sua sau khi co data that

- `config/project_config.json`
- `data/scripts/sample_script.txt`
- `data/images/metadata.json`
- `src/tts_engine.py`
- `src/retrieve_images.py`
- `src/resolve_integration.py`

## 9. Tai lieu bo sung

- `docs/DATA_SCHEMA.md`: format data de bo du lieu that vao
- `docs/IMPLEMENTATION_GUIDE.md`: cach thay mock bang he thong that
- `docs/REPORT_TEMPLATE.md`: van phong bao cao de tai
- `docs/TEST_CHECKLIST.md`: checklist test demo
- `docs/TRAINING_GUIDE.md`: huong dan chuan bi va train dataset TTS
