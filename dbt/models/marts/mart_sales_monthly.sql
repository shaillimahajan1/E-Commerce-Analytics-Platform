with item_sales as (
    select
        strftime(cast(o.order_purchase_timestamp as date), '%Y-%m-01') as sales_month,
        coalesce(c.product_category_name_english, p.product_category_name, 'unlabeled') as product_category_name_english,
        i.order_id,
        cust.customer_unique_id,
        i.price,
        i.freight_value,
        i.total_item_value
    from {{ ref('stg_order_items') }} i
    inner join {{ ref('stg_orders') }} o on i.order_id = o.order_id
    inner join {{ ref('stg_customers') }} cust on o.customer_id = cust.customer_id
    left join {{ ref('stg_products') }} p on i.product_id = p.product_id
    left join {{ ref('stg_category_translation') }} c on p.product_category_name = c.product_category_name
    where o.order_status not in ('canceled', 'unavailable')
),

monthly_category as (
    select
        cast(sales_month as date) as sales_month,
        product_category_name_english,
        count(distinct order_id) as total_orders,
        count(distinct customer_unique_id) as unique_customers,
        count(*) as total_units_sold,
        round(sum(price), 2) as gross_merchandise_value,
        round(sum(freight_value), 2) as total_freight_value,
        round(sum(total_item_value), 2) as total_sales_value,
        round(avg(price), 2) as average_item_price,
        round(sum(price) / nullif(count(distinct order_id), 0), 2) as average_order_value
    from item_sales
    group by sales_month, product_category_name_english
)

select * from monthly_category
