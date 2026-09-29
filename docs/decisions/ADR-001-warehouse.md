# ADR-001: Cloud Data Warehouse Selection (Google BigQuery & DuckDB Parity)

## Status
**Accepted**

## Context
The platform requires an enterprise-scale analytical data warehouse capable of ingesting millions of e-commerce records, performing multi-stage dimensional transformations, and serving low-latency queries to downstream BI tools (Power BI). Additionally, the project must be 100% reproducible by independent hiring managers and developers without mandating paid cloud accounts or complex local database daemon setups.

## Decision
1. **Primary Production Data Warehouse**: **Google BigQuery**.
   - Serverless architecture with automated compute scaling and petabyte separation of storage and compute.
   - Built-in columnar storage (Capacitor) supporting partition pruning by date and clustering on high-cardinality foreign keys (`customer_unique_id`, `product_id`).
   - Native integration with Google Cloud IAM, Cloud Storage, and Power BI DirectQuery/Import connectors.
2. **Local Development & CI Parity Engine**: **DuckDB**.
   - In-process, zero-dependency columnar SQL engine embedded directly in the repository.
   - Implements full ANSI SQL, window functions, and native Parquet read/write capabilities identical to BigQuery standard SQL.
   - Allows full ELT execution, 104 dbt tests, and Power BI Parquet export in under 5 seconds locally.

## Alternatives Considered
* **Snowflake**: Highly capable, but requires paid virtual warehouse credits and external cloud staging (S3/GCS) for basic CLI operation.
* **PostgreSQL / MySQL**: Row-oriented transactional RDBMS. Query performance degrades significantly on wide dimensional joins and analytical aggregate scans across millions of rows.
* **Pure SQLite**: Embedded, but lacks full columnar analytical engine optimizations and modern window function speed compared to DuckDB.

## Tradeoffs & Consequences
* **Positive**: Production BigQuery models and local execution share 100% standard SQL compatibility. Pipeline can be evaluated locally in seconds or pushed directly to GCP BigQuery.
* **Tradeoff**: Slight dialect variances in array generation and date diffs are abstracted through portable dbt macros (`datediff`, `date_spine`).
