Inventory Analysis

A Python-based inventory analysis project that transforms simulated weekly demand into inventory policy decisions.

The project analyses demand for 40 products over 52 weeks, performs ABC classification, evaluates inventory risk, compares forecasting methods, and tests different safety-stock policies based on total cost.

All data is simulated. The project demonstrates how demand analysis, forecasting, and inventory modelling can support operational decisions.

---

Contents

1. Project Structure
2. How to Run
3. How the Analysis Works
4. Output
5. Main Findings
6. Limitations
7. Requirements and License

---

1. Project Structure

inventory-analysis/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── 01_create_data.py
│   └── Lesson 1: Simulate weekly demand for 40 products
│
├── 02_abc.py
│   └── Lesson 2: ABC analysis based on revenue contribution
│
├── 03_inventory_risk.py
│   └── Lesson 3: Analyse stockouts, fill rate, and overstock
│
├── 04_forecast.py
│   └── Lesson 4: Compare demand forecasting methods
│
├── 05_safety_stock.py
│   └── Lesson 5: Compare inventory policies by total cost
│
└── 06_report.py
    └── Lesson 6: Generate the Excel report


Each script builds on the previous script's output. The project therefore follows the workflow:

Raw Demand
    ↓
ABC Analysis
    ↓
Inventory Risk
    ↓
Demand Forecast
    ↓
Safety Stock Policy
    ↓
Inventory Decision

---

2. How to Run

Step 1 — Install the requirements

pip install -r requirements.txt

Step 2 — Generate the demand data.

python 01_create_data.py

This generates simulated weekly demand for 40 products over 52 weeks.

The demand includes seasonal variation to represent changes in demand throughout the year.

Step 3 — Run the ABC analysis

python 02_abc.py

This classifies products according to their contribution to total revenue.

The analysis uses the conventional approximate thresholds:

* Class A: first 80% of cumulative revenue
* Class B: next 15%
* Class C: final 5%

Step 4 — Analyse inventory risk

python 03_inventory_risk.py

This simulates inventory without safety stock and measures:

* Stockouts
* Fill rate
* Inventory levels
* Overstock

Step 5 — Compare forecasting methods

python 04_forecast.py

This compares three forecasting approaches:

* Flat forecast
* Moving-average forecast
* Seasonal forecast

The forecasts are evaluated against the simulated demand.

Step 6 — Compare inventory policies

python 05_safety_stock.py

This compares three stocking policies using a total-cost model based on:

* Lost profit from stockouts
* Inventory holding cost

The objective is to identify which policy provides the best cost-performance trade-off.

Step 7 — Generate the Excel report

python 06_report.py

This generates:

inventory_report.xlsx

The workbook contains the main calculations, results, and charts.

Note: Close inventory_report.xlsx before running 06_report.py again. Otherwise, Python may not be able to overwrite the file.

---

3. How the Analysis Works

Demand Simulation

The project simulates weekly demand for 40 products over one year.

Each product has its own demand characteristics, including:

* Average demand
* Price
* Seasonal variation
* Random demand variation

The resulting dataset provides the input for the inventory analysis.

ABC Analysis

The ABC analysis ranks products according to their total revenue contribution.

Products are then classified according to their cumulative contribution to revenue.

This helps identify which products deserve greater inventory-management attention.

Inventory Risk

The inventory-risk model simulates inventory without safety stock.

It tracks whether available inventory can satisfy weekly demand and calculates indicators such as:

Column 1	Column 2
KPI	Description
Stockout	Demand that cannot be fulfilled because inventory is insufficient.
Fill rate	Percentage of demand fulfilled from available inventory.
Overstock	Inventory remaining after demand is satisfied.
Inventory value	The value of stock held in inventory.


Demand Forecasting

Three forecasting approaches are compared:

1. Flat Forecast

Uses average historical demand as the forecast.

2. Moving Average

Uses recent demand to estimate future demand.

3. Seasonal Forecast

Uses the seasonal pattern observed in the previous year to estimate future demand.

The forecasting methods are compared using forecast accuracy.

Safety Stock and Inventory Policies

The final analysis compares different inventory policies.

The model considers two main cost components:

Total Cost
    =
Lost Profit from Stockouts
    +
Inventory Holding Cost

A policy with more inventory can reduce stockouts and increase the fill rate, but it also increases the cost of holding inventory.

The objective is therefore not simply to maximise inventory or fill rate, but to identify an economically reasonable policy.

---

4. Output

The 06_report.py script generates:

inventory_report.xlsx

The workbook contains the main results from the analysis.

ABC Analysis

The report shows:

* Product revenue
* Revenue ranking
* Cumulative revenue contribution
* ABC classification

This identifies the products that contribute most significantly to total revenue.

Inventory Risk

The report includes indicators such as:

* Stockouts
* Fill rate
* Overstock
* Inventory value

These show the consequences of operating without safety stock.

Forecast Comparison

The forecasting analysis compares:

* Flat forecast
* Moving-average forecast
* Seasonal forecast

The results show which approach provides the most accurate estimate under the simulated demand pattern.

Inventory Policy Comparison

The policy analysis compares:

* Forecast-based ordering
* Safety-stock policies
* Lost-profit cost
* Holding cost
* Total cost
* Fill rate

This connects the analytical results to an actual inventory-management decision.

---

5. Main Findings

Using the default random seed:

* 14 of 40 products are classified as Class A and generate approximately 82% of total revenue.
* The seasonal forecast is the most accurate forecasting method under the simulated demand pattern.
* Using the seasonal forecast without safety stock produces the lowest total cost, approximately 53% lower than ordering based on average demand.
* Adding safety stock increases the fill rate to approximately 100%, but also significantly increases inventory value.
* Safety stock becomes economically attractive when the cost of a stockout is sufficiently high relative to the cost of holding additional inventory.

The main lesson is that the inventory decision is a cost trade-off, rather than simply a question of maximising service level.

---

6. Limitations

The project uses several simplifying assumptions.

* All demand and product data are simulated.
* The seasonal forecast uses the same underlying seasonal pattern from the previous year, which makes its performance more favourable than it would necessarily be with real-world data.
* The model covers only one year of weekly demand.
* The cost model treats a lost sale as lost profit only.
* Customer dissatisfaction and customer loss are not modelled.
* Penalties, expedited shipping, and other stockout-related costs are not included.
* Lead-time variability is simplified.
* Supplier constraints and minimum order quantities are not modelled.
* The inventory policies are evaluated using simulated rather than historical company data.

These assumptions mean that the results should be interpreted as a demonstration of the methodology, rather than as a real inventory recommendation.

---

7. Requirements and License

Requirements

* Python 3.9+
* Pandas
* NumPy
* OpenPyXL
* Matplotlib

See requirements.txt for the exact dependencies.

License

This project is licensed under the MIT License.
