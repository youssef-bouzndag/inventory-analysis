import numpy as np
import pandas as pd

rng = np.random.default_rng(42)   # fixed seed: same data every run

N_PRODUCTS = 40
N_WEEKS = 52

#Products
categories = ["Home", "Office", "Garden", "Kitchen"]

products = pd.DataFrame({
    "product_id": [f"P{i:02d}" for i in range(1, N_PRODUCTS + 1)],
    "category": rng.choice(categories, N_PRODUCTS),
    "unit_cost": rng.uniform(5, 80, N_PRODUCTS).round(2),
    "lead_time_weeks": rng.integers(1, 5, N_PRODUCTS),      # 1 to 4 weeks
})
products["unit_price"] = (products["unit_cost"] * rng.uniform(1.2, 1.5, N_PRODUCTS)).round(2)
# Average weekly demand: a few products sell a lot, most sell little
products["avg_weekly_demand"] = rng.lognormal(mean=3.5, sigma=0.9, size=N_PRODUCTS).round(0)

# Seasonality: how strongly each category rises and falls during the year
season = {"Home": 0.10, "Office": 0.05, "Garden": 0.50, "Kitchen": 0.25}
products["season_strength"] = products["category"].map(season)
#Weekly demand 
rows = []
for _, p in products.iterrows():
    for week in range(1, N_WEEKS + 1):
        wave = 1 + p["season_strength"] * np.sin(2 * np.pi * (week - 10) / 52)
        mean = p["avg_weekly_demand"] * wave
        units = max(0, round(rng.normal(mean, 0.25 * mean)))   # 25% random variation
        rows.append({"product_id": p["product_id"], "week": week, "units": units})
demand = pd.DataFrame(rows)
#Save 
products.to_csv("products.csv", index=False)
demand.to_csv("demand.csv", index=False)
#Quick look
print("Products:", len(products), "| Weeks:", N_WEEKS, "| Demand rows:", len(demand))
print()
print(products.head(8).to_string(index=False))

total = demand.groupby("product_id")["units"].sum().sort_values(ascending=False)
print("\nTotal units sold:", int(total.sum()))
print("Top 5 products share of units:", round(total.head(5).sum() / total.sum() * 100, 1), "%")
print("Bottom 20 products share of units:", round(total.tail(20).sum() / total.sum() * 100, 1), "%")