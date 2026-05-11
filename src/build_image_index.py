import json
import os
from pathlib import Path
from PIL import Image
import torch
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def build_index():
    print("Loading CLIP model (sentence-transformers/clip-ViT-B-32)...")
    # Sử dụng CLIP để có thể nhúng cả chữ và ảnh
    model = SentenceTransformer('clip-ViT-B-32')

    image_dir = Path("data/images")
    if not image_dir.exists():
        print(f"Directory {image_dir} not found!")
        return

    image_paths = []
    images = []

    print(f"Scanning images in {image_dir}...")
    for file_path in image_dir.glob("*.jpg"):
        try:
            img = Image.open(file_path)
            # Chỉ tải ảnh vào để encode, convert sang RGB
            images.append(img.convert("RGB"))
            image_paths.append(str(file_path.as_posix()))
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    if not images:
        print("No images found to index.")
        return

    print(f"Encoding {len(images)} images. This might take a while...")
    # Encode toàn bộ ảnh thành vector
    embeddings = model.encode(images, batch_size=32, show_progress_bar=True, convert_to_numpy=True)
    
    # Chuẩn hóa (Normalize) các vector để dùng Inner Product (giống Cosine Similarity)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    # Sử dụng Inner Product cho việc đo lường độ tương đồng cosine
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Lưu FAISS index
    index_path = image_dir / "faiss_index.bin"
    faiss.write_index(index, str(index_path))

    # Lưu danh sách map ID -> đường dẫn file
    paths_path = image_dir / "image_paths.json"
    with open(paths_path, "w", encoding="utf-8") as f:
        json.dump(image_paths, f, indent=2, ensure_ascii=False)

    print("--------------------------------------------------")
    print("THÀNH CÔNG RỰC RỠ! 🎉")
    print(f"Đã lập chỉ mục {len(image_paths)} hình ảnh.")
    print(f"- FAISS Index lưu tại: {index_path}")
    print(f"- Image Paths lưu tại: {paths_path}")
    print("Bây giờ hệ thống Tìm kiếm Ảnh bằng AI đã sẵn sàng!")

if __name__ == "__main__":
    build_index()
