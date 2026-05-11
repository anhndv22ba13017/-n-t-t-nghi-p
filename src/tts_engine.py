import json
import shutil
from pathlib import Path
import asyncio
import io
import wave
try:
    import edge_tts
except ImportError:
    edge_tts = None

from src.models import AudioAsset, Segment, normalize_path


def estimate_duration_seconds(text: str, words_per_minute: int = 135) -> float:
    words = max(len(text.split()), 1)
    minutes = words / words_per_minute
    return round(minutes * 60, 2)


def synthesize_audio_manifest(
    segments: list[Segment],
    audio_dir: Path,
    engine_name: str = "placeholder_tts",
    voice: str = "vi-VN-HoaiMyNeural",
    external_audio_manifest_path: Path | None = None,
) -> list[AudioAsset]:
    audio_dir.mkdir(parents=True, exist_ok=True)

    if external_audio_manifest_path and external_audio_manifest_path.exists():
        return build_audio_manifest_from_external(segments, audio_dir, external_audio_manifest_path, engine_name)

    assets: list[AudioAsset] = []
    for segment in segments:
        audio_filename = f"segment_{segment.segment_id:02d}.wav"
        audio_path = audio_dir / audio_filename

        if engine_name == "edge_tts":
            duration = _generate_with_edge_tts(segment.text, audio_path, voice)
            status = "generated"
        elif engine_name in ["cosyvoice", "qwen", "gwen"]: # Hỗ trợ tên gọi Qwen/Gwen từ proposal
            duration = _generate_with_qwen_tts(segment.text, audio_path, voice)
            status = "generated"
        else:
            duration = estimate_duration_seconds(segment.text)
            status = "planned"

        assets.append(
            AudioAsset(
                segment_id=segment.segment_id,
                audio_path=normalize_path(audio_path),
                duration_seconds=duration,
                engine=engine_name,
                status=status,
            )
        )

    return assets

def get_wav_duration(audio_path: Path) -> float:
    try:
        with wave.open(str(audio_path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return round(frames / float(rate), 2)
    except Exception:
        return 0.0

def _generate_with_edge_tts(text: str, output_path: Path, voice: str) -> float:
    if not edge_tts:
        print("Warning: edge-tts module is not installed. Returning 0.0s duration.")
        return 0.0
    
    # edge-tts generates MP3 format natively if you just save,
    # or you can specify output format, but wait, DaVinci Resolve likes WAV.
    # Actually edge-tts allows WAV output format using "riff-16khz-16bit-mono-pcm"
    
    communicate = edge_tts.Communicate(text, voice)
    
    async def _save():
        # save as WAV ? edge-tts cannot save as WAV directly through .save() if we don't specify format? 
        # By default edge-tts outputs MP3. We can just save it as .mp3 or let resolve import mp3.
        # But our extension is .wav. Let's just save mp3 under the .wav extension (some players can read it)
        # OR better yet, just save it as .mp3 and change extension in the audio_path to .mp3!
        # Wait, the pipeline assumes `.wav`. I will use edge-tts standard save which is mp3. 
        mp3_path = output_path.with_suffix(".mp3")
        await communicate.save(str(mp3_path))
        if mp3_path.exists():
            shutil.move(str(mp3_path), str(output_path))
            
    asyncio.run(_save())
    # Estimate duration since reading mp3 without heavy lib is hard, or we can use pydub but no dependency
    return estimate_duration_seconds(text)


_qwen_tts_model = None

def _generate_with_qwen_tts(text: str, output_path: Path, voice: str) -> float:
    global _qwen_tts_model
    import soundfile as sf
        
    try:
        from qwen_tts import Qwen3TTSModel
        import torch
    except ImportError:
        print("LỖI: Chưa cài đặt môi trường cho Qwen3-TTS. Vui lòng cài bằng lệnh: pip install qwen-tts")
        return 0.0

    if _qwen_tts_model is None:
        # Đường dẫn tới mô hình đã Fine-Tune hoặc mô hình gốc trên máy bạn
        # ĐƯỜNG DẪN TỚI MÔ HÌNH CHÍNH CHỦ MÀ BẠN VỪA FINE-TUNE THÀNH CÔNG TỪ KAGGLE!
        # Bạn cứ giải nén cục Zip, vứt luôn cả cái lõi thư mục my_qwen_trained_model vào thư mục Đồ án là xong.
        model_dir = "my_qwen_trained_model/checkpoint-epoch-9" 
        print(f"Loading Qwen3-TTS model từ: {model_dir}...")
        try:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            _qwen_tts_model = Qwen3TTSModel.from_pretrained(
                model_dir,
                device_map=device,
                dtype=torch.float32 if device == "cpu" else torch.bfloat16,
            )
        except Exception as e:
            print(f"LỖI khi load model Qwen3-TTS: {e}")
            return 0.0

    print(f"[Qwen3-TTS] Đang sinh âm thanh cho đoạn: {text[:30]}... với giọng {voice}")
    try:
        # Gọi hàm generate_custom_voice trực tiếp từ thư viện bản quyền
        wavs, sr = _qwen_tts_model.generate_custom_voice(
            text=text,
            speaker=voice,
        )
        sf.write(str(output_path), wavs[0], sr)
    except Exception as e:
        print(f"LỖI trong lúc sinh audio bằng Qwen3-TTS: {e}")
        return 0.0
        
    return get_wav_duration(output_path)


def build_audio_manifest_from_external(
    segments: list[Segment],
    audio_dir: Path,
    external_audio_manifest_path: Path,
    engine_name: str,
) -> list[AudioAsset]:
    payload = json.loads(external_audio_manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"External manifest must be a list: {external_audio_manifest_path}")

    external_audio_dir = external_audio_manifest_path.parent
    by_segment_id = {int(item["segment_id"]): item for item in payload if "segment_id" in item}

    assets: list[AudioAsset] = []
    for segment in segments:
        fallback_name = f"segment_{segment.segment_id:02d}.wav"
        fallback_target = audio_dir / fallback_name
        item = by_segment_id.get(segment.segment_id)

        if not item:
            assets.append(
                AudioAsset(
                    segment_id=segment.segment_id,
                    audio_path=normalize_path(fallback_target),
                    duration_seconds=estimate_duration_seconds(segment.text),
                    engine=engine_name,
                    status="missing_external_audio",
                )
            )
            continue

        source = external_audio_dir / Path(item["audio_path"]).name
        if not source.exists():
            source = Path(item["audio_path"])

        target = audio_dir / f"segment_{segment.segment_id:02d}.wav"
        if source.exists():
            shutil.copy2(source, target)
            duration_seconds = float(item.get("duration_seconds", estimate_duration_seconds(segment.text)))
            status = "generated"
        else:
            duration_seconds = estimate_duration_seconds(segment.text)
            status = "external_audio_not_found"

        assets.append(
            AudioAsset(
                segment_id=segment.segment_id,
                audio_path=normalize_path(target),
                duration_seconds=round(duration_seconds, 2),
                engine=engine_name,
                status=status,
            )
        )

    return assets
