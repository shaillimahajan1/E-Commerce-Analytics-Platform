with delivery as (
    select * from {{ ref('int_delivery_metrics') }}
),

orders as (
    select
        order_id,
        customer_unique_id,
        customer_city,
        customer_state,
        customer_zip_code_prefix,
        distinct_sellers_count,
        total_items_value,
        total_freight_value,
        avg_review_score
    from {{ ref('int_orders_enriched') }}
),

final as (
    select
        d.order_id,
        d.customer_id,
        o.customer_unique_id,
        cast(strftime(cast(d.order_purchase_timestamp as date), '%Y%m%d') as integer) as order_purchase_date_key,
        o.customer_city,
        o.customer_state,
        o.customer_zip_code_prefix,
        
        -- Delivery milestones
        d.order_purchase_timestamp,
        d.order_approved_at,
        d.order_delivered_carrier_date,
        d.order_delivered_customer_date,
        d.order_estimated_delivery_date,
        
        -- Durations & SLA
        d.days_to_approve,
        d.days_to_carrier,
        d.days_transit,
        d.actual_delivery_days,
        d.estimated_delivery_days,
        d.delivery_delay_days,
        d.is_on_time,
        d.is_late_delivery,
        
        -- Associated metrics
        o.total_freight_value,
        o.total_items_value,
        o.avg_review_score
    from delivery d
    inner join orders o on d.order_id = o.order_id
)

select * from final
