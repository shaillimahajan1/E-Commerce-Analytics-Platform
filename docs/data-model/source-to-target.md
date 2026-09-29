# Source to Target Mapping

This document provides column-level mapping from raw landed CSV source tables through dbt transformations to final analytical fact and dimension models.

---

## 1. `raw_orders` -> `stg_orders` -> `fct_orders`

| Source Table | Source Column | Target Table | Target Column | Transformation | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `raw_orders` | `order_id` | `fct_orders` | `order_id` | `cast(order_id as varchar)` | Unique order identifier. |
| `raw_orders` | `customer_id` | `fct_orders` | `customer_id` | `cast(customer_id as varchar)` | Transaction token linking to customer order session. |
| `raw_customers`| `customer_unique_id`| `fct_orders` | `customer_unique_id` | `join stg_customers on customer_id` | Persistent real-world customer identifier. |
| `raw_orders` | `order_purchase_timestamp` | `fct_orders` | `order_purchase_date_key` | `cast(strftime(date, '%Y%m%d') as int)` | Integer foreign key linking to `dim_date`. |
| `raw_orders` | `order_status` | `fct_orders` | `order_status` | `lower(trim(order_status))` | Standardized order lifecycle status. |
| `raw_orders` | `order_purchase_timestamp` | `fct_orders` | `order_purchase_timestamp` | `cast(order_purchase_timestamp as timestamp)` | Precise UTC timestamp of order placement. |
| `raw_orders` | `order_approved_at` | `fct_orders` | `order_approved_at` | `cast(order_approved_at as timestamp)` | Payment approval timestamp. |
| `raw_orders` | `order_delivered_carrier_date` | `fct_orders` | `order_delivered_carrier_date` | `cast(order_delivered_carrier_date as timestamp)` | Seller handover to carrier timestamp. |
| `raw_orders` | `order_delivered_customer_date` | `fct_orders` | `order_delivered_customer_date` | `cast(order_delivered_customer_date as timestamp)` | Doorstep delivery timestamp. |
| `raw_orders` | `order_estimated_delivery_date` | `fct_orders` | `order_estimated_delivery_date` | `cast(order_estimated_delivery_date as timestamp)` | Promised delivery SLA date committed at checkout. |
| `raw_order_items`| `price` | `fct_orders` | `gross_merchandise_value`| `round(sum(price), 2)` | Total merchandise value of items in order. |
| `raw_order_items`| `freight_value` | `fct_orders` | `total_freight_value` | `round(sum(freight_value), 2)` | Total shipping fees charged to customer. |
| `raw_order_items`| `price + freight_value` | `fct_orders` | `total_order_value` | `round(sum(price + freight_value), 2)` | Total financial gross order value. |
| `raw_payments` | `payment_value` | `fct_orders` | `total_payment_value` | `round(sum(payment_value), 2)` | Total payments collected across tenders. |
| `raw_reviews` | `review_score` | `fct_orders` | `avg_review_score` | `round(avg(review_score), 2)` | Average customer satisfaction score. |
| Derived | `delivered vs purchase` | `fct_orders` | `actual_delivery_days` | `datediff('day', purchase, delivered)` | Actual fulfillment duration in days. |
| Derived | `estimated vs purchase` | `fct_orders` | `estimated_delivery_days` | `datediff('day', purchase, estimated)` | Promised fulfillment duration in days. |
| Derived | `delivered vs estimated`| `fct_orders` | `is_on_time` | `case when delivered <= estimated then 1 else 0 end` | Binary flag indicating SLA compliance. |
| Derived | `delivered vs estimated`| `fct_orders` | `is_late_delivery` | `case when delivered > estimated then 1 else 0 end` | Binary flag indicating late delivery. |

---

## 2. `raw_order_items` -> `stg_order_items` -> `fct_order_items`

| Source Table | Source Column | Target Table | Target Column | Transformation | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `raw_order_items`| `order_id, order_item_id` | `fct_order_items` | `order_item_key` | `generate_surrogate_key(['order_id', 'order_item_id'])` | Primary key surrogate hash. |
| `raw_order_items`| `order_id` | `fct_order_items` | `order_id` | `cast(order_id as varchar)` | Parent order foreign key. |
| `raw_order_items`| `order_item_id` | `fct_order_items` | `order_item_id` | `cast(order_item_id as integer)` | Sequence number of item in order. |
| `raw_order_items`| `product_id` | `fct_order_items` | `product_id` | `cast(product_id as varchar)` | Product foreign key. |
| `raw_order_items`| `seller_id` | `fct_order_items` | `seller_id` | `cast(seller_id as varchar)` | Merchant seller foreign key. |
| `raw_order_items`| `shipping_limit_date` | `fct_order_items` | `shipping_limit_date` | `cast(shipping_limit_date as timestamp)` | Seller fulfillment dispatch deadline. |
| `raw_order_items`| `price` | `fct_order_items` | `item_price` | `cast(price as double)` | Unit merchandise price in BRL. |
| `raw_order_items`| `freight_value` | `fct_order_items` | `item_freight_value` | `cast(freight_value as double)` | Freight fee allocated to item. |
| `raw_sellers`, `raw_customers` | `seller_state, customer_state` | `fct_order_items` | `is_same_state_shipping` | `case when seller_state = customer_state then 1 else 0 end` | Flag identifying local vs cross-border transit. |

---

## 3. `raw_customers` -> `stg_customers` -> `dim_customer`

| Source Table | Source Column | Target Table | Target Column | Transformation | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `raw_customers` | `customer_unique_id` | `dim_customer` | `customer_unique_id` | `cast(customer_unique_id as varchar)` | Persistent real-world customer identifier. |
| `raw_orders` | `order_purchase_timestamp` | `dim_customer` | `first_order_timestamp` | `min(order_purchase_timestamp)` | Acquisition order timestamp. |
| `raw_orders` | `order_purchase_timestamp` | `dim_customer` | `latest_order_timestamp` | `max(order_purchase_timestamp)` | Most recent order timestamp. |
| `raw_orders` | `order_id` | `dim_customer` | `lifetime_order_count` | `count(distinct order_id)` | Total orders placed across lifetime. |
| `raw_orders` | `total_order_cost` | `dim_customer` | `lifetime_order_value` | `round(sum(total_order_cost), 2)` | Total monetary revenue contributed. |
| Derived | `lifetime_order_count` | `dim_customer` | `is_repeat_customer` | `case when count > 1 then 1 else 0 end` | Flag identifying repeat purchaser. |
| Derived | `first vs latest` | `dim_customer` | `customer_lifespan_days` | `datediff('day', first, latest)` | Elapsed active lifespan in days. |
| Derived | `latest vs max dataset` | `dim_customer` | `days_since_last_order` | `datediff('day', latest, max_date)` | Recency metric for RFM analysis. |
| Derived | `RFM Quintiles` | `dim_customer` | `rfm_segment` | `Conditional classification` | Assigned behavioral cohort (e.g. Champions, Loyal). |

---

## 4. `raw_products` -> `stg_products` -> `dim_product`

| Source Table | Source Column | Target Table | Target Column | Transformation | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `raw_products` | `product_id` | `dim_product` | `product_id` | `cast(product_id as varchar)` | Primary catalog SKU identifier. |
| `raw_category_translation` | `product_category_name_english` | `dim_product` | `product_category_name_english` | `coalesce(translation, raw, 'unlabeled')` | Standardized English category name. |
| `raw_products` | `product_name_lenght` | `dim_product` | `product_name_length` | `cast(lenght as integer)` | Character length of product title. |
| `raw_products` | `product_weight_g` | `dim_product` | `product_weight_g` | `cast(weight as double)` | Weight in grams. |
| `raw_products` | `length, height, width` | `dim_product` | `product_volume_cm3` | `round(length * height * width, 2)` | Volumetric space in cubic centimeters. |
| Derived | `weight & volume` | `dim_product` | `freight_size_tier` | `Case logic on weight & volume` | Logistics tier (Bulky, Medium, Standard). |

---

## 5. `raw_geolocation` -> `stg_geolocation` -> `dim_location`

| Source Table | Source Column | Target Table | Target Column | Transformation | Business Meaning |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `raw_geolocation` | `geolocation_zip_code_prefix` | `dim_location` | `zip_code_prefix` | `cast(prefix as varchar)` | 5-digit zip code prefix. |
| `raw_geolocation` | `geolocation_lat` | `dim_location` | `avg_latitude` | `round(avg(lat), 6)` | Centroid latitude coordinate. |
| `raw_geolocation` | `geolocation_lng` | `dim_location` | `avg_longitude` | `round(avg(lng), 6)` | Centroid longitude coordinate. |
| `raw_geolocation` | `geolocation_city` | `dim_location` | `primary_city` | `Mode city via window rank` | Most frequent city name for prefix. |
| `raw_geolocation` | `geolocation_state`| `dim_location` | `primary_state` | `upper(trim(state))` | 2-letter state code. |
| Derived | `primary_state` | `dim_location` | `macro_region` | `IBGE regional mapping` | Official Brazilian macro-region. |
