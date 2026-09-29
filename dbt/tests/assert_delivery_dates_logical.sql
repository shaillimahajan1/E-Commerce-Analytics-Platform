-- Business Rule Test: Delivery date must be on or after purchase timestamp
-- Returns failing records (dbt expects 0 rows for test to pass)
select
    order_id,
    order_purchase_timestamp,
    order_delivered_customer_date
from {{ ref('stg_orders') }}
where order_delivered_customer_date is not null
  and order_purchase_timestamp is not null
  and order_delivered_customer_date < order_purchase_timestamp
