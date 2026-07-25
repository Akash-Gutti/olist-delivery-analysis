# Olist Delivery & Satisfaction Analysis

Does late delivery cost customer satisfaction, and where in the fulfilment chain
does the delay originate?

**[Dashboard](https://datastudio.google.com/reporting/bd0ee20b-185d-4020-9f81-e0ab2fd821eb)** · **[Findings](docs/findings.md)** · **[SQL](sql/analysis.sql)**

## Summary

Analysis of 96,455 delivered orders from the Olist Brazilian e-commerce marketplace
(2016–2018), joined across orders, reviews, customers and products.

- Late delivery collapses satisfaction: on-time orders average 4.29 stars, late
  orders 2.57. 54% of late orders leave a 1–2 star review — six times the on-time
  rate, scaling monotonically with the size of the delay.
- The delay originates in transit (25.7 days for late orders vs 7.9 on-time), not
  seller handling or approval.
- Transit tracks distance from the São Paulo seller hub: northern states run 3–4×
  the transit time of the southeast, with satisfaction falling in step.
- The problem is systemic across product categories, not concentrated in any one —
  it is a regional logistics issue.

## Data

[Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
— ~100k real orders across nine linked tables, 2016–2018.

## Approach

1. **Load** — nine CSVs to PostgreSQL with primary keys and foreign-key indexes
   (`load_to_postgres.py`, `sql/schema.sql`)
2. **Profile** — order status, timestamp completeness, review coverage and
   duplicates (`profile.py`)
3. **Model** — a SQL view defining the analysable population and pre-computing
   lifecycle gaps via timestamp arithmetic (`sql/build_view.sql`)
4. **Analyse** — delivery bands, lateness vs satisfaction, lifecycle origin,
   geographic and category breakdowns across multi-table joins (`sql/analysis.sql`)
5. **Report** — two-page Looker Studio dashboard for operations stakeholders

## Reproducing

```bash
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
# download the Olist dataset from Kaggle into data/raw/
$env:PG_PASSWORD="your_password"
python load_to_postgres.py
# run sql/schema.sql and sql/build_view.sql in your SQL client
python export_for_looker.py
```

## Structure

```
├── load_to_postgres.py          # nine tables into Postgres
├── profile.py                   # data quality profile
├── export_for_looker.py         # dashboard extracts
├── sql/
│   ├── schema.sql               # keys and indexes
│   ├── build_view.sql           # the delivery_analysis view
│   └── analysis.sql             # the five analytical queries
├── docs/
│   └── findings.md              # results and interpretation
└── data/looker/                 # dashboard source CSVs
```