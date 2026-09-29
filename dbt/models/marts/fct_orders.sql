with orders_enriched as (
    select * from {{ ref('int_orders_enriched') }}
),

delivery_metrics as (
    select * from {{ ref('int_delivery_metrics') }}
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.customer_unique_id,
        cast(strftime(cast(o.order_purchase_timestamp as date), '%Y%m%d') as integer) as order_purchase_date_key,
        o.customer_city,
        o.customer_state,
        o.customer_zip_code_prefix,
        o.order_status,
        
        -- Timestamps
        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        
        -- Order Value & Financial Measures (BRL)
        o.total_item_count,
        o.distinct_products_count,
        o.distinct_sellers_count,
        o.total_items_value as gross_merchandise_value,
        o.total_freight_value,
        o.total_order_cost as total_order_value,
        o.total_payment_value,
        o.payment_attempts_count,
        o.max_payment_installments,
        
        -- Payment flags
        o.has_credit_card_payment,
        o.has_boleto_payment,
        o.has_voucher_payment,
        o.has_debit_card_payment,
        
        -- Review Measures
        o.review_count,
        o.avg_review_score,
        o.has_review_comment,
        
        -- Operational Delivery SLA Measures
        d.days_to_approve,
        d.days_to_carrier,
        d.days_transit,
        d.actual_delivery_days,
        d.estimated_delivery_days,
        d.delivery_delay_days,
        coalesce(d.is_on_time, 0) as is_on_time,
        coalesce(d.is_late_delivery, 0) as is_late_delivery
    from orders_enriched o
    left join delivery_metrics d on o.order_id = d.order_id
)

select * from final
