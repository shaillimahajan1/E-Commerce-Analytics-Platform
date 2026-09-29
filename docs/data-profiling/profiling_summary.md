# Olist E-Commerce Dataset - Data Profiling Summary

> Generated automatically by the Python Data Profiling Engine prior to BigQuery loading.

- **Generated At**: `2026-09-29T08:02:52.538815` UTC
- **Total Datasets Inspected**: 9

## Overview Table

| Table Name | File Size (MB) | Row Count | Col Count | Nulls Present? | Candidate PK | Anomalies Found |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [`olist_customers_dataset`](olist_customers_dataset.md) | 8.62 | 99,441 | 5 | No | `customer_id` | 0 |
| [`olist_geolocation_dataset`](olist_geolocation_dataset.md) | 58.44 | 1,000,163 | 5 | No | `None (Composite)` | 2 |
| [`olist_order_items_dataset`](olist_order_items_dataset.md) | 14.72 | 112,650 | 7 | No | `None (Composite)` | 0 |
| [`olist_order_payments_dataset`](olist_order_payments_dataset.md) | 5.51 | 103,886 | 5 | No | `None (Composite)` | 1 |
| [`olist_order_reviews_dataset`](olist_order_reviews_dataset.md) | 13.78 | 99,224 | 7 | Yes | `None (Composite)` | 0 |
| [`olist_orders_dataset`](olist_orders_dataset.md) | 16.84 | 99,441 | 8 | Yes | `order_id, customer_id` | 1 |
| [`olist_products_dataset`](olist_products_dataset.md) | 2.27 | 32,951 | 9 | Yes | `product_id` | 0 |
| [`olist_sellers_dataset`](olist_sellers_dataset.md) | 0.17 | 3,095 | 4 | No | `seller_id` | 0 |
| [`product_category_name_translation`](product_category_name_translation.md) | 0.0 | 71 | 2 | No | `product_category_name, product_category_name_english` | 0 |

## Key Architecture Observations for Staging & Modeling

1. **`olist_orders_dataset`**: Has 99,441 records. Primary key is `order_id`. Notice that cancelled/unavailable orders do not have delivery timestamps. In staging, `order_delivered_customer_date` should be kept as NULLable timestamp.
2. **`olist_order_items_dataset`**: Grain is `order_id` + `order_item_id`. Multiple items can share the same `order_id`. Price and freight are positive.
3. **`olist_order_payments_dataset`**: Composite key on `(order_id, payment_sequential)`. Total payment types include credit_card, boleto, voucher, debit_card. Multiple vouchers can exist on a single order.
4. **`olist_geolocation_dataset`**: Has duplicate `geolocation_zip_code_prefix` records because geolocation points are sampled across zip prefixes. Must be grouped and averaged by zip code in staging.
5. **`olist_customers_dataset`**: Contains both `customer_id` (order-level transaction token) and `customer_unique_id` (the true real-world returning person identifier). Retention and RFM analysis MUST use `customer_unique_id`.
6. **`olist_products_dataset`**: Product categories are in Portuguese; joins to `product_category_name_translation` are required to generate English category dimensions.
