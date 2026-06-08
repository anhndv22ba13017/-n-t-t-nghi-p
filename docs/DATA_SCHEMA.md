# Data Schema

Tai lieu nay mo ta format data de ban bo du lieu that vao sau.

## 1. Script input

File:

- `data/scripts/sample_script.txt`

Format:

- van ban thuong
- co the gom nhieu doan
- moi doan co the cach nhau bang dong trong

## 2. Image metadata

File:

- `data/images/metadata.json`

Format:

```json
[
  {
    "path": "data/images/example.jpg",
    "scene": "urban",
    "tone": "calm",
    "tags": ["city", "street", "morning"]
  }
]
```

Y nghia:

- `path`: duong dan toi anh
- `scene`: nhan boi canh
- `tone`: nhan cam xuc
- `tags`: tu khoa mo ta anh

Ngoai ra, project cung co the sinh tap tin index phu hop cho AI image retrieval:

- `data/images/faiss_index.bin`
- `data/images/image_paths.json`

`faiss_index.bin` la index vector chua embedding cua metadata anh.
`image_paths.json` luu danh sach duong dan anh ung voi index.

## 3. Analysis output

File:

- `data/outputs/analysis.json`

Format:

```json
[
  {
    "segment_id": 1,
    "keywords": ["voice", "image", "script"],
    "scene": "urban",
    "tone": "uplifting",
    "summary": "A quick summary of the narration segment.",
    "visuals": ["city street", "morning light"],
    "narration_style": "bright and optimistic",
    "actions": ["generate", "describe"],
    "context": "during a fast-paced city tour",
    "emotional_tone": "positive"
  }
]
```

Y nghia:

- `keywords`: tu khoa chinh cua doan
- `scene`: boi canh de chon anh
- `tone`: tam trang hoac kieu trinh bay
- `summary`: tom tat ngan
- `visuals`: y tuong hinh anh
- `narration_style`: phong cach doc
- `actions`: hanh dong hoat dong
- `context`: boi canh / noi dung dong thoi
- `emotional_tone`: cam xuc chinh

## 4. Audio output

File duoc tao trong:

- `data/outputs/audio/`

Manifest:

- `data/outputs/audio_manifest.json`

Format:

```json
[
  {
    "segment_id": 1,
    "audio_path": "data/outputs/audio/segment_01.wav",
    "duration_seconds": 4.8,
    "engine": "placeholder_tts",
    "status": "planned"
  }
]
```

## 4. Timeline output

File:

- `data/outputs/timeline_plan.json`

Format:

```json
[
  {
    "segment_id": 1,
    "start_seconds": 0.0,
    "end_seconds": 4.8,
    "duration_seconds": 4.8,
    "audio_path": "data/outputs/audio/segment_01.wav",
    "image_path": "data/images/example.jpg",
    "narration_text": "Sample text",
    "scene": "urban",
    "tone": "calm",
    "visual_reason": "scene:urban"
  }
]
```

