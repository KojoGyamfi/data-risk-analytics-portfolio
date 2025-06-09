# 🧾 Case Study: Attribution Analysis for Multi-Region Options Book

## 🎯 Objective

A trading risk analyst is tasked with explaining daily and cumulative P&L on a portfolio of equity options spanning Tech, Energy, Healthcare, and FMCG sectors across US, EU, and APAC.

---

## 🔍 Step 1: Identify Top Contributors

Using the dashboard:
- Group by **sector**
- See that **Tech** and **Energy** had the largest actual and explained P&L

---

## 📉 Step 2: Analyze Greek Attribution

- In Tech, **Delta** and **Gamma** dominate P&L
- In Energy, **Vega** is significant — consistent with recent volatility changes

---

## ⚠️ Step 3: Spot Residuals

- The residual column shows a growing unexplained P&L in **Healthcare**
- Drilldown shows it's driven by a set of long Vega positions
- Possibly due to misestimated vol skew or expiration proximity

---

## 📈 Step 4: View Cumulative Trends

- In the cumulative chart, **FMCG** shows divergence between actual and explained — alerts need to be set

---

## 🔍 Step 5: Drill Down on Sector

- Analyst selects **Healthcare**
- Trade-level table shows one trade with large residual on 2025-06-15
- Analyst can now investigate pricing model assumptions or trade booking

---

## ✅ Outcome

Analyst identifies:
- Sector- and trade-level drivers of P&L
- Residuals requiring escalation
- Trends that align or diverge from model expectations

This improves transparency and supports daily sign-off for trading desks.
