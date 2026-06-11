import os
from PIL import Image, ImageDraw, ImageFont

def draw_rag_baseline(output_path, font_path="arial.ttf"):
    img = Image.new("RGB", (1200, 500), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype(font_path, 28)
        font_header = ImageFont.truetype(font_path, 20)
        font_body = ImageFont.truetype(font_path, 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((600, 40), "Standard RAG vs AI Video Assistant Pipeline", fill="#184C78", font=font_title, anchor="mm")
    draw.line((100, 70, 1100, 70), fill="#DC143C", width=3)

    # Standard RAG
    draw.text((250, 110), "Standard Text RAG System", fill="#184C78", font=font_header, anchor="mm")
    draw.rectangle((50, 140, 450, 420), outline="#184C78", width=2, fill="#F5F5F5")
    draw.text((250, 280), "Query Text\n\n     |\n     v\nVector Search (Text database)\n\n     |\n     v\nGenerate Text Answer (LLM)", fill="#333333", font=font_body, anchor="mm")

    # VS Divider
    draw.line((600, 120, 600, 440), fill="#C0C0C0", width=2)
    draw.text((600, 280), "VS", fill="#DC143C", font=font_header, anchor="mm")

    # Our AI Video Pipeline
    draw.text((950, 110), "AI Video Assistant Pipeline (Ours)", fill="#184C78", font=font_header, anchor="mm")
    draw.rectangle((750, 140, 1150, 420), outline="#006400", width=2, fill="#F0FFF0")
    draw.text((950, 280), "Input Script Text\n\n     |\n     v\nParallel Generation:\n1) Fine-tuned Qwen3-TTS -> Audio (.wav)\n2) CLIP + FAISS Vector Search -> Images\n\n     |\n     v\nTime Alignment & Timeline Sync\n\n     |\n     v\nDaVinci Resolve Timeline (.fcpxml)", fill="#333333", font=font_body, anchor="mm")

    img.save(output_path)
    print(f"RAG baseline comparison saved to: {output_path}")

def draw_clip_embedding_space(output_path, font_path="arial.ttf"):
    img = Image.new("RGB", (800, 600), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype(font_path, 26)
        font_header = ImageFont.truetype(font_path, 18)
        font_body = ImageFont.truetype(font_path, 13)
    except Exception:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((400, 40), "CLIP Joint Image-Text Embedding Space", fill="#184C78", font=font_title, anchor="mm")
    draw.line((80, 65, 720, 65), fill="#DC143C", width=3)

    # Draw 2D Vector Axes
    draw.line((150, 500, 150, 150), fill="#666666", width=2) # Y axis
    draw.line((150, 500, 650, 500), fill="#666666", width=2) # X axis
    draw.text((150, 130), "Feature Dimension Y", fill="#666666", font=font_body, anchor="mm")
    draw.text((650, 520), "Feature Dimension X", fill="#666666", font=font_body, anchor="mm")

    # Center origin
    origin = (150, 500)

    # 1. Text query vector (Red)
    text_end = (420, 250)
    draw.line((origin[0], origin[1], text_end[0], text_end[1]), fill="#DC143C", width=4)
    draw.polygon([(text_end[0]-5, text_end[1]+10), (text_end[0]+10, text_end[1]-5), (text_end[0]+8, text_end[1]+8)], fill="#DC143C")
    draw.text((text_end[0]+20, text_end[1]-20), "Text Query Vector V_q\n'A scene in nature'", fill="#DC143C", font=font_body, anchor="lm")

    # 2. Image match 1: Close Match (Green)
    img1_end = (480, 210)
    draw.line((origin[0], origin[1], img1_end[0], img1_end[1]), fill="#008000", width=3)
    draw.polygon([(img1_end[0]-8, img1_end[1]+10), (img1_end[0]+5, img1_end[1]-8), (img1_end[0]+4, img1_end[1]+5)], fill="#008000")
    draw.text((img1_end[0]+20, img1_end[1]), "Image Vector V_i1 (Forest image)\n[Best Match: Cosine Sim = 87.5%]", fill="#008000", font=font_body, anchor="lm")

    # 3. Image match 2: Far Match (Blue)
    img2_end = (260, 200)
    draw.line((origin[0], origin[1], img2_end[0], img2_end[1]), fill="#184C78", width=3)
    draw.polygon([(img2_end[0]-10, img2_end[1]+10), (img2_end[0]-2, img2_end[1]-10), (img2_end[0]+8, img2_end[1]+5)], fill="#184C78")
    draw.text((img2_end[0]-10, img2_end[1]-30), "Image Vector V_i2\n(City skyline)\n[Sim = 35.2%]", fill="#184C78", font=font_body, anchor="mm")

    # Angle arc (Theta) representation
    draw.arc((100, 450, 200, 550), start=315, end=330, fill="#333333", width=2)
    draw.text((220, 430), "theta (Cosine Angle)", fill="#333333", font=font_body)

    img.save(output_path)
    print(f"CLIP embedding space saved to: {output_path}")

def draw_resolve_timeline_structure(output_path, font_path="arial.ttf"):
    img = Image.new("RGB", (1200, 500), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype(font_path, 28)
        font_header = ImageFont.truetype(font_path, 20)
        font_body = ImageFont.truetype(font_path, 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((600, 40), "DaVinci Resolve Timeline Track Layout", fill="#184C78", font=font_title, anchor="mm")
    draw.line((100, 70, 1100, 70), fill="#DC143C", width=3)

    # Timeline header/rulers
    draw.rectangle((200, 120, 1100, 150), fill="#D3D3D3")
    draw.text((220, 135), "00:00", fill="#333333", font=font_body, anchor="lm")
    draw.text((450, 135), "00:05", fill="#333333", font=font_body, anchor="lm")
    draw.text((680, 135), "00:10", fill="#333333", font=font_body, anchor="lm")
    draw.text((910, 135), "00:15", fill="#333333", font=font_body, anchor="lm")

    # Video Track V1
    draw.rectangle((50, 180, 180, 280), fill="#184C78", outline="#FFFFFF")
    draw.text((115, 230), "Video V1\n(Images)", fill="#FFFFFF", font=font_header, anchor="mm")

    # Video Clips on timeline
    draw.rectangle((200, 180, 480, 280), fill="#E6F2FF", outline="#184C78", width=2)
    draw.text((340, 230), "image_01.jpg\n(Duration: 5.6s)", fill="#184C78", font=font_body, anchor="mm")

    draw.rectangle((480, 180, 800, 280), fill="#E6F2FF", outline="#184C78", width=2)
    draw.text((640, 230), "image_02.jpg\n(Duration: 6.4s)", fill="#184C78", font=font_body, anchor="mm")

    draw.rectangle((800, 180, 1100, 280), fill="#E6F2FF", outline="#184C78", width=2)
    draw.text((950, 230), "image_03.jpg\n(Duration: 6.0s)", fill="#184C78", font=font_body, anchor="mm")

    # Audio Track A1
    draw.rectangle((50, 310, 180, 410), fill="#006400", outline="#FFFFFF")
    draw.text((115, 360), "Audio A1\n(Voice WAVs)", fill="#FFFFFF", font=font_header, anchor="mm")

    # Audio Clips on timeline
    draw.rectangle((200, 310, 480, 410), fill="#F0FFF0", outline="#006400", width=2)
    draw.text((340, 360), "segment_01.wav\n(5.6s mono PCM)", fill="#006400", font=font_body, anchor="mm")

    draw.rectangle((480, 310, 800, 410), fill="#F0FFF0", outline="#006400", width=2)
    draw.text((640, 360), "segment_02.wav\n(6.4s mono PCM)", fill="#006400", font=font_body, anchor="mm")

    draw.rectangle((800, 310, 1100, 410), fill="#F0FFF0", outline="#006400", width=2)
    draw.text((950, 360), "segment_03.wav\n(6.0s mono PCM)", fill="#006400", font=font_body, anchor="mm")

    # Visual sync indicator line
    draw.line((480, 150, 480, 440), fill="#DC143C", width=2, joint="miter")
    draw.line((800, 150, 800, 440), fill="#DC143C", width=2, joint="miter")
    draw.text((485, 430), "Sync Cut 1", fill="#DC143C", font=font_body)
    draw.text((805, 430), "Sync Cut 2", fill="#DC143C", font=font_body)

    img.save(output_path)
    print(f"Resolve timeline layout saved to: {output_path}")

if __name__ == "__main__":
    import os
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
            
    draw_rag_baseline("docs/rag_baseline.png", font_path)
    draw_clip_embedding_space("docs/clip_embedding_space.png", font_path)
    draw_resolve_timeline_structure("docs/resolve_timeline_structure.png", font_path)
