-- Business Rule Test: Payment values must not be negative
-- Returns failing records (dbt expects 0 rows for test to pass)
select
    payment_key,
    order_id,
    payment_value
from {{ ref('stg_payments') }}
where payment_value < 0.0
