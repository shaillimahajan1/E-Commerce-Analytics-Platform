with sellers as (
    select * from {{ ref('stg_sellers') }}
),

metrics as (
    select * from {{ ref('int_seller_metrics') }}
),

final as (
    select
        s.seller_id,
        s.seller_zip_code_prefix,
        s.seller_city,
        s.seller_state,
        
        coalesce(m.total_units_sold, 0) as lifetime_units_sold,
        coalesce(m.total_orders_count, 0) as lifetime_orders_count,
        coalesce(m.distinct_customers_count, 0) as distinct_customers_served,
        coalesce(m.distinct_products_offered, 0) as distinct_products_offered,
        coalesce(m.total_revenue, 0.0) as lifetime_revenue,
        coalesce(m.total_freight_collected, 0.0) as lifetime_freight_collected,
        coalesce(m.avg_item_price, 0.0) as average_item_price,
        coalesce(m.delivered_orders_count, 0) as delivered_orders_count,
        coalesce(m.on_time_orders_count, 0) as on_time_orders_count,
        coalesce(m.late_orders_count, 0) as late_orders_count,
        coalesce(m.on_time_rate_pct, 100.0) as on_time_rate_pct,
        coalesce(m.avg_delivery_days, 0.0) as average_delivery_days,
        coalesce(m.avg_seller_review_score, 0.0) as average_review_score,
        coalesce(m.total_seller_reviews, 0) as total_reviews_received,
        
        -- Seller Tier Classification
        case
            when coalesce(m.total_revenue, 0.0) >= 50000 then 'Tier 1 - Enterprise (R$50k+)'
            when coalesce(m.total_revenue, 0.0) >= 10000 then 'Tier 2 - Growth (R$10k-50k)'
            when coalesce(m.total_revenue, 0.0) >= 1000 then 'Tier 3 - Established (R$1k-10k)'
            else 'Tier 4 - Long Tail (<R$1k)'
        end as seller_revenue_tier
    from sellers s
    left join metrics m on s.seller_id = m.seller_id
)

select * from final
