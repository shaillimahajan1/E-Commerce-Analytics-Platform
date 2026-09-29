with seller_base as (
    select * from {{ ref('dim_seller') }}
),

total_marketplace as (
    select sum(lifetime_revenue) as total_marketplace_revenue
    from seller_base
),

ranked_sellers as (
    select
        s.seller_id,
        s.seller_city,
        s.seller_state,
        s.seller_revenue_tier,
        s.lifetime_units_sold,
        s.lifetime_orders_count,
        s.distinct_customers_served,
        s.distinct_products_offered,
        s.lifetime_revenue,
        s.lifetime_freight_collected,
        s.average_item_price,
        s.delivered_orders_count,
        s.on_time_orders_count,
        s.late_orders_count,
        s.on_time_rate_pct,
        s.average_delivery_days,
        s.average_review_score,
        s.total_reviews_received,
        
        -- Revenue Ranking
        rank() over (order by s.lifetime_revenue desc) as revenue_rank,
        dense_rank() over (order by s.lifetime_orders_count desc) as order_volume_rank,
        
        -- Marketplace Revenue Share %
        round((s.lifetime_revenue / nullif(m.total_marketplace_revenue, 0)) * 100, 4) as revenue_share_pct
    from seller_base s
    cross join total_marketplace m
)

select * from ranked_sellers
