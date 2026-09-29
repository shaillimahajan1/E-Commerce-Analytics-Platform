# ADR-002: Dimensional Star Schema vs 3NF & One Big Table (OBT)

## Status
**Accepted**

## Context
Raw marketplace data contains 9 normalized relational tables with varying cardinality (100k orders, 112k items, 103k payments, 99k reviews, 33k products, 3k sellers, 1M geolocation points). We need a target modeling pattern that balances BI usability, query performance, storage efficiency, and analytical flexibility.

## Decision
Adopt a **Kimball Dimensional Star Schema** with dedicated Fact tables (`fct_orders`, `fct_order_items`, `fct_payments`, `fct_reviews`, `fct_delivery`) and conformed Dimension tables (`dim_customer`, `dim_product`, `dim_seller`, `dim_date`, `dim_location`).

## Alternatives Considered
* **One Big Table (OBT)**: Flattening everything into a single massive 100+ column table at the order item grain.
  * *Rejected*: Causes severe data duplication (e.g. customer name/address repeated for every item in an order), inflates payment values if joined directly without multi-fact modeling, and complicates customer-level RFM aggregations.
* **Third Normal Form (3NF)**: Maintaining normalized transactional schemas.
  * *Rejected*: Requires 8+ joins for basic reporting; poor comprehension for business analysts; excessive join latency in BI tools.
* **Data Vault 2.0**: Hubs, Links, and Satellites.
  * *Rejected*: Over-engineered for a mid-sized e-commerce analytics platform; adds unnecessary transformation overhead without distinct enterprise audit requirements.

## Tradeoffs & Consequences
* **Positive**: Clean separation of facts and dimensions enables intuitive self-service reporting in Power BI; eliminates double counting; allows separate analysis of payments, items, and reviews.
* **Positive**: Conformed dimensions (`dim_customer`, `dim_product`, `dim_seller`) provide unified cross-domain slicing.
* **Tradeoff**: Requires analytics engineers to maintain disciplined grain definitions and surrogate keys across facts and dimensions.
