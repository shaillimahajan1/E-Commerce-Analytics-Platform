with source as (
    select * from {{ source('ecommerce_raw', 'raw_products') }}
),

renamed as (
    select
        cast(product_id as varchar) as product_id,
        nullif(lower(trim(cast(product_category_name as varchar))), '') as product_category_name,
        cast(product_name_lenght as integer) as product_name_length,
        cast(product_description_lenght as integer) as product_description_length,
        cast(product_photos_qty as integer) as product_photos_qty,
        cast(product_weight_g as double) as product_weight_g,
        cast(product_length_cm as double) as product_length_cm,
        cast(product_height_cm as double) as product_height_cm,
        cast(product_width_cm as double) as product_width_cm,
        round(cast(product_length_cm as double) * cast(product_height_cm as double) * cast(product_width_cm as double), 2) as product_volume_cm3
    from source
)

select * from renamed
