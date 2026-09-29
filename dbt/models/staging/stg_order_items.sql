with source as (
    select * from {{ source('ecommerce_raw', 'raw_order_items') }}
),

renamed as (
    select
        {{ generate_surrogate_key(['order_id', 'order_item_id']) }} as order_item_key,
        cast(order_id as varchar) as order_id,
        cast(order_item_id as integer) as order_item_id,
        cast(product_id as varchar) as product_id,
        cast(seller_id as varchar) as seller_id,
        cast(shipping_limit_date as timestamp) as shipping_limit_date,
        cast(price as double) as price,
        cast(freight_value as double) as freight_value,
        cast(price as double) + cast(freight_value as double) as total_item_value
    from source
)

select * from renamed
