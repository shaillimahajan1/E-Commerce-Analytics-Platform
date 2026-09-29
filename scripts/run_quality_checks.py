"""
CLI Runner to execute Data Quality Framework and write docs/data-quality/quality.md
"""

import json
import sys
from pathlib import Path

# Add project root to sys.path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from src.validation.quality_checker import DataQualityFramework


def main():
    db_path = repo_root / "data" / "processed" / "ecommerce_warehouse.duckdb"
    output_dir = repo_root / "docs" / "data-quality"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to warehouse: {db_path}")
    if not db_path.exists():
        print(f"[ERROR] Database does not exist: {db_path}")
        sys.exit(1)

    checker = DataQualityFramework(db_path=db_path)
    results = checker.run_checks()
    
    # Save markdown and json reports
    md_content = checker.generate_markdown_report(results)
    (output_dir / "quality.md").write_text(md_content, encoding="utf-8")
    (output_dir / "quality_report.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    s = results["summary"]
    print(f"\n[DATA QUALITY RESULTS]")
    print(f"Total Checks: {s['total_checks']} | Passed: {s['passed']} | Warnings: {s['warned']} | Failed: {s['failed']}")
    print(f"Report generated: {output_dir / 'quality.md'}")

    if s["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
