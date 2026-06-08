from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Segment:
    segment_id: int
    text: str
    sentence_count: int
    estimated_words: int
    estimated_characters: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SegmentAnalysis:
    segment_id: int
    keywords: list[str]
    scene: str
    tone: str
    summary: str
    suggested_visuals: list[str]
    narration_style: str
    actions: list[str]
    context: str
    emotional_tone: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AudioAsset:
    segment_id: int
    audio_path: str
    duration_seconds: float
    engine: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ImageAsset:
    segment_id: int
    image_path: str
    score: float
    reason: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TimelineClip:
    segment_id: int
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    audio_path: str
    image_path: str
    narration_text: str
    scene: str
    tone: str
    visual_reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def normalize_path(path: Path) -> str:
    return str(path.as_posix())
