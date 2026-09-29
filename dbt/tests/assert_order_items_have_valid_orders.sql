-- Referential Integrity Test: All order items must reference an existing order
-- Returns orphan line items (dbt expects 0 rows for test to pass)
select
    i.order_item_key,
    i.order_id
from {{ ref('stg_order_items') }} i
left join {{ ref('stg_orders') }} o on i.order_id = o.order_id
where o.order_id is null
