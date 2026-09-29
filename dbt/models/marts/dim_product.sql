with products as (
    select * from {{ ref('stg_products') }}
),

categories as (
    select * from {{ ref('stg_category_translation') }}
),

metrics as (
    select * from {{ ref('int_product_metrics') }}
),

final as (
    select
        p.product_id,
        coalesce(c.product_category_name_english, p.product_category_name, 'unlabeled') as product_category_name_english,
        coalesce(p.product_category_name, 'unlabeled') as product_category_name_portuguese,
        p.product_name_length,
        p.product_description_length,
        p.product_photos_qty,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm,
        p.product_volume_cm3,
        
        -- Size & weight classification
        case
            when p.product_weight_g >= 10000 or p.product_volume_cm3 >= 50000 then 'Bulky / Heavy'
            when p.product_weight_g >= 3000 or p.product_volume_cm3 >= 15000 then 'Medium Freight'
            when p.product_weight_g is not null then 'Standard Parcel'
            else 'Unknown'
        end as freight_size_tier,
        
        -- Historical metrics
        coalesce(m.total_units_sold, 0) as lifetime_units_sold,
        coalesce(m.total_orders_count, 0) as lifetime_orders_count,
        coalesce(m.total_revenue, 0.0) as lifetime_revenue,
        coalesce(m.total_freight, 0.0) as lifetime_freight_generated,
        coalesce(m.average_price, 0.0) as average_unit_price,
        coalesce(m.avg_review_score, 0.0) as average_review_score,
        coalesce(m.total_reviews_count, 0) as total_reviews_count
    from products p
    left join categories c on p.product_category_name = c.product_category_name
    left join metrics m on p.product_id = m.product_id
)

select * from final
