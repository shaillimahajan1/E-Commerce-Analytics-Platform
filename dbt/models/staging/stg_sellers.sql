with source as (
    select * from {{ source('ecommerce_raw', 'raw_sellers') }}
),

renamed as (
    select
        cast(seller_id as varchar) as seller_id,
        cast(seller_zip_code_prefix as varchar) as seller_zip_code_prefix,
        trim(cast(seller_city as varchar)) as seller_city,
        upper(trim(cast(seller_state as varchar))) as seller_state
    from source
)

select * from renamed
