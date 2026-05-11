import argparse
from pathlib import Path

from src.analyze import analyze_segments, build_analysis_prompts, build_analysis_requests, load_external_analysis
from src.build_timeline import build_timeline_plan, export_timeline_outputs
from src.config import AppConfig, load_config
from src.preprocess import load_script, segment_script
from src.resolve_integration import export_resolve_import_plan
from src.retrieve_images import load_image_catalog, match_images_for_segments
from src.tts_engine import synthesize_audio_manifest
from src.utils import ensure_directories, write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Video Assistant prototype pipeline")
    parser.add_argument("--config", type=str, default="config/project_config.json", help="Path to JSON config file")
    return parser.parse_args()


def run_pipeline(config: AppConfig) -> None:
    ensure_directories(
        [
            config.output_dir,
            config.audio_output_dir,
            config.reports_dir,
        ]
    )

    script_text = load_script(config.script_path)
    segments = segment_script(script_text, max_sentences_per_segment=config.max_sentences_per_segment)
    
    if config.analysis_mode == "external_llm" and config.external_analysis_path and config.external_analysis_path.exists():
        print(f"Loading external LLM analysis from {config.external_analysis_path}...")
        analyses = load_external_analysis(config.external_analysis_path)
    else:
        print("Running rule-based analysis (or external JSON not found yet)...")
        analyses = analyze_segments(segments)

    prompts = build_analysis_prompts(segments)
    analysis_requests = build_analysis_requests(
        segments,
        config.analysis_provider,
        config.analysis_model,
        config.target_language,
    )
    image_catalog = load_image_catalog(config.image_metadata_path)
    image_matches = match_images_for_segments(segments, analyses, image_catalog)
    audio_manifest = synthesize_audio_manifest(
        segments,
        config.audio_output_dir,
        config.tts_engine_name,
        config.tts_voice,
        config.external_audio_manifest_path,
    )
    timeline_plan = build_timeline_plan(segments, analyses, audio_manifest, image_matches)

    export_timeline_outputs(config.output_dir, segments, analyses, audio_manifest, image_matches, timeline_plan)
    export_resolve_import_plan(config.output_dir, timeline_plan, config)
    write_json(config.output_dir / "analysis_prompts.json", prompts)
    write_json(config.output_dir / "analysis_requests.json", analysis_requests)
    write_json(config.reports_dir / "project_summary.json", config.to_summary_dict())

    print("Pipeline completed.")
    print("Outputs saved in output directory.")


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).parent
    config = load_config(base_dir / args.config)
    run_pipeline(config)


if __name__ == "__main__":
    main()
