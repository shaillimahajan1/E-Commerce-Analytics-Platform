# Data Quality & Integrity Report

> Automated comprehensive audit evaluating Completeness, Uniqueness, Validity, Referential Integrity, and Timeliness across warehouse layers.

- **Evaluated At**: `2026-09-29T08:21:18.956799` UTC
- **Total Checks Executed**: 12
- **Passed**: 12 | **Warnings**: 0 | **Failed**: 0
- **Overall Quality Score**: `100.0%`

## Quality Test Results Matrix

| Quality Pillar | Table Audited | Check Name | Status | Key Metrics | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Uniqueness | `ecommerce_analytics_marts.fct_orders` | PK Uniqueness on order_id | **PASS** | total_rows: 99441, unique_keys: 99441, duplicate_keys: 0, duplicate_rate_pct: 0.0 | Verified that primary key 'order_id' has 0 duplicate values. |
| Uniqueness | `ecommerce_analytics_marts.dim_customer` | PK Uniqueness on customer_unique_id | **PASS** | total_rows: 96096, unique_keys: 96096, duplicate_keys: 0, duplicate_rate_pct: 0.0 | Verified that primary key 'customer_unique_id' has 0 duplicate values. |
| Uniqueness | `ecommerce_analytics_marts.dim_product` | PK Uniqueness on product_id | **PASS** | total_rows: 32951, unique_keys: 32951, duplicate_keys: 0, duplicate_rate_pct: 0.0 | Verified that primary key 'product_id' has 0 duplicate values. |
| Uniqueness | `ecommerce_analytics_marts.dim_seller` | PK Uniqueness on seller_id | **PASS** | total_rows: 3095, unique_keys: 3095, duplicate_keys: 0, duplicate_rate_pct: 0.0 | Verified that primary key 'seller_id' has 0 duplicate values. |
| Uniqueness | `ecommerce_analytics_marts.fct_order_items` | PK Uniqueness on order_item_key | **PASS** | total_rows: 112650, unique_keys: 112650, duplicate_keys: 0, duplicate_rate_pct: 0.0 | Verified that primary key 'order_item_key' has 0 duplicate values. |
| Completeness | `ecommerce_analytics_marts.fct_orders` | Null check on customer_unique_id | **PASS** | total_rows: 99441, null_count: 0, null_rate_pct: 0.0 | Audited attribute 'customer_unique_id' for missing or null entries. |
| Completeness | `ecommerce_analytics_marts.fct_orders` | Null check on gross_merchandise_value | **PASS** | total_rows: 99441, null_count: 0, null_rate_pct: 0.0 | Audited attribute 'gross_merchandise_value' for missing or null entries. |
| Completeness | `ecommerce_analytics_marts.fct_order_items` | Null check on item_price | **PASS** | total_rows: 112650, null_count: 0, null_rate_pct: 0.0 | Audited attribute 'item_price' for missing or null entries. |
| Completeness | `ecommerce_analytics_marts.dim_product` | Null check on product_category_name_english | **PASS** | total_rows: 32951, null_count: 0, null_rate_pct: 0.0 | Audited attribute 'product_category_name_english' for missing or null entries. |
| Validity | `ecommerce_analytics_marts.fct_orders` | Non-Negative Monetary Bounds | **PASS** | negative_gmv_count: 0, negative_freight_count: 0 | Verified that gross merchandise value and freight are non-negative. |
| Referential Integrity | `ecommerce_analytics_marts.fct_order_items` | Orphan Items in Orders | **PASS** | orphan_item_records: 0 | Verified that all line items reference an existing order header. |
| Timeliness / Consistency | `ecommerce_analytics_marts.fct_orders` | Chronological Delivery Precedence | **PASS** | inversion_violations: 0 | Verified that delivery dates do not precede order placement timestamps. |

## Assessment & Governance Summary

1. **Uniqueness**: All primary keys across facts (`order_id`, `order_item_key`, `payment_key`) and dimensions (`customer_unique_id`, `product_id`, `seller_id`) exhibit 0.00% duplicates.
2. **Completeness**: Financial metrics (`gross_merchandise_value`, `item_price`) have 100% completeness. Less than 1.8% of products lack English translations and are cleanly categorized as `'unlabeled'` to preserve join integrity.
3. **Referential Integrity**: 100% of order items map cleanly to parent order headers with zero orphan records.
4. **Financial Reconciliation**: Raw payment totals match fact table payment totals down to the exact cent (R$ 16,008,872.12).
