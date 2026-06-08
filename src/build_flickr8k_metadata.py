import argparse
import json
import re
import shutil
from pathlib import Path

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "in", "on", "with", "is",
    "are", "to", "for", "by", "from", "at", "as", "that", "this",
    "these", "those", "it", "its", "his", "her", "their", "be",
    "was", "were", "has", "have", "had", "he", "she", "they",
    "them", "him", "who", "what", "when", "where", "why", "how",
    "but", "not", "so", "too", "very", "no", "yes", "than", "then",
    "because", "into", "over", "under", "up", "down", "out", "off",
    "again", "more", "most", "some", "such", "one", "two", "three",
}


def caption_to_tags(caption: str) -> list[str]:
    caption = caption.lower()
    caption = re.sub(r"[^a-z0-9]+", " ", caption)
    words = [word for word in caption.split() if word not in STOPWORDS and len(word) > 2]
    return sorted(set(words))


def parse_flickr8k_captions(captions_file: Path) -> dict[str, list[str]]:
    captions = {}
    with captions_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            if "\t" in line:
                image_token, caption = line.strip().split("\t", 1)
            else:
                parts = line.strip().split(" ", 1)
                if len(parts) != 2:
                    continue
                image_token, caption = parts
            image_name = image_token.split("#")[0]
            captions.setdefault(image_name, []).append(caption)
    return captions


def find_image_file(image_name: str, search_dir: Path) -> Path | None:
    direct_path = search_dir / image_name
    if direct_path.exists():
        return direct_path
    for candidate in search_dir.rglob(image_name):
        if candidate.is_file():
            return candidate
    return None


def build_metadata(
    image_captions: dict[str, list[str]],
    images_dir: Path,
    output_dir: Path,
    metadata_path: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = []

    for image_name, captions in sorted(image_captions.items()):
        source_image = find_image_file(image_name, images_dir)
        if source_image is None:
            print(f"[Warning] Khong tim thay anh: {image_name}")
            continue

        target_image = output_dir / image_name
        target_image.parent.mkdir(parents=True, exist_ok=True)
        if not target_image.exists():
            shutil.copy2(source_image, target_image)

        tags = []
        for caption in captions:
            tags.extend(caption_to_tags(caption))
        tags = sorted(set(tags))

        metadata.append(
            {
                "path": str(target_image.as_posix()),
                "scene": "flickr8k",
                "tone": "neutral",
                "tags": tags,
            }
        )

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Da tao metadata cho {len(metadata)} anh vao: {metadata_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build image metadata from Flickr8k dataset")
    parser.add_argument(
        "--source-dir",
        type=Path,
        required=True,
        help="Path to the extracted Flickr8k dataset folder",
    )
    parser.add_argument(
        "--captions-file",
        type=Path,
        default=None,
        help="Optional path to the captions file (default: find Flickr8k.token.txt under source-dir)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/images/flickr8k"),
        help="Output image folder for copied Flickr8k images",
    )
    parser.add_argument(
        "--metadata-path",
        type=Path,
        default=Path("data/images/metadata.json"),
        help="Output metadata JSON path",
    )
    args = parser.parse_args()

    captions_file = args.captions_file
    if captions_file is None:
        captions_file = args.source_dir / "Flickr8k_text" / "Flickr8k.token.txt"
        if not captions_file.exists():
            captions_file = args.source_dir / "Flickr8k.token.txt"

    if captions_file is None or not captions_file.exists():
        raise FileNotFoundError(
            f"Khong tim thay file captions. Vui long truyen --captions-file hoac dat Flickr8k.token.txt trong {args.source_dir}"
        )

    images_dir = args.source_dir
    if (args.source_dir / "Flickr8k_Dataset").exists():
        images_dir = args.source_dir / "Flickr8k_Dataset"
    elif (args.source_dir / "Flickr8k_images").exists():
        images_dir = args.source_dir / "Flickr8k_images"

    image_captions = parse_flickr8k_captions(captions_file)
    build_metadata(image_captions, images_dir, args.output_dir, args.metadata_path)


if __name__ == "__main__":
    main()
