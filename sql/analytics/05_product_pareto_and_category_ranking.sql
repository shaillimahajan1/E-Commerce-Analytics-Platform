-- ==============================================================================
-- 05. PRODUCT PARETO ANALYSIS & CATEGORY RANKINGS
-- ==============================================================================
-- Objectives:
-- 1. Identify product catalog concentration (80/20 Pareto principle verification).
-- 2. Rank products by Gross Merchandise Value within each product category.
-- 3. Analyze category performance across units sold, GMV, and customer review scores.
-- 4. Calculate catalog contribution of the Pareto Core vs Long Tail.
-- ==============================================================================

-- PART 1: Macro Pareto Principle Verification
with pareto_summary as (
    select
        pareto_segment,
        count(*) as total_sku_count,
        sum(lifetime_units_sold) as total_units_sold,
        round(sum(lifetime_revenue), 2) as total_segment_revenue,
        round(avg(average_price), 2) as avg_product_price,
        round(avg(average_review_score), 2) as avg_review_score
    from ecommerce_analytics_marts.mart_product_performance
    group by pareto_segment
),

total_catalog as (
    select
        count(*) as catalog_skus,
        sum(lifetime_revenue) as total_catalog_revenue
    from ecommerce_analytics_marts.mart_product_performance
)

select
    p.pareto_segment,
    p.total_sku_count,
    round((cast(p.total_sku_count as double) / c.catalog_skus) * 100, 2) as sku_share_pct,
    p.total_units_sold,
    p.total_segment_revenue,
    round((p.total_segment_revenue / c.total_catalog_revenue) * 100, 2) as revenue_share_pct,
    p.avg_product_price,
    p.avg_review_score
from pareto_summary p
cross join total_catalog c
order by p.total_segment_revenue desc;


-- PART 2: Top 3 Products within the Top 10 Marketplace Categories
with category_totals as (
    select
        product_category_name_english,
        round(sum(lifetime_revenue), 2) as category_total_revenue,
        rank() over (order by sum(lifetime_revenue) desc) as category_rank
    from ecommerce_analytics_marts.dim_product
    where product_category_name_english != 'unlabeled'
    group by product_category_name_english
)

select
    ct.category_rank,
    p.product_category_name_english,
    p.category_revenue_rank,
    p.product_id,
    p.freight_size_tier,
    p.lifetime_units_sold,
    p.lifetime_revenue as product_revenue,
    round((p.lifetime_revenue / ct.category_total_revenue) * 100, 2) as category_revenue_share_pct,
    p.average_unit_price,
    p.average_review_score
from ecommerce_analytics_marts.mart_product_performance p
inner join category_totals ct on p.product_category_name_english = ct.product_category_name_english
where ct.category_rank <= 10
  and p.category_revenue_rank <= 3
order by ct.category_rank asc, p.category_revenue_rank asc;
