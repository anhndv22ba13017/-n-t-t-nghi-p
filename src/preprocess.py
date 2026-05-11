import re
from pathlib import Path

from src.models import Segment


def load_script(script_path: Path) -> str:
    text = script_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Script is empty: {script_path}")
    return text


def clean_text(text: str) -> str:
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    normalized = clean_text(text)
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [part.strip() for part in parts if part.strip()]


def segment_script(text: str, max_sentences_per_segment: int = 2) -> list[Segment]:
    sentences = split_sentences(text)
    segments: list[Segment] = []

    current: list[str] = []
    segment_id = 1

    for sentence in sentences:
        current.append(sentence)
        if len(current) >= max_sentences_per_segment:
            segment_text = " ".join(current)
            segments.append(
                Segment(
                    segment_id=segment_id,
                    text=segment_text,
                    sentence_count=len(current),
                    estimated_words=len(segment_text.split()),
                    estimated_characters=len(segment_text),
                )
            )
            segment_id += 1
            current = []

    if current:
        segment_text = " ".join(current)
        segments.append(
            Segment(
                segment_id=segment_id,
                text=segment_text,
                sentence_count=len(current),
                estimated_words=len(segment_text.split()),
                estimated_characters=len(segment_text),
            )
        )

    return segments
