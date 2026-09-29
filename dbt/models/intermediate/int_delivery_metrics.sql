with orders as (
    select * from {{ ref('stg_orders') }}
),

final as (
    select
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,
        
        -- Operational duration metrics in fractional days
        case 
            when order_approved_at is not null and order_purchase_timestamp is not null
            then {{ datediff('order_purchase_timestamp', 'order_approved_at', 'day') }}
            else null 
        end as days_to_approve,

        case 
            when order_delivered_carrier_date is not null and order_purchase_timestamp is not null
            then {{ datediff('order_purchase_timestamp', 'order_delivered_carrier_date', 'day') }}
            else null 
        end as days_to_carrier,

        case 
            when order_delivered_customer_date is not null and order_delivered_carrier_date is not null
            then {{ datediff('order_delivered_carrier_date', 'order_delivered_customer_date', 'day') }}
            else null 
        end as days_transit,

        case 
            when order_delivered_customer_date is not null and order_purchase_timestamp is not null
            then {{ datediff('order_purchase_timestamp', 'order_delivered_customer_date', 'day') }}
            else null 
        end as actual_delivery_days,

        case 
            when order_estimated_delivery_date is not null and order_purchase_timestamp is not null
            then {{ datediff('order_purchase_timestamp', 'order_estimated_delivery_date', 'day') }}
            else null 
        end as estimated_delivery_days,

        -- SLA delay calculation
        case 
            when order_delivered_customer_date is not null and order_estimated_delivery_date is not null
            then {{ datediff('order_estimated_delivery_date', 'order_delivered_customer_date', 'day') }}
            else null 
        end as delivery_delay_days,

        -- Performance flags
        case
            when order_delivered_customer_date is null then null
            when cast(order_delivered_customer_date as date) <= cast(order_estimated_delivery_date as date) then 1
            else 0
        end as is_on_time,

        case
            when order_delivered_customer_date is null then null
            when cast(order_delivered_customer_date as date) > cast(order_estimated_delivery_date as date) then 1
            else 0
        end as is_late_delivery
    from orders
    where order_status = 'delivered'
)

select * from final
