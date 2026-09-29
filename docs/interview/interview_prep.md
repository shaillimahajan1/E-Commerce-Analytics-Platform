# Interview Preparation Guide & Project Defense

This comprehensive guide prepares you to present, explain, and defend every engineering and architectural decision made in the **E-Commerce Analytics Platform** during senior Analytics Engineer, Data Engineer, and Lead BI Developer interviews.

---

## 1. Project Explanations (Elevator Pitches)

### The 30-Second Explanation
> *"I designed and built an end-to-end, production-grade E-Commerce Analytics Platform using the Brazilian Olist marketplace dataset (100k orders, R$ 16M payments). Rather than building a toy pandas script, I implemented strict separation of concerns: Python for SHA-checksummed raw ingestion and schema contract validation; Google BigQuery and DuckDB for cloud warehouse storage; dbt Core for a 3-layer dimensional star schema with 104 automated tests; Dockerized Apache Airflow for DAG orchestration and financial reconciliation; advanced analytical SQL for cohorts and RFM segmentation; and a 6-page star-schema Power BI semantic model with explicit DAX measures."*

### The 2-Minute Explanation
> *"In multi-seller e-commerce marketplaces, business stakeholders often struggle with fragmented visibility across revenue velocity, merchant SLA fulfillment, and customer retention. I built this platform to demonstrate how a modern analytics engineer can independently own the entire data lifecycle from raw landing to executive decision-making.*
>
> *Starting from 9 raw landed files, I engineered an automated Python ingestion engine that verifies cryptographic SHA-256 checksums, validates schema contracts, and logs every load into a warehouse audit trail. On the warehouse layer, I built a modular dbt project structured across Staging, Intermediate, and Marts layers. The data model follows Kimball dimensional modeling, establishing conformed dimensions (`dim_customer`, `dim_product`, `dim_seller`, `dim_date`, `dim_location`) and granular facts (`fct_orders`, `fct_order_items`, `fct_payments`, `fct_reviews`, `fct_delivery`).*
>
> *To guarantee data reliability, I authored 104 automated dbt data tests alongside a 5-pillar Python Quality Framework checking completeness, uniqueness, referential integrity, validity, and chronological consistency. The pipeline is fully orchestrated using an Apache Airflow DAG containerized in Docker Compose, featuring automated retries and an end-to-end reconciliation check that independently verifies zero row loss and penny-accurate financial totals. Finally, I authored an advanced analytical SQL portfolio covering monthly cohort retention and RFM quintile segmentation, paired with a 6-page production Power BI semantic model featuring an explicit DAX measure repository."*

### The 5-Minute Technical Deep Dive
> *"Let's walk through the architectural layers from raw data ingestion to consumption.*
>
> **1. Ingestion & Contract Validation**:
> *Rather than letting malformed data silently corrupt warehouse tables, my Python ingestion engine uses an Extract -> Validate -> Load -> Audit pattern. The extractor computes SHA-256 hashes to guarantee data immutability. The validator runs contract checks on expected schemas, row counts, and primary key nulls using Pydantic and pandas. Validated records are loaded into `ecommerce_raw` using BigQuery batch jobs or local embedded DuckDB, writing an audit record (`raw_ingestion_audit`) tracking load timestamps, row counts, and elapsed duration.*
>
> **2. Transformation Architecture (dbt Core)**:
> *I avoided in-memory Pandas transforms to leverage the warehouse's columnar compute engine. In dbt:*
> - *`staging/`: Views that standardize string casing, cast timestamps, clean column names (e.g. fixing Portuguese typos like `lenght` to `length`), and deduplicate geolocation sensor readings by aggregating to unique zip prefix coordinate centroids.*
> - *`intermediate/`: View models that enrich entities without repeating business logic, including order-level payment/item aggregations, customer purchase timelines, and delivery duration metrics.*
> - *`marts/`: Physical tables materialized as a Kimball Star Schema. I enforced strict grains: `fct_orders` at the order header grain, `fct_order_items` at the line-item grain, and conformed dimensions like `dim_customer` representing unique human buyers (`customer_unique_id`).*
>
> **3. Data Quality & Financial Reconciliation**:
> *Quality is enforced at two distinct levels: 104 dbt generic and business rule tests (such as verifying delivery dates occur on or after purchase timestamps), and an independent reconciliation script. The reconciliation check verifies across Raw, Staging, and Marts layers that all 99,441 orders match with 0 row loss, 0 orphan items, and total collected payments match down to the exact cent: R$ 16,008,872.12.*
>
> **4. Orchestration & Local/Cloud Parity**:
> *The entire pipeline is orchestrated by an Apache Airflow DAG (`ecommerce_analytics_pipeline`) running in Docker Compose with a PostgreSQL metadata database. Crucially, Airflow orchestrates via CLI/Operators and never processes transformation data inside worker memory. To ensure 100% reproducibility, I engineered dual-target profiles: running locally via embedded DuckDB without cloud cost, or deploying directly to Google BigQuery with partition pruning and clustering.*
>
> **5. Analytics & Business Intelligence**:
> *Downstream, I authored an advanced SQL analytics portfolio including 12-month cohort retention matrices, RFM quintile segmentation, product Pareto 80/20 curves, and route logistics analysis. In Power BI, I designed a 6-page interactive report powered by explicit DAX measures, avoiding implicit aggregations and enforcing single-directional filter propagation."*

---

## 2. Technical Interview Questions (Based on Project)

### SQL Interview Questions (15 Questions)

1. **How do you calculate Month-over-Month (MoM) revenue growth in SQL?**
   * *Answer*: Use `LAG(monthly_gmv, 1) OVER (ORDER BY month_start_date)` inside a CTE, then compute `((monthly_gmv - prev_month_gmv) / prev_month_gmv) * 100` in the outer query, guarding against division by zero with `NULLIF()`.
2. **How did you build the customer retention cohort matrix?**
   * *Answer*: Grouped orders by `customer_unique_id` to find the minimum purchase month (`cohort_month`), joined back to subsequent orders, and computed `month_number = (year_diff * 12) + month_diff`. Divided active customers in each elapsed month by `cohort_size` and pivoted using conditional aggregation (`MAX(CASE WHEN month_number = 1 THEN retention_rate_pct END)`).
3. **What is the difference between `RANK()`, `DENSE_RANK()`, and `ROW_NUMBER()` in product rankings?**
   * *Answer*: If two products tie with identical GMV: `ROW_NUMBER()` assigns sequential numbers arbitrarily (1, 2); `RANK()` assigns identical ranks and skips subsequent ranks (1, 1, 3); `DENSE_RANK()` assigns identical ranks without gaps (1, 1, 2).
4. **How do you calculate a 3-month trailing rolling average in SQL?**
   * *Answer*: Use window aggregation: `AVG(monthly_gmv) OVER (ORDER BY month_start_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`.
5. **How did you implement the Pareto 80/20 principle in SQL?**
   * *Answer*: Computed running cumulative revenue using `SUM(lifetime_revenue) OVER (ORDER BY lifetime_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)`, divided by the total catalog revenue scalar, and flagged SKUs where cumulative percentage was `<= 0.80`.
6. **How did you handle deduplication of geolocation coordinates in staging?**
   * *Answer*: Grouped by `zip_code_prefix` and computed `AVG(latitude)` and `AVG(longitude)` while using `ROW_NUMBER() OVER (PARTITION BY zip_code_prefix ORDER BY city_frequency DESC)` to pick the primary city and state.
7. **Why should you avoid `SELECT *` in production BigQuery and analytical SQL?**
   * *Answer*: BigQuery is a columnar store where query cost and scan latency depend directly on the specific columns scanned. `SELECT *` forces a full scan of all columns across all micro-partitions, dramatically inflating compute costs.
8. **How do you prevent integer division truncation in SQL?**
   * *Answer*: Explicitly cast the numerator or denominator to `FLOAT` / `DOUBLE`, or multiply by `1.0` before dividing.
9. **How do you implement RFM quintile scoring in SQL?**
   * *Answer*: Using `NTILE(5) OVER (ORDER BY metric ASC/DESC)`. For Recency, order descending by days since last order so recent buyers receive 5; for Monetary, order ascending by spend so high spenders receive 5.
10. **What is conditional aggregation and where was it used?**
    * *Answer*: Combining aggregate functions with `CASE` expressions (e.g. `SUM(CASE WHEN is_late_delivery = 1 THEN 1 ELSE 0 END)`), used in seller scorecards and delivery SLA summaries.
11. **How do you identify orphan records between two tables?**
    * *Answer*: Perform a `LEFT JOIN` from child to parent and filter `WHERE parent.pk IS NULL`.
12. **How do you handle `NULL` values when creating composite surrogate keys?**
    * *Answer*: Use `COALESCE(CAST(col AS VARCHAR), '_null_sentinel_')` inside a hash function (MD5/SHA) to ensure deterministic hashing and prevent null collisions.
13. **What is the purpose of `UNBOUNDED PRECEDING` in a window frame?**
    * *Answer*: It instructs the window function to include all rows from the beginning of the partition up to the current row, enabling cumulative running totals.
14. **How do you calculate the difference between two timestamps in hours across different SQL dialects?**
    * *Answer*: In ANSI/BigQuery, `DATE_DIFF(end_ts, start_ts, HOUR)`. In DuckDB, `DATEDIFF('hour', start_ts, end_ts)`. We abstracted this into a portable dbt macro.
15. **How do you verify financial reconciliation across multiple aggregate levels in a single query?**
    * *Answer*: Using `UNION ALL` across independent queries querying Raw payments, Staging payments, Fact payments, and Fact orders, standardizing column aliases to compare results in one output table.

---

### Data Modeling Questions (10 Questions)

1. **Why choose a Star Schema over Third Normal Form (3NF)?**
   * *Answer*: 3NF optimizes for transaction throughput and OLTP consistency, requiring 8+ joins for basic queries. A Star Schema denormalizes descriptive context into conformed dimensions, optimizing for analytical scans, aggregations, and business user comprehension.
2. **What is the grain of `fct_orders` vs `fct_order_items`?**
   * *Answer*: `fct_orders` is at the order header grain (one row per order), holding order-level financial and fulfillment totals. `fct_order_items` is at the line-item grain (one row per item), linking specific products and sellers.
3. **How do you avoid double-counting revenue when analyzing order items and orders?**
   * *Answer*: Never join `fct_orders` and `fct_order_items` directly to sum order-level totals. In Power BI, separate explicit measures are built on each fact table, and dimensions filter both facts independently.
4. **Why is `dim_customer` keyed on `customer_unique_id` rather than `customer_id`?**
   * *Answer*: In Olist, `customer_id` is an order session token created anew for every transaction. `customer_unique_id` is the persistent identifier representing the actual human buyer across multiple repeat purchases.
5. **What is a conformed dimension and which dimensions in your model are conformed?**
   * *Answer*: A dimension that has a consistent meaning and key across multiple fact tables. `dim_date`, `dim_customer`, `dim_product`, `dim_seller`, and `dim_location` are all conformed dimensions filtering multiple facts.
6. **Why create a separate `fct_delivery` fact table instead of putting all delivery fields in `fct_orders`?**
   * *Answer*: `fct_delivery` has a distinct operational audience (logistics/supply chain) and only includes fulfilled/delivered orders, isolating delivery SLA metrics without polluting commercial order reporting.
7. **What is a surrogate key and how did you construct it?**
   * *Answer*: A system-generated, non-business unique identifier. We used deterministic MD5 hashes of composite natural keys (e.g. `MD5(order_id || '-' || order_item_id)`), ensuring consistent keys without stateful sequence generators.
8. **What is the difference between a Type 1 and Type 2 Slowly Changing Dimension (SCD)?**
   * *Answer*: SCD1 overwrites old attributes (e.g. customer city update overwrites previous city). SCD2 preserves historical state by adding new rows with `valid_from`, `valid_to`, and `is_current` flags.
9. **How would you model customer address changes in this platform using SCD2?**
   * *Answer*: Use dbt snapshots (`dbt snapshot`) on `stg_customers` using `customer_unique_id` as the unique key and `updated_at` as the check strategy.
10. **What is a degenerate dimension and are there any in this project?**
    * *Answer*: A dimension attribute stored directly in a fact table without joining to a dimension table, such as `order_status` in `fct_orders`.

---

### dbt Questions (10 Questions)

1. **What is the purpose of the 3-layer dbt architecture (Staging, Intermediate, Marts)?**
   * *Answer*: Staging cleans and renames raw tables (1:1); Intermediate aggregates and enriches business entities to prevent repeated logic (DRY principle); Marts materialize curated star schema models for BI consumption.
2. **Why materialize staging models as views and marts as tables?**
   * *Answer*: Staging views avoid storing duplicate data and always query the freshest raw records. Marts are materialized as physical tables to precompute aggregations and deliver sub-second queries to Power BI.
3. **What generic tests are built into dbt and where are they configured?**
   * *Answer*: `unique`, `not_null`, `relationships`, and `accepted_values`, configured in `schema.yml` files.
4. **How do custom singular business rule tests work in dbt?**
   * *Answer*: Written as SQL files in `tests/`. dbt runs the query; if it returns 0 rows, the test passes. If it returns 1 or more rows (failing records), the test fails.
5. **How did you handle the Brazilian Portuguese column typos (`lenght`) in dbt?**
   * *Answer*: In `stg_products.sql`, explicitly aliased `product_name_lenght as product_name_length`, creating an English data contract for all downstream models.
6. **What is `ref()` and `source()` in dbt and why use them instead of hardcoding table names?**
   * *Answer*: `source()` references raw sources defined in `sources.yml`. `ref()` references upstream dbt models. Both dynamically construct the dependency DAG and interpolate target schemas based on active environment profiles.
7. **How does dbt documentation work?**
   * *Answer*: Descriptions in YAML files are compiled by `dbt docs generate` into `manifest.json` and `catalog.json`, rendering a searchable website with data dictionary and interactive lineage graphs.
8. **How does dbt handle environment isolation (Dev vs Prod)?**
   * *Answer*: Through `profiles.yml` targets. In `dev`, dbt builds into local or sandbox schemas; in `prod`, it builds into production schemas using service account credentials.
9. **What is a dbt macro and where did you use one?**
   * *Answer*: Reusable Jinja-SQL code snippets. Used for `generate_surrogate_key`, `round_currency`, and `datediff` (abstracting BigQuery vs DuckDB syntax).
10. **How would you implement an incremental model in dbt for `fct_orders`?**
    * *Answer*: Add `config(materialized='incremental', unique_key='order_id')` and include `{% if is_incremental() %} WHERE order_purchase_timestamp > (SELECT MAX(order_purchase_timestamp) FROM {{ this }}) {% endif %}`.

---

### BigQuery Questions (10 Questions)

1. **How does BigQuery's storage architecture differ from traditional RDBMS?**
   * *Answer*: BigQuery uses Capacitor, a proprietary columnar storage format separated completely from compute (Borg/Dremel), enabling independent scaling and cost optimization.
2. **What is the difference between partitioning and clustering in BigQuery?**
   * *Answer*: Partitioning physically segments a table by date/timestamp/integer into daily/monthly partitions, pruning entire blocks from scans. Clustering sorts data within partitions based on up to 4 columns, colocating related rows.
3. **How is `fct_orders` partitioned and clustered?**
   * *Answer*: Partitioned by `DATE(order_purchase_timestamp)` (monthly granularity) to prune historical date ranges; clustered on `customer_unique_id` and `customer_state`.
4. **How does BigQuery pricing work and how does our model optimize it?**
   * *Answer*: BigQuery on-demand pricing charges per byte scanned ($6.25/TB). Partition pruning and clustering minimize bytes scanned, avoiding expensive full-table scans.
5. **What is BigQuery BI Engine?**
   * *Answer*: An in-memory analysis service that accelerates SQL queries from Power BI and Looker Studio by caching frequently accessed tables and columns.
6. **How do you handle nested and repeated fields in BigQuery?**
   * *Answer*: Using `STRUCT` (objects) and `ARRAY` (repeated elements), queried using `UNNEST()`.
7. **What is slot contention in BigQuery?**
   * *Answer*: Slots are virtual CPUs used to execute SQL queries. Contention occurs when concurrent queries exhaust available slots, causing jobs to queue.
8. **How do you load CSVs into BigQuery via Python?**
   * *Answer*: Using `bigquery.Client().load_table_from_file()` with `LoadJobConfig` specifying schema autodetect, skip leading rows, and write disposition.
9. **What is BigQuery's `SAFE_DIVIDE()` function?**
   * *Answer*: Returns `NULL` instead of throwing a division-by-zero error when the denominator is 0.
10. **How do you secure sensitive columns in BigQuery?**
    * *Answer*: Using Policy Tags and BigQuery Column-Level Access Control (IAM tags) to restrict column visibility to authorized roles.

---

### Airflow Questions (10 Questions)

1. **What is the role of Apache Airflow in this analytics platform?**
   * *Answer*: Orchestrator. It schedules DAG runs, verifies dependencies, manages retries, executes CLI commands, and tracks execution history. It does NOT process data in memory.
2. **What happens if an Airflow DAG fails at `run_dbt_marts`?**
   * *Answer*: Airflow halts downstream tasks (`run_dbt_tests`, `run_analytics_validation`), logs the exact model failure, sends alert notifications, and retries based on configured task retry policies. Once fixed, the operator can clear the failed task in the Airflow UI to resume execution without rerunning upstream stages.
3. **Why use `LocalExecutor` instead of `SequentialExecutor` in our Docker Compose setup?**
   * *Answer*: `SequentialExecutor` uses SQLite and executes only one task at a time. `LocalExecutor` uses PostgreSQL and spawns parallel worker processes, enabling concurrent task execution.
4. **How are task dependencies defined in Airflow?**
   * *Answer*: Using the bitshift operator (`>>`), e.g., `ingest_to_raw >> run_dbt_staging >> run_dbt_intermediate >> run_dbt_marts`.
5. **What is an Airflow Sensor and where could it be used?**
   * *Answer*: A specialized operator that polls for an external condition (e.g. `GCSObjectExistenceSensor` or `FileSensor` waiting for source files to land in an S3/GCS bucket before triggering ingestion).
6. **How do you prevent Airflow from scheduling a massive backfill of historical runs?**
   * *Answer*: Set `catchup=False` in the DAG definition and use an appropriate `start_date`.
7. **What are Airflow Pools?**
   * *Answer*: Pools limit concurrency for arbitrary sets of tasks, preventing the pipeline from overwhelming database connection limits or API rate limits.
8. **What is XCom in Airflow and did we use it?**
   * *Answer*: Cross-Communication mechanism allowing tasks to exchange small pieces of metadata (e.g. file names, row counts). Used for task metadata passing, never for large tabular datasets.
9. **How do you pass secrets and credentials to Airflow tasks securely?**
   * *Answer*: Via Airflow Connections and Variables stored in Secret Managers (GCP Secret Manager, HashiCorp Vault, AWS Secrets Manager) or environment variables, never hardcoded in DAG files.
10. **What is the difference between `execution_date` and `logical_date` in modern Airflow?**
    * *Answer*: In Airflow 2.2+, `logical_date` is the modern name for `execution_date`, representing the start of the data interval being processed, distinct from the wall-clock run timestamp.

---

### Python Questions (10 Questions)

1. **Why use Python for ingestion rather than loading CSVs directly via dbt seeds?**
   * *Answer*: dbt seeds are designed for small static lookup tables (<1,000 rows). Loading 1.5 million rows via dbt seeds causes extreme repository bloat, slow git operations, and poor compile times. Python provides robust streaming, checksum hashing, contract validation, and audit tracking.
2. **How did you calculate cryptographic checksums (SHA-256) in Python?**
   * *Answer*: Used `hashlib.sha256()` with chunked binary reading (`iter(lambda: f.read(65536), b'')`) to calculate hashes efficiently without loading multi-gigabyte files into RAM.
3. **How does Pydantic or dataclasses enforce data contracts?**
   * *Answer*: By defining explicit attribute schemas with strict type hints, validating incoming dictionary keys, and raising structured validation errors on schema violations.
4. **What is the advantage of using PyArrow over standard Pandas for columnar processing?**
   * *Answer*: PyArrow uses the Apache Arrow columnar memory format, enabling zero-copy reads, superior multi-threaded compression (Zstandard/Snappy), and 5-10x faster Parquet serialization than standard pandas.
5. **How did you structure logging across your ingestion modules?**
   * *Answer*: Built a centralized `src/utils/logger.py` returning configured `logging.Logger` instances with standardized formats (`timestamp | level | [module] message`).
6. **What is the difference between `read_csv` and `read_csv_auto` in DuckDB Python?**
   * *Answer*: DuckDB's `read_csv_auto` leverages multi-threaded parallel sniffing to infer data types, date formats, and delimiters, executing significantly faster than Python-level Pandas parsers.
7. **How do you write unit tests for file extractors using pytest?**
   * *Answer*: Use pytest's `tmp_path` fixture to dynamically create temporary mock CSV files, test extraction success, and verify that `FileNotFoundError` or `ExtractionError` is raised when files are missing or empty.
8. **What is the purpose of `python-dotenv`?**
   * *Answer*: Loads key-value pairs from a local `.env` file into `os.environ`, keeping secrets and configurations out of source control.
9. **How do you ensure Python scripts return standard UNIX exit codes?**
   * *Answer*: Using `sys.exit(0)` on success and `sys.exit(1)` on failure, allowing orchestrators (Airflow/Bash/CI) to detect pipeline failures cleanly.
10. **How do you handle memory constraints when profiling large datasets in Python?**
    * *Answer*: Read headers separately with `nrows=0`, sample rows if necessary, or stream chunked iterators rather than loading entire tables into single memory arrays.

---

### Power BI & DAX Questions (20 Questions)

1. **Why avoid implicit measures in Power BI?**
   * *Answer*: Implicit measures rely on visual-level defaults (e.g. auto-summing columns), leading to inconsistent business definitions, accidental summing of IDs/surrogate keys, and an inability to apply advanced filter context modifications via `CALCULATE()`.
2. **How does `CALCULATE()` modify filter context in DAX?**
   * *Answer*: `CALCULATE()` evaluates an expression in a modified filter context. It can add new filters, overwrite existing column filters, or convert existing row context into an equivalent filter context (context transition).
3. **What is the difference between `DIVIDE(A, B, 0)` and `A / B` in DAX?**
   * *Answer*: `DIVIDE()` internally performs safe division, returning the alternative result (`0` or `BLANK()`) when dividing by zero or encountering nulls, preventing `#ERROR` in visual cards.
4. **How did you compute Month-over-Month (MoM) revenue growth in DAX?**
   * *Answer*: Used `CALCULATE([Gross Merchandise Value], DATEADD(dim_date[date_day], -1, MONTH))` to get prior month GMV, then used `DIVIDE(Current - Prior, Prior, BLANK())`.
5. **Why mark `dim_date` as an official Date Table in Power BI?**
   * *Answer*: Marking as Date Table informs the VertiPaq engine to use the explicit calendar table for time intelligence functions (`DATEADD`, `SAMEPERIODLASTYEAR`), and disables automatic hidden internal date hierarchies that bloat PBIX file size.
6. **What is the difference between `USERELATIONSHIP()` and an active relationship?**
   * *Answer*: Power BI allows only one active relationship between two tables at a time. Inactive relationships (e.g. from `dim_date` to `order_delivered_customer_date`) can be temporarily activated inside a measure using `USERELATIONSHIP()`.
7. **How does single-direction cross-filtering protect star schema performance?**
   * *Answer*: Single-direction ensures filter flow travels strictly from dimension to fact tables. Bi-directional cross-filtering introduces ambiguity, slows down query performance, and can cause unexpected cross-table filter leakage.
8. **What is VertiPaq and how does it achieve high compression?**
   * *Answer*: VertiPaq is Power BI's in-memory columnar database engine. It achieves high compression using dictionary encoding, run-length encoding (RLE), bit-packing, and value encoding on numeric columns.
9. **How do you reduce Power BI semantic model memory size?**
   * *Answer*: Remove unnecessary high-cardinality columns (GUIDs, timestamps with seconds), split datetime into separate date and time columns, hide surrogate keys, turn off auto date/time, and remove duplicate raw tables.
10. **What is Context Transition in DAX?**
    * *Answer*: The automatic conversion of row context into an equivalent filter context, triggered whenever a measure is referenced inside an iterator function (like `SUMX` or `CALCULATE`).

---

## 3. Defense of Challenge Questions (Section 56)

### "Why BigQuery? Why not Snowflake?"
> *"Both are top-tier cloud data warehouses. We selected BigQuery for three key reasons: First, BigQuery is completely serverless—there are no virtual warehouses to spin up, resize, or suspend, which eliminates idle cluster compute costs for sporadic batch pipelines. Second, BigQuery's native integration with Google Cloud IAM and Power BI DirectQuery/Import connectors provides seamless enterprise governance. Third, BigQuery's partition pruning on dates combined with clustering on customer and seller IDs delivers predictable query performance at low on-demand cost. However, because our transformations are written in standardized ANSI SQL in dbt, migrating to Snowflake would require only changing the dbt adapter in `profiles.yml` without rewriting our business transformation logic."*

### "Why dbt? Why not transform everything in Python Pandas?"
> *"Transforming data in Python Pandas creates a brittle 'black box' ETL anti-pattern. First, Pandas transforms data in single-node worker memory; as data grows from 100k rows to 100 million, in-memory scripts suffer out-of-memory crashes. Second, dbt pushes computation down directly into the warehouse, taking full advantage of BigQuery's massively parallel processing (MPP) compute clusters. Third, dbt provides version-controlled data lineage graphs, automated documentation catalogs, and native data testing (104 automated tests in our build), bringing true software engineering rigor to SQL modeling that custom Python scripts cannot match."*

### "Why Airflow? What happens if Airflow fails halfway through?"
> *"Airflow provides centralized DAG visualization, automated scheduling, execution history, and configurable retry policies with exponential backoff. If the pipeline fails halfway through—for example, if `run_dbt_marts` fails due to a schema mismatch—Airflow halts downstream execution (`run_dbt_tests` and `run_analytics_validation`), alerts the engineering team, and logs the exact error. Because our dbt marts are idempotent (`CREATE OR REPLACE TABLE`), once the root cause is resolved, the on-call engineer can simply restart the failed task from the Airflow UI, and the pipeline resumes without duplicating rows or leaving the warehouse in an inconsistent state."*

### "How do you handle duplicate orders and prevent double counting?"
> *"We address duplication at multiple defensive layers: In ingestion, `validate.py` audits row counts and detects duplicate primary keys. In staging, surrogate keys are generated. In the dimensional model, we maintain strict grain separation: `fct_orders` holds order-level totals (GMV, freight, payments) at the `order_id` grain, while `fct_order_items` holds line items at the `(order_id, order_item_id)` grain. In Power BI, we never join these two facts directly to perform additive aggregations; instead, conformed dimensions slice each fact independently, eliminating fan-out Cartesian products and double counting."*

### "How do you handle late-arriving data?"
> *"In our current batch architecture, dbt models rebuild physical tables idempotently. To productionize late-arriving data at scale, we would implement incremental dbt models using a lookback window:*
> ```sql
> {% if is_incremental() %}
>   where updated_at >= (select max(updated_at) - interval '3 days' from {{ this }})
> {% endif %}
> ```
> *This ensures that any order updated, delivered, or reviewed up to 3 days after initial purchase is captured and merged via BigQuery's native `MERGE` statement without requiring full historical table rebuilds."*

### "What is the grain of your fact table? Why is this a fact instead of a dimension?"
> *"The grain of `fct_orders` is exactly one row per customer order transaction. It is modeled as a Fact table because it contains measurable, quantitative business events (monetary values, item counts, delivery durations) that change with every transaction and are aggregated across dimensions. Conversely, `dim_customer` is a Dimension table because it represents an entity that exists independently of a single order, providing descriptive context (location, RFM segment, lifetime tier) by which facts are filtered."*

### "How would you implement SCD Type 2?"
> *"For dimensions where historical tracking is essential (e.g. a seller moving warehouse locations or a customer moving states), we would implement dbt Snapshots (`dbt snapshot`). dbt automatically creates and manages an SCD2 table with `dbt_scd_id`, `dbt_valid_from`, `dbt_valid_to`, and `dbt_updated_at` columns using a timestamp or check-hash strategy, allowing analysts to reconstruct historical point-in-time state."*

### "How would you optimize a slow BigQuery query?"
> *"I follow a systematic 5-step optimization checklist:
> 1. **Inspect Query Execution Plan**: Check the BigQuery Execution Details in the console to identify bottlenecks (e.g. high slot time, data spilling to disk, compute-heavy joins).
> 2. **Filter on Partition Columns**: Ensure the `WHERE` clause filters on the partitioned date column (`order_purchase_timestamp`) to maximize block pruning.
> 3. **Cluster on Join/Filter Keys**: Cluster tables on high-cardinality join keys (`customer_unique_id`, `seller_id`) to reduce shuffling.
> 4. **Eliminate `SELECT *`**: Select only the exact columns required for downstream computation.
> 5. **Avoid Repeated Aggregations**: Materialize intermediate subqueries as physical dbt tables or use CTEs with window functions rather than self-joining the same table multiple times."*
