# Power BI DAX Measures Library

All metrics in this project are defined as **explicit DAX measures**. Implicit summarizations (such as default sums in Power BI) are disabled to ensure consistent business definitions across all six report pages.

Measures are hosted in a dedicated disconnected table `_Measures` organized into logical display folders.

---

## Folder: `01 Financials & Revenue`

### `[Total Revenue]`
```dax
Total Revenue = 
SUM(fct_orders[total_order_value])
```
* **Description**: Total order gross value inclusive of product price and freight in Brazilian Real (BRL).
* **Format**: Currency (`R$ #,##0.00`)
* **Filter Context**: Filtered by `dim_date`, `dim_customer`, `dim_location`. Excludes cancelled orders when slicer is applied.

### `[Gross Merchandise Value]`
```dax
Gross Merchandise Value = 
SUM(fct_orders[gross_merchandise_value])
```
* **Description**: Total product merchandise value excluding freight charges.
* **Format**: Currency (`R$ #,##0.00`)

### `[Total Freight]`
```dax
Total Freight = 
SUM(fct_orders[total_freight_value])
```
* **Description**: Total shipping and freight costs collected from customers.
* **Format**: Currency (`R$ #,##0.00`)

### `[Freight Share %]`
```dax
Freight Share % = 
DIVIDE([Total Freight], [Total Revenue], 0)
```
* **Description**: Percentage of total revenue consumed by freight charges.
* **Format**: Percentage (`0.0%`)

### `[Total Payments]`
```dax
Total Payments = 
SUM(fct_payments[payment_value])
```
* **Description**: Total monetary amount successfully collected across all payment instruments.
* **Format**: Currency (`R$ #,##0.00`)

### `[Average Order Value]`
```dax
Average Order Value = 
DIVIDE([Gross Merchandise Value], [Total Orders], 0)
```
* **Description**: Average merchandise spend per completed order.
* **Format**: Currency (`R$ #,##0.00`)

---

## Folder: `02 Time Intelligence`

### `[Revenue Prior Month]`
```dax
Revenue Prior Month = 
CALCULATE(
    [Gross Merchandise Value],
    DATEADD(dim_date[date_day], -1, MONTH)
)
```
* **Description**: Merchandise revenue in the immediate preceding month.
* **Format**: Currency (`R$ #,##0.00`)

### `[Revenue MoM %]`
```dax
Revenue MoM % = 
VAR CurrentGMV = [Gross Merchandise Value]
VAR PreviousGMV = [Revenue Prior Month]
RETURN
    IF(
        NOT ISBLANK(PreviousGMV) && PreviousGMV > 0,
        DIVIDE(CurrentGMV - PreviousGMV, PreviousGMV, BLANK()),
        BLANK()
    )
```
* **Description**: Month-over-Month percentage change in GMV.
* **Format**: Percentage (`+0.0%;-0.0%;0.0%`)

### `[Revenue Prior Year]`
```dax
Revenue Prior Year = 
CALCULATE(
    [Gross Merchandise Value],
    SAMEPERIODLASTYEAR(dim_date[date_day])
)
```
* **Description**: Merchandise revenue in the equivalent period 12 months prior.
* **Format**: Currency (`R$ #,##0.00`)

### `[Revenue YoY %]`
```dax
Revenue YoY % = 
VAR CurrentGMV = [Gross Merchandise Value]
VAR PrevYearGMV = [Revenue Prior Year]
RETURN
    IF(
        NOT ISBLANK(PrevYearGMV) && PrevYearGMV > 0,
        DIVIDE(CurrentGMV - PrevYearGMV, PrevYearGMV, BLANK()),
        BLANK()
    )
```
* **Description**: Year-over-Year percentage change in GMV.
* **Format**: Percentage (`+0.0%;-0.0%;0.0%`)

### `[Rolling 3-Month Revenue]`
```dax
Rolling 3-Month Revenue = 
CALCULATE(
    [Gross Merchandise Value],
    DATESINPERIOD(
        dim_date[date_day],
        MAX(dim_date[date_day]),
        -3,
        MONTH
    )
)
```
* **Description**: Trailing 3-month cumulative merchandise revenue for trend smoothing.
* **Format**: Currency (`R$ #,##0.00`)

---

## Folder: `03 Customer Metrics`

### `[Total Orders]`
```dax
Total Orders = 
DISTINCTCOUNT(fct_orders[order_id])
```
* **Description**: Total count of unique order transactions.
* **Format**: Whole number (`#,##0`)

### `[Total Customers]`
```dax
Total Customers = 
DISTINCTCOUNT(fct_orders[customer_unique_id])
```
* **Description**: Count of distinct real-world customers with active purchase history.
* **Format**: Whole number (`#,##0`)

### `[Repeat Customer Count]`
```dax
Repeat Customer Count = 
CALCULATE(
    DISTINCTCOUNT(dim_customer[customer_unique_id]),
    dim_customer[lifetime_order_count] > 1
)
```
* **Description**: Count of unique customers who placed more than 1 lifetime order.
* **Format**: Whole number (`#,##0`)

### `[Repeat Customer %]`
```dax
Repeat Customer % = 
DIVIDE([Repeat Customer Count], [Total Customers], 0)
```
* **Description**: Percentage of active customer base making repeat purchases.
* **Format**: Percentage (`0.0%`)

### `[Customer Lifetime Value]`
```dax
Customer Lifetime Value = 
DIVIDE([Gross Merchandise Value], [Total Customers], 0)
```
* **Description**: Average revenue contributed per unique customer.
* **Format**: Currency (`R$ #,##0.00`)

---

## Folder: `04 Operations & Fulfillment SLA`

### `[Delivered Order Count]`
```dax
Delivered Order Count = 
CALCULATE(
    [Total Orders],
    fct_orders[order_status] = "delivered"
)
```
* **Description**: Count of orders successfully delivered to customer destination.
* **Format**: Whole number (`#,##0`)

### `[On-Time Order Count]`
```dax
On-Time Order Count = 
CALCULATE(
    [Total Orders],
    fct_orders[is_on_time] = 1
)
```
* **Description**: Orders delivered on or before the promised estimated delivery date.
* **Format**: Whole number (`#,##0`)

### `[Late Order Count]`
```dax
Late Order Count = 
CALCULATE(
    [Total Orders],
    fct_orders[is_late_delivery] = 1
)
```
* **Description**: Orders delivered after the promised estimated delivery date.
* **Format**: Whole number (`#,##0`)

### `[On-Time Delivery %]`
```dax
On-Time Delivery % = 
DIVIDE([On-Time Order Count], [Delivered Order Count], 0)
```
* **Description**: Percentage of delivered orders meeting delivery date SLA commitments.
* **Format**: Percentage (`0.0%`)

### `[Late Delivery %]`
```dax
Late Delivery % = 
DIVIDE([Late Order Count], [Delivered Order Count], 0)
```
* **Description**: Percentage of delivered orders that missed delivery date SLA commitments.
* **Format**: Percentage (`0.0%`)

### `[Average Delivery Days]`
```dax
Average Delivery Days = 
AVERAGE(fct_delivery[actual_delivery_days])
```
* **Description**: Average elapsed duration in days from order purchase to final customer delivery.
* **Format**: Decimal (`0.0 days`)

### `[Average Promised Days]`
```dax
Average Promised Days = 
AVERAGE(fct_delivery[estimated_delivery_days])
```
* **Description**: Average estimated delivery SLA communicated to customers at checkout.
* **Format**: Decimal (`0.0 days`)

### `[Average Carrier Transit Days]`
```dax
Average Carrier Transit Days = 
AVERAGE(fct_delivery[days_transit])
```
* **Description**: Average days spent in logistics carrier transit from seller dispatch to customer.
* **Format**: Decimal (`0.0 days`)

---

## Folder: `05 Satisfaction & Quality`

### `[Total Reviews]`
```dax
Total Reviews = 
COUNTROWS(fct_reviews)
```
* **Description**: Total customer satisfaction survey submissions.
* **Format**: Whole number (`#,##0`)

### `[Average Review Score]`
```dax
Average Review Score = 
AVERAGE(fct_reviews[review_score])
```
* **Description**: Mean satisfaction rating on 1 to 5 star scale.
* **Format**: Decimal (`0.00`)

### `[5-Star Review %]`
```dax
5-Star Review % = 
DIVIDE(
    CALCULATE([Total Reviews], fct_reviews[review_score] = 5),
    [Total Reviews],
    0
)
```
* **Description**: Proportion of customer reviews awarding the highest rating.
* **Format**: Percentage (`0.0%`)

### `[Detractor Review % (1-2 Stars)]`
```dax
Detractor Review % (1-2 Stars) = 
DIVIDE(
    CALCULATE([Total Reviews], fct_reviews[review_score] IN {1, 2}),
    [Total Reviews],
    0
)
```
* **Description**: Proportion of negative detractor reviews (1 or 2 stars).
* **Format**: Percentage (`0.0%`)
