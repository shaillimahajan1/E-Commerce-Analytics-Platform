# Dimensional Data Model Specification

## 1. Dimensional Modeling Approach

The platform implements a **Kimball Star Schema** dimensional model. In contrast to 3NF transactional models (which prioritize insert performance and minimize redundancy at the expense of query complexity and joins), the dimensional star schema is optimized specifically for analytical queries, business metric aggregation, and BI dashboard responsiveness.

```mermaid
erDiagram
    dim_date ||--o{ fct_orders : "order_purchase_date_key"
    dim_date ||--o{ fct_order_items : "order_purchase_date_key"
    dim_customer ||--o{ fct_orders : "customer_unique_id"
    dim_product ||--o{ fct_order_items : "product_id"
    dim_seller ||--o{ fct_order_items : "seller_id"
    dim_location ||--o{ fct_orders : "customer_zip_code_prefix"
    fct_orders ||--o{ fct_order_items : "order_id"
    fct_orders ||--o{ fct_payments : "order_id"
    fct_orders ||--o{ fct_reviews : "order_id"
    fct_orders ||--|| fct_delivery : "order_id"

    dim_date {
        int date_key PK
        date date_day
        int year
        string month_name
        string year_month
        int is_weekend
    }

    dim_customer {
        string customer_unique_id PK
        timestamp first_order_timestamp
        int lifetime_order_count
        double lifetime_order_value
        string rfm_segment
    }

    dim_product {
        string product_id PK
        string product_category_name_english
        double product_weight_g
        double product_volume_cm3
        string freight_size_tier
    }

    dim_seller {
        string seller_id PK
        string seller_state
        double lifetime_revenue
        double on_time_rate_pct
        string seller_revenue_tier
    }

    dim_location {
        string zip_code_prefix PK
        string primary_city
        string primary_state
        string macro_region
        double avg_latitude
        double avg_longitude
    }

    fct_orders {
        string order_id PK
        string customer_unique_id FK
        int order_purchase_date_key FK
        double gross_merchandise_value
        double total_freight_value
        double total_order_value
        string order_status
        int is_on_time
        int is_late_delivery
    }

    fct_order_items {
        string order_item_key PK
        string order_id FK
        string product_id FK
        string seller_id FK
        double item_price
        double item_freight_value
        int is_same_state_shipping
    }

    fct_payments {
        string payment_key PK
        string order_id FK
        string payment_type
        int payment_installments
        double payment_value
    }

    fct_reviews {
        string review_key PK
        string order_id FK
        int review_score
        string review_comment_message
        int review_response_time_hours
    }

    fct_delivery {
        string order_id PK
        double actual_delivery_days
        double estimated_delivery_days
        double delivery_delay_days
        int is_on_time
        int is_late_delivery
    }
```

---

## 2. Fact Tables

### 2.1 `fct_orders`
* **Grain**: One row per customer order transaction (`order_id`).
* **Primary Key**: `order_id`
* **Foreign Keys**: `customer_unique_id`, `order_purchase_date_key`, `customer_zip_code_prefix`.
* **Business Purpose**: Core commercial transaction reporting. Contains consolidated order financial measures (GMV, freight, total order value), payment summaries, satisfaction ratings, and operational fulfillment flags.

### 2.2 `fct_order_items`
* **Grain**: One row per individual item line within an order (`order_item_key` = MD5 of `order_id` + `order_item_id`).
* **Primary Key**: `order_item_key`
* **Foreign Keys**: `order_id`, `product_id`, `seller_id`, `customer_id`, `order_purchase_date_key`.
* **Business Purpose**: Granular product-level analysis, pricing dynamics, unit volume, and seller-to-buyer shipping route dynamics.

### 2.3 `fct_payments`
* **Grain**: One row per payment instrument attempt (`payment_key` = MD5 of `order_id` + `payment_sequential`).
* **Primary Key**: `payment_key`
* **Foreign Keys**: `order_id`.
* **Business Purpose**: Tender analysis, payment installment behavior, voucher redemptions, and credit card share.

### 2.4 `fct_reviews`
* **Grain**: One row per customer review submission (`review_key` = MD5 of `review_id` + `order_id`).
* **Primary Key**: `review_key`
* **Foreign Keys**: `order_id`.
* **Business Purpose**: Customer satisfaction ratings (1-5), feedback sentiment analysis, and response latency.

### 2.5 `fct_delivery`
* **Grain**: One row per delivered order (`order_id`).
* **Primary Key**: `order_id`
* **Foreign Keys**: `customer_id`.
* **Business Purpose**: Operational supply chain analysis, carrier transit durations, promised SLA accuracy, and delivery delay tracking.

---

## 3. Dimension Tables

### 3.1 `dim_customer`
* **Grain**: One row per persistent unique human customer (`customer_unique_id`).
* **Primary Key**: `customer_unique_id`
* **Business Purpose**: Customer lifetime value, repeat buyer identification, RFM segmentation (Champions, Loyal, Recent, At Risk, Hibernating), and regional residence.

### 3.2 `dim_product`
* **Grain**: One row per unique catalog product (`product_id`).
* **Primary Key**: `product_id`
* **Business Purpose**: Product merchandising, English category classifications, physical dimensions, weight, and volumetric freight sizing tiers.

### 3.3 `dim_seller`
* **Grain**: One row per marketplace seller (`seller_id`).
* **Primary Key**: `seller_id`
* **Business Purpose**: Merchant scorecarding, lifetime revenue tiering (Enterprise, Growth, Established, Long Tail), on-time fulfillment rates, and customer review averages.

### 3.4 `dim_date`
* **Grain**: One row per calendar day.
* **Primary Key**: `date_key` (YYYYMMDD integer)
* **Business Purpose**: Time-series analytics, period-over-period comparisons (MoM, YoY), day-of-week seasonality, and calendar attributes.

### 3.5 `dim_location`
* **Grain**: One row per Brazilian 5-digit zip code prefix (`zip_code_prefix`).
* **Primary Key**: `zip_code_prefix`
* **Business Purpose**: Geographic spatial mapping, centroid latitude/longitude coordinates, state groupings, and official Brazilian IBGE macro-regions (Southeast, South, Northeast, Central-West, North).
