# Data Profile: `olist_order_reviews_dataset`

- **Source File**: `olist_order_reviews_dataset.csv` (13.78 MB)
- **Total Rows**: 99,224
- **Total Columns**: 7
- **Duplicate Rows**: 0
- **Candidate Primary Key(s)**: _None (Composite key or non-unique source)_
- **Profile Date**: `2026-09-29T08:02:56.020313` UTC

## Column Summary

| Column Name | Inferred Type | Null Count | Null % | Unique Count | Unique % | Candidate PK |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `review_id` | categorical/text | 0 | 0.0% | 98,410 | 99.18% | No |
| `order_id` | categorical/text | 0 | 0.0% | 98,673 | 99.44% | No |
| `review_score` | numeric | 0 | 0.0% | 5 | 0.01% | No |
| `review_comment_title` | categorical/text | 87,656 | 88.34% | 4,527 | 4.56% | No |
| `review_comment_message` | categorical/text | 58,247 | 58.7% | 36,159 | 36.44% | No |
| `review_creation_date` | datetime | 0 | 0.0% | 636 | 0.64% | No |
| `review_answer_timestamp` | datetime | 0 | 0.0% | 98,248 | 99.02% | No |

## Numeric Distributions

| Column | Min | Max | Mean | Std | Median | Zero Count | Negative Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `review_score` | 1.0 | 5.0 | 4.0864 | 1.3476 | 5.0 | 0 | 0 |

## Date Boundaries

| Column | Min Date | Max Date | Invalid Date Count |
| :--- | :--- | :--- | :--- |
| `review_creation_date` | `2016-10-02 00:00:00` | `2018-08-31 00:00:00` | 0 |
| `review_answer_timestamp` | `2016-10-07 18:32:28` | `2018-10-29 12:27:35` | 0 |

## Detected Anomalies & Data Quality Warnings

- _No critical domain anomalies detected._
