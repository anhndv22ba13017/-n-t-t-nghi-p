import json
from pathlib import Path

from src.models import AudioAsset, ImageAsset, Segment, SegmentAnalysis, TimelineClip


def build_timeline_plan(
    segments: list[Segment],
    analyses: list[SegmentAnalysis],
    audio_assets: list[AudioAsset],
    image_assets: list[ImageAsset],
) -> list[TimelineClip]:
    analysis_map = {item.segment_id: item for item in analyses}
    audio_map = {item.segment_id: item for item in audio_assets}
    image_map = {item.segment_id: item for item in image_assets}

    current_time = 0.0
    clips: list[TimelineClip] = []

    for segment in segments:
        audio = audio_map[segment.segment_id]
        image = image_map[segment.segment_id]
        analysis = analysis_map[segment.segment_id]

        start_seconds = round(current_time, 2)
        end_seconds = round(current_time + audio.duration_seconds, 2)

        clips.append(
            TimelineClip(
                segment_id=segment.segment_id,
                start_seconds=start_seconds,
                end_seconds=end_seconds,
                duration_seconds=audio.duration_seconds,
                audio_path=audio.audio_path,
                image_path=image.image_path,
                narration_text=segment.text,
                scene=analysis.scene,
                tone=analysis.tone,
                visual_reason=image.reason,
            )
        )

        current_time = end_seconds

    return clips


def _write_json(path: Path, payload: list[dict]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def export_timeline_outputs(
    output_dir: Path,
    segments: list[Segment],
    analyses: list[SegmentAnalysis],
    audio_assets: list[AudioAsset],
    image_assets: list[ImageAsset],
    timeline_plan: list[TimelineClip],
) -> None:
    _write_json(output_dir / "segments.json", [item.to_dict() for item in segments])
    _write_json(output_dir / "analysis.json", [item.to_dict() for item in analyses])
    _write_json(output_dir / "audio_manifest.json", [item.to_dict() for item in audio_assets])
    _write_json(output_dir / "image_matches.json", [item.to_dict() for item in image_assets])
    _write_json(output_dir / "timeline_plan.json", [item.to_dict() for item in timeline_plan])
