"""
Unit tests for data extraction and warehouse loading components.
"""

import hashlib
import tempfile
from pathlib import Path
import duckdb
import pytest

from ingestion.extract import FileExtractor, ExtractionError
from ingestion.load import WarehouseLoader


@pytest.fixture
def temp_raw_dir(tmp_path):
    """Creates temporary directory with mock raw files."""
    f1 = tmp_path / "mock_customers.csv"
    f1.write_text("customer_id,customer_state\nc1,SP\nc2,RJ\n", encoding="utf-8")
    return tmp_path


def test_file_extractor_discovery(temp_raw_dir):
    extractor = FileExtractor(raw_dir=temp_raw_dir, expected_files=["mock_customers.csv"])
    meta = extractor.extract_all()
    assert "mock_customers.csv" in meta
    assert meta["mock_customers.csv"]["size_bytes"] > 0
    assert len(meta["mock_customers.csv"]["sha256"]) == 64


def test_file_extractor_missing_file_raises_error(temp_raw_dir):
    extractor = FileExtractor(raw_dir=temp_raw_dir, expected_files=["missing_file.csv"])
    with pytest.raises(ExtractionError):
        extractor.extract_all()


def test_file_extractor_empty_file_raises_error(temp_raw_dir):
    empty_file = temp_raw_dir / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    extractor = FileExtractor(raw_dir=temp_raw_dir, expected_files=["empty.csv"])
    with pytest.raises(ExtractionError):
        extractor.extract_all()


def test_warehouse_loader_local(tmp_path):
    db_file = tmp_path / "test_warehouse.duckdb"
    csv_file = tmp_path / "test_orders.csv"
    csv_file.write_text("order_id,status,val\no1,delivered,10.5\no2,shipped,20.0\n", encoding="utf-8")

    loader = WarehouseLoader(raw_dataset="test_raw", local_db_path=db_file)
    res = loader.load_to_local_warehouse(file_path=csv_file, table_name="raw_orders", dataset_name="orders")

    assert res["status"] == "SUCCESS"
    assert res["row_count"] == 2

    # Verify audit row
    with duckdb.connect(str(db_file)) as conn:
        audit_rows = conn.execute("SELECT dataset_name, row_count, status FROM test_raw.raw_ingestion_audit").fetchall()
        assert len(audit_rows) == 1
        assert audit_rows[0][0] == "orders"
        assert audit_rows[0][1] == 2
        assert audit_rows[0][2] == "SUCCESS"
