"""
Extraction component of the Ingestion Pipeline.

Responsible for:
- Discovering expected source files in data/raw
- Generating cryptographic checksums (SHA-256) for audit traceability
- Validating file presence and non-zero byte size
- Collecting file system metadata
"""

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.utils.logger import get_logger

logger = get_logger("ingestion.extract")


class ExtractionError(Exception):
    """Raised when extraction discovery fails."""
    pass


class FileExtractor:
    """Discovers and inspects input files."""

    def __init__(self, raw_dir: Path, expected_files: Optional[List[str]] = None):
        self.raw_dir = Path(raw_dir)
        self.expected_files = expected_files or []

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        """Calculates SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def inspect_file(self, filename: str) -> Dict[str, Any]:
        """Inspects a single file and extracts its metadata."""
        file_path = self.raw_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Required source file not found: {file_path}")

        file_size = file_path.stat().st_size
        if file_size == 0:
            raise ExtractionError(f"Source file is empty (0 bytes): {file_path}")

        checksum = self.compute_sha256(file_path)

        return {
            "filename": filename,
            "path": str(file_path.resolve()),
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "sha256": checksum,
            "modified_time": file_path.stat().st_mtime
        }

    def extract_all(self) -> Dict[str, Dict[str, Any]]:
        """Discovers and validates all expected files."""
        logger.info(f"Scanning raw landing directory: {self.raw_dir}")
        if not self.raw_dir.exists():
            raise FileNotFoundError(f"Raw landing directory does not exist: {self.raw_dir}")

        extracted_metadata = {}
        missing_files = []

        for expected in self.expected_files:
            try:
                meta = self.inspect_file(expected)
                extracted_metadata[expected] = meta
                logger.info(f"Discovered: {expected} ({meta['size_mb']} MB, SHA: {meta['sha256'][:10]}...)")
            except (FileNotFoundError, ExtractionError) as e:
                logger.error(str(e))
                missing_files.append(expected)

        if missing_files:
            raise ExtractionError(f"Missing or invalid required source files: {missing_files}")

        logger.info(f"Successfully extracted metadata for {len(extracted_metadata)} source files.")
        return extracted_metadata
