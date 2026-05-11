# Kế hoạch Đánh giá và Fine-tune TTS (Qwen CosyVoice vs Coqui-TTS)

## 1. Cập nhật chia tập Train/Test/Valid

Hiện tại hệ thống chỉ chia tập `train` và `valid`. Tôi sẽ mở rộng cấu hình để chia thêm tập `test` dành riêng cho việc đánh giá khách quan.

### Các file cần sửa:
1. **`src/training_config.py`**:
   - Thêm trường `test_ratio: float` và `test_manifest_name: str`.
2. **`config/training_prep_config.json`**:
   - Bổ sung cấu hình `"test_ratio": 0.1` (sử dụng 10% cho tập test).
3. **`src/training_prep.py`**:
   - Viết lại hàm `split_train_valid` thành `split_train_valid_test`.
   - Sinh ra file `test_manifest.jsonl`.
   - Cập nhật thống kê `training_prep_report.json`.

---

## 2. Tạo Pipeline Đánh Giá & Tính WER

Do quá trình xử lý âm thanh tốn nhiều tài nguyên, tôi sẽ thiết kế logic ưu tiên có thể **chạy tốt trên cả Local (nếu có GPU) và Kaggle**.

### File được tạo mới: `evaluate_tts.ipynb`
Script đánh giá này sẽ thực hiện các bước sau:
1. **Đọc dữ liệu test**: Tải file `test_manifest.jsonl` vừa sinh ra.
2. **Sinh Audio (Synthesis)**: Thiết lập cấu trúc (Interface) để bạn đẩy text cho hai model:
   - *Coqui-TTS* (mô hình bạn từng train).
   - *Qwen CosyVoice* (mô hình chuẩn bị train/call API).
3. **Word Error Rate (WER)**:
   - Dùng mô hình `faster-whisper` nghe cả 2 loại audio.
   - Dùng thư viện `jiwer` so sánh transcript Whisper sinh ra với bản text gốc.
   - Xuất ra bảng kết quả WER xem mô hình nào có lỗi thấp hơn (đọc rõ/chuẩn chữ hơn).

---

## 3. Hướng dẫn huấn luyện Qwen TTS (CosyVoice)
Việc Fine-tune mô hình cỡ như Qwen CosyVoice yêu cầu VRAM lớn (ví dụ RTX 3090, 4090, hoặc T4/P100 x2 trên Kaggle). Do đó, tôi sẽ tạo ra file hướng dẫn quá trình:

### File được tạo mới: `docs/QWEN_TTS_GUIDE.md`
- Hướng dẫn thiết lập môi trường CosyVoice (Alibaba/Qwen).
- Cách tải tập dataset bạn vưa chia ở trên (Train/Valid) lên Kaggle để huấn luyện với các thông số cấu hình.
- Xuất checkpoint ra để mang vào bước sinh audio cho mục 2.

> **Nếu bạn đã rõ kế hoạch này, tôi sẽ tiến hành ngay bây giờ nhé!**
