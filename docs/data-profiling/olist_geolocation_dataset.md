# Data Profile: `olist_geolocation_dataset`

- **Source File**: `olist_geolocation_dataset.csv` (58.44 MB)
- **Total Rows**: 1,000,163
- **Total Columns**: 5
- **Duplicate Rows**: 261,831
- **Candidate Primary Key(s)**: _None (Composite key or non-unique source)_
- **Profile Date**: `2026-09-29T08:02:54.837264` UTC

## Column Summary

| Column Name | Inferred Type | Null Count | Null % | Unique Count | Unique % | Candidate PK |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `geolocation_zip_code_prefix` | numeric | 0 | 0.0% | 19,015 | 1.9% | No |
| `geolocation_lat` | numeric | 0 | 0.0% | 717,360 | 71.72% | No |
| `geolocation_lng` | numeric | 0 | 0.0% | 717,613 | 71.75% | No |
| `geolocation_city` | categorical/text | 0 | 0.0% | 8,011 | 0.8% | No |
| `geolocation_state` | categorical/text | 0 | 0.0% | 27 | 0.0% | No |

## Numeric Distributions

| Column | Min | Max | Mean | Std | Median | Zero Count | Negative Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `geolocation_zip_code_prefix` | 1001.0 | 99990.0 | 36574.1665 | 30549.3357 | 26530.0 | 0 | 0 |
| `geolocation_lat` | -36.6053744107061 | 45.06593318269697 | -21.1762 | 5.7159 | -22.91937749486411 | 0 | 998827 |
| `geolocation_lng` | -101.46676644931476 | 121.10539381057764 | -46.3905 | 4.2697 | -46.63787866960149 | 0 | 1000160 |

## Detected Anomalies & Data Quality Warnings

- **[HIGH] DUPLICATE_ROWS**: Found 261831 exact duplicate rows across all columns.
- **[INFO] MULTIPLE_COORDINATES_PER_ZIP**: 17972 zip code prefixes have multiple coordinates, requiring deduplication/averaging in staging.
