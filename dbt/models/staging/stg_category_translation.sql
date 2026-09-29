with source as (
    select * from {{ source('ecommerce_raw', 'raw_category_translation') }}
),

renamed as (
    select
        lower(trim(cast(product_category_name as varchar))) as product_category_name,
        lower(trim(cast(product_category_name_english as varchar))) as product_category_name_english
    from source
)

select * from renamed
