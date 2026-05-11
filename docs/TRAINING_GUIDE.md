# Training Guide

Tai lieu nay huong dan chuan bi dataset va train TTS tren Kaggle GPU.

## 1. Muc tieu

Sau buoc nay, ban se co:

- dataset da duoc copy ra thu muc rieng
- manifest da duoc loc
- train manifest
- valid manifest
- report thong ke du lieu

## 2. Chuan bi local

Can file:

- `audio_pipeline_final.zip`

Lenh chay:

```bash
python prepare_training_data.py
```

Neu muon dung file config khac:

```bash
python prepare_training_data.py --config config/training_prep_config.json
```

## 3. Dau ra sau khi chuan bi

Thu muc:

- `data/training_workspace/training_dataset/audio/`
- `data/training_workspace/training_dataset/metadata/`
- `data/training_workspace/training_dataset/reports/`

File quan trong:

- `prepared_manifest.jsonl`
- `train_manifest.jsonl`
- `valid_manifest.jsonl`
- `rejected_manifest.jsonl`
- `training_prep_report.json`

## 4. Ban phai kiem tra gi truoc khi train

- transcript co sai nhieu khong
- cac sample bi reject co nen cuu lai khong
- valid split co du da dang khong
- audio co bi qua ngan hoac qua dai khong

## 5. Upload len Kaggle

Upload thu muc:

- `data/training_workspace/training_dataset/`

Hoac zip no lai roi upload nhu mot dataset.

## 6. Huong train an toan

Ban nen train theo cach:

1. chay thu mot notebook train ngan
2. train it step de kiem tra pipeline
3. test inference
4. moi train tiep lau hon

## 7. Sau khi train xong

Ban se can:

- checkpoint
- config model
- file tokenizer hoac vocab neu framework can

Sau do sua:

- `src/tts_engine.py`

de goi model da fine-tune.

## 8. Neu ban dung Qwen3 cho buoc phan tich script

Phan train TTS va phan phan tich script la hai viec khac nhau.
Neu ban dang fix Qwen3, hay nho:

- TTS fine-tune xong thi noi vao `src/tts_engine.py`
- Qwen3 dung cho phan tich script thi cau hinh o `config/project_config.json`

Ba khoa lien quan:

- `analysis_mode`
- `analysis_provider`
- `analysis_model`

Sau khi chay pipeline, kiem tra them file:

- `data/outputs/analysis_requests.json`

File nay giup ban dua cac segment sang Qwen3 de lay JSON phan tich co cau truc.
