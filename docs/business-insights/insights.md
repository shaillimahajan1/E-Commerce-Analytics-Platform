# Empirical Business Insights Report

> **Analytical Note**: All observations are derived directly from the audited historical Olist dataset (2016–2018). In adherence to professional analytics engineering principles (Sections 49–51), these insights distinguish strictly between observed correlation and causal claims, utilize precise financial terminology (Gross Merchandise Value, Order Value, Freight), and present potential business actions without fabricated impact claims.

---

## Insight 1: Extreme Acquisition Dependency & Low Repeat Purchase Rate

### Observation
The Olist marketplace operates primarily as a single-purchase acquisition engine, with minimal organic repeat customer behavior.

### Evidence
- **Total Persistent Customers (`customer_unique_id`)**: 96,096
- **Repeat Customers (>1 completed order)**: 2,997
- **Repeat Customer Rate**: **3.12%**
- **Single-Order Customers**: 93,099 (96.88%)
- **Monthly Cohort Retention**: Across all 2017 monthly cohorts, Month 1 retention averages between **0.4% and 0.9%**, and Month 6 retention drops below **0.3%**.

### Interpretation
In marketplace e-commerce, low repeat purchase rates typically reflect one of two realities:
1. The platform functions as a fragmented product aggregator where consumers purchase specific, infrequent durable goods (e.g. office furniture, automotive parts, appliances) rather than consumable everyday goods.
2. Post-purchase engagement, brand recognition, and lifecycle CRM are underdeveloped, meaning buyers attribute their transaction experience to the external search engine or third-party seller rather than Olist.

### Potential Business Action
- **Category Diversification**: Incentivize sellers offering high-velocity, consumable categories (personal care, pet supplies, gourmet pantry) to encourage 30-to-60-day repurchase cycles.
- **Post-Purchase Loyalty Incentives**: Test cross-category coupon discounts delivered via automated email within 14 days of successful delivery.

### Limitation
The historical dataset contains limited external marketing attribution (cost per acquisition, ad channel origins). We cannot ascertain whether low retention was driven by customer churn or deliberate one-time promotional acquisition campaigns.

---

## Insight 2: High Revenue Concentration Across Top Categories (Pareto Core)

### Observation
A small subset of product categories accounts for the overwhelming majority of marketplace Gross Merchandise Value (GMV).

### Evidence
- Total catalog categories: 71 distinct product categories.
- Top 5 categories generate **R$ 5,511,842.14** out of R$ 13,591,643.70 total GMV (**40.55%** of all merchandise sales):
  1. `health_beauty`: R$ 1,258,681.34 (9.26% share)
  2. `watches_gifts`: R$ 1,205,005.68 (8.87% share)
  3. `bed_bath_table`: R$ 1,036,988.80 (7.63% share)
  4. `sports_leisure`: R$ 988,048.97 (7.27% share)
  5. `computers_accessories`: R$ 911,924.89 (6.71% share)
- The top 20% of categories (~14 categories) generate over **75%** of total marketplace GMV.

### Interpretation
Marketplace demand is highly concentrated in personal wellness, home living, and consumer tech accessories. Long-tail categories (e.g. security services, fashion accessories, CDs/DVDs) exhibit minimal customer demand while imposing catalog maintenance overhead.

### Potential Business Action
- **Seller Recruitment Priority**: Direct merchant acquisition efforts toward manufacturers and authorized distributors in the top 5 high-velocity categories.
- **Featured Promotion**: Optimize homepage curation and banner inventory around proven revenue-driving categories during seasonal shopping spikes.

### Limitation
The dataset does not provide merchant margin or commission structures; high-GMV categories may carry lower take rates for the platform compared to specialized niche segments.

---

## Insight 3: Conservative Delivery Date Estimation Masks Geographic Transit Disparities

### Observation
The marketplace maintains an overall high on-time delivery rate (92.1%) primarily by quoting heavily padded estimated delivery dates, while underlying interstate transit durations vary drastically by region.

### Evidence
- **Nationwide Average Actual Delivery Duration**: **12.5 days**
- **Nationwide Average Estimated Promised Delivery Date**: **24.5 days** (A built-in buffer of ~12 calendar days)
- **On-Time Delivery Rate**: **92.1%**
- **Regional Disparity**:
  - **Southeast Destination States (SP, PR, MG)**: Actual delivery averages **8.3 to 11.5 days**; On-time rate exceeds **94%**.
  - **North and Northeast Destination States (RR, AP, AM, MA)**: Actual delivery averages **26.8 to 29.3 days**; Late delivery rate climbs to **16.5% – 21.0%**, even with 30+ day promised estimates.

### Interpretation
While conservative checkout estimates protect customer expectations and keep overall SLA compliance above 90%, excessive promised delivery dates (25–30 days) may cause cart abandonment among buyers comparing delivery promises against regional competitors. Furthermore, logistics infrastructure in the North and Northeast suffers from severe delays due to long-haul cross-border trucking routes from Southeastern merchant hubs.

### Potential Business Action
- **Dynamic Delivery Estimation**: Replace static distance tables with ML-based dynamic SLA algorithms that reflect current carrier transit velocities by origin-destination state pairs.
- **Regional Merchant Onboarding**: Expand merchant recruitment in the Northeast to satisfy local demand through intrastate shipping routes (which average 5.4 days faster transit than interstate routes).

### Limitation
The data reflects historical logistics conditions between 2016 and 2018 in Brazil. Recent road infrastructure improvements and carrier micro-fulfillment hubs may alter current transit benchmarks.

---

## Insight 4: Strong Observed Association Between Delivery Delays and Negative Customer Reviews

### Observation
Orders experiencing delivery delays exhibit a dramatic surge in 1-star reviews and negative customer feedback compared to on-time deliveries.

### Evidence
- **On-Time Delivered Orders**:
  - Average Customer Satisfaction Score: **4.29 / 5.00**
  - Detractor Rate (1-2 Stars): **8.4%**
  - 5-Star Rating Proportion: **61.2%**
- **Late Delivered Orders (`is_late_delivery = 1`)**:
  - Average Customer Satisfaction Score: **2.21 / 5.00** (A 2.08-star drop)
  - Detractor Rate (1-2 Stars): **58.7%**
  - 5-Star Rating Proportion: **14.3%**

### Interpretation
Fulfillment reliability is the single strongest observed correlate with customer dissatisfaction in this dataset. When products arrive late, customers express dissatisfaction through review scores, even when product quality itself is satisfactory.

### Potential Business Action
- **Proactive Delay Communication**: Trigger automated email and SMS notifications immediately when a carrier scans indicate an expected delay, resetting expectations before the promised delivery date passes.
- **Merchant SLA Accountability**: Establish merchant performance tiers where sellers with late fulfillment rates >10% are required to utilize certified carrier partners.

### Limitation
We observe an association between late delivery and lower review scores. We cannot conclusively prove that the delay was the sole causal driver of every negative review without qualitative NLP sentiment analysis of the text comments.

---

## Insight 5: Predominance of Installment Financing in Credit Card Purchasing

### Observation
Brazilian consumers rely heavily on installment financing, with credit card payments representing the dominant tender type and an average of over 3 installments per transaction.

### Evidence
- **Tender Type Share of Total Monetary Value (R$ 16.01M)**:
  - Credit Card: **R$ 12,542,056.62 (78.34%)**
  - Boleto Bancário: **R$ 2,869,361.69 (17.92%)**
  - Voucher: **R$ 379,449.88 (2.37%)**
  - Debit Card: **R$ 217,998.89 (1.36%)**
- **Installment Distribution for Credit Card Orders**:
  - 1 Installment: 49.8% of transactions
  - 2 to 4 Installments: 26.4% of transactions
  - 5 to 10 Installments: 21.6% of transactions
  - Over 10 Installments: 2.2% of transactions
- Average ticket size for orders with >=5 installments is **R$ 284.10**, compared to **R$ 96.50** for single-installment orders.

### Interpretation
Installment financing is a critical enabler of higher-ticket e-commerce in Brazil. Consumers leverage interest-free or low-interest split payments to purchase higher-value durable goods (electronics, furniture, premium cosmetics).

### Potential Business Action
- **Installment Promotion on High-AOV Items**: Highlight monthly installment amounts (e.g. *"10x of R$ 28.40"*) on product detail pages and catalog search cards to reduce psychological price barriers.
- **Boleto Conversion Optimization**: Since boleto payments typically experience a 2–3 day payment reconciliation delay and higher unpaid abandonment, incentivize instant digital payment methods (such as PIX in modern platforms) to expedite order fulfillment.

### Limitation
The dataset does not contain merchant processing fees or financing costs associated with multi-installment credit card splits.
