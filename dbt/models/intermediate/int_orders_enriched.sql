with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

items_agg as (
    select
        order_id,
        count(order_item_key) as total_item_count,
        count(distinct product_id) as distinct_products_count,
        count(distinct seller_id) as distinct_sellers_count,
        round(sum(price), 2) as total_items_value,
        round(sum(freight_value), 2) as total_freight_value,
        round(sum(total_item_value), 2) as total_order_cost
    from {{ ref('stg_order_items') }}
    group by order_id
),

payments_agg as (
    select
        order_id,
        count(payment_key) as payment_attempts_count,
        max(payment_installments) as max_payment_installments,
        round(sum(payment_value), 2) as total_payment_value,
        max(case when payment_type = 'credit_card' then 1 else 0 end) as has_credit_card_payment,
        max(case when payment_type = 'boleto' then 1 else 0 end) as has_boleto_payment,
        max(case when payment_type = 'voucher' then 1 else 0 end) as has_voucher_payment,
        max(case when payment_type = 'debit_card' then 1 else 0 end) as has_debit_card_payment
    from {{ ref('stg_payments') }}
    group by order_id
),

reviews_agg as (
    select
        order_id,
        count(review_key) as review_count,
        round(avg(review_score), 2) as avg_review_score,
        max(case when review_comment_message is not null then 1 else 0 end) as has_review_comment
    from {{ ref('stg_reviews') }}
    group by order_id
),

final as (
    select
        o.order_id,
        o.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        c.customer_zip_code_prefix,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        
        -- Item metrics
        coalesce(i.total_item_count, 0) as total_item_count,
        coalesce(i.distinct_products_count, 0) as distinct_products_count,
        coalesce(i.distinct_sellers_count, 0) as distinct_sellers_count,
        coalesce(i.total_items_value, 0.0) as total_items_value,
        coalesce(i.total_freight_value, 0.0) as total_freight_value,
        coalesce(i.total_order_cost, 0.0) as total_order_cost,
        
        -- Payment metrics
        coalesce(p.payment_attempts_count, 0) as payment_attempts_count,
        coalesce(p.max_payment_installments, 1) as max_payment_installments,
        coalesce(p.total_payment_value, 0.0) as total_payment_value,
        coalesce(p.has_credit_card_payment, 0) as has_credit_card_payment,
        coalesce(p.has_boleto_payment, 0) as has_boleto_payment,
        coalesce(p.has_voucher_payment, 0) as has_voucher_payment,
        coalesce(p.has_debit_card_payment, 0) as has_debit_card_payment,
        
        -- Review metrics
        coalesce(r.review_count, 0) as review_count,
        r.avg_review_score,
        coalesce(r.has_review_comment, 0) as has_review_comment
    from orders o
    inner join customers c on o.customer_id = c.customer_id
    left join items_agg i on o.order_id = i.order_id
    left join payments_agg p on o.order_id = p.order_id
    left join reviews_agg r on o.order_id = r.order_id
)

select * from final
