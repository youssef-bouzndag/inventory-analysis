import numpy as np
import pandas as pd

HORIZON = 4          # forecasts are made 4 weeks ahead (the longest lead time)
MA_WEEKS = 4         # moving average uses 4 weeks of sales
products = pd.read_csv("products.csv")
demand = pd.read_csv("demand.csv")            # this year (the year we test on)
abc = pd.read_csv("abc.csv")[["product_id", "class"]]
#Last year's sales (simulated with the same pattern, new randomness)
rng = np.random.default_rng(7)
rows = []
for _, p in products.iterrows():
    for week in range(1, 53):
        wave = 1 + p["season_strength"] * np.sin(2 * np.pi * (week - 10) / 52)
        mean = p["avg_weekly_demand"] * wave
        rows.append({"product_id": p["product_id"], "category": p["category"],
                     "week": week, "units": max(0, round(rng.normal(mean, 0.25 * mean)))})
history = pd.DataFrame(rows)
history.to_csv("history.csv", index=False)
#What we learn from last year
level = history.groupby("product_id")["units"].mean()    # average weekly sales per product
# Seasonal index per category: that week's sales divided by the yearly average
cat_week = history.groupby(["category", "week"])["units"].sum().unstack()
index = cat_week.div(cat_week.mean(axis=1), axis=0)
# Smooth with a 5-week moving average (wrapping around the year) to remove noise
padded = pd.concat([index.iloc[:, -2:], index, index.iloc[:, :2]], axis=1)
index = padded.T.rolling(5, center=True).mean().T.iloc[:, 2:-2]
#Forecast every week of this year, using only information available 4 weeks earlier
out = []
for _, p in products.iterrows():
    actual = demand[demand["product_id"] == p["product_id"]].sort_values("week")["units"].tolist()
    for week in range(HORIZON + MA_WEEKS, 53):                   # weeks 8 to 52
        window = actual[week - HORIZON - MA_WEEKS: week - HORIZON]   # 4 weeks that ended 4 weeks ago
        out.append({
            "product_id": p["product_id"],
            "category": p["category"],
            "week": week,
            "actual": actual[week - 1],
            "flat": level[p["product_id"]],                                  # last year's average
            "moving_avg": sum(window) / MA_WEEKS,                            # latest 4 weeks known
            "seasonal": level[p["product_id"]] * index.loc[p["category"], week],
        })
fc = pd.DataFrame(out).merge(abc, on="product_id")
fc.round(1).to_csv("forecast.csv", index=False)

#Accuracy
methods = ["flat", "moving_avg", "seasonal"]

def accuracy(df):
    res = {}
    for m in methods:
        res[m + " error %"] = round((df[m] - df["actual"]).abs().sum() / df["actual"].sum() * 100, 1)
    return pd.Series(res)

print("Error % (lower is better; total absolute error / total sales)")
print(accuracy(fc).to_string())
for col in ["category", "class"]:
    table = pd.DataFrame({g: accuracy(d) for g, d in fc.groupby(col)}).T
    print(f"\nBy {col}:")
    print(table.to_string())

print("\nBias % (positive = forecast too high):")
for m in methods:
    print(f"  {m}: {round((fc[m] - fc['actual']).sum() / fc['actual'].sum() * 100, 1)}")