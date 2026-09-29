"""
End-to-End Orchestrated Ingestion Pipeline.

Executes the four-stage ingestion workflow:
1. Extract (discover source files, compute SHA256 checksums)
2. Validate (validate schemas, row counts, and primary key nulls)
3. Load (load to raw warehouse dataset)
4. Audit (verify audit log entries)
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml
from dotenv import load_dotenv

from ingestion.extract import FileExtractor
from ingestion.validate import FileValidator
from ingestion.load import WarehouseLoader
from src.utils.logger import get_logger

# Load environment variables if .env exists
load_dotenv()
logger = get_logger("ingestion.pipeline")


class IngestionPipeline:
    """Coordinates extract, validate, load, and audit steps."""

    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.repo_root = self.config_path.resolve().parent.parent
        self.raw_dir = self.repo_root / self.config["storage"]["raw_dir"]
        self.tables_cfg = self.config.get("tables", {})
        self.loader = WarehouseLoader(
            raw_dataset=self.config["gcp"]["datasets"]["raw"],
            local_db_path=self.repo_root / self.config["storage"]["local_db_path"]
        )

    def run(self, selected_dataset: Optional[str] = None, dry_run: bool = False) -> bool:
        """Executes the pipeline."""
        logger.info("==================================================================")
        logger.info("Starting E-Commerce Raw Ingestion Pipeline (ELT Stage 1)")
        logger.info("==================================================================")

        datasets_to_run = (
            {selected_dataset: self.tables_cfg[selected_dataset]}
            if selected_dataset and selected_dataset in self.tables_cfg
            else self.tables_cfg
        )

        expected_filenames = [cfg["source_file"] for cfg in datasets_to_run.values()]

        # -------------------------------------------------------------
        # STAGE 1: EXTRACT
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 1/4: EXTRACT] Discovering & Inspecting Source Files ---")
        extractor = FileExtractor(raw_dir=self.raw_dir, expected_files=expected_filenames)
        try:
            extracted_meta = extractor.extract_all()
        except Exception as e:
            logger.critical(f"Extraction failed: {e}")
            return False

        # -------------------------------------------------------------
        # STAGE 2: VALIDATE
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 2/4: VALIDATE] Verifying Schema Contracts & Quality ---")
        validation_results = {}
        has_validation_failures = False

        for dataset_key, cfg in datasets_to_run.items():
            source_file = self.raw_dir / cfg["source_file"]
            validator = FileValidator(
                file_path=source_file,
                expected_columns=cfg.get("expected_columns"),
                primary_key=cfg.get("primary_key")
            )
            res = validator.validate()
            validation_results[dataset_key] = res
            if not res.is_valid:
                has_validation_failures = True

        if has_validation_failures:
            logger.critical("Validation stage encountered blocking errors. Aborting load.")
            return False

        if dry_run:
            logger.info("\n[DRY RUN COMPLETED] All extract and validation checks passed successfully.")
            return True

        # -------------------------------------------------------------
        # STAGE 3: LOAD
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 3/4: LOAD] Loading Raw Datasets into Warehouse ---")
        load_summary = []
        has_load_failures = False

        for dataset_key, cfg in datasets_to_run.items():
            source_file = self.raw_dir / cfg["source_file"]
            raw_table_name = cfg["raw_table"]
            try:
                res = self.loader.load_dataset(
                    file_path=source_file,
                    table_name=raw_table_name,
                    dataset_name=dataset_key
                )
                load_summary.append(res)
            except Exception as e:
                logger.error(f"Failed to load dataset '{dataset_key}': {e}")
                has_load_failures = True

        if has_load_failures:
            logger.critical("Load stage encountered errors.")
            return False

        # -------------------------------------------------------------
        # STAGE 4: AUDIT SUMMARY
        # -------------------------------------------------------------
        logger.info("\n--- [STAGE 4/4: AUDIT] Ingestion Audit Verification ---")
        logger.info(f"{'Dataset':<22} | {'Table':<30} | {'Status':<8} | {'Rows Loaded':<12} | {'Time (s)':<8}")
        logger.info("-" * 88)
        total_rows = 0
        for item in load_summary:
            total_rows += item["row_count"]
            logger.info(
                f"{item['dataset_name']:<22} | {item['table_name']:<30} | {item['status']:<8} | {item['row_count']:<12,d} | {item['execution_time_seconds']:<8.2f}"
            )
        logger.info("-" * 88)
        logger.info(f"Total Rows Ingested: {total_rows:,} across {len(load_summary)} raw tables.")
        logger.info("==================================================================")
        logger.info("Ingestion Pipeline Completed Successfully.")
        logger.info("==================================================================")
        return True


def main():
    parser = argparse.ArgumentParser(description="E-Commerce Analytics Platform Ingestion Pipeline")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to pipeline configuration YAML file"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="Optional single dataset name to ingest (e.g. orders, customers)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execute extract and validate stages without loading to warehouse"
    )

    args = parser.parse_args()
    pipeline = IngestionPipeline(config_path=Path(args.config))
    success = pipeline.run(selected_dataset=args.dataset, dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
