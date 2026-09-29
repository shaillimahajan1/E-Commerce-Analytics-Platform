"""
CLI Runner to profile all Olist datasets and write docs to docs/data-profiling/
"""

import sys
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from src.profiling.profiler import profile_all_datasets

def main():
    raw_dir = repo_root / "data" / "raw"
    output_dir = repo_root / "docs" / "data-profiling"
    
    print(f"Starting dataset profiling...")
    print(f"  Source directory : {raw_dir}")
    print(f"  Output directory : {output_dir}\n")
    
    if not raw_dir.exists():
        print(f"[ERROR] Raw data directory does not exist: {raw_dir}")
        sys.exit(1)
        
    summary = profile_all_datasets(raw_dir, output_dir)
    print(f"\n[SUCCESS] Profiled {summary['total_files']} datasets.")
    print(f"Profiling documentation generated in: {output_dir}")

if __name__ == "__main__":
    main()
