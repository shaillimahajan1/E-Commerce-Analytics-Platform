with source as (
    select * from {{ source('ecommerce_raw', 'raw_payments') }}
),

renamed as (
    select
        {{ generate_surrogate_key(['order_id', 'payment_sequential']) }} as payment_key,
        cast(order_id as varchar) as order_id,
        cast(payment_sequential as integer) as payment_sequential,
        lower(trim(cast(payment_type as varchar))) as payment_type,
        cast(payment_installments as integer) as payment_installments,
        cast(payment_value as double) as payment_value
    from source
)

select * from renamed
