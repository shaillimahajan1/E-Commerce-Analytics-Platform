# Power BI Report Design Blueprints (6 Pages)

This document provides layout blueprints, wireframe architectures, KPI assignments, and visual specifications for the 6-page production Power BI report.

---

# Design Philosophy & Standards (Section 38 Compliance)
1. **Curated Color Palette**:
   - Primary Accent: Midnight Indigo (`#1E293B`)
   - Brand Blue: Corporate Slate Blue (`#2563EB`)
   - Supporting Green (Positive / On-Time): Forest Emerald (`#059669`)
   - Supporting Red (Negative / Late): Crimson Alert (`#DC2626`)
   - Background: Neutral Cool Gray (`#F8FAFC`)
   - Card Surfaces: Pure White (`#FFFFFF`) with 1px border (`#E2E8F0`)
2. **Visual Clutter Elimination**: Zero decorative gauges, zero 3D visuals, zero uninformative donut/pie charts with >3 slices.
3. **Information Hierarchy**:
   - Top banner: Global Title + Date / Category / Region Slicers.
   - Row 1: High-level KPI Metric Cards with context / MoM delta.
   - Row 2: Macro Trend Visual (Line / Area / Combo chart) + Geographic / Category split.
   - Row 3: Detail Matrix or Performance Ranking Table with data bars.

---

# PAGE 1 — EXECUTIVE OVERVIEW

### Purpose & Audience
Provides the C-Suite (CEO, COO, CFO) and VP of Marketplace with an immediate, high-level pulse of commercial health, operational reliability, and customer satisfaction across Brazil.

### Business Questions Answered
1. What is our current Gross Merchandise Value (GMV), order volume, and Average Order Value?
2. Are revenue and orders trending up or down month-over-month?
3. What percentage of customer shipments are arriving on time vs late?
4. How satisfied are our buyers (average review score)?
5. Which Brazilian macro-regions generate the highest order volume?

### Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: E-Commerce Marketplace Executive Overview | Filters: [Date Range] [Macro Region] [State]  |
+---------------------------------------------------------------------------------------------------+
| [ GMV: R$ 13.59M ]   [ Total Orders: 99.4K ]   [ AOV: R$ 136.68 ]   [ On-Time: 92.1% ]   [ CSAT: 4.09★ ] |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 1: Monthly GMV & Order Volume Trend (2016-2018)      | VISUAL 2: Orders by Macro Region    |
| (Line & Clustered Column: GMV on Column, Orders on Line)    | (Horizontal Clustered Bar Chart)    |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 3: Top 10 Product Categories by Revenue Contribution | VISUAL 4: Regional Fulfillment SLA  |
| (Horizontal Bar Chart with % Share)                         | (Matrix: Region, Orders, On-Time %) |
+---------------------------------------------------------------------------------------------------+
```

### Visual Specifications
* **KPI Card 1**: `[Gross Merchandise Value]` with dynamic indicator vs `[Revenue Prior Month]`.
* **KPI Card 2**: `[Total Orders]`.
* **KPI Card 3**: `[Average Order Value]`.
* **KPI Card 4**: `[On-Time Delivery %]` (Green if >=90%, Red if <90%).
* **KPI Card 5**: `[Average Review Score]` formatted as decimal with star rating icon.
* **Visual 1 (Primary)**: Line and Clustered Column Chart.
  * X-Axis: `dim_date[year_month]`
  * Column Values: `[Gross Merchandise Value]`
  * Line Values: `[Total Orders]`
* **Visual 2**: Clustered Bar Chart.
  * Y-Axis: `dim_location[macro_region]`
  * X-Axis: `[Total Orders]`
  * Data Label: % of Total.
* **Visual 3**: Clustered Bar Chart.
  * Y-Axis: `dim_product[product_category_name_english]`
  * X-Axis: `[Gross Merchandise Value]` (Top 10 filtered).
* **Visual 4**: Matrix Table.
  * Rows: `dim_location[macro_region]` -> `dim_location[primary_state]`
  * Values: `[Total Orders]`, `[Gross Merchandise Value]`, `[Average Delivery Days]`, `[On-Time Delivery %]`.

---

# PAGE 2 — SALES & REVENUE

### Purpose & Audience
Designed for Commercial Directors and Category Managers to dissect financial trends, order velocity, ticket size (AOV), and payment method adoption.

### Business Questions Answered
1. What is our Month-over-Month (MoM) and Year-over-Year (YoY) revenue growth trajectory?
2. How does freight cost compare to product merchandise value over time?
3. What payment methods (Credit Card, Boleto, Voucher, Debit) dominate transaction value?
4. Are customers choosing installments, and what is the average installment count?

### Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: Commercial Revenue & Sales Analytics | Filters: [Date Range] [Payment Method] [Category]  |
+---------------------------------------------------------------------------------------------------+
| [ GMV: R$ 13.59M ]   [ Freight: R$ 2.42M ]   [ Freight %: 15.1% ]   [ MoM Growth: +4.2% ]         |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 1: Monthly Merchandise GMV vs Freight Value          | VISUAL 2: Payment Instrument Share  |
| (Stacked Column Chart: GMV + Freight = Total Revenue)       | (Donut Chart: Value by Tender Type) |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 3: Monthly Growth Trajectory (% MoM & YoY)           | VISUAL 4: Payment Installment Depth |
| (Line Chart: % Change with 0% baseline benchmark)           | (Clustered Column: Orders by #)     |
+---------------------------------------------------------------------------------------------------+
```

### Visual Specifications
* **KPI Card 1**: `[Gross Merchandise Value]`.
* **KPI Card 2**: `[Total Freight]`.
* **KPI Card 3**: `[Freight Share %]`.
* **KPI Card 4**: `[Revenue MoM %]`.
* **Visual 1**: 100% Stacked Column Chart or Stacked Column Chart.
  * X-Axis: `dim_date[year_month]`
  * Values: `[Gross Merchandise Value]`, `[Total Freight]`
* **Visual 2**: Donut Chart.
  * Legend: `fct_payments[payment_type]`
  * Values: `[Total Payments]`
* **Visual 3**: Line Chart.
  * X-Axis: `dim_date[year_month]`
  * Values: `[Revenue MoM %]`, `[Revenue YoY %]`
  * Reference Line: Constant Line at 0%.
* **Visual 4**: Column Chart.
  * X-Axis: `fct_payments[payment_installments]`
  * Values: `[Total Payments]`, `[Total Orders]`

---

# PAGE 3 — CUSTOMER ANALYTICS & RETENTION

### Purpose & Audience
Built for Growth Marketers and Customer Lifecycle (CRM) Managers to monitor customer acquisition cohorts, repeat purchase loyalty, and RFM behavioral segments.

### Business Questions Answered
1. How many unique customers have purchased on Olist, and what percentage return for a 2nd order?
2. What are the retention rates of monthly customer acquisition cohorts over 12 months?
3. How are customers distributed across RFM segments (Champions, Loyal, Recent, At Risk)?
4. What is the Customer Lifetime Value (CLV) across segments and geographic regions?

### Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: Customer Lifecycle, Cohorts & RFM Analytics | Filters: [Acquisition Year] [State] [RFM]   |
+---------------------------------------------------------------------------------------------------+
| [ Total Customers: 96.1K ]   [ Repeat Buyers: 2.99K ]   [ Repeat %: 3.1% ]   [ Avg CLV: R$ 141.4 ] |
+---------------------------------------------------------------------------------------------------+
| VISUAL 1: Customer Cohort Retention Heatmap Matrix (Acquisition Month vs M0-M12 Elapsed Months)   |
| (Matrix visual with conditional background gradient based on retention_rate_pct)                  |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 2: RFM Customer Segment Breakdown                    | VISUAL 3: Customer Value by State   |
| (Treemap / Bar Chart: Customer Count & Revenue by Segment)  | (Scatter / Bar: Customers vs AOV)   |
+---------------------------------------------------------------------------------------------------+
```

### Visual Specifications
* **KPI Card 1**: `[Total Customers]` (Count of distinct `customer_unique_id`).
* **KPI Card 2**: `[Repeat Customer Count]`.
* **KPI Card 3**: `[Repeat Customer %]` (Key marketplace retention insight: ~3.1%).
* **KPI Card 4**: `[Customer Lifetime Value]`.
* **Visual 1 (Flagship Cohort Matrix)**: Matrix Visual.
  * Rows: `mart_customer_retention[cohort_month]` (formatted YYYY-MM)
  * Columns: `mart_customer_retention[month_number]` (0, 1, 2, ..., 12)
  * Values: `AVERAGE(mart_customer_retention[retention_rate_pct])`
  * Conditional Formatting: Background color scales from Cool White (0%) to Dark Slate Blue (100%).
* **Visual 2**: Clustered Bar / Treemap Chart.
  * Category: `dim_customer[rfm_segment]`
  * Values: `[Total Customers]`, Tooltip: `[Total Revenue]`.
* **Visual 3**: Clustered Column Chart.
  * X-Axis: `dim_customer[primary_customer_state]` (Top 10)
  * Values: `[Total Customers]`, `[Customer Lifetime Value]`.

---

# PAGE 4 — SELLER PERFORMANCE & HEALTH

### Purpose & Audience
Designed for Marketplace Operations and Merchant Success teams to monitor vendor SLA compliance, revenue tiers, and late delivery rates.

### Business Questions Answered
1. How concentrated is marketplace revenue across our active sellers?
2. Which sellers exhibit high cancellation or late delivery rates (>10% late)?
3. Does poor delivery SLA compliance correlate with lower customer review scores?
4. Which geographic hubs house our top merchants?

### Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: Seller Performance & Vendor SLA Scorecards | Filters: [Seller Tier] [Seller State]        |
+---------------------------------------------------------------------------------------------------+
| [ Active Sellers: 3,095 ]   [ Top Tier GMV: 62.4% ]   [ Avg Delivery: 12.5d ]   [ Avg CSAT: 4.1★ ] |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 1: Seller Revenue Tier Distribution                  | VISUAL 2: Delivery SLA vs Ratings   |
| (Donut / Stacked Bar: Sellers by Revenue Tier)              | (Scatter Plot: Late % vs Avg Review)|
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 3: Detailed Seller Scorecard Matrix (Rank, Seller ID, State, Orders, GMV, On-Time %, CSAT) |
| (Searchable Matrix with conditional color formatting on SLA and Review Score)                     |
+---------------------------------------------------------------------------------------------------+
```

### Visual Specifications
* **KPI Card 1**: `DISTINCTCOUNT(dim_seller[seller_id])`.
* **KPI Card 2**: Revenue share of Tier 1 & Tier 2 sellers.
* **KPI Card 3**: `[Average Delivery Days]`.
* **KPI Card 4**: `[Average Review Score]`.
* **Visual 1**: Donut Chart.
  * Legend: `dim_seller[seller_revenue_tier]`
  * Values: `SUM(dim_seller[lifetime_revenue])`
* **Visual 2**: Scatter Plot.
  * X-Axis: `dim_seller[late_orders_count] / dim_seller[delivered_orders_count]` (Late Rate %)
  * Y-Axis: `dim_seller[average_review_score]`
  * Size: `dim_seller[lifetime_orders_count]`
  * Tooltip: `dim_seller[seller_id]`, `dim_seller[seller_city]`
* **Visual 3**: Interactive Matrix.
  * Rows: `mart_seller_performance[revenue_rank]`, `mart_seller_performance[seller_id]`
  * Values: `[Gross Merchandise Value]`, `[Total Orders]`, `[On-Time Delivery %]`, `[Average Delivery Days]`, `[Average Review Score]`.

---

# PAGE 5 — DELIVERY & OPERATIONS

### Purpose & Audience
Built for the VP of Supply Chain, Logistics Managers, and Carrier Partner teams to track regional fulfillment latency, promised vs actual delivery SLAs, and carrier performance.

### Business Questions Answered
1. What is the nationwide average fulfillment duration from order placement to doorstep delivery?
2. How accurate are our customer-facing estimated delivery dates (promised SLA)?
3. What percentage of shipments arrive late, and which states experience the highest delays?
4. How do interstate cross-border shipments compare to local intrastate routes in delivery time and freight costs?

### Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: Logistics, Fulfillment & Delivery SLA Analytics | Filters: [Date Range] [Origin] [Dest]  |
+---------------------------------------------------------------------------------------------------+
| [ Avg Delivery: 12.5d ]   [ Promised: 24.5d ]   [ On-Time %: 92.1% ]   [ Late Rate %: 7.9% ]      |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 1: Actual Delivery Days vs Promised SLA by Month     | VISUAL 2: Route Dynamics Breakdown  |
| (Line Chart: Actual Days vs Estimated Days over Time)       | (Bar Chart: Intra vs Interstate)    |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 3: State-by-State Delivery SLA Performance Map       | VISUAL 4: Delivery Delay Outliers   |
| (Filled Map / Ranked Bar: Average Delivery Days by State)   | (Histogram: Days Early vs Days Late)|
+---------------------------------------------------------------------------------------------------+
```

### Visual Specifications
* **KPI Card 1**: `[Average Delivery Days]`.
* **KPI Card 2**: `[Average Promised Days]` (Shows buffer built into checkout estimates: ~24.5d vs 12.5d actual).
* **KPI Card 3**: `[On-Time Delivery %]`.
* **KPI Card 4**: `[Late Delivery %]`.
* **Visual 1**: Line Chart.
  * X-Axis: `dim_date[year_month]`
  * Values: `[Average Delivery Days]`, `[Average Promised Days]`
* **Visual 2**: Clustered Bar Chart.
  * Category: Shipping Route (`Intrastate` vs `Interstate`)
  * Values: `[Average Delivery Days]`, `[Freight Share %]`, `[Late Delivery %]`
* **Visual 3**: Horizontal Clustered Bar Chart (Ranked by Delivery Duration).
  * Y-Axis: `fct_delivery[customer_state]`
  * X-Axis: `[Average Delivery Days]`
  * Color Hue: Highlight states exceeding 18 days (e.g. North/Northeast states like AP, RR, AM).
* **Visual 4**: Column Chart.
  * X-Axis: Delivery Delay Days Bracket (Binned: `<= -10d (Early)`, `-5 to 0d`, `1 to 5d (Late)`, `> 5d (Severe Late)`)
  * Values: `[Total Orders]`.

---

# PAGE 6 — PRODUCT PERFORMANCE & CATALOG CONCENTRATION

### Purpose & Audience
Built for Merchandising Leads, Inventory Planners, and Category Managers to analyze catalog velocity, product ratings, returns/complaints, and Pareto concentration.

### Business Questions Answered
1. What percentage of products generate the top 80% of marketplace revenue (Pareto Core)?
2. What are our top-selling individual SKUs by revenue and volume?
3. Which product categories maintain high sales velocity while preserving high review scores?
4. What freight sizing tiers (Bulky/Heavy vs Standard Parcel) generate the most order volume?

### Layout Wireframe
```text
+---------------------------------------------------------------------------------------------------+
| HEADER: Product Catalog & Category Performance | Filters: [Category] [Freight Tier] [Pareto Seg]  |
+---------------------------------------------------------------------------------------------------+
| [ Total SKUs: 32.9K ]   [ Pareto Core SKUs: ~18% ]   [ Avg Price: R$ 120.6 ]   [ Avg Rating: 4.1★]|
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 1: Cumulative Pareto 80/20 Revenue Curve             | VISUAL 2: Category Matrix Scatter   |
| (Line Chart: % SKUs vs % Cumulative Revenue)                | (Scatter: Units Sold vs Avg CSAT)   |
+-------------------------------------------------------------+-------------------------------------+
| VISUAL 3: Top 25 Highest Grossing Products Table            | VISUAL 4: Volume by Freight Sizing  |
| (Table: SKU ID, Category, Units Sold, GMV, Avg Rating)      | (Donut Chart: Units by Tier)        |
+---------------------------------------------------------------------------------------------------+
```

### Visual Specifications
* **KPI Card 1**: Total active catalog products count (`DISTINCTCOUNT(dim_product[product_id])`).
* **KPI Card 2**: Pareto Core SKU Count (`CALCULATE(COUNTROWS(dim_product), mart_product_performance[pareto_segment] = "Top 80% Revenue Contributor (Pareto Core)")`).
* **KPI Card 3**: `AVERAGE(dim_product[average_unit_price])`.
* **KPI Card 4**: `AVERAGE(dim_product[average_review_score])`.
* **Visual 1**: Line Chart (Pareto Curve).
  * X-Axis: `mart_product_performance[overall_revenue_rank]`
  * Values: `mart_product_performance[cumulative_revenue_pct]`
  * Reference Line: Constant horizontal line at 80%.
* **Visual 2**: Scatter Plot (Category Health Matrix).
  * X-Axis: Category Units Sold
  * Y-Axis: Category Average Review Score
  * Size: Category Gross Merchandise Value
  * Category Labels: `dim_product[product_category_name_english]`
* **Visual 3**: Table.
  * Columns: `product_id`, `product_category_name_english`, `freight_size_tier`, `lifetime_units_sold`, `lifetime_revenue`, `average_review_score`.
* **Visual 4**: Donut Chart.
  * Legend: `dim_product[freight_size_tier]`
  * Values: `SUM(dim_product[lifetime_units_sold])`.
