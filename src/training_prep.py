import json
import random
import shutil
import zipfile
from pathlib import Path
from typing import Any
from collections import defaultdict

from src.training_config import TrainingPrepConfig
from src.utils import ensure_directories, write_json, write_jsonl


def extract_dataset_zip(zip_path: Path, target_dir: Path) -> None:
    ensure_directories([target_dir])
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(target_dir)


def load_manifest_from_extracted_dir(
    extracted_root_dir: Path,
    manifest_inside_zip: str,
) -> list[dict[str, Any]]:
    manifest_path = extracted_root_dir / Path(manifest_inside_zip)
    lines = manifest_path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def normalize_text(text: str) -> str:
    text = " ".join(text.split())
    replacements = {
        "  ": " ",
        " ,": ",",
        " .": ".",
        " !": "!",
        " ?": "?",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text.strip()


def is_likely_usable_text(text: str, min_text_length: int, require_vietnamese_text: bool) -> bool:
    if len(text.strip()) < min_text_length:
        return False

    if require_vietnamese_text:
        vietnamese_marks = (
            "\u0103\u00e2\u0111\u00ea\u00f4\u01a1\u01b0"
            "\u00e1\u00e0\u1ea3\u00e3\u1ea1\u1ea5\u1ea7\u1ea9\u1eab\u1ead"
            "\u1eaf\u1eb1\u1eb3\u1eb5\u1eb7\u00e9\u00e8\u1ebb\u1ebd\u1eb9"
            "\u1ebf\u1ec1\u1ec3\u1ec5\u1ec7\u00ed\u00ec\u1ec9\u0129\u1ecb"
            "\u00f3\u00f2\u1ecf\u00f5\u1ecd\u1ed1\u1ed3\u1ed5\u1ed7\u1ed9"
            "\u1edb\u1edd\u1edf\u1ee1\u1ee3\u00fa\u00f9\u1ee7\u0169\u1ee5"
            "\u1ee9\u1eeb\u1eed\u1eef\u1ef1\u00fd\u1ef3\u1ef7\u1ef9\u1ef5"
        )
        if not any(char in text.lower() for char in vietnamese_marks):
            return False

    return True


def build_relative_audio_path(raw_audio_path: str) -> str:
    marker = "/kaggle/working/audio_pipeline/"
    normalized = raw_audio_path.replace("\\", "/")
    if marker in normalized:
        return normalized.split(marker, 1)[1]
    return normalized.lstrip("/")


def copy_audio_files(
    entries: list[dict[str, Any]],
    extracted_root_dir: Path,
    working_dataset_dir: Path,
) -> list[dict[str, Any]]:
    prepared_entries: list[dict[str, Any]] = []

    for item in entries:
        relative_audio_path = build_relative_audio_path(item["audio_filepath"])
        source_path = extracted_root_dir / relative_audio_path
        if not source_path.exists():
            filename = Path(relative_audio_path).name
            matches = list(extracted_root_dir.rglob(filename))
            if not matches:
                raise FileNotFoundError(f"Could not locate audio file for manifest entry: {item['audio_filepath']}")
            source_path = matches[0]
        target_path = working_dataset_dir / "audio" / Path(relative_audio_path).name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

        prepared_entries.append(
            {
                "id": item["id"],
                "speaker": item.get("speaker", "spk0"),
                "speaker_id": item.get("speaker_id", 0),
                "audio_filepath": str(target_path.as_posix()),
                "duration": item["duration"],
                "sampling_rate": item.get("sampling_rate", 16000),
                "language": item.get("language", "vi"),
                "text": normalize_text(item["text"]),
                "source_audio": item.get("source_audio"),
                "start": item.get("start"),
                "end": item.get("end"),
            }
        )

    return prepared_entries


def filter_entries(
    entries: list[dict[str, Any]],
    config: TrainingPrepConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for item in entries:
        duration = float(item["duration"])
        text = item["text"]
        reasons: list[str] = []

        if duration < config.min_duration_seconds:
            reasons.append("duration_too_short")
        if duration > config.max_duration_seconds:
            reasons.append("duration_too_long")
        if not is_likely_usable_text(text, config.min_text_length, config.require_vietnamese_text):
            reasons.append("text_quality_low")

        if reasons:
            rejected.append({**item, "reject_reasons": reasons})
        else:
            kept.append(item)

    return kept, rejected


def split_train_valid_test(
    entries: list[dict[str, Any]],
    validation_ratio: float,
    test_ratio: float,
    random_seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    shuffled = list(entries)
    random.Random(random_seed).shuffle(shuffled)

    valid_count = max(1, int(len(shuffled) * validation_ratio)) if shuffled else 0
    test_count = max(1, int(len(shuffled) * test_ratio)) if shuffled else 0
    
    valid_entries = shuffled[:valid_count]
    test_entries = shuffled[valid_count:valid_count + test_count]
    train_entries = shuffled[valid_count + test_count:]
    return train_entries, valid_entries, test_entries


def summarize_entries(entries: list[dict[str, Any]]) -> dict[str, Any]:
    if not entries:
        return {
            "count": 0,
            "total_duration_seconds": 0.0,
            "average_duration_seconds": 0.0,
            "min_duration_seconds": 0.0,
            "max_duration_seconds": 0.0,
        }

    durations = [float(item["duration"]) for item in entries]
    return {
        "count": len(entries),
        "total_duration_seconds": round(sum(durations), 2),
        "average_duration_seconds": round(sum(durations) / len(durations), 2),
        "min_duration_seconds": round(min(durations), 2),
        "max_duration_seconds": round(max(durations), 2),
    }


def prepare_training_dataset(config: TrainingPrepConfig) -> dict[str, str]:
    ensure_directories(
        [
            config.extracted_root_dir,
            config.working_dataset_dir,
            config.working_dataset_dir / "audio",
            config.working_dataset_dir / "metadata",
            config.working_dataset_dir / "reports",
        ]
    )

    extract_dataset_zip(config.dataset_zip_path, config.extracted_root_dir)
    raw_manifest_entries = load_manifest_from_extracted_dir(
        config.extracted_root_dir,
        config.manifest_inside_zip,
    )
    copied_entries = copy_audio_files(raw_manifest_entries, config.extracted_root_dir, config.working_dataset_dir)
    prepared_entries, rejected_entries = filter_entries(copied_entries, config)
    train_entries, valid_entries, test_entries = split_train_valid_test(
        prepared_entries,
        config.validation_ratio,
        config.test_ratio,
        config.random_seed,
    )

    metadata_dir = config.working_dataset_dir / "metadata"
    reports_dir = config.working_dataset_dir / "reports"
    prepared_manifest_path = metadata_dir / config.prepared_manifest_name
    train_manifest_path = metadata_dir / config.train_manifest_name
    valid_manifest_path = metadata_dir / config.valid_manifest_name
    test_manifest_path = metadata_dir / config.test_manifest_name
    rejected_manifest_path = metadata_dir / "rejected_manifest.jsonl"
    report_path = reports_dir / config.report_name

    write_jsonl(prepared_manifest_path, prepared_entries)
    write_jsonl(train_manifest_path, train_entries)
    write_jsonl(valid_manifest_path, valid_entries)
    write_jsonl(test_manifest_path, test_entries)
    write_jsonl(rejected_manifest_path, rejected_entries)
    
    # Export Kaldi-style formats for CosyVoice training
    kaldi_dir = config.working_dataset_dir / "kaldi"
    for split_name, entries in [("train", train_entries), ("valid", valid_entries), ("test", test_entries)]:
        if not entries:
            continue
        split_dir = kaldi_dir / split_name
        ensure_directories([split_dir])
        
        # We must use absolute paths for Kaggle because tools/extract_embedding runs deep in scripts
        # The working_dataset_dir on Kaggle is typically /kaggle/working/training_dataset
        
        spk2utt = defaultdict(list)
        with open(split_dir / "wav.scp", "w", encoding="utf-8") as f_wav, \
             open(split_dir / "text", "w", encoding="utf-8") as f_text, \
             open(split_dir / "utt2spk", "w", encoding="utf-8") as f_utt2spk:
            for item in entries:
                # 'id' should not contain spaces
                utt_id = str(item["id"]).replace(" ", "_")
                # 'speaker' might be custom or spk0
                spk = str(item["speaker"]).replace(" ", "_")
                
                # Trích xuất đúng tên tệp âm thanh (bỏ qua đường dẫn c:/Users... của Windows)
                audio_filename = Path(item["audio_filepath"]).name
                # Gán đường dẫn tuyệt đối CHUẨN XÁC trên Linux/Kaggle
                audio_path = f"/kaggle/working/training_dataset/audio/{audio_filename}"
                
                f_wav.write(f"{utt_id} {audio_path}\n")
                f_text.write(f"{utt_id} {item['text']}\n")
                f_utt2spk.write(f"{utt_id} {spk}\n")
                spk2utt[spk].append(utt_id)
                
        with open(split_dir / "spk2utt", "w", encoding="utf-8") as f_spk2utt:
            for spk, utts in spk2utt.items():
                f_spk2utt.write(f"{spk} {' '.join(utts)}\n")

    report = {
        "config": config.to_dict(),
        "source_manifest_rows": len(raw_manifest_entries),
        "prepared_rows": len(prepared_entries),
        "rejected_rows": len(rejected_entries),
        "train_rows": len(train_entries),
        "valid_rows": len(valid_entries),
        "test_rows": len(test_entries),
        "prepared_summary": summarize_entries(prepared_entries),
        "train_summary": summarize_entries(train_entries),
        "valid_summary": summarize_entries(valid_entries),
        "test_summary": summarize_entries(test_entries),
        "report_notes": [
            "Review rejected_manifest.jsonl before training.",
            "Spot-check transcript quality in prepared_manifest.jsonl.",
            "Upload the training_dataset directory to Kaggle for fine-tuning.",
        ],
    }
    write_json(report_path, report)

    return {
        "prepared_manifest_path": str(prepared_manifest_path),
        "train_manifest_path": str(train_manifest_path),
        "valid_manifest_path": str(valid_manifest_path),
        "test_manifest_path": str(test_manifest_path),
        "report_path": str(report_path),
    }
