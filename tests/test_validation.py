"""
Unit tests for data validation component.
"""

from pathlib import Path
import pytest
from ingestion.validate import FileValidator


def test_validator_valid_schema(tmp_path):
    f = tmp_path / "valid.csv"
    f.write_text("order_id,customer_id,status\nord_1,cust_1,delivered\nord_2,cust_2,shipped\n", encoding="utf-8")

    validator = FileValidator(
        file_path=f,
        expected_columns=["order_id", "customer_id"],
        primary_key=["order_id"]
    )
    res = validator.validate()
    assert res.is_valid is True
    assert res.row_count == 2
    assert len(res.errors) == 0


def test_validator_missing_column(tmp_path):
    f = tmp_path / "missing_col.csv"
    f.write_text("order_id,status\nord_1,delivered\n", encoding="utf-8")

    validator = FileValidator(
        file_path=f,
        expected_columns=["order_id", "customer_id"],
        primary_key=["order_id"]
    )
    res = validator.validate()
    assert res.is_valid is False
    assert "customer_id" in res.missing_columns
    assert any("Missing required columns" in err for err in res.errors)


def test_validator_primary_key_null(tmp_path):
    f = tmp_path / "null_pk.csv"
    f.write_text("order_id,customer_id\n,cust_1\nord_2,cust_2\n", encoding="utf-8")

    validator = FileValidator(
        file_path=f,
        expected_columns=["order_id", "customer_id"],
        primary_key=["order_id"]
    )
    res = validator.validate()
    assert res.is_valid is False
    assert any("contains 1 NULL values" in err for err in res.errors)


def test_validator_empty_csv(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("order_id,customer_id\n", encoding="utf-8")

    validator = FileValidator(
        file_path=f,
        expected_columns=["order_id", "customer_id"],
        primary_key=["order_id"]
    )
    res = validator.validate()
    assert res.is_valid is False
    assert any("0 records" in err for err in res.errors)
