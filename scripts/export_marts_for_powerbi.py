"""
Exports all curated dbt marts tables from the warehouse to Parquet
files under data/processed/ for seamless, high-speed Power BI Desktop ingestion.
"""

from pathlib import Path
import duckdb

def export_marts():
    repo_root = Path(__file__).resolve().parent.parent
    db_path = repo_root / "data" / "processed" / "ecommerce_warehouse.duckdb"
    output_dir = repo_root / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not db_path.exists():
        print(f"[ERROR] Warehouse database does not exist at: {db_path}")
        return

    marts_tables = [
        "dim_date",
        "dim_customer",
        "dim_product",
        "dim_seller",
        "dim_location",
        "fct_orders",
        "fct_order_items",
        "fct_payments",
        "fct_reviews",
        "fct_delivery",
        "mart_sales_monthly",
        "mart_customer_retention",
        "mart_seller_performance",
        "mart_product_performance"
    ]

    print(f"Connecting to {db_path}...")
    with duckdb.connect(str(db_path)) as conn:
        for tbl in marts_tables:
            out_file = output_dir / f"{tbl}.parquet"
            conn.execute(f"""
                COPY ecommerce_analytics_marts.{tbl} 
                TO '{out_file.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD);
            """)
            size_mb = out_file.stat().st_size / (1024 * 1024)
            print(f"[EXPORTED] ecommerce_analytics_marts.{tbl:<25} -> {tbl}.parquet ({size_mb:.2f} MB)")

    print("\nAll dimensional marts exported to Parquet for Power BI Desktop successfully.")

if __name__ == "__main__":
    export_marts()
