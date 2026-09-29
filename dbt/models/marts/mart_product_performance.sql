with products as (
    select * from {{ ref('dim_product') }}
),

total_catalog as (
    select sum(lifetime_revenue) as total_catalog_revenue
    from products
),

ranked_products as (
    select
        p.product_id,
        p.product_category_name_english,
        p.product_category_name_portuguese,
        p.freight_size_tier,
        p.lifetime_units_sold,
        p.lifetime_orders_count,
        p.lifetime_revenue,
        p.lifetime_freight_generated,
        p.average_unit_price,
        p.average_review_score,
        p.total_reviews_count,
        
        -- Category Rankings
        rank() over (
            partition by p.product_category_name_english 
            order by p.lifetime_revenue desc
        ) as category_revenue_rank,
        
        -- Overall Catalog Revenue Ranking
        rank() over (order by p.lifetime_revenue desc) as overall_revenue_rank,
        
        -- Running cumulative revenue for Pareto analysis
        sum(p.lifetime_revenue) over (
            order by p.lifetime_revenue desc
            rows between unbounded preceding and current row
        ) as cumulative_revenue
    from products p
),

final as (
    select
        rp.product_id,
        rp.product_category_name_english,
        rp.product_category_name_portuguese,
        rp.freight_size_tier,
        rp.lifetime_units_sold,
        rp.lifetime_orders_count,
        rp.lifetime_revenue,
        rp.lifetime_freight_generated,
        rp.average_unit_price,
        rp.average_review_score,
        rp.total_reviews_count,
        rp.category_revenue_rank,
        rp.overall_revenue_rank,
        rp.cumulative_revenue,
        
        -- Cumulative Pareto Share %
        round((rp.cumulative_revenue / nullif(tc.total_catalog_revenue, 0)) * 100, 2) as cumulative_revenue_pct,
        
        -- Pareto classification: 80% of revenue from top 20% products
        case
            when (rp.cumulative_revenue / nullif(tc.total_catalog_revenue, 0)) <= 0.80 then 'Top 80% Revenue Contributor (Pareto Core)'
            else 'Long Tail Catalog'
        end as pareto_segment
    from ranked_products rp
    cross join total_catalog tc
)

select * from final
