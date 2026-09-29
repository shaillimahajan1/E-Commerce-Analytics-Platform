"""
Script to download the authentic Brazilian E-Commerce Public Dataset by Olist
Source: HuggingFace mirror of the official Olist Kaggle dataset.
"""

import os
import sys
import urllib.request
import urllib.parse
from pathlib import Path

DATA_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
]

BASE_URL = "https://huggingface.co/datasets/shawnzzzh/AgenticDataBench/resolve/main/datasets/ecommerce/Brazilian%20E-Commerce/"

def download_file(filename: str, target_dir: Path):
    target_path = target_dir / filename
    if target_path.exists() and target_path.stat().st_size > 0:
        print(f"[SKIP] {filename} already exists ({target_path.stat().st_size / (1024*1024):.2f} MB)")
        return True

    encoded_name = urllib.parse.quote(filename)
    url = BASE_URL + encoded_name
    print(f"[DOWNLOADING] {filename} from {url}...")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp, open(target_path, "wb") as out_file:
            content_length = resp.headers.get("Content-Length")
            total_size = int(content_length) if content_length else None
            downloaded = 0
            chunk_size = 64 * 1024
            
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    percent = (downloaded / total_size) * 100
                    sys.stdout.write(f"\r  -> {percent:.1f}% ({downloaded / (1024*1024):.2f} MB)")
                    sys.stdout.flush()
            print(f"\n[DONE] {filename} saved successfully ({target_path.stat().st_size / (1024*1024):.2f} MB)")
            return True
    except Exception as e:
        print(f"\n[ERROR] Failed to download {filename}: {e}")
        if target_path.exists():
            target_path.unlink()
        return False

def main():
    repo_root = Path(__file__).resolve().parent.parent
    raw_dir = repo_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Target directory: {raw_dir}")
    print(f"Downloading {len(DATA_FILES)} Olist dataset files...\n")
    
    success_count = 0
    for filename in DATA_FILES:
        if download_file(filename, raw_dir):
            success_count += 1
            
    print(f"\n==========================================")
    print(f"Downloaded {success_count}/{len(DATA_FILES)} files successfully.")
    print(f"==========================================")
    
    if success_count < len(DATA_FILES):
        sys.exit(1)

if __name__ == "__main__":
    main()
