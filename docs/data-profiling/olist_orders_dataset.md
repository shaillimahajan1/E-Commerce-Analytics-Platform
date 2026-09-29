# Data Profile: `olist_orders_dataset`

- **Source File**: `olist_orders_dataset.csv` (16.84 MB)
- **Total Rows**: 99,441
- **Total Columns**: 8
- **Duplicate Rows**: 0
- **Candidate Primary Key(s)**: `order_id`, `customer_id`
- **Profile Date**: `2026-09-29T08:02:56.903994` UTC

## Column Summary

| Column Name | Inferred Type | Null Count | Null % | Unique Count | Unique % | Candidate PK |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | categorical/text | 0 | 0.0% | 99,441 | 100.0% | Yes |
| `customer_id` | categorical/text | 0 | 0.0% | 99,441 | 100.0% | Yes |
| `order_status` | categorical/text | 0 | 0.0% | 8 | 0.01% | No |
| `order_purchase_timestamp` | datetime | 0 | 0.0% | 98,875 | 99.43% | No |
| `order_approved_at` | categorical/text | 160 | 0.16% | 90,733 | 91.24% | No |
| `order_delivered_carrier_date` | datetime | 1,783 | 1.79% | 81,018 | 81.47% | No |
| `order_delivered_customer_date` | datetime | 2,965 | 2.98% | 95,664 | 96.2% | No |
| `order_estimated_delivery_date` | datetime | 0 | 0.0% | 459 | 0.46% | No |

## Date Boundaries

| Column | Min Date | Max Date | Invalid Date Count |
| :--- | :--- | :--- | :--- |
| `order_purchase_timestamp` | `2016-09-04 21:15:19` | `2018-10-17 17:30:18` | 0 |
| `order_delivered_carrier_date` | `2016-10-08 10:34:01` | `2018-09-11 19:48:28` | 0 |
| `order_delivered_customer_date` | `2016-10-11 13:46:32` | `2018-10-17 13:22:46` | 0 |
| `order_estimated_delivery_date` | `2016-09-30 00:00:00` | `2018-11-12 00:00:00` | 0 |

## Detected Anomalies & Data Quality Warnings

- **[HIGH] MISSING_DELIVERY_DATE_FOR_DELIVERED**: 8 orders with status 'delivered' have NULL delivered_customer_date.
