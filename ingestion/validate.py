"""
Validation component of the Ingestion Pipeline.

Ensures incoming data conforms to expected contracts before warehouse loading:
- Expected column presence
- Non-empty row counts
- Parse validity
- Basic schema compatibility
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger("ingestion.validate")


class ValidationError(Exception):
    """Raised when validation constraints are violated."""
    pass


@dataclass
class ValidationResult:
    """Stores the outcome of dataset validation."""
    filename: str
    is_valid: bool
    row_count: int
    column_count: int
    present_columns: List[str]
    missing_columns: List[str]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class FileValidator:
    """Validates CSV files against predefined contract rules."""

    def __init__(self, file_path: Path, expected_columns: Optional[List[str]] = None, primary_key: Optional[List[str]] = None):
        self.file_path = Path(file_path)
        self.expected_columns = expected_columns or []
        self.primary_key = primary_key or []

    def validate(self, sample_size: Optional[int] = None) -> ValidationResult:
        """Runs validation checks on the CSV file."""
        errors = []
        warnings = []
        
        try:
            # Read header first
            header_df = pd.read_csv(self.file_path, nrows=0)
            actual_columns = list(header_df.columns)
        except Exception as e:
            errors.append(f"Failed to parse CSV header: {e}")
            return ValidationResult(
                filename=self.file_path.name,
                is_valid=False,
                row_count=0,
                column_count=0,
                present_columns=[],
                missing_columns=self.expected_columns,
                errors=errors
            )

        # Check for missing required columns
        missing_cols = [c for c in self.expected_columns if c not in actual_columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Check row count
        try:
            df = pd.read_csv(self.file_path, nrows=sample_size)
            row_count = len(df)
            col_count = len(df.columns)
            
            if row_count == 0:
                errors.append("File contains 0 records.")

            # Validate primary key nulls if PK columns exist
            if self.primary_key:
                for pk_col in self.primary_key:
                    if pk_col in df.columns:
                        null_pks = int(df[pk_col].isna().sum())
                        if null_pks > 0:
                            errors.append(f"Primary key column '{pk_col}' contains {null_pks} NULL values.")
                            
                        # If single PK, check uniqueness
                        if len(self.primary_key) == 1 and sample_size is None:
                            dups = int(df[pk_col].duplicated().sum())
                            if dups > 0:
                                warnings.append(f"Primary key column '{pk_col}' has {dups} duplicate values.")

        except Exception as e:
            errors.append(f"Failed to read dataset rows: {e}")
            row_count = 0
            col_count = len(actual_columns)

        is_valid = len(errors) == 0
        if is_valid:
            logger.info(f"Validation PASSED: {self.file_path.name} ({row_count:,} rows, {col_count} cols)")
        else:
            logger.error(f"Validation FAILED: {self.file_path.name} - Errors: {errors}")

        return ValidationResult(
            filename=self.file_path.name,
            is_valid=is_valid,
            row_count=row_count,
            column_count=col_count,
            present_columns=actual_columns,
            missing_columns=missing_cols,
            errors=errors,
            warnings=warnings
        )
