with source as (
    select * from {{ source('ecommerce_raw', 'raw_reviews') }}
),

renamed as (
    select
        {{ generate_surrogate_key(['review_id', 'order_id']) }} as review_key,
        cast(review_id as varchar) as review_id,
        cast(order_id as varchar) as order_id,
        cast(review_score as integer) as review_score,
        nullif(trim(cast(review_comment_title as varchar)), '') as review_comment_title,
        nullif(trim(cast(review_comment_message as varchar)), '') as review_comment_message,
        cast(review_creation_date as timestamp) as review_creation_date,
        cast(review_answer_timestamp as timestamp) as review_answer_timestamp
    from source
)

select * from renamed
