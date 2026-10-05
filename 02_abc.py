import pandas as pd

products = pd.read_csv("products.csv")
demand = pd.read_csv("demand.csv")
#Revenue and profit per product
total_units = demand.groupby("product_id")["units"].sum().rename("units_sold")
abc = products.merge(total_units, on="product_id")
abc["revenue"] = (abc["units_sold"] * abc["unit_price"]).round(2)
abc["profit"] = (abc["units_sold"] * (abc["unit_price"] - abc["unit_cost"])).round(2)
#Sort by revenue, then cumulative share
abc = abc.sort_values("revenue", ascending=False).reset_index(drop=True)
abc["revenue_%"] = abc["revenue"] / abc["revenue"].sum() * 100
abc["cumulative_%"] = abc["revenue_%"].cumsum()
abc["cumulative_before_%"] = abc["cumulative_%"] - abc["revenue_%"]
#Classes: A = first 80% of revenue, B = next 15%, C = last 5% 
def classify(before):
    if before < 80:
        return "A"
    if before < 95:
        return "B"
    return "C"

abc["class"] = abc["cumulative_before_%"].apply(classify)
#Summary per class
summary = abc.groupby("class").agg(
    products=("product_id", "count"),
    revenue=("revenue", "sum"),
    profit=("profit", "sum"),
).reset_index()
summary["products_%"] = (summary["products"] / len(abc) * 100).round(1)
summary["revenue_%"] = (summary["revenue"] / abc["revenue"].sum() * 100).round(1)
summary["profit_%"] = (summary["profit"] / abc["profit"].sum() * 100).round(1)

abc.round(2).to_csv("abc.csv", index=False)

print(abc[["product_id", "category", "units_sold", "revenue", "revenue_%",
           "cumulative_%", "class"]].head(10).round(1).to_string(index=False))
print()
print(summary[["class", "products", "products_%", "revenue_%", "profit_%"]].to_string(index=False))
print()
print("Revenue by category:")
print(abc.groupby("category")["revenue"].sum().sort_values(ascending=False).round(0).to_string())