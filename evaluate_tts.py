import json
import os
import shutil
from pathlib import Path
from tqdm.auto import tqdm
import jiwer
import soundfile as sf
import torch

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Vui lòng cài đặt faster-whisper: pip install faster-whisper")
    exit(1)

# Cấu hình đường dẫn
TEST_MANIFEST = Path("data/training_workspace/training_dataset/metadata/test_manifest.jsonl")
OUTPUT_EVAL_DIR = Path("data/reports/evaluation")
OUTPUT_EVAL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR = Path("my_qwen_trained_model/checkpoint-epoch-9")

# 1. Khởi tạo Faster-Whisper ASR Model
print("[1] Loading Whisper ASR Model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
try:
    asr_model = WhisperModel("small", device=device, compute_type=compute_type)
except Exception as e:
    print(f"Error loading whisper: {e}")
    asr_model = None

# 2. Khởi tạo Qwen3-TTS Model
qwen_model = None
def load_qwen():
    global qwen_model
    if not MODEL_DIR.exists():
        print(f"Không tìm thấy thư mục mô hình Qwen3-TTS tại: {MODEL_DIR}")
        return False
    try:
        from qwen_tts import Qwen3TTSModel
        print(f"[2] Loading Qwen3-TTS Model from {MODEL_DIR}...")
        qwen_model = Qwen3TTSModel.from_pretrained(
            str(MODEL_DIR),
            device_map=device,
            dtype=torch.float32 if device == "cpu" else torch.bfloat16,
        )
        return True
    except ImportError:
        print("Vui lòng cài đặt qwen-tts: pip install qwen-tts")
        return False
    except Exception as e:
        print(f"Lỗi khi load Qwen3-TTS: {e}")
        return False

def transcribe_audio(audio_path):
    if asr_model is None: return "(asr error)"
    try:
        segments, _ = asr_model.transcribe(str(audio_path), language="vi", beam_size=5)
        text = " ".join([s.text for s in segments]).strip()
        return text
    except Exception as e:
        print(f"ASR Error on {audio_path}: {e}")
        return ""

def calculate_wer(reference_text, generated_text):
    # Làm sạch cơ bản văn bản tiếng Việt
    ref = reference_text.lower().replace(",", "").replace(".", "").replace("?", "").replace("!", "").strip()
    hyp = generated_text.lower().replace(",", "").replace(".", "").replace("?", "").replace("!", "").strip()
    try:
        if not ref: return 0.0
        return jiwer.wer(ref, hyp)
    except Exception:
        return 1.0

def main():
    print("="*50)
    print("   QWEN3-TTS WORD ERROR RATE (WER) EVALUATION")
    print("="*50)

    if not load_qwen():
        print("Dừng đánh giá do không load được mô hình TTS.")
        return

    if not TEST_MANIFEST.exists():
        print(f"File Test không tồn tại: {TEST_MANIFEST}")
        return

    lines = open(TEST_MANIFEST, "r", encoding="utf-8").read().splitlines()
    test_cases = [json.loads(x) for x in lines if x.strip()]
    
    results = []
    print(f"\n[3] Bắt đầu đánh giá trên {len(test_cases)} mẫu kiểm thử (Test cases)...")

    for idx, item in enumerate(tqdm(test_cases, desc="Evaluating")):
        text = item["text"]
        speaker = item.get("speaker", "spk0")
        
        qwen_audio_path = OUTPUT_EVAL_DIR / f"test_qwen_{idx:03d}.wav"
        
        # 1. Sinh âm thanh bằng mô hình đã train
        try:
            wavs, sr = qwen_model.generate_custom_voice(text=text, speaker=speaker)
            sf.write(str(qwen_audio_path), wavs[0], sr)
        except Exception as e:
            print(f"Lỗi khi sinh audio cho câu {idx}: {e}")
            continue
            
        # 2. Nghe và nhận diện âm thanh đầu ra
        whisper_qwen = transcribe_audio(qwen_audio_path)
        
        # 3. Tính điểm sai số WER
        wer_qwen = calculate_wer(text, whisper_qwen)
        
        results.append({
            "id": item.get("id", f"item_{idx}"),
            "original_text": text,
            "transcription": whisper_qwen,
            "wer": wer_qwen
        })
        
    print("\n" + "="*50)
    print("   KẾT QUẢ ĐÁNH GIÁ (RESULTS)")
    print("="*50)
    
    if results:
        avg_wer = sum(r["wer"] for r in results) / len(results)
        accuracy = max(100.0 - (avg_wer * 100), 0)
        
        print(f"Tổng số câu đã đánh giá: {len(results)}")
        print(f"Tỷ lệ lỗi từ vựng (Average WER): {avg_wer * 100:.2f}%")
        print(f"Độ nhận diện chính xác ước tính: {accuracy:.2f}%")
        print("=> WER càng thấp thì mô hình đọc càng chuẩn!")
        
        # Lưu báo cáo chi tiết
        report_path = OUTPUT_EVAL_DIR / "wer_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "model": str(MODEL_DIR),
                "total_cases": len(results),
                "average_wer": avg_wer,
                "accuracy_percent": accuracy,
                "details": results
            }, f, ensure_ascii=False, indent=2)
        print(f"\nBáo cáo chi tiết từng câu được lưu tại: {report_path}")
    else:
        print("Không có kết quả nào được sinh ra.")

if __name__ == "__main__":
    main()
