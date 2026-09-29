with reviews as (
    select * from {{ ref('stg_reviews') }}
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
        r.review_key,
        r.review_id,
        r.order_id,
        o.customer_id,
        cast(strftime(cast(o.order_purchase_timestamp as date), '%Y%m%d') as integer) as order_purchase_date_key,
        r.review_score,
        r.review_creation_date,
        r.review_answer_timestamp,
        case when r.review_comment_title is not null then 1 else 0 end as has_comment_title,
        case when r.review_comment_message is not null then 1 else 0 end as has_comment_message,
        r.review_comment_title,
        r.review_comment_message,
        
        -- Response latency in hours
        case 
            when r.review_answer_timestamp is not null and r.review_creation_date is not null
            then {{ datediff('r.review_creation_date', 'r.review_answer_timestamp', 'hour') }}
            else null
        end as review_response_time_hours
    from reviews r
    left join orders o on r.order_id = o.order_id
)

select * from final
