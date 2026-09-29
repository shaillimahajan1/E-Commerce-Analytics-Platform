-- ==============================================================================
-- EXPLORATORY DATA ANALYSIS QUERIES
-- ==============================================================================
-- Queries used to discover dataset characteristics, outliers, and distributions.
-- ==============================================================================

-- 1. Order Status Breakdown
select
    order_status,
    count(*) as order_count,
    round((count(*) * 100.0) / sum(count(*)) over (), 2) as percentage
from ecommerce_raw.raw_orders
group by order_status
order by order_count desc;

-- 2. Payment Method Distribution & Average Installments
select
    payment_type,
    count(*) as transaction_count,
    round(sum(cast(payment_value as double)), 2) as total_volume_brl,
    round(avg(cast(payment_value as double)), 2) as avg_transaction_value,
    round(avg(cast(payment_installments as integer)), 1) as avg_installments
from ecommerce_raw.raw_payments
group by payment_type
order by total_volume_brl desc;

-- 3. Review Score Distribution
select
    review_score,
    count(*) as total_reviews,
    round((count(*) * 100.0) / sum(count(*)) over (), 2) as percentage,
    count(case when review_comment_message is not null then 1 end) as reviews_with_written_comment
from ecommerce_raw.raw_reviews
group by review_score
order by review_score desc;

-- 4. Geographic Concentration of Customers and Sellers
select
    c.customer_state,
    count(distinct c.customer_unique_id) as total_customers,
    count(distinct s.seller_id) as total_sellers
from ecommerce_analytics_staging.stg_customers c
full outer join ecommerce_analytics_staging.stg_sellers s on c.customer_state = s.seller_state
group by c.customer_state
order by total_customers desc;
