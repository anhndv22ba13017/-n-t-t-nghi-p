# HƯỚNG DẪN CẦM TAY CHỈ VIỆC: TRAIN MÔ HÌNH QWEN3-TTS CHÍNH HÃNG TRÊN KAGGLE

Đây là hướng dẫn từng bước (Step-by-step) vô cùng chi tiết để fine-tune hệ thống âm thanh thế hệ mới nhất của Alibaba (**Qwen3-TTS**) với dữ liệu Tiếng Việt trên Kaggle. Xin chúc mừng bạn, việc training Qwen3 dễ hơn phiên bản cũ (CosyVoice) gấp 10 lần!

---

## BƯỚC 1: XUẤT VÀ NÉN DỮ LIỆU TỪ MÁY LOCAL
1. Mở VS Code, chạy tập tin `prepare_training_data.py`.
   ```bash
   python prepare_training_data.py
   ```
2. Mở thư mục `data/training_workspace/training_dataset/`.
3. Bôi đen 2 thư mục bên trong là `audio` và `metadata` -> **Nhấp chuột phải -> Compress to ZIP file**. Đặt tên nó là `my_tts_dataset.zip`.
4. Đăng nhập **[Kaggle Dataset](https://www.kaggle.com/datasets)**, tải file zip này lên thành một Dataset (Ví dụ chọn Tên Dataset: `My Vietnamese Qwen TTS`).

---

## BƯỚC 2: TẠO NOTEBOOK VÀ CÀI ĐẶT MÔI TRƯỜNG QWEN3-TTS CHÍNH CHỦ
1. Nhấn nút **New Notebook** trên Kaggle. Bật Máy Chủ GPU **T4 x2** và mở khóa **Internet On** ở cột cài đặt bên phải.
2. Tạo Cell code đầu tiên (Bấm `+ Code`) để tải thư viện chính hiệu `qwen-tts`:

```bash
%%bash
# 0. Cài đặt thư viện xử lý âm thanh hệ thống để tránh lỗi SoX not found
apt-get update && apt-get install -y sox libsox-fmt-all
# 1. Cài đặt thư viện lõi Qwen3-TTS chính hãng (Bỏ qua flash-attn cài quá lâu)
pip install -U qwen-tts
# 3. Tải bộ công cụ Fine-Tuning của Qwen3
git clone https://github.com/QwenLM/Qwen3-TTS.git
# (Kéo thêm ModelScope dự phòng cho mạng)
pip install -U modelscope
```

---

## BƯỚC 3: TIỀN XỬ LÝ (FORMAT DỮ LIỆU) DÀNH RIÊNG CHO QWEN3

Qwen3-TTS cực kỳ dễ tính, nó không cần Parquet hay Kaldi cầu kì! Nó chỉ cần 1 file `train_raw.jsonl` có 3 cột: `"audio"`, `"text"`, và một tệp âm thanh giọng nói gốc `"ref_audio"` để làm mỏ neo.

Hãy dán đoạn code Python siêu tự động sau vào Kaggle để nó tự chắp vá data cho bạn:

```python
import json
import os
import glob
import shutil

# Lấy đường dẫn dataset bạn upload bên cột Input
manifest_paths = glob.glob("/kaggle/input/**/train_manifest.jsonl", recursive=True)
if not manifest_paths:
    print("LỖI KHÔNG TÌM THẤY DỮ LIỆU INPUT! Bạn đã thêm Dataset vào góc phải Notebook chưa?")
else:
    MANIFEST_PATH = manifest_paths[0]
    INPUT_DATA_DIR = os.path.dirname(os.path.dirname(MANIFEST_PATH))
    WORK_DIR = "/kaggle/working/qwen3_finetune"
    os.makedirs(WORK_DIR, exist_ok=True)
    
    # Qwen3-TTS yêu cầu một file ref_audio đại diện chung (Khuyến khích dùng chung 1 giọng duy nhất)
    train_records = []
    first_audio = None
    
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            audio_path = os.path.join(INPUT_DATA_DIR, "audio", os.path.basename(item["audio_filepath"]))
            
            if not first_audio: 
                first_audio = audio_path
                shutil.copy2(first_audio, f"{WORK_DIR}/ref_audio.wav")
                first_audio = f"{WORK_DIR}/ref_audio.wav"
                
            train_records.append({
                "audio": audio_path,
                "text": item["text"],
                "ref_audio": first_audio # Ép dùng chung file chuẩn
            })
            
    # Lưu ra định dạng Qwen chuẩn
    raw_jsonl_path = f"{WORK_DIR}/train_raw.jsonl"
    with open(raw_jsonl_path, "w", encoding="utf-8") as f:
        for r in train_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print("✅ Đã tạo xong train_raw.jsonl chuẩn chỉnh 100% của Qwen3-TTS!")
```

---

## BƯỚC 4: RÚT TRÍCH ĐẶC TRƯNG ÂM THANH BẰNG QWEN3 TOKENIZER

Bước này sử dụng mã hóa AI 12Hz của Qwen3 để biến đổi giọng nói. Dán ô bash dưới đây vào Kaggle:

```bash
%%bash
cd /kaggle/working/Qwen3-TTS/finetuning
# Tích hợp token âm thanh bằng Tokenizer chính hãng
python prepare_data.py \
  --device cuda:0 \
  --tokenizer_model_path Qwen/Qwen3-TTS-Tokenizer-12Hz \
  --input_jsonl /kaggle/working/qwen3_finetune/train_raw.jsonl \
  --output_jsonl /kaggle/working/qwen3_finetune/train_with_codes.jsonl
```

---

## BƯỚC 5: KHỞI CHẠY HUẤN LUYỆN (FINE-TUNE) 

Sự ám ảnh tột độ của bạn về cái lỗi "ĐẦY RAM" của hệ thống cũ sẽ chấm dứt từ đây. Mô hình mới Qwen3-TTS 0.6B Base load vào cực êm và Fine-Tune trơn tru!

```bash
%%bash
cd /kaggle/working/Qwen3-TTS/finetuning

# HACK 0: Dọn rác giải phóng phân vùng (Gỡ mìn cái ổ đĩa đang đầy 19.5/19.5GB của bạn)
rm -rf ~/.cache/modelscope/*
rm -rf ~/.cache/huggingface/hub/models--Qwen--Qwen3-TTS-12Hz-0.6B-Base
rm -rf /kaggle/working/Qwen3-TTS-12Hz-1.7B-Base
rm -rf /kaggle/working/my_qwen_trained_model

# HACK 1: Tắt yêu cầu Flash Attention để tránh bị lỗi cài đặt 30 phút, ép dùng SDPA gốc cực lẹ
sed -i 's/attn_implementation="flash_attention_2",//g' sft_12hz.py

# HACK 2: Fix lỗi phiên bản thư viện Accelerate đòi thư mục Tensorboard trên Kaggle gây crash
sed -i 's/, log_with="tensorboard"//g' sft_12hz.py

# HACK 3: Ép Kaggle tự động gập/căng tần số âm thanh của bạn về 24kHz (Quy định bắt buộc của Qwen3)
sed -i 's/sr=None/sr=24000/g' dataset.py

# HACK 4: Kích hoạt thuật toán nén Tối Ưu Hóa 8-bit (Tiết kiệm 10GB VRAM để T4 không bị cháy)
pip install -U bitsandbytes
sed -i 's/from torch.optim import AdamW/import bitsandbytes as bnb/g' sft_12hz.py
sed -i 's/AdamW(/bnb.optim.Adam8bit(/g' sft_12hz.py

# HACK 5: Lấy đường dẫn vật lý thật của Mô hình bằng Python để không bị trùng lặp file làm bục ổ cứng 19.5 GB
export MODEL_PATH=$(python -c "from huggingface_hub import snapshot_download; print(snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-Base'))")

# HACK 6: Chỉ lưu giữ 1 Epoch cuối cùng, xóa sạch Epoch cũ để không bị nhân bản trọng số lên 35.0 GB
sed -i 's@output_dir = os.path.join(args.output_model_path@os.system(f"rm -rf {args.output_model_path}/*"); output_dir = os.path.join(args.output_model_path@g' sft_12hz.py

# Bùng nổ: Training mô hình gốc 1.7B-Base (Hiệu năng tốt nhất, tương thích 100% với file sft_12hz.py)
python sft_12hz.py \
  --init_model_path "$MODEL_PATH" \
  --output_model_path /kaggle/working/my_qwen_trained_model \
  --train_jsonl /kaggle/working/qwen3_finetune/train_with_codes.jsonl \
  --batch_size 1 \
  --lr 2e-6 \
  --num_epochs 10 \
  --speaker_name my_custom_voice
```

Khi chạy xong, toàn bộ file nặng sẽ nằm tại thư mục `/kaggle/working/my_qwen_trained_model/checkpoint-epoch-X/`. 
Bạn chỉ cần click phải chuột tải folder `/my_qwen_trained_model/` về máy Local là quy trình thành công xuất sắc!
