-- ==============================================================================
-- 03. RFM (RECENCY, FREQUENCY, MONETARY) SEGMENTATION ANALYSIS
-- ==============================================================================
-- Methodology & Assumptions:
-- 1. Recency (R): Elapsed days between the customer's most recent order and the
--    dataset boundary (maximum order timestamp in dataset: 2018-10-17).
--    Scored into quintiles (1-5) via NTILE(5): Score 5 = most recently purchased.
-- 2. Frequency (F): Total lifetime completed orders placed by the persistent customer.
--    Threshold-based scoring: 1 order = 1, 2 orders = 3, 3 orders = 4, 4+ orders = 5.
-- 3. Monetary (M): Total lifetime spend (sum of item prices and freight).
--    Scored into quintiles (1-5) via NTILE(5): Score 5 = top 20% spending tier.
--
-- Analytical Note:
-- E-commerce marketplaces with long repurchase cycles (e.g. furniture, large electronics)
-- naturally exhibit a low repeat frequency rate compared to fast-moving consumer goods.
-- ==============================================================================

-- PART 1: RFM Segment Summary & Value Contribution
with segment_aggregates as (
    select
        rfm_segment,
        count(*) as customer_count,
        sum(lifetime_order_count) as total_orders_placed,
        round(sum(lifetime_order_value), 2) as total_segment_spend,
        round(avg(lifetime_order_value), 2) as avg_monetary_value,
        round(avg(days_since_last_order), 1) as avg_recency_days,
        round(avg(lifetime_order_count), 2) as avg_order_frequency,
        round(avg(average_review_score_given), 2) as avg_satisfaction_score
    from ecommerce_analytics_marts.dim_customer
    group by rfm_segment
),

total_base as (
    select
        count(*) as total_customers,
        sum(lifetime_order_value) as total_spend
    from ecommerce_analytics_marts.dim_customer
)

select
    s.rfm_segment,
    s.customer_count,
    round((cast(s.customer_count as double) / b.total_customers) * 100, 2) as customer_share_pct,
    s.total_segment_spend,
    round((s.total_segment_spend / b.total_spend) * 100, 2) as revenue_share_pct,
    s.avg_monetary_value,
    s.avg_recency_days,
    s.avg_order_frequency,
    s.avg_satisfaction_score
from segment_aggregates s
cross join total_base b
order by s.total_segment_spend desc;


-- PART 2: Identification of Top 'Champions' & High-Value Retention Candidates
select
    customer_unique_id,
    rfm_segment,
    rfm_recency_score,
    rfm_frequency_score,
    rfm_monetary_score,
    days_since_last_order,
    lifetime_order_count,
    lifetime_order_value,
    primary_customer_state,
    primary_customer_city,
    average_review_score_given
from ecommerce_analytics_marts.dim_customer
where rfm_segment in ('Champions', 'Loyal Customers', 'High-Value New')
order by lifetime_order_value desc
limit 25;
