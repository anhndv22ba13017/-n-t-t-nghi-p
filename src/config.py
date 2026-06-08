import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class AppConfig:
    project_name: str
    timeline_name: str
    script_path: Path
    image_metadata_path: Path
    output_dir: Path
    audio_output_dir: Path
    reports_dir: Path
    max_sentences_per_segment: int
    tts_engine_name: str
    tts_voice: str
    tts_model_path: Path | None
    external_audio_manifest_path: Path | None
    analysis_mode: str
    analysis_provider: str
    analysis_model: str | None
    external_analysis_path: Path | None
    image_strategy: str
    target_language: str
    fps: int

    def to_summary_dict(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "timeline_name": self.timeline_name,
            "script_path": str(self.script_path),
            "image_metadata_path": str(self.image_metadata_path),
            "output_dir": str(self.output_dir),
            "audio_output_dir": str(self.audio_output_dir),
            "reports_dir": str(self.reports_dir),
            "max_sentences_per_segment": self.max_sentences_per_segment,
            "tts_engine_name": self.tts_engine_name,
            "tts_voice": self.tts_voice,
            "tts_model_path": str(self.tts_model_path) if self.tts_model_path else None,
            "external_audio_manifest_path": str(self.external_audio_manifest_path) if self.external_audio_manifest_path else None,
            "analysis_mode": self.analysis_mode,
            "analysis_provider": self.analysis_provider,
            "analysis_model": self.analysis_model,
            "external_analysis_path": str(self.external_analysis_path) if self.external_analysis_path else None,
            "image_strategy": self.image_strategy,
            "target_language": self.target_language,
            "fps": self.fps,
        }


def load_config(config_path: Path) -> AppConfig:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    root = config_path.parent.parent

    external_audio_manifest = payload.get("external_audio_manifest_path")
    external_analysis_path = payload.get("external_analysis_path")

    return AppConfig(
        project_name=payload["project_name"],
        timeline_name=payload["timeline_name"],
        script_path=root / payload["script_path"],
        image_metadata_path=root / payload["image_metadata_path"],
        output_dir=root / payload["output_dir"],
        audio_output_dir=root / payload["audio_output_dir"],
        reports_dir=root / payload["reports_dir"],
        max_sentences_per_segment=payload.get("max_sentences_per_segment", 2),
        tts_engine_name=payload.get("tts_engine_name", "edge_tts"),
        tts_voice=payload.get("tts_voice", "vi-VN-HoaiMyNeural"),
        tts_model_path=(root / payload["tts_model_path"]) if payload.get("tts_model_path") else None,
        external_audio_manifest_path=(root / external_audio_manifest) if external_audio_manifest else None,
        analysis_mode=payload.get("analysis_mode", "rule_based"),
        analysis_provider=payload.get("analysis_provider", "local"),
        analysis_model=payload.get("analysis_model"),
        external_analysis_path=(root / external_analysis_path) if external_analysis_path else None,
        image_strategy=payload.get("image_strategy", "metadata_keyword_match"),
        target_language=payload.get("target_language", "en"),
        fps=payload.get("fps", 25),
    )
