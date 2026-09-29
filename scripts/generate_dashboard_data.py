"""
Generates static JSON data bundle from the curated dbt analytical marts
in ecommerce_warehouse.duckdb for the web-based GitHub Pages dashboard.
"""

import json
from pathlib import Path
import duckdb

def generate_dashboard_data():
    repo_root = Path(__file__).resolve().parent.parent
    db_path = repo_root / "data" / "processed" / "ecommerce_warehouse.duckdb"
    out_dir = repo_root / "dashboard"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Connecting to {db_path}...")
    with duckdb.connect(str(db_path)) as conn:
        # 1. Executive Summary KPIs
        kpis = conn.execute("""
            SELECT 
                round(sum(gross_merchandise_value), 2) as total_gmv,
                round(sum(total_freight_value), 2) as total_freight,
                round(sum(total_order_value), 2) as total_revenue,
                count(distinct order_id) as total_orders,
                count(distinct customer_unique_id) as total_customers,
                round(sum(gross_merchandise_value) / count(distinct order_id), 2) as aov,
                round((cast(sum(is_on_time) as double) / count(*)) * 100, 2) as on_time_pct,
                round((cast(sum(is_late_delivery) as double) / count(*)) * 100, 2) as late_pct,
                round(avg(actual_delivery_days), 1) as avg_delivery_days,
                round(avg(avg_review_score), 2) as avg_csat
            FROM ecommerce_analytics_marts.fct_orders
            WHERE order_status not in ('canceled', 'unavailable');
        """).df().to_dict(orient="records")[0]

        # Repeat customer stats
        repeat_stats = conn.execute("""
            SELECT 
                count(distinct case when lifetime_order_count > 1 then customer_unique_id end) as repeat_customers,
                count(distinct customer_unique_id) as total_customers,
                round(count(distinct case when lifetime_order_count > 1 then customer_unique_id end) * 100.0 / count(distinct customer_unique_id), 2) as repeat_rate_pct
            FROM ecommerce_analytics_marts.dim_customer;
        """).df().to_dict(orient="records")[0]
        kpis.update(repeat_stats)

        # 2. Monthly Revenue & Order Trend
        monthly_trend = conn.execute("""
            SELECT 
                strftime(d.date_day, '%Y-%m') as year_month,
                count(distinct f.order_id) as orders,
                count(distinct f.customer_unique_id) as customers,
                round(sum(f.gross_merchandise_value), 2) as gmv,
                round(sum(f.total_freight_value), 2) as freight,
                round(sum(f.gross_merchandise_value) / count(distinct f.order_id), 2) as aov
            FROM ecommerce_analytics_marts.fct_orders f
            INNER JOIN ecommerce_analytics_marts.dim_date d ON f.order_purchase_date_key = d.date_key
            WHERE f.order_status not in ('canceled', 'unavailable')
              AND d.date_day >= date '2017-01-01' AND d.date_day <= date '2018-08-31'
            GROUP BY 1
            ORDER BY 1 ASC;
        """).df().to_dict(orient="records")

        # 3. Top Categories by GMV
        top_categories = conn.execute("""
            SELECT 
                product_category_name_english as category,
                round(sum(gross_merchandise_value), 2) as gmv,
                sum(total_orders) as orders,
                sum(total_units_sold) as units,
                round(avg(average_order_value), 2) as avg_order_val
            FROM ecommerce_analytics_marts.mart_sales_monthly
            WHERE product_category_name_english != 'unlabeled'
            GROUP BY 1
            ORDER BY gmv DESC
            LIMIT 10;
        """).df().to_dict(orient="records")

        # 4. Customer Cohort Retention Matrix
        cohort_matrix = conn.execute("""
            SELECT 
                strftime(cohort_month, '%Y-%m') as cohort,
                month_number,
                cohort_size,
                active_customers,
                retention_rate_pct
            FROM ecommerce_analytics_marts.mart_customer_retention
            WHERE cohort_month >= date '2017-01-01' AND cohort_month <= date '2018-05-01'
              AND month_number <= 12
            ORDER BY cohort_month ASC, month_number ASC;
        """).df().to_dict(orient="records")

        # 5. RFM Segment Distribution
        rfm_segments = conn.execute("""
            SELECT 
                rfm_segment as segment,
                count(*) as customer_count,
                round(sum(lifetime_order_value), 2) as total_spend,
                round(avg(lifetime_order_value), 2) as avg_clv,
                round(avg(days_since_last_order), 0) as avg_recency_days
            FROM ecommerce_analytics_marts.dim_customer
            GROUP BY 1
            ORDER BY total_spend DESC;
        """).df().to_dict(orient="records")

        # 6. Payment Instrument Splits
        payment_splits = conn.execute("""
            SELECT 
                payment_type,
                count(*) as transactions,
                round(sum(payment_value), 2) as total_value,
                round(avg(payment_installments), 1) as avg_installments
            FROM ecommerce_analytics_marts.fct_payments
            GROUP BY 1
            ORDER BY total_value DESC;
        """).df().to_dict(orient="records")

        # 7. Regional Logistics by Macro-Region & State
        regional_logistics = conn.execute("""
            SELECT 
                l.macro_region,
                f.customer_state as state,
                count(*) as orders,
                round(avg(f.actual_delivery_days), 1) as avg_delivery_days,
                round(avg(f.estimated_delivery_days), 1) as promised_delivery_days,
                round((cast(sum(f.is_on_time) as double) / count(*)) * 100, 1) as on_time_pct,
                round((cast(sum(f.is_late_delivery) as double) / count(*)) * 100, 1) as late_pct,
                round(avg(f.total_freight_value), 2) as avg_freight
            FROM ecommerce_analytics_marts.fct_delivery f
            LEFT JOIN ecommerce_analytics_marts.dim_location l ON f.customer_zip_code_prefix = l.zip_code_prefix
            GROUP BY 1, 2
            HAVING count(*) >= 100
            ORDER BY avg_delivery_days ASC;
        """).df().to_dict(orient="records")

        # 8. Top 15 Sellers by Revenue
        top_sellers = conn.execute("""
            SELECT 
                revenue_rank,
                seller_id,
                seller_city,
                seller_state,
                seller_revenue_tier,
                lifetime_revenue,
                lifetime_orders_count,
                on_time_rate_pct,
                average_delivery_days,
                average_review_score
            FROM ecommerce_analytics_marts.mart_seller_performance
            ORDER BY revenue_rank ASC
            LIMIT 15;
        """).df().to_dict(orient="records")

        # 9. Top 15 Products by Revenue
        top_products = conn.execute("""
            SELECT 
                overall_revenue_rank as rank,
                product_id,
                product_category_name_english as category,
                freight_size_tier as size_tier,
                lifetime_units_sold,
                lifetime_revenue,
                average_unit_price,
                average_review_score,
                cumulative_revenue_pct,
                pareto_segment
            FROM ecommerce_analytics_marts.mart_product_performance
            ORDER BY overall_revenue_rank ASC
            LIMIT 15;
        """).df().to_dict(orient="records")

        # 10. Multi-Dimensional Interactive Cube (Year-Month x Category x Macro-Region)
        dimensional_cube = conn.execute("""
            WITH loc AS (
                SELECT DISTINCT primary_state, macro_region FROM ecommerce_analytics_marts.dim_location
            )
            SELECT 
                strftime(o.order_purchase_timestamp, '%Y-%m') AS ym,
                coalesce(p.product_category_name_english, 'Other') AS cat,
                coalesce(loc.macro_region, 'Southeast') AS reg,
                count(distinct o.order_id) AS ord,
                round(sum(i.item_price), 2) AS gmv,
                round(sum(i.item_freight_value), 2) AS frt,
                round(avg(o.is_on_time) * 100, 1) AS ont,
                round(avg(o.avg_review_score), 2) AS csat
            FROM ecommerce_analytics_marts.fct_orders o
            JOIN ecommerce_analytics_marts.fct_order_items i ON o.order_id = i.order_id
            LEFT JOIN ecommerce_analytics_marts.dim_product p ON i.product_id = p.product_id
            LEFT JOIN loc ON o.customer_state = loc.primary_state
            WHERE o.order_status NOT IN ('canceled', 'unavailable') 
              AND strftime(o.order_purchase_timestamp, '%Y-%m') BETWEEN '2017-01' AND '2018-08'
            GROUP BY 1, 2, 3
            ORDER BY 1, 2, 3;
        """).df().to_dict(orient="records")

        data_bundle = {
            "kpis": kpis,
            "monthly_trend": monthly_trend,
            "top_categories": top_categories,
            "cohort_matrix": cohort_matrix,
            "rfm_segments": rfm_segments,
            "payment_splits": payment_splits,
            "regional_logistics": regional_logistics,
            "top_sellers": top_sellers,
            "top_products": top_products,
            "cube": dimensional_cube
        }

        out_file = out_dir / "data.js"
        out_file.write_text(f"window.DASHBOARD_DATA = {json.dumps(data_bundle, indent=2)};", encoding="utf-8")
        print(f"[SUCCESS] Exported dashboard data bundle to: {out_file} ({out_file.stat().st_size / 1024:.1f} KB)")

if __name__ == "__main__":
    generate_dashboard_data()
