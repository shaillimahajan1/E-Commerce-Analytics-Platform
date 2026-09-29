with base_customer as (
    select * from {{ ref('int_customer_orders') }}
),

rfm_scored as (
    select
        customer_unique_id,
        first_order_timestamp,
        latest_order_timestamp,
        lifetime_order_count,
        lifetime_order_value,
        lifetime_freight_value,
        lifetime_payment_value,
        average_order_value,
        average_review_score_given,
        primary_customer_state,
        primary_customer_city,
        primary_zip_code_prefix,
        is_repeat_customer,
        customer_lifespan_days,
        days_since_last_order,
        
        -- RFM Scoring Quintiles
        -- Recency: Lower days since last order = higher score (5 = most recent)
        ntile(5) over (order by days_since_last_order desc) as rfm_recency_score,
        
        -- Frequency: 1 order = score 1; repeat buyers get higher scores
        case 
            when lifetime_order_count = 1 then 1
            when lifetime_order_count = 2 then 3
            when lifetime_order_count = 3 then 4
            else 5
        end as rfm_frequency_score,
        
        -- Monetary: Higher lifetime order value = higher score
        ntile(5) over (order by lifetime_order_value asc) as rfm_monetary_score
    from base_customer
),

final as (
    select
        customer_unique_id,
        first_order_timestamp,
        latest_order_timestamp,
        lifetime_order_count,
        lifetime_order_value,
        lifetime_freight_value,
        lifetime_payment_value,
        average_order_value,
        average_review_score_given,
        primary_customer_state,
        primary_customer_city,
        primary_zip_code_prefix,
        is_repeat_customer,
        customer_lifespan_days,
        days_since_last_order,
        rfm_recency_score,
        rfm_frequency_score,
        rfm_monetary_score,
        
        -- Customer Segment Definition
        case
            when rfm_recency_score >= 4 and rfm_frequency_score >= 3 and rfm_monetary_score >= 4 
                then 'Champions'
            when rfm_frequency_score >= 3 
                then 'Loyal Customers'
            when rfm_recency_score >= 4 and rfm_frequency_score = 1 and rfm_monetary_score >= 4 
                then 'High-Value New'
            when rfm_recency_score >= 4 and rfm_frequency_score = 1 
                then 'Recent Customers'
            when rfm_recency_score between 2 and 3 and rfm_frequency_score >= 2 
                then 'Potential Loyalists'
            when rfm_recency_score <= 2 and rfm_frequency_score >= 2 
                then 'At Risk Repeat'
            when rfm_recency_score <= 2 and rfm_frequency_score = 1 and rfm_monetary_score >= 3 
                then 'About to Sleep'
            else 'Hibernating'
        end as rfm_segment
    from rfm_scored
)

select * from final
