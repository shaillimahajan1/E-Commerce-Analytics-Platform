# Table Grain & Relationship Specifications

This document defines the strict analytical grain, primary keys, foreign keys, and business definitions for all fact and dimension tables in the analytics platform.

---

## Fact Tables

### 1. `fct_orders`
* **Table**: `fct_orders`
* **Grain**: Exactly one row per customer order transaction.
* **Primary Key**: `order_id`
* **Foreign Keys**:
  * `customer_id` -> references `stg_customers` (order transaction token)
  * `customer_unique_id` -> references `dim_customer`
  * `order_purchase_date_key` -> references `dim_date`
  * `customer_zip_code_prefix` -> references `dim_location`
* **Business Meaning**: Captures consolidated order commercial outcomes, financial measures (GMV, freight, total order value), payment summaries, review scores, and operational fulfillment flags.

---

### 2. `fct_order_items`
* **Table**: `fct_order_items`
* **Grain**: Exactly one row per individual item line within an order.
* **Primary Key**: `order_item_key` (Deterministic MD5 hash of `order_id` + `order_item_id`)
* **Foreign Keys**:
  * `order_id` -> references `fct_orders`
  * `product_id` -> references `dim_product`
  * `seller_id` -> references `dim_seller`
  * `customer_id` -> references `stg_customers`
  * `customer_unique_id` -> references `dim_customer`
  * `order_purchase_date_key` -> references `dim_date`
* **Business Meaning**: Contains granular line-item prices, freight charges, shipping deadlines, and seller-to-buyer transit route indicators.

---

### 3. `fct_payments`
* **Table**: `fct_payments`
* **Grain**: Exactly one row per order payment transaction attempt.
* **Primary Key**: `payment_key` (Deterministic MD5 hash of `order_id` + `payment_sequential`)
* **Foreign Keys**:
  * `order_id` -> references `fct_orders`
  * `customer_id` -> references `stg_customers`
  * `order_purchase_date_key` -> references `dim_date`
* **Business Meaning**: Records payment instrument choices (credit card, boleto, voucher, debit), installment counts, and split-tender payment amounts.

---

### 4. `fct_reviews`
* **Table**: `fct_reviews`
* **Grain**: Exactly one row per customer satisfaction review submission.
* **Primary Key**: `review_key` (Deterministic MD5 hash of `review_id` + `order_id`)
* **Foreign Keys**:
  * `order_id` -> references `fct_orders`
  * `order_purchase_date_key` -> references `dim_date`
* **Business Meaning**: Captures customer satisfaction ratings on a 1-5 star scale, review comments, survey dispatch timestamps, and response latency.

---

### 5. `fct_delivery`
* **Table**: `fct_delivery`
* **Grain**: Exactly one row per delivered customer order.
* **Primary Key**: `order_id`
* **Foreign Keys**:
  * `customer_id` -> references `stg_customers`
  * `customer_unique_id` -> references `dim_customer`
  * `customer_zip_code_prefix` -> references `dim_location`
  * `order_purchase_date_key` -> references `dim_date`
* **Business Meaning**: Dedicated operational fulfillment fact tracking carrier dispatch time, transit time, delivery SLA delay days, and on-time delivery flags.

---

## Dimension Tables

### 6. `dim_customer`
* **Table**: `dim_customer`
* **Grain**: Exactly one row per unique real-world human customer.
* **Primary Key**: `customer_unique_id`
* **Foreign Keys**: `primary_zip_code_prefix` -> references `dim_location`
* **Business Meaning**: Represents persistent customer identities across multiple orders. Tracks lifetime order frequency, lifetime spend, customer lifespan, and RFM behavioral segmentation.

---

### 7. `dim_product`
* **Table**: `dim_product`
* **Grain**: Exactly one row per catalog product SKU.
* **Primary Key**: `product_id`
* **Foreign Keys**: None (root dimension)
* **Business Meaning**: Contains product catalog attributes, English category translations, physical weight and volume, freight sizing tiers, and historical units sold.

---

### 8. `dim_seller`
* **Table**: `dim_seller`
* **Grain**: Exactly one row per marketplace merchant seller.
* **Primary Key**: `seller_id`
* **Foreign Keys**: `seller_zip_code_prefix` -> references `dim_location`
* **Business Meaning**: Contains merchant profiles, geographic origin, lifetime revenue performance tiers, on-time SLA fulfillment rates, and customer review ratings.

---

### 9. `dim_date`
* **Table**: `dim_date`
* **Grain**: Exactly one row per calendar day.
* **Primary Key**: `date_key` (YYYYMMDD integer)
* **Foreign Keys**: None (time spine)
* **Business Meaning**: Official enterprise date dimension supporting time intelligence calculations (MoM, YoY, YTD), day-of-week seasonality, and calendar reporting.

---

### 10. `dim_location`
* **Table**: `dim_location`
* **Grain**: Exactly one row per Brazilian 5-digit zip code prefix.
* **Primary Key**: `zip_code_prefix`
* **Foreign Keys**: None (geographic lookup)
* **Business Meaning**: Deduplicated geographic coordinate centroids (average latitude and longitude), primary city name, state abbreviation, and Brazilian IBGE macro-regions.
