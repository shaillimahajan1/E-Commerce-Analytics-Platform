with payments as (
    select * from {{ ref('stg_payments') }}
),

orders as (
    select
        order_id,
        customer_id,
        order_purchase_timestamp
    from {{ ref('stg_orders') }}
),

final as (
    select
        p.payment_key,
        p.order_id,
        o.customer_id,
        cast(strftime(cast(o.order_purchase_timestamp as date), '%Y%m%d') as integer) as order_purchase_date_key,
        p.payment_sequential,
        p.payment_type,
        p.payment_installments,
        p.payment_value,
        case when p.payment_installments > 1 then 1 else 0 end as is_installment_payment
    from payments p
    left join orders o on p.order_id = o.order_id
)

select * from final
