# Data Profile: `olist_products_dataset`

- **Source File**: `olist_products_dataset.csv` (2.27 MB)
- **Total Rows**: 32,951
- **Total Columns**: 9
- **Duplicate Rows**: 0
- **Candidate Primary Key(s)**: `product_id`
- **Profile Date**: `2026-09-29T08:02:56.992396` UTC

## Column Summary

| Column Name | Inferred Type | Null Count | Null % | Unique Count | Unique % | Candidate PK |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | categorical/text | 0 | 0.0% | 32,951 | 100.0% | Yes |
| `product_category_name` | categorical/text | 610 | 1.85% | 73 | 0.22% | No |
| `product_name_lenght` | numeric | 610 | 1.85% | 66 | 0.2% | No |
| `product_description_lenght` | numeric | 610 | 1.85% | 2,960 | 8.98% | No |
| `product_photos_qty` | numeric | 610 | 1.85% | 19 | 0.06% | No |
| `product_weight_g` | numeric | 2 | 0.01% | 2,204 | 6.69% | No |
| `product_length_cm` | numeric | 2 | 0.01% | 99 | 0.3% | No |
| `product_height_cm` | numeric | 2 | 0.01% | 102 | 0.31% | No |
| `product_width_cm` | numeric | 2 | 0.01% | 95 | 0.29% | No |

## Numeric Distributions

| Column | Min | Max | Mean | Std | Median | Zero Count | Negative Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `product_name_lenght` | 5.0 | 76.0 | 48.4769 | 10.2457 | 51.0 | 0 | 0 |
| `product_description_lenght` | 4.0 | 3992.0 | 771.4953 | 635.1152 | 595.0 | 0 | 0 |
| `product_photos_qty` | 1.0 | 20.0 | 2.189 | 1.7368 | 1.0 | 0 | 0 |
| `product_weight_g` | 0.0 | 40425.0 | 2276.4725 | 4282.0387 | 700.0 | 4 | 0 |
| `product_length_cm` | 7.0 | 105.0 | 30.8151 | 16.9145 | 25.0 | 0 | 0 |
| `product_height_cm` | 2.0 | 105.0 | 16.9377 | 13.6376 | 13.0 | 0 | 0 |
| `product_width_cm` | 6.0 | 118.0 | 23.1967 | 12.079 | 20.0 | 0 | 0 |

## Detected Anomalies & Data Quality Warnings

- _No critical domain anomalies detected._
