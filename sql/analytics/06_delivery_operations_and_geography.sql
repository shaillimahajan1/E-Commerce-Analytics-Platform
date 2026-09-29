-- ==============================================================================
-- 06. DELIVERY OPERATIONS AND GEOGRAPHIC PERFORMANCE
-- ==============================================================================
-- Analytical Guideline (Section 49 & 50):
-- - Observed correlations between transit duration and geography must not be
--   interpreted as causal. We observe historical fulfillment time across Brazilian states.
-- - Metric definitions:
--   actual_delivery_days = order_delivered_customer_date - order_purchase_timestamp
--   estimated_delivery_days = order_estimated_delivery_date - order_purchase_timestamp
--   late_delivery_rate_pct = (late_orders / delivered_orders) * 100
-- ==============================================================================

-- PART 1: Operational Fulfillment Durations by Customer State & Macro-Region
select
    l.macro_region,
    f.customer_state,
    count(distinct f.order_id) as total_delivered_orders,
    round(avg(f.actual_delivery_days), 1) as avg_actual_delivery_days,
    round(avg(f.estimated_delivery_days), 1) as avg_promised_delivery_days,
    round(avg(f.delivery_delay_days), 1) as avg_delay_days,
    round((cast(sum(f.is_late_delivery) as double) / count(*)) * 100, 2) as late_delivery_rate_pct,
    round((cast(sum(f.is_on_time) as double) / count(*)) * 100, 2) as on_time_delivery_rate_pct,
    round(avg(f.total_freight_value), 2) as avg_freight_cost_brl,
    round(avg(f.avg_review_score), 2) as avg_customer_review_score
from ecommerce_analytics_marts.fct_delivery f
left join ecommerce_analytics_marts.dim_location l on f.customer_zip_code_prefix = l.zip_code_prefix
group by l.macro_region, f.customer_state
having count(distinct f.order_id) >= 50
order by avg_actual_delivery_days desc;


-- PART 2: Route Dynamics: Same-State Shipping vs Interstate Cross-Border Transit
select
    case when i.is_same_state_shipping = 1 then 'Intrastate (Seller & Buyer in Same State)'
         else 'Interstate (Cross-Border Transit)'
    end as shipping_route_type,
    count(distinct i.order_id) as total_orders,
    count(*) as total_items_shipped,
    round(avg(i.item_price), 2) as avg_item_price,
    round(avg(i.item_freight_value), 2) as avg_freight_per_item,
    round(sum(i.item_freight_value) / nullif(sum(i.item_price), 0) * 100, 2) as freight_to_price_ratio_pct,
    round(avg(d.actual_delivery_days), 1) as avg_delivery_days,
    round((cast(sum(d.is_late_delivery) as double) / nullif(count(d.order_id), 0)) * 100, 2) as late_delivery_rate_pct
from ecommerce_analytics_marts.fct_order_items i
inner join ecommerce_analytics_marts.fct_delivery d on i.order_id = d.order_id
group by 1
order by avg_delivery_days desc;
