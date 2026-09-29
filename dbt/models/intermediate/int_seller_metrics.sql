with items as (
    select * from {{ ref('int_order_items_enriched') }}
),

delivery as (
    select * from {{ ref('int_delivery_metrics') }}
),

reviews as (
    select * from {{ ref('stg_reviews') }}
),

seller_reviews as (
    select
        i.seller_id,
        round(avg(r.review_score), 2) as avg_seller_review_score,
        count(distinct r.review_id) as total_seller_reviews
    from items i
    inner join reviews r on i.order_id = r.order_id
    group by i.seller_id
),

seller_deliveries as (
    select
        i.seller_id,
        count(distinct d.order_id) as delivered_orders_count,
        sum(d.is_on_time) as on_time_orders_count,
        sum(d.is_late_delivery) as late_orders_count,
        round(avg(d.actual_delivery_days), 2) as avg_delivery_days
    from items i
    inner join delivery d on i.order_id = d.order_id
    group by i.seller_id
),

seller_sales as (
    select
        i.seller_id,
        max(i.seller_city) as seller_city,
        max(i.seller_state) as seller_state,
        count(i.order_item_key) as total_units_sold,
        count(distinct i.order_id) as total_orders_count,
        count(distinct i.customer_unique_id) as distinct_customers_count,
        count(distinct i.product_id) as distinct_products_offered,
        round(sum(i.price), 2) as total_revenue,
        round(sum(i.freight_value), 2) as total_freight_collected,
        round(avg(i.price), 2) as avg_item_price,
        min(i.order_purchase_timestamp) as first_active_date,
        max(i.order_purchase_timestamp) as latest_active_date
    from items i
    group by i.seller_id
),

final as (
    select
        ss.seller_id,
        ss.seller_city,
        ss.seller_state,
        ss.total_units_sold,
        ss.total_orders_count,
        ss.distinct_customers_count,
        ss.distinct_products_offered,
        ss.total_revenue,
        ss.total_freight_collected,
        ss.avg_item_price,
        ss.first_active_date,
        ss.latest_active_date,
        coalesce(sd.delivered_orders_count, 0) as delivered_orders_count,
        coalesce(sd.on_time_orders_count, 0) as on_time_orders_count,
        coalesce(sd.late_orders_count, 0) as late_orders_count,
        round(
            case 
                when coalesce(sd.delivered_orders_count, 0) > 0 
                then (cast(sd.on_time_orders_count as double) / sd.delivered_orders_count) * 100 
                else 100.0 
            end, 2
        ) as on_time_rate_pct,
        coalesce(sd.avg_delivery_days, 0.0) as avg_delivery_days,
        coalesce(sr.avg_seller_review_score, 0.0) as avg_seller_review_score,
        coalesce(sr.total_seller_reviews, 0) as total_seller_reviews
    from seller_sales ss
    left join seller_deliveries sd on ss.seller_id = sd.seller_id
    left join seller_reviews sr on ss.seller_id = sr.seller_id
)

select * from final
