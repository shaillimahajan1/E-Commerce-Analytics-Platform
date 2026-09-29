with orders_enriched as (
    select * from {{ ref('int_orders_enriched') }}
),

dataset_boundary as (
    select max(order_purchase_timestamp) as max_dataset_timestamp
    from orders_enriched
),

customer_aggregates as (
    select
        o.customer_unique_id,
        min(o.order_purchase_timestamp) as first_order_timestamp,
        max(o.order_purchase_timestamp) as latest_order_timestamp,
        count(distinct o.order_id) as lifetime_order_count,
        round(sum(o.total_order_cost), 2) as lifetime_order_value,
        round(sum(o.total_freight_value), 2) as lifetime_freight_value,
        round(sum(o.total_payment_value), 2) as lifetime_payment_value,
        round(avg(o.total_order_cost), 2) as average_order_value,
        round(avg(o.avg_review_score), 2) as average_review_score_given,
        max(o.customer_state) as primary_customer_state,
        max(o.customer_city) as primary_customer_city,
        max(o.customer_zip_code_prefix) as primary_zip_code_prefix
    from orders_enriched o
    group by o.customer_unique_id
),

final as (
    select
        ca.customer_unique_id,
        ca.first_order_timestamp,
        ca.latest_order_timestamp,
        ca.lifetime_order_count,
        ca.lifetime_order_value,
        ca.lifetime_freight_value,
        ca.lifetime_payment_value,
        ca.average_order_value,
        ca.average_review_score_given,
        ca.primary_customer_state,
        ca.primary_customer_city,
        ca.primary_zip_code_prefix,
        
        -- Behavioral segmentation flags
        case when ca.lifetime_order_count > 1 then 1 else 0 end as is_repeat_customer,
        {{ datediff('ca.first_order_timestamp', 'ca.latest_order_timestamp', 'day') }} as customer_lifespan_days,
        {{ datediff('ca.latest_order_timestamp', 'db.max_dataset_timestamp', 'day') }} as days_since_last_order
    from customer_aggregates ca
    cross join dataset_boundary db
)

select * from final
