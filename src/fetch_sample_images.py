import os
import json
import urllib.request
import ssl
import random

def fetch_sample_images():
    output_dir = "data/images"
    os.makedirs(output_dir, exist_ok=True)
    
    metadata_path = os.path.join(output_dir, "metadata.json")
    
    # Bypass SSL verification for MSYS python environments
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print("Fetching 100 sample images from Picsum API...")
    url = "https://picsum.photos/v2/list?page=1&limit=100"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching API: {e}")
        return

    metadata = []
    
    scenes = ["urban", "nature", "people", "technology", "abstract", "weather", "interior"]
    tones = ["neutral", "calm", "dramatic", "energetic", "melancholic", "inspirational"]
    all_tags = ["city", "street", "forest", "mountain", "ocean", "rain", "sunshine", "night", "desk", "coffee", "laptop", "crowd", "quiet", "fast", "future"]

    print(f"Downloading {len(data)} images...")
    for i, item in enumerate(data):
        # Resize to 800x600 for faster download
        download_url = f"https://picsum.photos/id/{item['id']}/800/600"
        filename = f"sample_{i+1:03d}.jpg"
        filepath = os.path.join(output_dir, filename)
        
        # Download image
        try:
            req_img = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_img, context=ctx) as response, open(filepath, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            print(f"Failed to download image {i+1}: {e}")
            continue
            
        # Generate random metadata tags
        scene = random.choice(scenes)
        tone = random.choice(tones)
        tags = random.sample(all_tags, k=random.randint(2, 5))
        
        metadata.append({
            "path": f"data/images/{filename}",
            "scene": scene,
            "tone": tone,
            "tags": tags
        })
        
        if (i+1) % 10 == 0:
            print(f"Downloaded {i+1}/100 images...")
            
    # Write metadata.json
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    print(f"\nSuccessfully downloaded images and created {metadata_path}")

if __name__ == "__main__":
    fetch_sample_images()
