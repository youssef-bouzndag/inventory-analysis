import pandas as pd

TARGET_WEEKS_EXTRA = 1       # order-up-to level covers lead time + 1 week of average demand
OVERSTOCK_WEEKS = 6          # more than this many weeks of cover = overstock

products = pd.read_csv("products.csv")
demand = pd.read_csv("demand.csv")
abc = pd.read_csv("abc.csv")[["product_id", "class"]]
rows = []
for _, p in products.iterrows():
    weekly = demand[demand["product_id"] == p["product_id"]].sort_values("week")["units"].tolist()
    lead = int(p["lead_time_weeks"])
    avg = p["avg_weekly_demand"]
    order_up_to = round(avg * (lead + TARGET_WEEKS_EXTRA))   # no safety stock

    on_hand = order_up_to          # start the year fully stocked
    arrivals = {}                  # week -> units arriving at the start of that week
    stockout_weeks = 0
    sold_total = 0
    lost_total = 0
    end_stock = []

    for week, d in enumerate(weekly, start=1):
        on_hand += arrivals.get(week, 0)           # 1. deliveries arrive
        sold = min(on_hand, d)                     # 2. customers buy
        lost = d - sold                            #    what we cannot sell is lost
        on_hand -= sold
        if lost > 0:
            stockout_weeks += 1
        sold_total += sold
        lost_total += lost
        end_stock.append(on_hand)

        on_order = sum(q for w, q in arrivals.items() if w > week)    # 3. review and order
        order = max(0, order_up_to - (on_hand + on_order))
        if order > 0:
            arrivals[week + lead] = arrivals.get(week + lead, 0) + order

    avg_stock = sum(end_stock) / len(end_stock)
    rows.append({
        "product_id": p["product_id"],
        "category": p["category"],
        "lead_time_weeks": lead,
        "order_up_to": order_up_to,
        "demand_total": sold_total + lost_total,
        "lost_units": lost_total,
        "stockout_weeks": stockout_weeks,
        "fill_rate_%": round(sold_total / (sold_total + lost_total) * 100, 1),
        "avg_stock_units": round(avg_stock, 1),
        "weeks_of_cover": round(avg_stock / avg, 1),
        "avg_stock_value": round(avg_stock * p["unit_cost"], 0),
        "lost_revenue": round(lost_total * p["unit_price"], 0),
    })
risk = pd.DataFrame(rows).merge(abc, on="product_id")
risk["overstock"] = risk["weeks_of_cover"] > OVERSTOCK_WEEKS
risk.to_csv("inventory_risk.csv", index=False)
#Summary per class
summary = risk.groupby("class").agg(
    products=("product_id", "count"),
    avg_fill_rate=("fill_rate_%", "mean"),
    stockout_weeks=("stockout_weeks", "sum"),
    lost_revenue=("lost_revenue", "sum"),
    avg_stock_value=("avg_stock_value", "sum"),
    overstocked=("overstock", "sum"),
).round(1).reset_index()
print(summary.to_string(index=False))
print()
print("Total lost revenue:", int(risk["lost_revenue"].sum()))
print("Total average stock value:", int(risk["avg_stock_value"].sum()))
print("Products with a stockout in more than 10 weeks:", int((risk["stockout_weeks"] > 10).sum()))
print()
print("Worst 5 by lost revenue:")
print(risk.sort_values("lost_revenue", ascending=False).head(5)[
    ["product_id", "class", "lead_time_weeks", "fill_rate_%", "stockout_weeks", "lost_revenue"]
].to_string(index=False))
print()
print("Overstocked products:", list(risk[risk["overstock"]]["product_id"]))
