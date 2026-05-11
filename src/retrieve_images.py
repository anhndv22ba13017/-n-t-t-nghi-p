import json
from pathlib import Path

from src.models import ImageAsset, Segment, SegmentAnalysis


def load_image_catalog(metadata_path: Path) -> list[dict]:
    if not metadata_path.exists():
        return []
    return json.loads(metadata_path.read_text(encoding="utf-8"))


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

    if analysis.scene.lower() == scene and scene:
        score += 3.0
        matched.append(f"scene:{analysis.scene}")

    if analysis.tone.lower() == tone and tone:
        score += 1.5
        matched.append(f"tone:{analysis.tone}")

    if not matched:
        matched.append("fallback")

    return score, ", ".join(matched)


def match_images_for_segments(
    segments: list[Segment],
    analyses: list[SegmentAnalysis],
    image_catalog: list[dict],
) -> list[ImageAsset]:
    
    # Try to load FAISS index and model
    faiss_index_path = Path("data/images/faiss_index.bin")
    image_paths_path = Path("data/images/image_paths.json")
    
    use_ai = False
    index = None
    image_paths = []
    model = None

    if faiss_index_path.exists() and image_paths_path.exists():
        try:
            print("\n[AI Image Retrieval] Khởi động AI Tìm kiếm ảnh bằng Vector (FAISS + CLIP)...")
            import faiss
            import numpy as np
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer('clip-ViT-B-32')
            index = faiss.read_index(str(faiss_index_path))
            with open(image_paths_path, "r", encoding="utf-8") as f:
                image_paths = json.load(f)
            use_ai = True
        except Exception as e:
            print(f"[Warning] Không thể nạp FAISS/CLIP: {e}. Chuyển về chế độ Rule-based cũ.")

    analysis_map = {analysis.segment_id: analysis for analysis in analyses}
    matches: list[ImageAsset] = []

    for segment in segments:
        analysis = analysis_map[segment.segment_id]
        best_path = "data/images/placeholders/default_scene.jpg"
        best_score = -1.0
        best_reason = "fallback"
        source = "metadata_catalog"

        if use_ai and model is not None and index is not None:
            import numpy as np
            # Tạo câu truy vấn (Text Query) từ kết quả phân tích kịch bản
            query = f"{analysis.summary} A scene showing {analysis.scene} with a {analysis.tone} tone. Keywords: {', '.join(analysis.keywords)}."
            print(f"  - Đang tìm ảnh cho đoạn: '{query[:50]}...'")
            
            # Encode text query
            text_emb = model.encode([query], convert_to_numpy=True)
            text_emb = text_emb / np.linalg.norm(text_emb, axis=1, keepdims=True)
            
            # Search FAISS (k=1)
            scores, indices = index.search(text_emb, 1)
            
            if indices[0][0] != -1:
                idx = indices[0][0]
                best_path = image_paths[idx]
                best_score = float(scores[0][0]) * 100.0  # Chuyển similarity sang hệ điểm 100
                best_reason = f"AI Semantic Match (Score: {best_score:.1f}%)"
                source = "faiss_clip"
        else:
            # Logic cũ (Rule-based Fallback)
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
