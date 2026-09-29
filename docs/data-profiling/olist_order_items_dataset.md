# Data Profile: `olist_order_items_dataset`

- **Source File**: `olist_order_items_dataset.csv` (14.72 MB)
- **Total Rows**: 112,650
- **Total Columns**: 7
- **Duplicate Rows**: 0
- **Candidate Primary Key(s)**: _None (Composite key or non-unique source)_
- **Profile Date**: `2026-09-29T08:02:55.323499` UTC

## Column Summary

| Column Name | Inferred Type | Null Count | Null % | Unique Count | Unique % | Candidate PK |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | categorical/text | 0 | 0.0% | 98,666 | 87.59% | No |
| `order_item_id` | numeric | 0 | 0.0% | 21 | 0.02% | No |
| `product_id` | categorical/text | 0 | 0.0% | 32,951 | 29.25% | No |
| `seller_id` | categorical/text | 0 | 0.0% | 3,095 | 2.75% | No |
| `shipping_limit_date` | datetime | 0 | 0.0% | 93,318 | 82.84% | No |
| `price` | numeric | 0 | 0.0% | 5,968 | 5.3% | No |
| `freight_value` | numeric | 0 | 0.0% | 6,999 | 6.21% | No |

## Numeric Distributions

| Column | Min | Max | Mean | Std | Median | Zero Count | Negative Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_item_id` | 1.0 | 21.0 | 1.1978 | 0.7051 | 1.0 | 0 | 0 |
| `price` | 0.85 | 6735.0 | 120.6537 | 183.6339 | 74.99 | 0 | 0 |
| `freight_value` | 0.0 | 409.68 | 19.9903 | 15.8064 | 16.26 | 383 | 0 |

## Date Boundaries

| Column | Min Date | Max Date | Invalid Date Count |
| :--- | :--- | :--- | :--- |
| `shipping_limit_date` | `2016-09-19 00:15:34` | `2020-04-09 22:35:08` | 0 |

## Detected Anomalies & Data Quality Warnings

- _No critical domain anomalies detected._
