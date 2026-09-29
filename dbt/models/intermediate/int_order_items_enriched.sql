with items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_delivered_customer_date,
        order_estimated_delivery_date
    from {{ ref('stg_orders') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

categories as (
    select * from {{ ref('stg_category_translation') }}
),

sellers as (
    select * from {{ ref('stg_sellers') }}
),

customers as (
    select
        customer_id,
        customer_unique_id,
        customer_city,
        customer_state
    from {{ ref('stg_customers') }}
),

final as (
    select
        i.order_item_key,
        i.order_id,
        i.order_item_id,
        i.product_id,
        i.seller_id,
        o.customer_id,
        c.customer_unique_id,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        i.shipping_limit_date,
        
        -- Economics
        i.price,
        i.freight_value,
        i.total_item_value,
        
        -- Product attributes
        coalesce(cat.product_category_name_english, p.product_category_name, 'unlabeled') as product_category_name_english,
        coalesce(p.product_category_name, 'unlabeled') as product_category_name_portuguese,
        p.product_weight_g,
        p.product_volume_cm3,
        
        -- Geographic dimensions
        s.seller_city,
        s.seller_state,
        c.customer_city,
        c.customer_state,
        case when s.seller_state = c.customer_state then 1 else 0 end as is_same_state_shipping
    from items i
    inner join orders o on i.order_id = o.order_id
    left join customers c on o.customer_id = c.customer_id
    left join products p on i.product_id = p.product_id
    left join categories cat on p.product_category_name = cat.product_category_name
    left join sellers s on i.seller_id = s.seller_id
)

select * from final
