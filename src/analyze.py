import json
from collections import Counter
from pathlib import Path

from src.models import Segment, SegmentAnalysis


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
    # Từ khóa dừng tiếng Việt (Vietnamese stopwords)
    "và", "là", "của", "các", "những", "cho", "từ", "trong", "vào", 
    "có", "không", "một", "như", "để", "ở", "với", "thì", "mà", 
    "này", "đó", "khi", "đã", "đang", "sẽ", "được", "bởi", "tại", "sự"
}

SCENE_KEYWORDS = {
    "city": "urban", "thành phố": "urban", "phố": "urban",
    "street": "urban", "đường": "urban", "đường phố": "urban",
    "market": "urban", "chợ": "urban", "siêu thị": "urban",
    "forest": "nature", "rừng": "nature",
    "river": "nature", "sông": "nature", "suối": "nature",
    "mountain": "nature", "núi": "nature", "đồi": "nature",
    "office": "indoor", "văn phòng": "indoor", "công ty": "indoor",
    "room": "indoor", "phòng": "indoor", "nhà": "indoor",
    "school": "education", "trường": "education", "trường học": "education", "lớp": "education",
    "technology": "technology", "công nghệ": "technology",
    "computer": "technology", "máy tính": "technology", "laptop": "technology",
    "phone": "technology", "điện thoại": "technology",
    "rain": "weather", "mưa": "weather",
    "sunrise": "morning", "bình minh": "morning",
    "morning": "morning", "sáng": "morning", "buổi sáng": "morning",
    "night": "night", "đêm": "night", "tối": "night", "buổi tối": "night",
}

TONE_KEYWORDS = {
    "calm": "calm", "yên bình": "calm", "nhẹ nhàng": "calm", "bình yên": "calm",
    "gentle": "calm", "êm đềm": "calm", "dịu dàng": "calm",
    "happy": "uplifting", "vui vẻ": "uplifting", "hạnh phúc": "uplifting", "tươi vui": "uplifting",
    "hope": "uplifting", "hy vọng": "uplifting", "tích cực": "uplifting",
    "dramatic": "dramatic", "kịch tính": "dramatic", "hồi hộp": "dramatic", "căng thẳng": "dramatic",
    "danger": "dramatic", "nguy hiểm": "dramatic",
    "sad": "emotional", "buồn": "emotional", "cảm động": "emotional", "xúc động": "emotional",
    "memory": "emotional", "kỷ niệm": "emotional", "ký ức": "emotional",
    "future": "inspirational", "tương lai": "inspirational", "định hướng": "inspirational",
    "dream": "inspirational", "ước mơ": "inspirational", "giấc mơ": "inspirational", "khát vọng": "inspirational",
}


def extract_keywords(text: str, top_k: int = 5) -> list[str]:
    tokens = [
        token.strip(".,!?;:()[]{}\"'").lower()
        for token in text.split()
        if token.strip(".,!?;:()[]{}\"'")
    ]
    filtered = [token for token in tokens if token not in STOPWORDS and len(token) > 2]
    counts = Counter(filtered)
    return [token for token, _ in counts.most_common(top_k)]


def infer_scene(keywords: list[str]) -> str:
    for keyword in keywords:
        if keyword in SCENE_KEYWORDS:
            return SCENE_KEYWORDS[keyword]
    return "general"


def infer_tone(keywords: list[str]) -> str:
    for keyword in keywords:
        if keyword in TONE_KEYWORDS:
            return TONE_KEYWORDS[keyword]
    return "neutral"


def summarize_segment(text: str, max_words: int = 10) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def build_visual_suggestions(keywords: list[str], scene: str) -> list[str]:
    suggestions = [scene]
    suggestions.extend(keywords[:3])
    deduped: list[str] = []
    for item in suggestions:
        if item and item not in deduped:
            deduped.append(item)
    return deduped


def infer_narration_style(tone: str) -> str:
    mapping = {
        "calm": "slow and warm",
        "uplifting": "bright and optimistic",
        "dramatic": "strong and cinematic",
        "emotional": "gentle and reflective",
        "inspirational": "clear and motivating",
        "neutral": "natural and balanced",
    }
    return mapping.get(tone, "natural and balanced")


def analyze_segments(segments: list[Segment]) -> list[SegmentAnalysis]:
    analyses: list[SegmentAnalysis] = []
    for segment in segments:
        keywords = extract_keywords(segment.text)
        analyses.append(
            SegmentAnalysis(
                segment_id=segment.segment_id,
                keywords=keywords,
                scene=infer_scene(keywords),
                tone=infer_tone(keywords),
                summary=summarize_segment(segment.text),
                suggested_visuals=build_visual_suggestions(keywords, infer_scene(keywords)),
                narration_style=infer_narration_style(infer_tone(keywords)),
            )
        )
    return analyses


def build_analysis_prompts(segments: list[Segment]) -> list[dict]:
    prompts: list[dict] = []
    for segment in segments:
        prompts.append(
            {
                "segment_id": segment.segment_id,
                "text": segment.text,
                "prompt": (
                    "Analyze this video narration segment and return JSON with keys "
                    "`keywords`, `scene`, `tone`, `summary`, `visuals`, and `narration_style`: "
                    f"{segment.text}"
                ),
            }
        )
    return prompts


def build_analysis_requests(
    segments: list[Segment],
    provider: str,
    model: str | None,
    target_language: str,
) -> list[dict]:
    requests: list[dict] = []
    normalized_provider = provider.strip().lower()
    normalized_model = model.strip() if model else None

    system_prompt = (
        "You analyze narration segments for an AI video pipeline. "
        "Return strict JSON with keys: keywords, scene, tone, summary, visuals, narration_style. "
        "Keep keywords and visuals concise. "
        f"Prefer {target_language} outputs when the input language allows it."
    )

    for segment in segments:
        user_prompt = (
            "Analyze the following narration segment and produce strict JSON only.\n"
            f"segment_id: {segment.segment_id}\n"
            f"text: {segment.text}"
        )
        requests.append(
            {
                "segment_id": segment.segment_id,
                "provider": normalized_provider,
                "model": normalized_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "expected_schema": {
                    "keywords": ["string"],
                    "scene": "string",
                    "tone": "string",
                    "summary": "string",
                    "visuals": ["string"],
                    "narration_style": "string",
                },
            }
        )

    return requests


def load_external_analysis(json_path: Path) -> list[SegmentAnalysis]:
    if not json_path.exists():
        print(f"Warning: External analysis file {json_path} not found. Returning empty list.")
        return []
    
    data = json.loads(json_path.read_text(encoding="utf-8"))
    analyses: list[SegmentAnalysis] = []
    
    for item in data:
        analyses.append(
            SegmentAnalysis(
                segment_id=item["segment_id"],
                keywords=item.get("keywords", []),
                scene=item.get("scene", "general"),
                tone=item.get("tone", "neutral"),
                summary=item.get("summary", ""),
                suggested_visuals=item.get("suggested_visuals", []),
                narration_style=item.get("narration_style", "natural"),
            )
        )
    return analyses
