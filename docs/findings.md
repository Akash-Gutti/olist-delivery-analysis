# Olist Delivery & Satisfaction Analysis — Findings

**Data:** Olist Brazilian E-Commerce public dataset. 96,455 delivered orders with a
complete delivery timeline, 2016–2018, joined across orders, reviews, customers,
order items and products.
**Dashboard:** [https://datastudio.google.com/reporting/bd0ee20b-185d-4020-9f81-e0ab2fd821eb]
**Analysis:** (https://github.com/Akash-Gutti/olist-delivery-analysis)/sql/analysis.sql

---

## Question

Does late delivery cost customer satisfaction, and where in the fulfilment chain
does the delay originate?

---

## Headline

Of 96,455 delivered orders, 8.1% (7,825) arrived after their estimated date. Those
late orders are catastrophic for satisfaction, the delay originates almost entirely
in transit rather than seller handling, and transit time tracks distance from the
São Paulo seller hub. This is a regional logistics problem, not a seller or category
one.

Three findings:

1. Late delivery collapses satisfaction: on-time orders average 4.29 stars, late
   orders 2.57 — and 54% of late orders leave a 1–2 star review, six times the
   on-time rate.
2. The delay lives in transit: late orders spend 25.7 days in carrier transit
   versus 7.9 for on-time orders. Approval and handling barely differ.
3. Transit tracks geography: northern states run 3–4× the transit time of the
   southeast, and their satisfaction scores fall accordingly.

---

## Finding 1 — Late delivery collapses satisfaction

The relationship is not subtle and it scales with the size of the delay.

| Delivery band | Orders | Avg review |
|---|---|---|
| On time or early | 88,630 | 4.29 |
| Late 1–3 days | 2,662 | 3.77 |
| Late 4–7 days | 1,818 | 2.32 |
| Late 8–14 days | 1,790 | 1.74 |
| Late 15+ days | 1,555 | 1.71 |

Every additional band of lateness drops the score, monotonically. Even a delay of
one to three days costs half a star; past a week, orders average below two.

The sharpest cut is the share of actively negative reviews. Among on-time orders,
9.2% leave a 1 or 2 star rating. Among late orders, 54.1% do — a near sixfold
increase.

The monotonic pattern matters more than any single number. A one-off correlation
could be noise or a confound; a dose-response that worsens at every step is the
signature of a real causal relationship. Delivery timing is not one factor among
many in how customers rate an order — for late orders it is close to the whole
story.

---

## Finding 2 — The delay originates in transit

Breaking the order lifecycle into its three gaps shows exactly where late orders
diverge from on-time ones.

| Stage | On-time (days) | Late (days) |
|---|---|---|
| Purchase → approval | 0.42 | 0.51 |
| Approval → carrier handover | 2.58 | 5.32 |
| Carrier → customer (transit) | 7.89 | 25.68 |

Approval is instant in both cases. Seller handling roughly doubles for late orders
but remains small in absolute terms. Transit, however, more than triples — a gap of
nearly eighteen days.

This locates the problem precisely. Late orders are not late because sellers are
slow to accept or dispatch them; they are late because the package spends an extra
two and a half weeks in the carrier network. For an operations team the implication
is direct: the lever is logistics and carrier performance, not seller onboarding or
approval workflow.

---

## Finding 3 — Transit tracks distance from the seller hub

If transit is the problem and most sellers are concentrated in São Paulo, distance
should predict delay. It does.

| State | Orders | Late % | Avg transit (days) | Avg review |
|---|---|---|---|---|
| Maranhão (MA) | 716 | 19.7 | 18.0 | 3.83 |
| Ceará (CE) | 1,278 | 15.3 | 17.9 | 3.94 |
| Bahia (BA) | 3,256 | 14.0 | 16.0 | 3.93 |
| São Paulo (SP) | 40,488 | 5.9 | 5.6 | 4.25 |
| Minas Gerais (MG) | 11,351 | 5.6 | 8.8 | 4.19 |
| Paraná (PR) | 4,923 | 5.0 | 8.8 | 4.24 |

São Paulo — the seller hub and largest market — is the best served on every
measure. The northern and northeastern states run three to four times its transit
time and rate their orders lower in step.

The chain is now complete end to end: distance drives transit, transit drives
lateness, lateness drives dissatisfaction. The practical reading is that
improvement effort should be regional. Whether the answer is northern distribution
centres, renegotiated carrier terms for long routes, or simply more honest delivery
estimates for distant states is an operational decision — but the data points
unambiguously at the north and northeast.

---

## Finding 4 — It is systemic, not category-specific

Late-delivery rates by product category cluster tightly between 8% and 13%, with no
dramatic outlier. The highest-volume categories — health & beauty (8,647 orders),
bed/bath/table (9,271) — sit close to the marketplace average.

This is itself a finding. There is no problem product type to fix; lateness is a
property of the fulfilment network, not of what is being shipped. It reinforces
Finding 3: the variable that predicts delay is geography, not category.

---

## What this analysis cannot tell you

- **Estimates are Olist's own, not a contractual SLA.** "Late" means later than
  Olist's predicted date. Those estimates are conservative — most orders beat them
  comfortably — so lateness here is a strong signal, but it is measured against an
  internal benchmark, not a promised delivery window.
- **No causal proof, only a strong dose-response.** The monotonic pattern is
  compelling but observational. A distant customer who receives a late delivery may
  differ in other ways from a nearby on-time one.
- **Review text not analysed.** Scores are used; the free-text reviews, which would
  reveal whether customers explicitly blame delivery, were not processed.
- **Data ends in 2018** and reflects one marketplace in one country.
- **No cost data**, so the financial impact of the satisfaction loss — churn,
  lifetime value — cannot be quantified.

---

## Method

Nine raw tables loaded to PostgreSQL. Analysis restricted to delivered orders with a
complete five-stamp timeline (96,455 of 99,441). Duplicate reviews resolved to one
per order, keeping the most recent. A SQL view (`delivery_analysis`) pre-computes
the lifecycle gaps and lateness flag using timestamp arithmetic; all findings query
that view. Full method: `sql/analysis.sql`.