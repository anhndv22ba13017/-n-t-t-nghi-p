import json
import os
import re
import ssl
import urllib.request
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

ACTION_KEYWORDS = {
    "create", "generate", "build", "find", "search", "match", "insert", "edit", "export",
    "tạo", "sinh", "xây dựng", "tìm", "phân tích", "ghép", "chèn", "xuất", "hiển thị", "làm",
    "đọc", "trình bày", "giải thích", "di chuyển", "chạy", "thực hiện",
}

CONTEXT_MARKERS = [
    "when", "while", "during", "at", "in", "trong", "khi", "tại", "vào", "giữa", "nhân dịp",
]


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


def extract_actions(text: str, max_actions: int = 3) -> list[str]:
    lower = text.lower()
    found = []
    for verb in ACTION_KEYWORDS:
        if verb in lower and verb not in found:
            found.append(verb)
        if len(found) >= max_actions:
            break

    if not found:
        tokens = [token.strip(".,!?;:()[]{}\"'").lower() for token in text.split()]
        found = [token for token in tokens if token not in STOPWORDS and len(token) > 2][:max_actions]

    return found


def infer_context(text: str) -> str:
    lower = text.lower()
    for marker in CONTEXT_MARKERS:
        match = re.search(r"\b" + re.escape(marker) + r"\b", lower)
        if match:
            sentence = text.strip()
            return sentence if len(sentence) <= 120 else summarize_segment(sentence, max_words=12)
    return summarize_segment(text, max_words=12)


def infer_emotional_tone(tone: str) -> str:
    mapping = {
        "calm": "calm",
        "uplifting": "positive",
        "dramatic": "intense",
        "emotional": "emotional",
        "inspirational": "hopeful",
        "neutral": "neutral",
    }
    return mapping.get(tone, tone)


def analyze_segments(segments: list[Segment]) -> list[SegmentAnalysis]:
    analyses: list[SegmentAnalysis] = []
    for segment in segments:
        keywords = extract_keywords(segment.text)
        scene = infer_scene(keywords)
        tone = infer_tone(keywords)
        analysis = SegmentAnalysis(
            segment_id=segment.segment_id,
            keywords=keywords,
            scene=scene,
            tone=tone,
            summary=summarize_segment(segment.text),
            suggested_visuals=build_visual_suggestions(keywords, scene),
            narration_style=infer_narration_style(tone),
            actions=extract_actions(segment.text),
            context=infer_context(segment.text),
            emotional_tone=infer_emotional_tone(tone),
        )
        analyses.append(analysis)
    return analyses


def build_analysis_prompts(segments: list[Segment]) -> list[dict]:
    prompts: list[dict] = []
    for segment in segments:
        prompts.append(
            {
                "segment_id": segment.segment_id,
                "text": segment.text,
                "prompt": (
                    "Analyze this video narration segment and return strict JSON with keys: "
                    "`keywords`, `scene`, `tone`, `summary`, `visuals`, `narration_style`, `actions`, "
                    "`context`, and `emotional_tone`. Describe the scene, emotion, and appropriate visual ideas. "
                    f"Text: {segment.text}"
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
                    "actions": ["string"],
                    "context": "string",
                    "emotional_tone": "string",
                },
            }
        )

    return requests


def _normalize_llm_provider(provider: str) -> str:
    return provider.strip().lower() if provider else "openai"


def _parse_llm_output(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        cleaned = content.strip()
        first_brace = cleaned.find("{")
        if first_brace != -1:
            cleaned = cleaned[first_brace:]
        return json.loads(cleaned)


def _build_analysis_from_payload(payload: dict, segment_id: int) -> SegmentAnalysis:
    visual_list = payload.get("visuals") or payload.get("suggested_visuals") or []
    return SegmentAnalysis(
        segment_id=segment_id,
        keywords=payload.get("keywords", []),
        scene=payload.get("scene", "general"),
        tone=payload.get("tone", "neutral"),
        summary=payload.get("summary", ""),
        suggested_visuals=visual_list,
        narration_style=payload.get("narration_style", "natural"),
        actions=payload.get("actions", []),
        context=payload.get("context", ""),
        emotional_tone=payload.get("emotional_tone", payload.get("tone", "neutral")),
    )


def run_llm_analysis(requests: list[dict], provider: str, model: str | None) -> list[SegmentAnalysis]:
    provider_name = _normalize_llm_provider(provider)
    if not requests:
        return []

    if provider_name in {"openai", "gpt", "gpt-4", "gpt-4o", "gpt-3.5-turbo"}:
        try:
            import openai
        except ImportError as e:
            raise ImportError(
                "OpenAI client is not installed. Install it with `pip install openai` "
                "or set another supported analysis provider."
            ) from e

        if model is None:
            raise ValueError("analysis_model must be set for OpenAI provider")

        analyses: list[SegmentAnalysis] = []
        for request in requests:
            response = openai.ChatCompletion.create(
                model=model,
                messages=request["messages"],
                temperature=0.2,
                max_tokens=512,
            )
            raw_text = response.choices[0].message.content
            payload = _parse_llm_output(raw_text)
            analyses.append(_build_analysis_from_payload(payload, request["segment_id"]))
        return analyses

    if provider_name in {"qwen", "qwen2", "qwen3"}:
        if model is None:
            raise ValueError("analysis_model must be set for Qwen provider")

        try:
            from qwen import ChatCompletion
        except ImportError:
            qwen_url = os.getenv("QWEN_API_URL")
            qwen_key = os.getenv("QWEN_API_KEY")
            if not qwen_url or not qwen_key:
                raise ImportError(
                    "Qwen package not installed and QWEN_API_URL/QWEN_API_KEY not configured. "
                    "Install a Qwen client or set the remote endpoint environment variables."
                )

            analyses = []
            for request in requests:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {qwen_key}",
                }
                payload = {
                    "model": model,
                    "messages": request["messages"],
                    "temperature": 0.2,
                }
                req = urllib.request.Request(
                    qwen_url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, context=ssl.create_default_context()) as resp:
                    raw_body = resp.read().decode("utf-8")
                response = json.loads(raw_body)
                raw_text = response["choices"][0]["message"]["content"]
                analyses.append(_build_analysis_from_payload(_parse_llm_output(raw_text), request["segment_id"]))
            return analyses

        analyses = []
        for request in requests:
            response = ChatCompletion.create(
                model=model,
                messages=request["messages"],
                temperature=0.2,
            )
            raw_text = response.choices[0].message.content
            analyses.append(_build_analysis_from_payload(_parse_llm_output(raw_text), request["segment_id"]))
        return analyses

    raise ValueError(
        f"Unsupported external analysis provider '{provider}'. "
        "Supported providers: openai"
    )


def load_external_analysis(json_path: Path) -> list[SegmentAnalysis]:
    if not json_path.exists():
        print(f"Warning: External analysis file {json_path} not found. Returning empty list.")
        return []
    
    data = json.loads(json_path.read_text(encoding="utf-8"))
    analyses: list[SegmentAnalysis] = []
    
    for item in data:
        visual_list = item.get("visuals") or item.get("suggested_visuals") or []
        analyses.append(
            SegmentAnalysis(
                segment_id=item["segment_id"],
                keywords=item.get("keywords", []),
                scene=item.get("scene", "general"),
                tone=item.get("tone", "neutral"),
                summary=item.get("summary", ""),
                suggested_visuals=visual_list,
                narration_style=item.get("narration_style", "natural"),
                actions=item.get("actions", []),
                context=item.get("context", ""),
                emotional_tone=item.get("emotional_tone", item.get("tone", "neutral")),
            )
        )
    return analyses
