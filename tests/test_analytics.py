"""
Unit tests for analytics logic, dimensional marts, and reconciliation.
"""

from pathlib import Path
import duckdb
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "processed" / "ecommerce_warehouse.duckdb"


@pytest.fixture(scope="module")
def db_conn():
    """Provides connection to local analytical warehouse."""
    if not DB_PATH.exists():
        pytest.skip("Warehouse database not found. Run ingestion & dbt first.")
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    yield conn
    conn.close()


def test_order_reconciliation_exact_match(db_conn):
    """Verifies that raw, staging, and facts order counts match exactly."""
    raw_count = db_conn.execute("SELECT count(*) FROM ecommerce_raw.raw_orders;").fetchone()[0]
    stg_count = db_conn.execute("SELECT count(*) FROM ecommerce_analytics_staging.stg_orders;").fetchone()[0]
    fct_count = db_conn.execute("SELECT count(*) FROM ecommerce_analytics_marts.fct_orders;").fetchone()[0]

    assert raw_count == stg_count
    assert stg_count == fct_count
    assert fct_count == 99441


def test_payment_reconciliation_exact_cents(db_conn):
    """Verifies that total payment amounts match down to the exact cent across layers."""
    raw_val = db_conn.execute("SELECT round(sum(cast(payment_value as double)), 2) FROM ecommerce_raw.raw_payments;").fetchone()[0]
    stg_val = db_conn.execute("SELECT round(sum(payment_value), 2) FROM ecommerce_analytics_staging.stg_payments;").fetchone()[0]
    fct_val = db_conn.execute("SELECT round(sum(payment_value), 2) FROM ecommerce_analytics_marts.fct_payments;").fetchone()[0]

    assert abs(raw_val - stg_val) < 0.01
    assert abs(stg_val - fct_val) < 0.01
    assert fct_val == 16008872.12


def test_no_orphan_order_items(db_conn):
    """Verifies referential integrity between fct_order_items and fct_orders."""
    orphan_count = db_conn.execute("""
        SELECT count(*) 
        FROM ecommerce_analytics_marts.fct_order_items i
        LEFT JOIN ecommerce_analytics_marts.fct_orders o ON i.order_id = o.order_id
        WHERE o.order_id IS NULL;
    """).fetchone()[0]

    assert orphan_count == 0


def test_chronological_delivery_validity(db_conn):
    """Verifies delivery timestamps occur on or after purchase timestamps."""
    inversions = db_conn.execute("""
        SELECT count(*) 
        FROM ecommerce_analytics_marts.fct_orders
        WHERE order_delivered_customer_date IS NOT NULL
          AND order_purchase_timestamp IS NOT NULL
          AND order_delivered_customer_date < order_purchase_timestamp;
    """).fetchone()[0]

    assert inversions == 0


def test_rfm_segments_non_empty(db_conn):
    """Verifies RFM segmentation assigns all customers to valid segments."""
    segments = db_conn.execute("""
        SELECT distinct rfm_segment 
        FROM ecommerce_analytics_marts.dim_customer;
    """).fetchall()
    
    seg_names = [s[0] for s in segments]
    assert "Champions" in seg_names
    assert "Loyal Customers" in seg_names
    assert "Recent Customers" in seg_names
    assert len(seg_names) >= 5


def test_delivery_sla_binary_flags(db_conn):
    """Verifies that on-time and late delivery flags are mutually exclusive and binary."""
    invalid_flags = db_conn.execute("""
        SELECT count(*) 
        FROM ecommerce_analytics_marts.fct_delivery
        WHERE is_on_time + is_late_delivery != 1;
    """).fetchone()[0]

    assert invalid_flags == 0
