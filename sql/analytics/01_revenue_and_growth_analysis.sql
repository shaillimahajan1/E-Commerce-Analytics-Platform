-- ==============================================================================
-- 01. REVENUE AND GROWTH ANALYSIS
-- ==============================================================================
-- Objectives:
-- 1. Calculate monthly GMV, order volume, unique customers, and Average Order Value (AOV).
-- 2. Compute Month-over-Month (MoM) and Year-over-Year (YoY) growth rates using window LAG().
-- 3. Calculate 3-month trailing rolling average revenue to smooth short-term seasonality.
-- 4. Calculate category-level revenue contributions and relative share % per month.
--
-- Target Schema: ecommerce_analytics_marts
-- ==============================================================================

-- PART 1: Monthly Marketplace Growth & Rolling Averages
with monthly_metrics as (
    select
        d.year_month,
        min(d.date_day) as month_start_date,
        count(distinct f.order_id) as total_orders,
        count(distinct f.customer_unique_id) as total_customers,
        round(sum(f.gross_merchandise_value), 2) as monthly_gmv,
        round(sum(f.total_freight_value), 2) as total_freight,
        round(sum(f.total_order_value), 2) as total_revenue,
        round(sum(f.gross_merchandise_value) / nullif(count(distinct f.order_id), 0), 2) as average_order_value
    from ecommerce_analytics_marts.fct_orders f
    inner join ecommerce_analytics_marts.dim_date d on f.order_purchase_date_key = d.date_key
    where f.order_status not in ('canceled', 'unavailable')
    group by d.year_month
),

growth_lagged as (
    select
        year_month,
        month_start_date,
        total_orders,
        total_customers,
        monthly_gmv,
        average_order_value,
        
        -- Prior Month and Prior Year GMV
        lag(monthly_gmv, 1) over (order by month_start_date) as prev_month_gmv,
        lag(monthly_gmv, 12) over (order by month_start_date) as prev_year_gmv,
        
        -- 3-Month Trailing Rolling Average GMV
        round(
            avg(monthly_gmv) over (
                order by month_start_date 
                rows between 2 preceding and current row
            ), 2
        ) as rolling_3m_avg_gmv
    from monthly_metrics
)

select
    year_month,
    total_orders,
    total_customers,
    monthly_gmv,
    average_order_value,
    prev_month_gmv,
    rolling_3m_avg_gmv,
    
    -- Month-over-Month Growth %
    round(
        case 
            when prev_month_gmv is not null and prev_month_gmv > 0 
            then ((monthly_gmv - prev_month_gmv) / prev_month_gmv) * 100 
            else null 
        end, 2
    ) as mom_growth_pct,
    
    -- Year-over-Year Growth %
    round(
        case 
            when prev_year_gmv is not null and prev_year_gmv > 0 
            then ((monthly_gmv - prev_year_gmv) / prev_year_gmv) * 100 
            else null 
        end, 2
    ) as yoy_growth_pct
from growth_lagged
order by month_start_date asc;


-- PART 2: Top Product Categories by Monthly Revenue Contribution Share %
with category_monthly as (
    select
        strftime(cast(f.order_purchase_timestamp as date), '%Y-%m') as year_month,
        p.product_category_name_english,
        round(sum(f.item_price), 2) as category_gmv,
        count(distinct f.order_id) as category_orders,
        count(*) as units_sold
    from ecommerce_analytics_marts.fct_order_items f
    inner join ecommerce_analytics_marts.dim_product p on f.product_id = p.product_id
    where f.order_status not in ('canceled', 'unavailable')
    group by 1, 2
),

category_with_shares as (
    select
        year_month,
        product_category_name_english,
        category_gmv,
        category_orders,
        units_sold,
        
        -- Total marketplace GMV for the month
        sum(category_gmv) over (partition by year_month) as monthly_total_gmv,
        
        -- Category Share of Monthly GMV
        round((category_gmv / sum(category_gmv) over (partition by year_month)) * 100, 2) as category_revenue_share_pct,
        
        -- Rank within month
        rank() over (partition by year_month order by category_gmv desc) as monthly_rank
    from category_monthly
)

select
    year_month,
    monthly_rank,
    product_category_name_english,
    category_gmv,
    category_revenue_share_pct,
    category_orders,
    units_sold
from category_with_shares
where monthly_rank <= 5
order by year_month desc, monthly_rank asc;
