with customer_orders as (
    select
        c.customer_unique_id,
        o.order_id,
        cast(strftime(cast(o.order_purchase_timestamp as date), '%Y-%m-01') as date) as order_month
    from {{ ref('stg_orders') }} o
    inner join {{ ref('stg_customers') }} c on o.customer_id = c.customer_id
    where o.order_status not in ('canceled', 'unavailable')
),

cohort_first_purchase as (
    select
        customer_unique_id,
        min(order_month) as cohort_month
    from customer_orders
    group by customer_unique_id
),

cohort_sizes as (
    select
        cohort_month,
        count(distinct customer_unique_id) as cohort_size
    from cohort_first_purchase
    group by cohort_month
),

cohort_activity as (
    select
        cf.cohort_month,
        co.order_month,
        (
            (extract(year from co.order_month) - extract(year from cf.cohort_month)) * 12 +
            (extract(month from co.order_month) - extract(month from cf.cohort_month))
        ) as month_number,
        count(distinct co.customer_unique_id) as active_customers
    from customer_orders co
    inner join cohort_first_purchase cf on co.customer_unique_id = cf.customer_unique_id
    group by cf.cohort_month, co.order_month
),

final as (
    select
        ca.cohort_month,
        ca.order_month,
        ca.month_number,
        cs.cohort_size,
        ca.active_customers,
        round((cast(ca.active_customers as double) / cs.cohort_size) * 100, 2) as retention_rate_pct
    from cohort_activity ca
    inner join cohort_sizes cs on ca.cohort_month = cs.cohort_month
    where ca.month_number >= 0
)

select * from final
