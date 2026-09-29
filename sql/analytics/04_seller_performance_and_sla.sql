-- ==============================================================================
-- 04. SELLER PERFORMANCE AND SLA ANALYSIS
-- ==============================================================================
-- Objectives:
-- 1. Rank sellers by Gross Merchandise Value and analyze order fulfillment volume.
-- 2. Evaluate operational SLA performance: average delivery days, on-time rate %, late rate %.
-- 3. Correlate delivery delays with customer satisfaction (average review scores).
-- 4. Segment sellers into performance quadrants based on SLA compliance and revenue.
-- ==============================================================================

-- PART 1: Top 20 Sellers by Revenue and SLA Compliance
select
    revenue_rank,
    seller_id,
    seller_city,
    seller_state,
    seller_revenue_tier,
    lifetime_revenue,
    revenue_share_pct,
    lifetime_orders_count,
    lifetime_units_sold,
    delivered_orders_count,
    on_time_rate_pct,
    round(100.0 - on_time_rate_pct, 2) as late_delivery_rate_pct,
    average_delivery_days,
    average_review_score,
    total_reviews_received
from ecommerce_analytics_marts.mart_seller_performance
where revenue_rank <= 20
order by revenue_rank asc;


-- PART 2: Operational Health by Seller State
select
    s.seller_state,
    count(distinct s.seller_id) as total_active_sellers,
    sum(s.lifetime_orders_count) as total_orders_fulfilled,
    round(sum(s.lifetime_revenue), 2) as total_state_revenue,
    round(avg(s.on_time_rate_pct), 2) as avg_on_time_rate_pct,
    round(avg(s.average_delivery_days), 1) as avg_delivery_days,
    round(avg(s.average_review_score), 2) as avg_seller_review_score
from ecommerce_analytics_marts.dim_seller s
group by s.seller_state
having count(distinct s.seller_id) >= 10
order by total_state_revenue desc;


-- PART 3: Delivery SLA vs Review Score Impact Analysis
-- Investigates the observed relationship between late deliveries and customer satisfaction ratings
select
    case 
        when on_time_rate_pct >= 95.0 then '1. Exceptional SLA (>=95% On-Time)'
        when on_time_rate_pct >= 90.0 then '2. High SLA (90-95% On-Time)'
        when on_time_rate_pct >= 80.0 then '3. Moderate SLA (80-90% On-Time)'
        else '4. Poor SLA (<80% On-Time)'
    end as sla_compliance_bracket,
    count(*) as seller_count,
    sum(lifetime_orders_count) as total_orders,
    round(sum(lifetime_revenue), 2) as total_revenue,
    round(avg(average_delivery_days), 1) as avg_delivery_days,
    round(avg(average_review_score), 2) as avg_review_score
from ecommerce_analytics_marts.dim_seller
where delivered_orders_count >= 10
group by 1
order by 1 asc;
