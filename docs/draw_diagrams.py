import os
from PIL import Image, ImageDraw, ImageFont

def draw_system_architecture(output_path, font_path="arial.ttf"):
    # Create image canvas (1200 x 800)
    img = Image.new("RGB", (1200, 800), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype(font_path, 28)
        font_header = ImageFont.truetype(font_path, 20)
        font_body = ImageFont.truetype(font_path, 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()

    # Draw Title
    draw.text((600, 40), "AI Video Assistant - System Architecture", fill="#184C78", font=font_title, anchor="mm")
    draw.line((100, 70, 1100, 70), fill="#DC143C", width=3)

    # 1. Text Preprocessor
    draw.rectangle((50, 150, 250, 280), outline="#184C78", width=3, fill="#F0F8FF")
    draw.text((150, 175), "Text Preprocessor", fill="#184C78", font=font_header, anchor="mm")
    draw.text((150, 215), "- Load raw script (.txt)\n- Normalization\n- Sentence chunking", fill="#333333", font=font_body, anchor="mm")

    # Arrow 1 -> 2
    draw.line((250, 215, 330, 215), fill="#DC143C", width=3)
    draw.polygon([(330, 210), (330, 220), (340, 215)], fill="#DC143C")

    # 2. Script Analyzer
    draw.rectangle((340, 150, 540, 280), outline="#184C78", width=3, fill="#F0F8FF")
    draw.text((440, 175), "Script Analyzer", fill="#184C78", font=font_header, anchor="mm")
    draw.text((440, 220), "- Keyword extraction\n- Scene & tone inference\n- LLM structured prompt\n  (Qwen2.5-7B)", fill="#333333", font=font_body, anchor="mm")

    # Fork Arrow 2 -> 3 (TTS) and 2 -> 4 (Image Search)
    draw.line((540, 215, 600, 215), fill="#DC143C", width=3)
    draw.line((600, 175, 600, 395), fill="#DC143C", width=3)
    
    # Arrow to TTS
    draw.line((600, 175, 650, 175), fill="#DC143C", width=3)
    draw.polygon([(650, 170), (650, 180), (660, 175)], fill="#DC143C")
    
    # Arrow to Image Search
    draw.line((600, 395, 650, 395), fill="#DC143C", width=3)
    draw.polygon([(650, 390), (650, 400), (660, 395)], fill="#DC143C")

    # 3. TTS Engine (Top Branch)
    draw.rectangle((660, 110, 860, 240), outline="#184C78", width=3, fill="#FFF5EE")
    draw.text((760, 135), "TTS Engine", fill="#184C78", font=font_header, anchor="mm")
    draw.text((760, 180), "- Qwen3-TTS Offline Model\n- Personal Voice SFT\n- 24kHz WAV Output", fill="#333333", font=font_body, anchor="mm")

    # 4. Image Retrieval (Bottom Branch)
    draw.rectangle((660, 330, 860, 460), outline="#184C78", width=3, fill="#FFF5EE")
    draw.text((760, 355), "Image Retrieval", fill="#184C78", font=font_header, anchor="mm")
    draw.text((760, 400), "- CLIP Text-Image Joint Emb.\n- FAISS Vector Index\n- Semantic Query Matching", fill="#333333", font=font_body, anchor="mm")

    # Join Arrows 3 & 4 -> 5 (Timeline Builder)
    draw.line((860, 175, 920, 175), fill="#DC143C", width=3)
    draw.line((860, 405, 920, 405), fill="#DC143C", width=3)
    draw.line((920, 175, 920, 405), fill="#DC143C", width=3)
    draw.line((920, 290, 950, 290), fill="#DC143C", width=3)
    draw.polygon([(950, 285), (950, 295), (960, 290)], fill="#DC143C")

    # 5. Timeline Builder
    draw.rectangle((960, 220, 1160, 360), outline="#184C78", width=3, fill="#F0FFF0")
    draw.text((1060, 245), "Timeline Builder", fill="#184C78", font=font_header, anchor="mm")
    draw.text((1060, 295), "- Duration measurement\n- Frame offset calculation\n- Audio-Visual alignment\n- FPS matching", fill="#333333", font=font_body, anchor="mm")

    # Arrow 5 -> 6 (Resolve Integration, placed lower)
    draw.line((1060, 360, 1060, 520), fill="#DC143C", width=3)
    draw.line((1060, 520, 600, 520), fill="#DC143C", width=3)
    draw.line((600, 520, 600, 560), fill="#DC143C", width=3)
    draw.polygon([(595, 560), (605, 560), (600, 570)], fill="#DC143C")

    # 6. Resolve Integration
    draw.rectangle((450, 570, 750, 710), outline="#184C78", width=3, fill="#F5F5DC")
    draw.text((600, 595), "DaVinci Resolve Integration", fill="#184C78", font=font_header, anchor="mm")
    draw.text((600, 645), "- FCPXML v1.5 Export (.fcpxml)\n- Auto import python scripts\n- Free & Studio Resolve support", fill="#333333", font=font_body, anchor="mm")

    # Save Image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"System architecture saved to: {output_path}")

def draw_data_flow(output_path, font_path="arial.ttf"):
    img = Image.new("RGB", (1200, 800), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype(font_path, 28)
        font_header = ImageFont.truetype(font_path, 20)
        font_body = ImageFont.truetype(font_path, 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((600, 40), "AI Video Assistant - Data Movement Flowchart", fill="#184C78", font=font_title, anchor="mm")
    draw.line((100, 70, 1100, 70), fill="#DC143C", width=3)

    # Sequence of Data Files
    # 1. raw_script.txt
    draw.rectangle((50, 150, 210, 230), outline="#184C78", fill="#E6F2FF")
    draw.text((130, 190), "Raw Script\n(sample_script.txt)", fill="#184C78", font=font_body, anchor="mm")

    draw.line((210, 190, 260, 190), fill="#DC143C", width=2)
    draw.polygon([(260, 185), (260, 195), (270, 190)], fill="#DC143C")

    # 2. segments.json
    draw.rectangle((270, 150, 430, 230), outline="#184C78", fill="#E6F2FF")
    draw.text((350, 190), "Segments Output\n(segments.json)", fill="#184C78", font=font_body, anchor="mm")

    draw.line((430, 190, 480, 190), fill="#DC143C", width=2)
    draw.polygon([(480, 185), (480, 195), (490, 190)], fill="#DC143C")

    # 3. analysis.json
    draw.rectangle((490, 150, 650, 230), outline="#184C78", fill="#E6F2FF")
    draw.text((570, 190), "Analysis Output\n(analysis.json)", fill="#184C78", font=font_body, anchor="mm")

    # Fork out of Analysis
    draw.line((650, 190, 700, 190), fill="#DC143C", width=2)
    draw.line((700, 190, 700, 350), fill="#DC143C", width=2)
    
    # To TTS -> WAV files
    draw.line((700, 190, 730, 190), fill="#DC143C", width=2)
    draw.polygon([(730, 185), (730, 195), (740, 190)], fill="#DC143C")
    
    # To Image matching
    draw.line((700, 350, 730, 350), fill="#DC143C", width=2)
    draw.polygon([(730, 345), (730, 355), (740, 350)], fill="#DC143C")

    # 4. Audio Wavs
    draw.rectangle((740, 150, 920, 230), outline="#184C78", fill="#FFF5EE")
    draw.text((830, 190), "TTS Wav Audios\n(segment_XX.wav)", fill="#184C78", font=font_body, anchor="mm")

    # 5. Image Matches
    draw.rectangle((740, 310, 920, 390), outline="#184C78", fill="#FFF5EE")
    draw.text((830, 350), "Matched Images\n(image_matches.json)", fill="#184C78", font=font_body, anchor="mm")

    # Link both to Timeline Plan
    draw.line((920, 190, 960, 190), fill="#DC143C", width=2)
    draw.line((920, 350, 960, 350), fill="#DC143C", width=2)
    draw.line((960, 190, 960, 350), fill="#DC143C", width=2)
    draw.line((960, 270, 990, 270), fill="#DC143C", width=2)
    draw.polygon([(990, 265), (990, 275), (1000, 270)], fill="#DC143C")

    # 6. timeline_plan.json
    draw.rectangle((1000, 230, 1160, 310), outline="#184C78", fill="#E6F2FF")
    draw.text((1080, 270), "Timeline Plan\n(timeline_plan.json)", fill="#184C78", font=font_body, anchor="mm")

    # Arrow down from timeline_plan
    draw.line((1080, 310, 1080, 460), fill="#DC143C", width=2)
    draw.line((1080, 460, 600, 460), fill="#DC143C", width=2)
    draw.line((600, 460, 600, 500), fill="#DC143C", width=2)
    draw.polygon([(595, 500), (605, 500), (600, 510)], fill="#DC143C")

    # 7. timeline_for_davinci.fcpxml & resolve_import_plan.json
    draw.rectangle((450, 510, 750, 610), outline="#184C78", fill="#FFF0F5")
    draw.text((600, 560), "XML Import & Scripts\n- timeline_for_davinci.fcpxml\n- resolve_import_plan.json\n- resolve_import_template.py", fill="#184C78", font=font_body, anchor="mm")

    draw.line((600, 610, 600, 650), fill="#DC143C", width=2)
    draw.polygon([(595, 650), (605, 650), (600, 660)], fill="#DC143C")

    # 8. DaVinci Resolve Timeline
    draw.rectangle((420, 660, 780, 740), outline="#006400", fill="#F0FFF0", width=3)
    draw.text((600, 700), "DaVinci Resolve Editing Suite\n(Final Synchronized Video Timeline)", fill="#006400", font=font_header, anchor="mm")

    img.save(output_path)
    print(f"Data flow diagram saved to: {output_path}")

def draw_infrastructure_topology(output_path, font_path="arial.ttf"):
    img = Image.new("RGB", (1200, 600), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype(font_path, 28)
        font_header = ImageFont.truetype(font_path, 20)
        font_body = ImageFont.truetype(font_path, 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((600, 40), "AI Video Assistant - Infrastructure Topology", fill="#184C78", font=font_title, anchor="mm")
    draw.line((100, 70, 1100, 70), fill="#DC143C", width=3)

    # Draw cloud side (Kaggle Cloud Platform)
    draw.rectangle((100, 130, 500, 450), outline="#184C78", width=3, fill="#F0F8FF")
    draw.text((300, 160), "Kaggle Cloud Server (Training)", fill="#184C78", font=font_header, anchor="mm")
    
    draw.rectangle((120, 200, 480, 430), outline="#87CEEB", fill="#FFFFFF")
    draw.text((300, 315), "HARDWARE SPECIFICATIONS:\n- 2x NVIDIA Tesla T4 GPUs (30GB total)\n- High VRAM SFT Training\n\nOPTIMIZATIONS IMPLEMENTED:\n- 8-bit Quantized SFT fine-tuning\n- Gradient Accumulation\n- Disk Quota Management (Under 19.5GB)\n- Output: checkpoint-epoch-9 (3.5GB)", fill="#333333", font=font_body, anchor="mm")

    # Download weight arrow
    draw.line((500, 290, 700, 290), fill="#DC143C", width=3)
    draw.polygon([(700, 280), (700, 300), (715, 290)], fill="#DC143C")
    draw.text((600, 260), "Download Model\nWeights (3.5GB)", fill="#DC143C", font=font_body, anchor="mm")

    # Draw local client side
    draw.rectangle((715, 130, 1115, 450), outline="#184C78", width=3, fill="#FFF5EE")
    draw.text((915, 160), "Local Client Machine (Inference)", fill="#184C78", font=font_header, anchor="mm")
    
    draw.rectangle((735, 200, 1095, 430), outline="#FFA07A", fill="#FFFFFF")
    draw.text((915, 315), "HARDWARE SPECIFICATIONS:\n- Local Desktop (CPU + CUDA GPU)\n\nSOFTWARE & FUNCTIONS:\n- Offline Qwen3-TTS Inference (WAV)\n- CLIP Text-Image Encoding\n- FAISS Vector Search\n- Local Pipeline Orchestration (main.py)\n- ASR Evaluation (Faster-Whisper)\n- DaVinci Resolve import (.fcpxml)", fill="#333333", font=font_body, anchor="mm")

    img.save(output_path)
    print(f"Infrastructure topology saved to: {output_path}")

if __name__ == "__main__":
    import sys
    # Find standard font
    font_opts = [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arial.ttf"
    ]
    font_path = "arial.ttf"
    for f in font_opts:
        if os.path.exists(f):
            font_path = f
            break
            
    draw_system_architecture("docs/system_architecture.png", font_path)
    draw_data_flow("docs/data_flow.png", font_path)
    draw_infrastructure_topology("docs/infrastructure_topology.png", font_path)
