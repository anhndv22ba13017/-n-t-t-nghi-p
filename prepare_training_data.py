import argparse
from pathlib import Path

from src.training_config import TrainingPrepConfig, load_training_prep_config
from src.training_prep import prepare_training_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare TTS training dataset")
    parser.add_argument(
        "--config",
        type=str,
        default="config/training_prep_config.json",
        help="Path to training preparation config file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).parent
    config: TrainingPrepConfig = load_training_prep_config(base_dir / args.config)
    report = prepare_training_dataset(config)

    print("Training dataset preparation completed.")
    print(f"Prepared manifest: {report['prepared_manifest_path']}")
    print(f"Train manifest: {report['train_manifest_path']}")
    print(f"Valid manifest: {report['valid_manifest_path']}")
    print(f"Test manifest: {report['test_manifest_path']}")
    print(f"Report: {report['report_path']}")


if __name__ == "__main__":
    main()

