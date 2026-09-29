-- ==============================================================================
-- 02. CUSTOMER COHORT RETENTION ANALYSIS
-- ==============================================================================
-- Methodology & Definitions:
-- 1. Cohort Definition: Customers are assigned to cohorts based on the calendar month
--    of their first completed purchase (cohort_month).
-- 2. Observation Period: September 2016 through October 2018.
-- 3. Denominator: Total distinct customers in the cohort who made their first purchase
--    in Month 0 (cohort_size).
-- 4. Retention Formula: (active_customers_in_month_n / cohort_size) * 100.
-- 5. Handling Incomplete Cohorts: Newer cohorts have fewer elapsed months. Months
--    exceeding the dataset boundary are represented as NULL rather than 0%.
-- ==============================================================================

-- PART 1: Detailed Cohort Activity Table
with customer_purchases as (
    select
        c.customer_unique_id,
        f.order_id,
        cast(strftime(cast(f.order_purchase_timestamp as date), '%Y-%m-01') as date) as order_month
    from ecommerce_analytics_marts.fct_orders f
    inner join ecommerce_analytics_marts.dim_customer c on f.customer_unique_id = c.customer_unique_id
    where f.order_status not in ('canceled', 'unavailable')
),

cohort_assignments as (
    select
        customer_unique_id,
        min(order_month) as cohort_month
    from customer_purchases
    group by customer_unique_id
),

cohort_summary as (
    select
        cohort_month,
        count(distinct customer_unique_id) as cohort_size
    from cohort_assignments
    group by cohort_month
),

cohort_activity as (
    select
        ca.cohort_month,
        cp.order_month,
        (
            (extract(year from cp.order_month) - extract(year from ca.cohort_month)) * 12 +
            (extract(month from cp.order_month) - extract(month from ca.cohort_month))
        ) as month_number,
        count(distinct cp.customer_unique_id) as active_customers
    from customer_purchases cp
    inner join cohort_assignments ca on cp.customer_unique_id = ca.customer_unique_id
    group by ca.cohort_month, cp.order_month
)

select
    ca.cohort_month,
    cs.cohort_size,
    ca.month_number,
    ca.active_customers,
    round((cast(ca.active_customers as double) / cs.cohort_size) * 100, 2) as retention_rate_pct
from cohort_activity ca
inner join cohort_summary cs on ca.cohort_month = cs.cohort_month
where ca.month_number >= 0
order by ca.cohort_month asc, ca.month_number asc;


-- PART 2: Pivoted Cohort Retention Matrix (Month 0 to Month 12)
with cohort_data as (
    select * from ecommerce_analytics_marts.mart_customer_retention
)

select
    cohort_month,
    max(cohort_size) as cohort_size,
    max(case when month_number = 0 then retention_rate_pct end) as m0_pct,
    max(case when month_number = 1 then retention_rate_pct end) as m1_pct,
    max(case when month_number = 2 then retention_rate_pct end) as m2_pct,
    max(case when month_number = 3 then retention_rate_pct end) as m3_pct,
    max(case when month_number = 4 then retention_rate_pct end) as m4_pct,
    max(case when month_number = 5 then retention_rate_pct end) as m5_pct,
    max(case when month_number = 6 then retention_rate_pct end) as m6_pct,
    max(case when month_number = 7 then retention_rate_pct end) as m7_pct,
    max(case when month_number = 8 then retention_rate_pct end) as m8_pct,
    max(case when month_number = 9 then retention_rate_pct end) as m9_pct,
    max(case when month_number = 10 then retention_rate_pct end) as m10_pct,
    max(case when month_number = 11 then retention_rate_pct end) as m11_pct,
    max(case when month_number = 12 then retention_rate_pct end) as m12_pct
from cohort_data
group by cohort_month
order by cohort_month asc;
