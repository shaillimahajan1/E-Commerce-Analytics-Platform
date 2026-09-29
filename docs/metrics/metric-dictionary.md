# Enterprise Metric Dictionary

This metric dictionary provides the canonical enterprise business definitions, formulas, underlying data sources, and analytical boundaries for all metrics reported across the analytics platform.

---

## 1. Commercial & Financial Metrics

### 1.1 Gross Merchandise Value (GMV)
* **Definition**: Total monetary value of products sold through the marketplace, exclusive of shipping and freight fees, before cancellations or returns.
* **SQL Expression**: `SUM(fct_order_items.item_price)`
* **Layer Source**: `fct_order_items` / `fct_orders.gross_merchandise_value`
* **Unit**: Brazilian Real (BRL / R$)
* **Analytical Limitation**: GMV measures transaction top-line merchandise scale; it does NOT represent platform net profit or margin, as merchant commissions and wholesale costs are not tracked in this dataset.

### 1.2 Total Freight Value
* **Definition**: Aggregate logistics and delivery shipping fees charged to buyers across all fulfilled orders.
* **SQL Expression**: `SUM(fct_orders.total_freight_value)`
* **Layer Source**: `fct_orders`
* **Unit**: Brazilian Real (BRL / R$)

### 1.3 Total Revenue (Gross Order Value)
* **Definition**: Cumulative financial transaction gross value, representing the exact sum of merchandise value and customer-paid freight.
* **SQL Expression**: `SUM(fct_orders.gross_merchandise_value + fct_orders.total_freight_value)`
* **Layer Source**: `fct_orders.total_order_value`
* **Unit**: Brazilian Real (BRL / R$)

### 1.4 Average Order Value (AOV)
* **Definition**: Mean merchandise spending per completed order transaction.
* **SQL Expression**: `DIVIDE(SUM(gross_merchandise_value), COUNT(DISTINCT order_id))`
* **Layer Source**: `fct_orders`
* **Unit**: Brazilian Real (BRL / R$)
* **Guideline**: Calculated using merchandise GMV (excluding freight) to reflect customer purchasing appetite rather than shipping distance inflation.

---

## 2. Customer Lifecycle & Retention Metrics

### 2.1 Unique Customers
* **Definition**: Count of distinct real-world human buyers identified across multi-year purchase history.
* **SQL Expression**: `COUNT(DISTINCT dim_customer.customer_unique_id)`
* **Layer Source**: `dim_customer` / `fct_orders.customer_unique_id`
* **Unit**: Integer
* **Crucial Note**: Differs from `customer_id`, which is merely an ephemeral transaction session token assigned per order.

### 2.2 Repeat Customer Rate %
* **Definition**: Proportion of the persistent customer base that has completed more than one lifetime purchase order.
* **SQL Expression**: `DIVIDE(COUNT(DISTINCT CASE WHEN lifetime_order_count > 1 THEN customer_unique_id END), COUNT(DISTINCT customer_unique_id)) * 100`
* **Layer Source**: `dim_customer`
* **Unit**: Percentage (`0.0%`)

### 2.3 Cohort Retention Rate %
* **Definition**: Percentage of buyers from an initial acquisition month (Month 0) who place at least one subsequent order in elapsed month $N$.
* **Formula**: $\text{Retention Rate}_{c, m} = \frac{\text{Active Customers in Month } m}{\text{Total Cohort Size in Month 0}} \times 100$
* **Layer Source**: `mart_customer_retention`
* **Unit**: Percentage (`0.0%`)

---

## 3. Logistics & Fulfillment SLA Metrics

### 3.1 Actual Delivery Days
* **Definition**: Elapsed calendar duration in days from customer purchase timestamp to carrier doorstep delivery.
* **SQL Expression**: `datediff('day', order_purchase_timestamp, order_delivered_customer_date)`
* **Layer Source**: `fct_delivery.actual_delivery_days`
* **Unit**: Days (`0.0 days`)
* **Population**: Only defined for delivered orders (`order_status = 'delivered'`).

### 3.2 Estimated Promised Delivery Days
* **Definition**: Promised SLA fulfillment duration in days communicated to the customer at checkout.
* **SQL Expression**: `datediff('day', order_purchase_timestamp, order_estimated_delivery_date)`
* **Layer Source**: `fct_delivery.estimated_delivery_days`
* **Unit**: Days (`0.0 days`)

### 3.3 On-Time Delivery %
* **Definition**: Proportion of delivered orders where actual doorstep delivery occurred on or before the promised estimated delivery date.
* **SQL Expression**: `DIVIDE(SUM(is_on_time), COUNT(*)) * 100`
* **Layer Source**: `fct_delivery`
* **Unit**: Percentage (`0.0%`)

### 3.4 Late Delivery %
* **Definition**: Proportion of delivered orders where actual doorstep delivery exceeded the promised estimated delivery date.
* **SQL Expression**: `DIVIDE(SUM(is_late_delivery), COUNT(*)) * 100`
* **Layer Source**: `fct_delivery`
* **Unit**: Percentage (`0.0%`)

---

## 4. Merchant & Product Metrics

### 4.1 Merchant Fulfillment On-Time %
* **Definition**: Percentage of orders fulfilled by a specific merchant that arrived on or before the customer SLA deadline.
* **SQL Expression**: `mart_seller_performance.on_time_rate_pct`
* **Layer Source**: `dim_seller` / `mart_seller_performance`
* **Unit**: Percentage (`0.0%`)

### 4.2 Customer Satisfaction Score (CSAT / Average Review)
* **Definition**: Arithmetic mean rating awarded by buyers on a 1 to 5 star scale.
* **SQL Expression**: `AVG(fct_reviews.review_score)`
* **Layer Source**: `fct_reviews`
* **Unit**: Decimal (`1.00 - 5.00`)

### 4.3 Pareto Revenue Contribution %
* **Definition**: Running cumulative percentage of total catalog GMV generated by products ranked in descending order of lifetime sales.
* **SQL Expression**: `SUM(lifetime_revenue) OVER (ORDER BY lifetime_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) / Total_GMV * 100`
* **Layer Source**: `mart_product_performance.cumulative_revenue_pct`
* **Unit**: Percentage (`0.0%`)
