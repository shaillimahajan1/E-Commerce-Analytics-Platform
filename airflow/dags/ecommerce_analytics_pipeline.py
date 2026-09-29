"""
Airflow Orchestration Pipeline for E-Commerce Analytics Platform.

Pipeline Topology:
start
  ↓
check_source_files (Inspect landing zone and verify SHA256 checksums)
  ↓
validate_source (Validate schema contracts and primary key nulls)
  ↓
ingest_to_raw (Batch load into Raw layer and write to raw_ingestion_audit)
  ↓
run_dbt_staging (Execute dbt staging views)
  ↓
run_dbt_intermediate (Execute dbt intermediate business transformations)
  ↓
run_dbt_marts (Execute dbt dimensional marts and fact tables)
  ↓
run_dbt_tests (Execute all 100+ generic and custom business rule tests)
  ↓
run_analytics_validation (Run metric reconciliation and financial consistency checks)
  ↓
finish
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to sys.path for Airflow workers
AIRFLOW_HOME = Path(os.environ.get("AIRFLOW_HOME", "/opt/airflow"))
if str(AIRFLOW_HOME) not in sys.path:
    sys.path.insert(0, str(AIRFLOW_HOME))

from airflow import DAG
try:
    from airflow.operators.empty import EmptyOperator
except ImportError:
    from airflow.operators.dummy import DummyOperator as EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Default task arguments
default_args = {
    "owner": "analytics_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
    "execution_timeout": timedelta(minutes=45)
}


def task_check_source_files(**context):
    """Verifies that all expected Olist dataset files exist and are non-empty."""
    from ingestion.extract import FileExtractor
    
    raw_dir = AIRFLOW_HOME / "data" / "raw"
    expected_files = [
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
    
    extractor = FileExtractor(raw_dir=raw_dir, expected_files=expected_files)
    meta = extractor.extract_all()
    print(f"[Airflow] Extraction check passed for {len(meta)} files.")
    return list(meta.keys())


def task_validate_source(**context):
    """Executes schema contract checks and PK null validation."""
    from ingestion.pipeline import IngestionPipeline
    
    config_path = AIRFLOW_HOME / "config" / "config.yaml"
    pipeline = IngestionPipeline(config_path=config_path)
    success = pipeline.run(dry_run=True)
    if not success:
        raise ValueError("Source data contract validation failed.")
    print("[Airflow] Source validation passed successfully.")


def task_ingest_to_raw(**context):
    """Loads raw data into warehouse and creates audit log records."""
    from ingestion.pipeline import IngestionPipeline
    
    config_path = AIRFLOW_HOME / "config" / "config.yaml"
    pipeline = IngestionPipeline(config_path=config_path)
    success = pipeline.run(dry_run=False)
    if not success:
        raise RuntimeError("Raw ingestion pipeline stage failed.")
    print("[Airflow] Ingestion to raw layer and audit logging completed.")


def task_analytics_validation(**context):
    """Runs post-dbt financial and metric reconciliation checks."""
    import duckdb
    
    db_path = AIRFLOW_HOME / "data" / "processed" / "ecommerce_warehouse.duckdb"
    if not db_path.exists():
        print(f"[Airflow] Warehouse db not found locally at {db_path}. Skipping local reconciliation check.")
        return True

    with duckdb.connect(str(db_path)) as conn:
        # Reconciliation Check 1: Orders count integrity between staging and marts
        stg_orders = conn.execute("SELECT count(*) FROM ecommerce_analytics_staging.stg_orders;").fetchone()[0]
        fct_orders = conn.execute("SELECT count(*) FROM ecommerce_analytics_marts.fct_orders;").fetchone()[0]
        print(f"[Reconciliation] Staging orders: {stg_orders:,} | Fact orders: {fct_orders:,}")
        if stg_orders != fct_orders:
            raise ValueError(f"Discrepancy detected: Staging orders ({stg_orders}) != Fact orders ({fct_orders})")

        # Reconciliation Check 2: Total item price integrity
        stg_item_val = conn.execute("SELECT round(sum(price), 2) FROM ecommerce_analytics_staging.stg_order_items;").fetchone()[0]
        fct_item_val = conn.execute("SELECT round(sum(item_price), 2) FROM ecommerce_analytics_marts.fct_order_items;").fetchone()[0]
        print(f"[Reconciliation] Staging GMV: R${stg_item_val:,.2f} | Fact GMV: R${fct_item_val:,.2f}")
        if abs(stg_item_val - fct_item_val) > 0.01:
            raise ValueError(f"Financial discrepancy: Staging GMV ({stg_item_val}) != Fact GMV ({fct_item_val})")

    print("[Airflow] All analytical reconciliation checks PASSED.")
    return True


with DAG(
    dag_id="ecommerce_analytics_pipeline",
    default_args=default_args,
    description="End-to-End ELT, dbt transformation, quality testing, and analytics reconciliation",
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["ecommerce", "elt", "dbt", "analytics", "production"]
) as dag:

    start = EmptyOperator(
        task_id="start"
    )

    check_source_files = PythonOperator(
        task_id="check_source_files",
        python_callable=task_check_source_files
    )

    validate_source = PythonOperator(
        task_id="validate_source",
        python_callable=task_validate_source
    )

    ingest_to_raw = PythonOperator(
        task_id="ingest_to_raw",
        python_callable=task_ingest_to_raw
    )

    run_dbt_staging = BashOperator(
        task_id="run_dbt_staging",
        bash_command="cd /opt/airflow/dbt && dbt run --select staging --profiles-dir .",
        env={"DBT_PROFILES_DIR": "/opt/airflow/dbt"}
    )

    run_dbt_intermediate = BashOperator(
        task_id="run_dbt_intermediate",
        bash_command="cd /opt/airflow/dbt && dbt run --select intermediate --profiles-dir .",
        env={"DBT_PROFILES_DIR": "/opt/airflow/dbt"}
    )

    run_dbt_marts = BashOperator(
        task_id="run_dbt_marts",
        bash_command="cd /opt/airflow/dbt && dbt run --select marts --profiles-dir .",
        env={"DBT_PROFILES_DIR": "/opt/airflow/dbt"}
    )

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command="cd /opt/airflow/dbt && dbt test --profiles-dir .",
        env={"DBT_PROFILES_DIR": "/opt/airflow/dbt"}
    )

    run_analytics_validation = PythonOperator(
        task_id="run_analytics_validation",
        python_callable=task_analytics_validation
    )

    finish = EmptyOperator(
        task_id="finish"
    )

    # Topology pipeline dependencies
    start >> check_source_files >> validate_source >> ingest_to_raw
    ingest_to_raw >> run_dbt_staging >> run_dbt_intermediate >> run_dbt_marts
    run_dbt_marts >> run_dbt_tests >> run_analytics_validation >> finish
