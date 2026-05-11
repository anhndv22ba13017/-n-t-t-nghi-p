import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class TrainingPrepConfig:
    dataset_zip_path: Path
    extracted_root_dir: Path
    working_dataset_dir: Path
    manifest_inside_zip: str
    min_duration_seconds: float
    max_duration_seconds: float
    min_text_length: int
    validation_ratio: float
    test_ratio: float
    random_seed: int
    require_vietnamese_text: bool
    train_manifest_name: str
    valid_manifest_name: str
    test_manifest_name: str
    prepared_manifest_name: str
    report_name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset_zip_path": str(self.dataset_zip_path),
            "extracted_root_dir": str(self.extracted_root_dir),
            "working_dataset_dir": str(self.working_dataset_dir),
            "manifest_inside_zip": self.manifest_inside_zip,
            "min_duration_seconds": self.min_duration_seconds,
            "max_duration_seconds": self.max_duration_seconds,
            "min_text_length": self.min_text_length,
            "validation_ratio": self.validation_ratio,
            "test_ratio": self.test_ratio,
            "random_seed": self.random_seed,
            "require_vietnamese_text": self.require_vietnamese_text,
            "train_manifest_name": self.train_manifest_name,
            "valid_manifest_name": self.valid_manifest_name,
            "test_manifest_name": self.test_manifest_name,
            "prepared_manifest_name": self.prepared_manifest_name,
            "report_name": self.report_name,
        }


def load_training_prep_config(config_path: Path) -> TrainingPrepConfig:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    root = config_path.parent.parent
    return TrainingPrepConfig(
        dataset_zip_path=root / payload["dataset_zip_path"],
        extracted_root_dir=root / payload["extracted_root_dir"],
        working_dataset_dir=root / payload["working_dataset_dir"],
        manifest_inside_zip=payload["manifest_inside_zip"],
        min_duration_seconds=payload.get("min_duration_seconds", 1.0),
        max_duration_seconds=payload.get("max_duration_seconds", 12.0),
        min_text_length=payload.get("min_text_length", 8),
        validation_ratio=payload.get("validation_ratio", 0.1),
        test_ratio=payload.get("test_ratio", 0.1),
        random_seed=payload.get("random_seed", 42),
        require_vietnamese_text=payload.get("require_vietnamese_text", True),
        train_manifest_name=payload.get("train_manifest_name", "train_manifest.jsonl"),
        valid_manifest_name=payload.get("valid_manifest_name", "valid_manifest.jsonl"),
        test_manifest_name=payload.get("test_manifest_name", "test_manifest.jsonl"),
        prepared_manifest_name=payload.get("prepared_manifest_name", "prepared_manifest.jsonl"),
        report_name=payload.get("report_name", "training_prep_report.json"),
    )

