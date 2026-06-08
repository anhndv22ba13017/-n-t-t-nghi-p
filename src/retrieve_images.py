import json
import re
from pathlib import Path

from src.build_flickr8k_metadata import build_metadata, parse_flickr8k_captions
from src.build_image_index import build_index
from src.models import ImageAsset, Segment, SegmentAnalysis


def _image_tags_from_filename(filename: str) -> list[str]:
    words = re.findall(r"[a-z0-9]{3,}", filename.lower())
    return sorted(set(words))


def _discover_images_from_directory(metadata_path: Path) -> list[dict]:
    root_dir = metadata_path.parent
    candidate_dirs = [
        root_dir / "flickr8k",
        root_dir / "flickr8k_raw",
        root_dir / "Flickr8k_Dataset",
        root_dir / "Flickr8k_images",
        root_dir,
    ]

    search_root = None
    for candidate in candidate_dirs:
        if candidate.exists() and candidate.is_dir():
            search_root = candidate
            break

    if search_root is None:
        return []

    discovered = []
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        for image_path in sorted(search_root.rglob(ext)):
            if "placeholders" in image_path.parts:
                continue
            if image_path.name.startswith("."):
                continue
            discovered.append(
                {
                    "path": str(image_path.as_posix()),
                    "scene": "flickr8k",
                    "tone": "neutral",
                    "tags": _image_tags_from_filename(image_path.stem),
                }
            )
    return discovered


def _save_auto_metadata(metadata_path: Path, catalog: list[dict]) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[Info] Tạo tự động metadata image vào {metadata_path} ({len(catalog)} mục)")


def _find_flickr8k_captions_and_images(metadata_path: Path) -> tuple[Path | None, Path | None]:
    search_roots = [metadata_path.parent, metadata_path.parent.parent, Path.cwd()]
    for root in search_roots:
        if not root.exists():
            continue
        for candidate in root.rglob("Flickr8k.token.txt"):
            image_base = candidate.parent
            if (image_base / "Flickr8k_Dataset").exists():
                return candidate, image_base / "Flickr8k_Dataset"
            if (image_base / "Flickr8k_images").exists():
                return candidate, image_base / "Flickr8k_images"
            if (image_base / "Flickr8k_text").exists():
                other = candidate.parent
                if (other / "Flickr8k_Dataset").exists():
                    return candidate, other / "Flickr8k_Dataset"
                if (other / "Flickr8k_images").exists():
                    return candidate, other / "Flickr8k_images"
            if candidate.parent == root:
                return candidate, root
    return None, None


def _build_flickr8k_metadata(metadata_path: Path) -> list[dict]:
    captions_file, images_dir = _find_flickr8k_captions_and_images(metadata_path)
    if captions_file is None or images_dir is None:
        return []
    print(f"[Info] Found Flickr8k data. Building metadata from {captions_file} and {images_dir}...")
    image_captions = parse_flickr8k_captions(captions_file)
    build_metadata(image_captions, images_dir, metadata_path.parent / "flickr8k", metadata_path)
    return json.loads(metadata_path.read_text(encoding="utf-8-sig"))


def load_image_catalog(metadata_path: Path) -> list[dict]:
    if not metadata_path.exists():
        metadata = _build_flickr8k_metadata(metadata_path)
        if metadata:
            return metadata

        discovered = _discover_images_from_directory(metadata_path)
        if discovered:
            _save_auto_metadata(metadata_path, discovered)
        return discovered

    try:
        catalog = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        catalog = json.loads(metadata_path.read_text(encoding="utf-8"))

    if isinstance(catalog, list) and len(catalog) == 0:
        metadata = _build_flickr8k_metadata(metadata_path)
        if metadata:
            return metadata

        discovered = _discover_images_from_directory(metadata_path)
        if discovered:
            _save_auto_metadata(metadata_path, discovered)
        return discovered

    return catalog


def score_image_candidate(analysis: SegmentAnalysis, image_item: dict) -> tuple[float, str]:
    score = 0.0
    matched: list[str] = []

    tags = set(tag.lower() for tag in image_item.get("tags", []))
    scene = image_item.get("scene", "").lower()
    tone = image_item.get("tone", "").lower()

    for keyword in analysis.keywords:
        if keyword.lower() in tags:
            score += 2.0
            matched.append(f"keyword:{keyword}")

    for visual in (analysis.suggested_visuals or []):
        if visual.lower() in tags:
            score += 1.5
            matched.append(f"visual:{visual}")

    if analysis.scene.lower() == scene and scene:
        score += 3.0
        matched.append(f"scene:{analysis.scene}")

    if analysis.tone.lower() == tone and tone:
        score += 1.5
        matched.append(f"tone:{analysis.tone}")

    if not matched:
        matched.append("fallback")

    return score, ", ".join(matched)


def _resolve_default_image_path(image_catalog: list[dict], metadata_path: Path) -> str:
    if image_catalog:
        return image_catalog[0].get("path", "")

    placeholder_path = metadata_path.parent / "placeholders" / "default_scene.jpg"
    if placeholder_path.exists():
        return str(placeholder_path.as_posix())

    return ""


def match_images_for_segments(
    segments: list[Segment],
    analyses: list[SegmentAnalysis],
    image_catalog: list[dict],
    metadata_path: Path,
    image_strategy: str = "metadata_keyword_match",
) -> list[ImageAsset]:
    
    faiss_index_path = metadata_path.parent / "faiss_index.bin"
    image_paths_path = metadata_path.parent / "image_paths.json"
    
    use_ai = False
    index = None
    image_paths: list[str] = []
    model = None
    strategy = image_strategy.strip().lower() if image_strategy else "metadata_keyword_match"

    if strategy not in {"auto", "faiss", "clip", "metadata_keyword_match", "metadata", "keyword"}:
        print(f"[Warning] Unknown image strategy '{image_strategy}'. Defaulting to metadata keyword matching.")
        strategy = "metadata_keyword_match"

    if strategy in {"metadata_keyword_match", "metadata", "keyword"}:
        print("[Image Retrieval] Using metadata keyword matching only.")
    else:
        if faiss_index_path.exists() and image_paths_path.exists():
            try:
                print("\n[AI Image Retrieval] Khởi động AI Tìm kiếm ảnh bằng Vector (FAISS + CLIP)...")
                import faiss
                import numpy as np
                from sentence_transformers import SentenceTransformer

                model = SentenceTransformer("clip-ViT-B-32")
                index = faiss.read_index(str(faiss_index_path))
                with open(image_paths_path, "r", encoding="utf-8") as f:
                    image_paths = json.load(f)
                use_ai = True
            except Exception as e:
                print(f"[Warning] Cannot load FAISS/CLIP: {e}. Falling back to rule-based mode.")
        else:
            print("[AI Image Retrieval] FAISS index not found. Attempting to build from data/images...")
            if build_index(metadata_path.parent):
                try:
                    import faiss
                    import numpy as np
                    from sentence_transformers import SentenceTransformer

                    model = SentenceTransformer("clip-ViT-B-32")
                    index = faiss.read_index(str(faiss_index_path))
                    with open(image_paths_path, "r", encoding="utf-8") as f:
                        image_paths = json.load(f)
                    use_ai = True
                    print("[AI Image Retrieval] FAISS index built and loaded successfully.")
                except Exception as e:
                    print(f"[Warning] Built FAISS index but failed to load it: {e}. Falling back to rule-based mode.")
            else:
                print("[AI Image Retrieval] Could not build FAISS index. Falling back to metadata keyword mode.")

    analysis_map = {analysis.segment_id: analysis for analysis in analyses}
    matches: list[ImageAsset] = []

    for segment in segments:
        analysis = analysis_map[segment.segment_id]
        best_path = _resolve_default_image_path(image_catalog, metadata_path)
        best_score = -1.0
        best_reason = "fallback"
        source = "metadata_catalog"

        if use_ai and model is not None and index is not None and image_paths:
            try:
                import numpy as np
                query = (
                    f"{analysis.summary} A scene showing {analysis.scene} with a {analysis.tone} tone. "
                    f"Keywords: {', '.join(analysis.keywords)}. Suggested visuals: {', '.join(analysis.suggested_visuals)}."
                )
                print(f"  - Đang tìm ảnh cho đoạn: '{query[:60]}...'")

                text_emb = model.encode([query], convert_to_numpy=True)
                if text_emb.ndim == 1:
                    text_emb = text_emb.reshape(1, -1)
                text_emb = text_emb / np.linalg.norm(text_emb, axis=1, keepdims=True)

                scores, indices = index.search(text_emb, 1)
                if indices[0][0] != -1:
                    idx = indices[0][0]
                    best_path = image_paths[idx]
                    best_score = float(scores[0][0]) * 100.0
                    best_reason = f"AI Semantic Match (Score: {best_score:.1f}%)"
                    source = "faiss_clip"
            except Exception as e:
                print(f"[Warning] AI image retrieval failed: {e}. Falling back to rule-based.")
                use_ai = False

        if not use_ai:
            for image_item in image_catalog:
                score, reason = score_image_candidate(analysis, image_item)
                if score > best_score:
                    best_score = score
                    best_reason = reason
                    best_path = image_item.get("path", best_path)

        matches.append(
            ImageAsset(
                segment_id=segment.segment_id,
                image_path=best_path,
                score=round(max(best_score, 0.0), 2),
                reason=best_reason,
                source=source,
            )
        )

    return matches
