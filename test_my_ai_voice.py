import torch
import soundfile as sf
import os
from src.tts_engine import get_qwen_tts_model

def get_voice():
    # Câu mà bạn muốn AI đọc thử
    test_text = "Xin chào, tôi là trợ lý ảo được bạn huấn luyện thành công trên Kaggle. Tôi đang sử dụng mô hình Qwen3 tỷ bảy tham số với giọng nói cực kỳ tự nhiên."
    
    print("--------------------------------------------------")
    print(f"[1] Đang tải siêu mô hình 3.5GB từ my_qwen_trained_model/checkpoint-epoch-9...")
    print("Vui lòng đợi một lát (Tải mô hình vào RAM sẽ mất khoảng 10-30 giây).")
    
    # Kích hoạt hàm gọi model TTS (Đã được cấu hình tự lấy checkpoint-epoch-9)
    try:
        model = get_qwen_tts_model()
    except Exception as e:
        print(f"\n[LỖI] Không thể nạp được mô hình. Lỗi chi tiết: {e}")
        return

    print("\n[2] Mô hình đã sẵn sàng! Đang tiến hành chuyển đổi văn bản thành giọng nói...")
    print(f"Văn bản: '{test_text}'")
    
    # Chạy Inference
    try:
        # Sử dụng API của Qwen3 để generate audio
        audio_data, seed = model.generate_custom_voice(text=test_text)
        
        # Lưu file
        output_file = "KIEM_TRA_GIONG_NOI.wav"
        sf.write(output_file, audio_data, 24000)
        
        print("\n[3] THÀNH CÔNG RỰC RỠ! 🎉🎉🎉")
        print(f"File âm thanh đã được lưu tại: {os.path.abspath(output_file)}")
        print("Bạn có thể ra ngoài màn hình Desktop, vào thư mục Đồ Án và mở file KIEM_TRA_GIONG_NOI.wav lên nghe thử nhé!")
    except Exception as e:
        print(f"\n[LỖI] Trong quá trình kết xuất giọng nói gặp lỗi: {e}")

if __name__ == "__main__":
    get_voice()
