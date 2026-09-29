# Data Profile: `olist_order_payments_dataset`

- **Source File**: `olist_order_payments_dataset.csv` (5.51 MB)
- **Total Rows**: 103,886
- **Total Columns**: 5
- **Duplicate Rows**: 0
- **Candidate Primary Key(s)**: _None (Composite key or non-unique source)_
- **Profile Date**: `2026-09-29T08:02:55.502028` UTC

## Column Summary

| Column Name | Inferred Type | Null Count | Null % | Unique Count | Unique % | Candidate PK |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | categorical/text | 0 | 0.0% | 99,440 | 95.72% | No |
| `payment_sequential` | numeric | 0 | 0.0% | 29 | 0.03% | No |
| `payment_type` | categorical/text | 0 | 0.0% | 5 | 0.0% | No |
| `payment_installments` | numeric | 0 | 0.0% | 24 | 0.02% | No |
| `payment_value` | numeric | 0 | 0.0% | 29,077 | 27.99% | No |

## Numeric Distributions

| Column | Min | Max | Mean | Std | Median | Zero Count | Negative Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `payment_sequential` | 1.0 | 29.0 | 1.0927 | 0.7066 | 1.0 | 0 | 0 |
| `payment_installments` | 0.0 | 24.0 | 2.8533 | 2.6871 | 1.0 | 2 | 0 |
| `payment_value` | 0.0 | 13664.08 | 154.1004 | 217.4941 | 100.0 | 9 | 0 |

## Detected Anomalies & Data Quality Warnings

- **[MEDIUM] NON_POSITIVE_PAYMENT**: 9 payments have value <= 0.00.
