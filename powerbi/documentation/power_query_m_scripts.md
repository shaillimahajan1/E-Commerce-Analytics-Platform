# Power Query (M) Loading Scripts

This document provides ready-to-use Power Query M code for connecting Power BI Desktop to Google BigQuery or local export tables.

---

## 1. Connecting to Google BigQuery

In Power BI Desktop:
1. Click **Get Data** -> **Google BigQuery**.
2. Sign in with your corporate Google Account or Service Account.
3. Replace `#"your-gcp-project-id"` with your actual GCP Project ID.

### Query Template for `fct_orders`:
```powerquery
let
    Source = GoogleBigQuery.Database(),
    Project = Source{[Name="your-gcp-project-id"]}[Data],
    AnalyticsSchema = Project{[Name="ecommerce_analytics_marts"]}[Data],
    FctOrdersTable = AnalyticsSchema{[Name="fct_orders"]}[Data],
    #"Changed Types" = Table.TransformColumnTypes(FctOrdersTable,{
        {"order_id", type text},
        {"customer_id", type text},
        {"customer_unique_id", type text},
        {"order_purchase_date_key", Int64.Type},
        {"customer_city", type text},
        {"customer_state", type text},
        {"order_status", type text},
        {"order_purchase_timestamp", type datetimezone},
        {"gross_merchandise_value", type number},
        {"total_freight_value", type number},
        {"total_order_value", type number},
        {"total_payment_value", type number},
        {"actual_delivery_days", type number},
        {"estimated_delivery_days", type number},
        {"is_on_time", Int64.Type},
        {"is_late_delivery", Int64.Type}
    })
in
    #"Changed Types"
```

---

## 2. Connecting to Local Warehouse (DuckDB / ODBC / Parquet)

If validating or demonstrating the platform locally without live BigQuery access, export the curated marts to local Parquet files via `scripts/export_marts_for_powerbi.py`:

```python
# Run: python scripts/export_marts_for_powerbi.py
# Exports all marts tables to data/processed/*.parquet for immediate Power BI ingestion
```

### Power Query M Script for Local Parquet Ingestion (`fct_orders`):
```powerquery
let
    Source = Parquet.Document(File.Contents("D:\E-COMMERCE ANALYTICS PLATFORM\ecommerce-analytics-platform\data\processed\fct_orders.parquet")),
    #"Changed Types" = Table.TransformColumnTypes(Source,{
        {"order_id", type text},
        {"customer_unique_id", type text},
        {"order_purchase_date_key", Int64.Type},
        {"customer_state", type text},
        {"gross_merchandise_value", type number},
        {"total_freight_value", type number},
        {"total_order_value", type number},
        {"is_on_time", Int64.Type},
        {"is_late_delivery", Int64.Type}
    })
in
    #"Changed Types"
```
