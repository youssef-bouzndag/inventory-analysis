import pandas as pd

Z_BY_CLASS = {"A": 2.05, "B": 1.65, "C": 1.28}    # about 98%, 95% and 90% service targets
HOLDING_RATE = 0.20      # yearly cost of holding stock, as a share of its value

products = pd.read_csv("products.csv")
demand = pd.read_csv("demand.csv")
history = pd.read_csv("history.csv")
abc = pd.read_csv("abc.csv")[["product_id", "class"]]
products = products.merge(abc, on="product_id")
#Seasonal forecast, learned from last year
level = history.groupby("product_id")["units"].mean()
cat_week = history.groupby(["category", "week"])["units"].sum().unstack()
index = cat_week.div(cat_week.mean(axis=1), axis=0)
padded = pd.concat([index.iloc[:, -2:], index, index.iloc[:, :2]], axis=1)
index = padded.T.rolling(5, center=True).mean().T.iloc[:, 2:-2]
#Forecast error per product, measured on LAST year (not on the year we test)
history["forecast"] = [level[p] * index.loc[c, w] for p, c, w in
                       zip(history["product_id"], history["category"], history["week"])]
history["error"] = history["units"] - history["forecast"]
sigma = history.groupby("product_id")["error"].std()        # typical weekly miss, in units
#Run one year of inventory with a given policy
def run(policy, z):
    """policy: 'average' or 'seasonal'. z: dict class -> safety factor (0 = no safety stock)."""
    rows = []
    for _, p in products.iterrows():
        pid, lead = p["product_id"], int(p["lead_time_weeks"])
        weekly = demand[demand["product_id"] == pid].sort_values("week")["units"].tolist()
        safety = z[p["class"]] * sigma[pid] * (lead + 1) ** 0.5

        def target(t):
            if policy == "average":
                base = p["avg_weekly_demand"] * (lead + 1)
            else:
                base = sum(level[pid] * index.loc[p["category"], (t + k - 1) % 52 + 1]
                           for k in range(1, lead + 2))
            return round(base + safety)

        on_hand, arrivals, stock, lost, sold = target(0), {}, [], 0, 0
        for week, d in enumerate(weekly, start=1):
            on_hand += arrivals.get(week, 0)
            s = min(on_hand, d)
            lost += d - s
            sold += s
            on_hand -= s
            stock.append(on_hand)
            position = on_hand + sum(q for w, q in arrivals.items() if w > week)
            order = max(0, target(week) - position)
            if order > 0:
                arrivals[week + lead] = arrivals.get(week + lead, 0) + order

        rows.append({"product_id": pid, "class": p["class"], "safety_stock": round(safety),
                     "lost_units": lost, "demand": lost + sold,
                     "lost_revenue": lost * p["unit_price"],
                     "lost_profit": lost * (p["unit_price"] - p["unit_cost"]),
                     "stock_value": sum(stock) / len(stock) * p["unit_cost"]})
    return pd.DataFrame(rows)


def summarize(df):
    lost_profit = df["lost_profit"].sum()
    holding = df["stock_value"].sum() * HOLDING_RATE
    return {"lost_revenue": round(df["lost_revenue"].sum()),
            "stock_value": round(df["stock_value"].sum()),
            "fill_rate_%": round((1 - df["lost_units"].sum() / df["demand"].sum()) * 100, 1),
            "lost_profit": round(lost_profit),
            "holding_cost": round(holding),
            "total_cost": round(lost_profit + holding)}


zero = {"A": 0, "B": 0, "C": 0}
#Compare policies
results = {
    "1. Average demand, no safety stock (Lesson 3)": run("average", zero),
    "2. Seasonal forecast, no safety stock": run("seasonal", zero),
    "3. Seasonal forecast + safety stock by class": run("seasonal", Z_BY_CLASS),
}
comparison = pd.DataFrame({name: summarize(df) for name, df in results.items()}).T
print(comparison.to_string())

#Trade-off: one safety factor for all products 
print("\nSafety factor for all products (seasonal forecast):")
sweep = []
for z_all in [0, 0.5, 1.0, 1.5, 2.0, 2.5]:
    r = summarize(run("seasonal", {"A": z_all, "B": z_all, "C": z_all}))
    sweep.append({"z": z_all, **r})
print(pd.DataFrame(sweep).to_string(index=False))

#Where the safety stock goes (policy 3)
final = results["3. Seasonal forecast + safety stock by class"]
print("\nPolicy 3 by class:")
print(final.groupby("class").agg(products=("product_id", "count"),
                                 safety_units=("safety_stock", "sum"),
                                 lost_revenue=("lost_revenue", "sum"),
                                 stock_value=("stock_value", "sum")).round(0).to_string())

comparison.to_csv("policy_comparison.csv")
final.round(1).to_csv("safety_stock.csv", index=False)