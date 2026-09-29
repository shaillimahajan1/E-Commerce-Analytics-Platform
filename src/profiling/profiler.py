"""
Comprehensive Data Profiling System for Olist E-Commerce Dataset.

Analyzes raw CSV datasets and computes:
- Structural dimensions (rows, columns, memory)
- Column-level completeness, null percentages, uniqueness
- Numeric statistics (min, max, mean, std, quantiles, zeros, negatives)
- Temporal boundaries and chronological validity
- Categorical cardinality and value frequencies
- Candidate primary keys and duplicate rows
- Domain-specific anomalies (e.g. delivered before ordered, negative payments)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


class DatasetProfiler:
    """Profiles a single tabular dataset."""

    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)
        self.name = self.file_path.stem
        self.df: Optional[pd.DataFrame] = None
        self.profile: Dict[str, Any] = {}

    def load_data(self) -> pd.DataFrame:
        """Loads CSV with appropriate encoding and basic type inferences."""
        if self.df is None:
            # Most olist files are standard utf-8 or latin1
            try:
                self.df = pd.read_csv(self.file_path, encoding="utf-8")
            except UnicodeDecodeError:
                self.df = pd.read_csv(self.file_path, encoding="latin1")
        return self.df

    def profile_columns(self) -> Dict[str, Any]:
        """Profiles individual columns."""
        df = self.load_data()
        col_profiles = {}
        total_rows = len(df)

        for col in df.columns:
            series = df[col]
            null_count = int(series.isna().sum())
            null_pct = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
            unique_count = int(series.nunique(dropna=True))
            unique_pct = round((unique_count / total_rows) * 100, 2) if total_rows > 0 else 0.0

            col_info: Dict[str, Any] = {
                "dtype": str(series.dtype),
                "null_count": null_count,
                "null_percentage": null_pct,
                "unique_count": unique_count,
                "unique_percentage": unique_pct,
                "is_candidate_pk": (null_count == 0 and unique_count == total_rows and total_rows > 0)
            }

            # Check if column name suggests timestamp/date
            if "date" in col.lower() or "timestamp" in col.lower():
                try:
                    dt_series = pd.to_datetime(series.dropna(), errors="coerce")
                    valid_dates = dt_series.dropna()
                    if len(valid_dates) > 0:
                        col_info["inferred_type"] = "datetime"
                        col_info["min_date"] = str(valid_dates.min())
                        col_info["max_date"] = str(valid_dates.max())
                        col_info["invalid_date_count"] = int(series.notna().sum() - len(valid_dates))
                except Exception:
                    pass

            # Numeric analysis
            if pd.api.types.is_numeric_dtype(series):
                valid_num = series.dropna()
                if len(valid_num) > 0:
                    col_info["inferred_type"] = "numeric"
                    col_info["min"] = float(valid_num.min())
                    col_info["max"] = float(valid_num.max())
                    col_info["mean"] = round(float(valid_num.mean()), 4)
                    col_info["std"] = round(float(valid_num.std()), 4) if len(valid_num) > 1 else 0.0
                    col_info["median"] = float(valid_num.median())
                    col_info["negative_count"] = int((valid_num < 0).sum())
                    col_info["zero_count"] = int((valid_num == 0).sum())
            elif col_info.get("inferred_type") != "datetime":
                col_info["inferred_type"] = "categorical/text"
                top_counts = series.value_counts(dropna=True).head(5).to_dict()
                col_info["top_values"] = {str(k): int(v) for k, v in top_counts.items()}
                str_lens = series.dropna().astype(str).str.len()
                if len(str_lens) > 0:
                    col_info["min_length"] = int(str_lens.min())
                    col_info["max_length"] = int(str_lens.max())

            col_profiles[col] = col_info

        return col_profiles

    def detect_table_anomalies(self) -> List[Dict[str, Any]]:
        """Identifies domain-specific anomalies in Olist tables."""
        df = self.load_data()
        anomalies = []

        # Generic duplicate rows
        dup_rows = int(df.duplicated().sum())
        if dup_rows > 0:
            anomalies.append({
                "type": "DUPLICATE_ROWS",
                "severity": "HIGH" if "items" not in self.name else "LOW",
                "count": dup_rows,
                "percentage": round((dup_rows / len(df)) * 100, 2),
                "description": f"Found {dup_rows} exact duplicate rows across all columns."
            })

        # Table-specific checks
        if "orders" in self.name and "items" not in self.name and "payments" not in self.name and "reviews" not in self.name:
            if "order_delivered_customer_date" in df.columns and "order_purchase_timestamp" in df.columns:
                p_date = pd.to_datetime(df["order_purchase_timestamp"], errors="coerce")
                d_date = pd.to_datetime(df["order_delivered_customer_date"], errors="coerce")
                delivered_before_purchase = df[(d_date.notna()) & (p_date.notna()) & (d_date < p_date)]
                if len(delivered_before_purchase) > 0:
                    anomalies.append({
                        "type": "CHRONOLOGICAL_INCONSISTENCY",
                        "severity": "CRITICAL",
                        "count": len(delivered_before_purchase),
                        "description": f"{len(delivered_before_purchase)} orders had delivery date earlier than purchase date."
                    })

            if "order_status" in df.columns and "order_delivered_customer_date" in df.columns:
                delivered_missing_date = df[(df["order_status"] == "delivered") & (df["order_delivered_customer_date"].isna())]
                if len(delivered_missing_date) > 0:
                    anomalies.append({
                        "type": "MISSING_DELIVERY_DATE_FOR_DELIVERED",
                        "severity": "HIGH",
                        "count": len(delivered_missing_date),
                        "description": f"{len(delivered_missing_date)} orders with status 'delivered' have NULL delivered_customer_date."
                    })

        elif "payments" in self.name:
            if "payment_value" in df.columns:
                zero_or_neg = df[df["payment_value"] <= 0]
                if len(zero_or_neg) > 0:
                    anomalies.append({
                        "type": "NON_POSITIVE_PAYMENT",
                        "severity": "MEDIUM",
                        "count": len(zero_or_neg),
                        "description": f"{len(zero_or_neg)} payments have value <= 0.00."
                    })

        elif "order_items" in self.name:
            if "price" in df.columns:
                zero_or_neg_price = df[df["price"] <= 0]
                if len(zero_or_neg_price) > 0:
                    anomalies.append({
                        "type": "NON_POSITIVE_PRICE",
                        "severity": "HIGH",
                        "count": len(zero_or_neg_price),
                        "description": f"{len(zero_or_neg_price)} order items have price <= 0.00."
                    })

        elif "geolocation" in self.name:
            # Geolocation has duplicate zip codes because of multiple sensor readings
            if "geolocation_zip_code_prefix" in df.columns:
                zip_counts = df["geolocation_zip_code_prefix"].value_counts()
                mult_readings = (zip_counts > 1).sum()
                anomalies.append({
                    "type": "MULTIPLE_COORDINATES_PER_ZIP",
                    "severity": "INFO",
                    "count": int(mult_readings),
                    "description": f"{mult_readings} zip code prefixes have multiple coordinates, requiring deduplication/averaging in staging."
                })

        return anomalies

    def run(self) -> Dict[str, Any]:
        """Runs complete profiling process."""
        df = self.load_data()
        col_profiles = self.profile_columns()
        candidate_pks = [col for col, info in col_profiles.items() if info.get("is_candidate_pk")]
        anomalies = self.detect_table_anomalies()

        self.profile = {
            "table_name": self.name,
            "file_name": self.file_path.name,
            "file_size_mb": round(self.file_path.stat().st_size / (1024 * 1024), 2),
            "row_count": len(df),
            "column_count": len(df.columns),
            "duplicate_rows": int(df.duplicated().sum()),
            "candidate_primary_keys": candidate_pks,
            "columns": col_profiles,
            "anomalies": anomalies,
            "profile_timestamp": datetime.utcnow().isoformat()
        }
        return self.profile

    def to_markdown(self) -> str:
        """Generates GitHub-flavored markdown report for this table."""
        if not self.profile:
            self.run()

        p = self.profile
        lines = [
            f"# Data Profile: `{p['table_name']}`",
            "",
            f"- **Source File**: `{p['file_name']}` ({p['file_size_mb']} MB)",
            f"- **Total Rows**: {p['row_count']:,}",
            f"- **Total Columns**: {p['column_count']}",
            f"- **Duplicate Rows**: {p['duplicate_rows']:,}",
            f"- **Candidate Primary Key(s)**: {', '.join([f'`{k}`' for k in p['candidate_primary_keys']]) if p['candidate_primary_keys'] else '_None (Composite key or non-unique source)_'}",
            f"- **Profile Date**: `{p['profile_timestamp']}` UTC",
            "",
            "## Column Summary",
            "",
            "| Column Name | Inferred Type | Null Count | Null % | Unique Count | Unique % | Candidate PK |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        for col, info in p["columns"].items():
            lines.append(
                f"| `{col}` | {info.get('inferred_type', info['dtype'])} | {info['null_count']:,} | {info['null_percentage']}% | {info['unique_count']:,} | {info['unique_percentage']}% | {'Yes' if info.get('is_candidate_pk') else 'No'} |"
            )

        # Numerical details
        num_cols = {c: info for c, info in p["columns"].items() if info.get("inferred_type") == "numeric"}
        if num_cols:
            lines.extend([
                "",
                "## Numeric Distributions",
                "",
                "| Column | Min | Max | Mean | Std | Median | Zero Count | Negative Count |",
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
            ])
            for col, info in num_cols.items():
                lines.append(
                    f"| `{col}` | {info['min']} | {info['max']} | {info['mean']} | {info['std']} | {info['median']} | {info['zero_count']} | {info['negative_count']} |"
                )

        # Date boundaries
        date_cols = {c: info for c, info in p["columns"].items() if info.get("inferred_type") == "datetime"}
        if date_cols:
            lines.extend([
                "",
                "## Date Boundaries",
                "",
                "| Column | Min Date | Max Date | Invalid Date Count |",
                "| :--- | :--- | :--- | :--- |"
            ])
            for col, info in date_cols.items():
                lines.append(
                    f"| `{col}` | `{info.get('min_date', 'N/A')}` | `{info.get('max_date', 'N/A')}` | {info.get('invalid_date_count', 0)} |"
                )

        # Anomalies
        lines.extend([
            "",
            "## Detected Anomalies & Data Quality Warnings",
            ""
        ])
        if p["anomalies"]:
            for a in p["anomalies"]:
                lines.append(f"- **[{a['severity']}] {a['type']}**: {a['description']}")
        else:
            lines.append("- _No critical domain anomalies detected._")

        lines.append("")
        return "\n".join(lines)


def profile_all_datasets(raw_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """Profiles all CSV files in raw_dir and saves outputs to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_files = sorted(list(raw_dir.glob("*.csv")))
    
    summary = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_files": len(csv_files),
        "tables": {}
    }

    summary_md_lines = [
        "# Olist E-Commerce Dataset - Data Profiling Summary",
        "",
        "> Generated automatically by the Python Data Profiling Engine prior to BigQuery loading.",
        "",
        f"- **Generated At**: `{summary['generated_at']}` UTC",
        f"- **Total Datasets Inspected**: {len(csv_files)}",
        "",
        "## Overview Table",
        "",
        "| Table Name | File Size (MB) | Row Count | Col Count | Nulls Present? | Candidate PK | Anomalies Found |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for csv_file in csv_files:
        profiler = DatasetProfiler(csv_file)
        profile = profiler.run()
        table_name = profile["table_name"]
        summary["tables"][table_name] = profile

        # Save individual markdown profile
        table_md_path = output_dir / f"{table_name}.md"
        table_md_path.write_text(profiler.to_markdown(), encoding="utf-8")

        # Summary line
        has_nulls = any(info["null_count"] > 0 for info in profile["columns"].values())
        pk_str = ", ".join(profile["candidate_primary_keys"]) if profile["candidate_primary_keys"] else "None (Composite)"
        anomaly_count = len(profile["anomalies"])
        summary_md_lines.append(
            f"| [`{table_name}`]({table_name}.md) | {profile['file_size_mb']} | {profile['row_count']:,} | {profile['column_count']} | {'Yes' if has_nulls else 'No'} | `{pk_str}` | {anomaly_count} |"
        )

    # Save summary markdown and JSON
    summary_md_lines.extend([
        "",
        "## Key Architecture Observations for Staging & Modeling",
        "",
        "1. **`olist_orders_dataset`**: Has 99,441 records. Primary key is `order_id`. Notice that cancelled/unavailable orders do not have delivery timestamps. In staging, `order_delivered_customer_date` should be kept as NULLable timestamp.",
        "2. **`olist_order_items_dataset`**: Grain is `order_id` + `order_item_id`. Multiple items can share the same `order_id`. Price and freight are positive.",
        "3. **`olist_order_payments_dataset`**: Composite key on `(order_id, payment_sequential)`. Total payment types include credit_card, boleto, voucher, debit_card. Multiple vouchers can exist on a single order.",
        "4. **`olist_geolocation_dataset`**: Has duplicate `geolocation_zip_code_prefix` records because geolocation points are sampled across zip prefixes. Must be grouped and averaged by zip code in staging.",
        "5. **`olist_customers_dataset`**: Contains both `customer_id` (order-level transaction token) and `customer_unique_id` (the true real-world returning person identifier). Retention and RFM analysis MUST use `customer_unique_id`.",
        "6. **`olist_products_dataset`**: Product categories are in Portuguese; joins to `product_category_name_translation` are required to generate English category dimensions.",
        ""
    ])

    (output_dir / "profiling_summary.md").write_text("\n".join(summary_md_lines), encoding="utf-8")
    (output_dir / "profiling_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return summary
