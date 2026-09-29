with items as (
    select * from {{ ref('int_order_items_enriched') }}
),

final as (
    select
        order_item_key,
        order_id,
        order_item_id,
        product_id,
        seller_id,
        customer_id,
        customer_unique_id,
        cast(strftime(cast(order_purchase_timestamp as date), '%Y%m%d') as integer) as order_purchase_date_key,
        order_status,
        order_purchase_timestamp,
        shipping_limit_date,
        order_delivered_customer_date,
        
        -- Measures (BRL)
        price as item_price,
        freight_value as item_freight_value,
        total_item_value,
        
        -- Dimension flags
        is_same_state_shipping,
        seller_state,
        customer_state
    from items
)

select * from final
