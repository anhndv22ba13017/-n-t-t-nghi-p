# Next Steps

Tai lieu nay giup ban di tiep tu bo khung hien tai den ban demo co the bao cao.

## 1. Muc tieu MVP

Can lam duoc 4 viec:

1. Doc script text.
2. Tao narration cho tung doan.
3. Chon anh phu hop cho tung doan.
4. Xuat timeline plan de dua vao DaVinci Resolve.

## 2. Lo trinh 8 tuan

### Tuan 1

- Cai Python.
- Chay `main.py`.
- Doc cac file trong `data/outputs`.
- Chinh sua `data/scripts/sample_script.txt` thanh script cua ban.

### Tuan 2

- Nang cap `src/preprocess.py`.
- Tach doan theo y nghia tot hon.
- Them metadata nhu do dai, scene hint, speaker note neu can.

### Tuan 3

- Ket noi TTS that trong `src/tts_engine.py`.
- Neu ban da co notebook audio cu, tai su dung logic xu ly audio tu notebook do.
- Doi `status="planned"` thanh `status="generated"` khi tao duoc file wav that.

### Tuan 4

- Them bo anh vao `data/images/`.
- Cap nhat `data/images/metadata.json`.
- Neu muon tot hon, thay retrieval rule-based bang CLIP + FAISS.

### Tuan 5

- Ghi script DaVinci Resolve that trong `src/resolve_integration.py`.
- Import image va audio vao media pool.
- Tao timeline.

### Tuan 6

- Kiem tra chat luong voice.
- Kiem tra anh co hop noi dung khong.
- Tinh toan lai thoi luong clip theo audio that.

### Tuan 7

- Thu nghiem voi 3 den 5 script khac nhau.
- Ghi lai ket qua de dua vao bao cao.
- Chup man hinh pipeline va timeline.

### Tuan 8

- Fix loi.
- Hoan thien slide.
- Viet bao cao.
- Quay video demo.

## 3. Cach noi voi notebook audio hien co

Ban dang co:

- `final_audio_pipeline_clean.ipynb`
- `my_audio_data.zip.zip`

Huong tan dung:

1. Doc notebook cu de tach phan tien xu ly audio va ASR.
2. Neu notebook tao duoc file wav hoac metadata, dua no vao `data/outputs/audio/`.
3. Sua `src/tts_engine.py` de:
   - tao file wav that, hoac
   - nap metadata audio co san tu notebook.

## 4. Cach nang cap module

### `src/preprocess.py`

Nang cap bang:

- `underthesea`
- `pyvi`
- `spacy`

### `src/analyze.py`

Nang cap bang:

- keyword extraction nang cao
- LLM prompt de tra ve `scene`, `tone`, `summary`
- Qwen3 de sinh phan tich co cau truc JSON

### `src/tts_engine.py`

Nang cap bang:

- OpenAI TTS
- Qwen TTS
- Coqui TTS

### `src/retrieve_images.py`

Nang cap bang:

- CLIP embedding
- FAISS
- ChromaDB

### `src/resolve_integration.py`

Nang cap bang:

- DaVinci Resolve Scripting API
- import media
- create timeline
- append clip

## 5. Dau ra can co de nop

Ban nen co cac thu sau:

- source code chia module
- mot script demo
- mot timeline demo
- mot video quay man hinh demo
- bao cao mo ta kien truc va quy trinh
