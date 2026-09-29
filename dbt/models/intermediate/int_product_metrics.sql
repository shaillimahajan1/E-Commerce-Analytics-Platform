with items as (
    select * from {{ ref('int_order_items_enriched') }}
),

reviews as (
    select * from {{ ref('stg_reviews') }}
),

product_reviews as (
    select
        i.product_id,
        round(avg(r.review_score), 2) as avg_review_score,
        count(distinct r.review_id) as total_reviews_count
    from items i
    inner join reviews r on i.order_id = r.order_id
    group by i.product_id
),

product_sales as (
    select
        i.product_id,
        max(i.product_category_name_english) as product_category_name_english,
        max(i.product_category_name_portuguese) as product_category_name_portuguese,
        max(i.product_weight_g) as product_weight_g,
        max(i.product_volume_cm3) as product_volume_cm3,
        count(i.order_item_key) as total_units_sold,
        count(distinct i.order_id) as total_orders_count,
        count(distinct i.seller_id) as distinct_sellers_count,
        round(sum(i.price), 2) as total_revenue,
        round(sum(i.freight_value), 2) as total_freight,
        round(avg(i.price), 2) as average_price,
        min(i.order_purchase_timestamp) as first_sale_timestamp,
        max(i.order_purchase_timestamp) as latest_sale_timestamp
    from items i
    group by i.product_id
),

final as (
    select
        ps.product_id,
        ps.product_category_name_english,
        ps.product_category_name_portuguese,
        ps.product_weight_g,
        ps.product_volume_cm3,
        ps.total_units_sold,
        ps.total_orders_count,
        ps.distinct_sellers_count,
        ps.total_revenue,
        ps.total_freight,
        ps.average_price,
        ps.first_sale_timestamp,
        ps.latest_sale_timestamp,
        coalesce(pr.avg_review_score, 0.0) as avg_review_score,
        coalesce(pr.total_reviews_count, 0) as total_reviews_count
    from product_sales ps
    left join product_reviews pr on ps.product_id = pr.product_id
)

select * from final
