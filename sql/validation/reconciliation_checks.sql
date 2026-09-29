-- ==============================================================================
-- RECONCILIATION AND DATA INTEGRITY CHECKS
-- ==============================================================================
-- Executes end-to-end reconciliation across Raw -> Staging -> Marts layers
-- to verify that no rows or financial value are lost, duplicated, or corrupted.
-- ==============================================================================

-- 1. ORDER RECORD COUNT RECONCILIATION
-- Verifies that raw orders, staging orders, and fct_orders have identical row counts
with order_reconciliation as (
    select '1. Raw Orders' as layer, count(*) as row_count from ecommerce_raw.raw_orders
    union all
    select '2. Staging Orders' as layer, count(*) as row_count from ecommerce_analytics_staging.stg_orders
    union all
    select '3. Fact Orders' as layer, count(*) as row_count from ecommerce_analytics_marts.fct_orders
)
select * from order_reconciliation;


-- 2. FINANCIAL REVENUE RECONCILIATION
-- Validates raw payment sums vs staging payment sums vs fact payment sums vs order items GMV
with financial_reconciliation as (
    select
        '1. Raw Payments' as layer,
        round(sum(cast(payment_value as double)), 2) as total_monetary_value
    from ecommerce_raw.raw_payments
    union all
    select
        '2. Staging Payments' as layer,
        round(sum(payment_value), 2) as total_monetary_value
    from ecommerce_analytics_staging.stg_payments
    union all
    select
        '3. Fact Payments' as layer,
        round(sum(payment_value), 2) as total_monetary_value
    from ecommerce_analytics_marts.fct_payments
    union all
    select
        '4. Fact Orders Total Payment Value' as layer,
        round(sum(total_payment_value), 2) as total_monetary_value
    from ecommerce_analytics_marts.fct_orders
    union all
    select
        '5. Fact Order Items GMV + Freight' as layer,
        round(sum(item_price + item_freight_value), 2) as total_monetary_value
    from ecommerce_analytics_marts.fct_order_items
)
select * from financial_reconciliation;


-- 3. ORPHAN RECORD VALIDATION
-- Verifies that foreign keys have 100% referential integrity
select 'Orphan Items (Missing in Orders)' as check_name, count(*) as violation_count
from ecommerce_analytics_marts.fct_order_items i
left join ecommerce_analytics_marts.fct_orders o on i.order_id = o.order_id
where o.order_id is null

union all

select 'Orphan Payments (Missing in Orders)' as check_name, count(*) as violation_count
from ecommerce_analytics_marts.fct_payments p
left join ecommerce_analytics_marts.fct_orders o on p.order_id = o.order_id
where o.order_id is null

union all

select 'Orphan Reviews (Missing in Orders)' as check_name, count(*) as violation_count
from ecommerce_analytics_marts.fct_reviews r
left join ecommerce_analytics_marts.fct_orders o on r.order_id = o.order_id
where o.order_id is null

union all

select 'Orphan Customers in Orders' as check_name, count(*) as violation_count
from ecommerce_analytics_marts.fct_orders o
left join ecommerce_analytics_marts.dim_customer c on o.customer_unique_id = c.customer_unique_id
where c.customer_unique_id is null;


-- 4. NON-NEGATIVE VALUE AND LOGICAL DATE VALIDATION
select
    count(case when gross_merchandise_value < 0 then 1 end) as negative_gmv_count,
    count(case when total_freight_value < 0 then 1 end) as negative_freight_count,
    count(case when total_payment_value < 0 then 1 end) as negative_payment_count,
    count(case when order_delivered_customer_date < order_purchase_timestamp then 1 end) as chronological_inversions
from ecommerce_analytics_marts.fct_orders;
