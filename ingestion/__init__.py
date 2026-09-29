"""
Ingestion package for E-Commerce Analytics Platform.
"""

from ingestion.extract import FileExtractor
from ingestion.validate import FileValidator, ValidationResult
from ingestion.load import WarehouseLoader
from ingestion.pipeline import IngestionPipeline

__all__ = [
    "FileExtractor",
    "FileValidator",
    "ValidationResult",
    "WarehouseLoader",
    "IngestionPipeline",
]
