"""
Load component of the Ingestion Pipeline.

Responsible for:
- Loading validated source files into the Raw Data Layer
- Supporting production Google BigQuery (with schema auto-detection / explicit schemas)
- Supporting embedded DuckDB warehouse for local development and CI/CD verification
- Writing persistent audit logs to 'raw_ingestion_audit'
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import duckdb
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger("ingestion.load")


class WarehouseLoader:
    """Manages raw dataset loading and audit logging."""

    def __init__(
        self,
        gcp_project_id: Optional[str] = None,
        raw_dataset: str = "ecommerce_raw",
        local_db_path: Optional[Path] = None
    ):
        self.gcp_project_id = gcp_project_id or os.getenv("GCP_PROJECT_ID")
        self.raw_dataset = raw_dataset
        self.local_db_path = local_db_path or Path("data/processed/ecommerce_warehouse.duckdb")
        self.local_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if BigQuery credentials and project exist
        self.has_bq_creds = bool(
            self.gcp_project_id and 
            (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_CLOUD_PROJECT"))
        )

    def _init_local_audit_table(self, conn: duckdb.DuckDBPyConnection):
        """Initializes raw_ingestion_audit in the local warehouse."""
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.raw_dataset};")
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.raw_dataset}.raw_ingestion_audit (
                audit_id VARCHAR PRIMARY KEY,
                dataset_name VARCHAR NOT NULL,
                source_file VARCHAR NOT NULL,
                load_timestamp TIMESTAMP NOT NULL,
                row_count BIGINT NOT NULL,
                status VARCHAR NOT NULL,
                error_message VARCHAR,
                execution_time_seconds DOUBLE NOT NULL
            );
        """)

    def load_to_local_warehouse(self, file_path: Path, table_name: str, dataset_name: str) -> Dict[str, Any]:
        """Loads CSV directly into local embedded warehouse with audit tracking."""
        start_time = time.time()
        audit_id = f"aud_{dataset_name}_{int(time.time()*1000)}"
        timestamp = datetime.utcnow()
        status = "SUCCESS"
        error_msg = None
        row_count = 0

        logger.info(f"Loading '{file_path.name}' into local warehouse table '{self.raw_dataset}.{table_name}'...")
        
        try:
            with duckdb.connect(str(self.local_db_path)) as conn:
                self._init_local_audit_table(conn)
                
                # Load CSV into raw table
                # We use read_csv_auto with all VARCHAR or auto detection for raw fidelity
                conn.execute(f"""
                    CREATE OR REPLACE TABLE {self.raw_dataset}.{table_name} AS 
                    SELECT * FROM read_csv_auto('{file_path.as_posix()}', all_varchar=False);
                """)
                
                row_count = conn.execute(f"SELECT COUNT(*) FROM {self.raw_dataset}.{table_name};").fetchone()[0]
                exec_time = round(time.time() - start_time, 3)

                # Record audit
                conn.execute(f"""
                    INSERT INTO {self.raw_dataset}.raw_ingestion_audit 
                    VALUES ('{audit_id}', '{dataset_name}', '{file_path.name}', '{timestamp.isoformat()}', {row_count}, '{status}', NULL, {exec_time});
                """)
                
            logger.info(f"[SUCCESS] Loaded {row_count:,} rows into {self.raw_dataset}.{table_name} in {exec_time}s.")
            return {
                "audit_id": audit_id,
                "dataset_name": dataset_name,
                "table_name": f"{self.raw_dataset}.{table_name}",
                "status": status,
                "row_count": row_count,
                "execution_time_seconds": exec_time,
                "target": "local_duckdb"
            }

        except Exception as e:
            status = "FAILED"
            error_msg = str(e)
            exec_time = round(time.time() - start_time, 3)
            logger.error(f"[FAILED] Failed to load {file_path.name}: {error_msg}")
            
            with duckdb.connect(str(self.local_db_path)) as conn:
                self._init_local_audit_table(conn)
                conn.execute(f"""
                    INSERT INTO {self.raw_dataset}.raw_ingestion_audit 
                    VALUES ('{audit_id}', '{dataset_name}', '{file_path.name}', '{timestamp.isoformat()}', 0, '{status}', '{error_msg.replace("'", "''")}', {exec_time});
                """)
                
            raise RuntimeError(f"Ingestion failed for {dataset_name}: {error_msg}") from e

    def load_to_bigquery(self, file_path: Path, table_name: str, dataset_name: str) -> Dict[str, Any]:
        """Loads CSV to Google BigQuery."""
        from google.cloud import bigquery
        
        start_time = time.time()
        timestamp = datetime.utcnow()
        audit_id = f"aud_{dataset_name}_{int(time.time()*1000)}"
        
        client = bigquery.Client(project=self.gcp_project_id)
        table_ref = f"{self.gcp_project_id}.{self.raw_dataset}.{table_name}"
        audit_ref = f"{self.gcp_project_id}.{self.raw_dataset}.raw_ingestion_audit"
        
        logger.info(f"Loading '{file_path.name}' into BigQuery table '{table_ref}'...")
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        try:
            with open(file_path, "rb") as source_file:
                load_job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
                load_job.result()  # Wait for job to finish
                
            destination_table = client.get_table(table_ref)
            row_count = destination_table.num_rows
            exec_time = round(time.time() - start_time, 3)
            
            # Record audit row in BigQuery
            audit_rows = [{
                "audit_id": audit_id,
                "dataset_name": dataset_name,
                "source_file": file_path.name,
                "load_timestamp": timestamp.isoformat(),
                "row_count": row_count,
                "status": "SUCCESS",
                "error_message": None,
                "execution_time_seconds": exec_time
            }]
            client.insert_rows_json(audit_ref, audit_rows)
            
            logger.info(f"[SUCCESS] Loaded {row_count:,} rows into BigQuery {table_ref} in {exec_time}s.")
            return {
                "audit_id": audit_id,
                "dataset_name": dataset_name,
                "table_name": table_ref,
                "status": "SUCCESS",
                "row_count": row_count,
                "execution_time_seconds": exec_time,
                "target": "bigquery"
            }
        except Exception as e:
            exec_time = round(time.time() - start_time, 3)
            logger.error(f"[FAILED] BigQuery load failed for {file_path.name}: {e}")
            raise

    def load_dataset(self, file_path: Path, table_name: str, dataset_name: str) -> Dict[str, Any]:
        """Loads to BigQuery if credentials available, otherwise local warehouse."""
        if self.has_bq_creds:
            try:
                return self.load_to_bigquery(file_path, table_name, dataset_name)
            except Exception as e:
                logger.warning(f"BigQuery load failed ({e}). Falling back to local warehouse loading.")
                return self.load_to_local_warehouse(file_path, table_name, dataset_name)
        else:
            return self.load_to_local_warehouse(file_path, table_name, dataset_name)
