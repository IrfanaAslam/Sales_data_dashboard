"""
generate_sample_data.py
Generates a sample sales CSV for the dashboard.
Run: python generate_sample_data.py
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

OUT = Path("sample_sales_data.csv")

PRODUCTS = [
    ("Alpha Hoodie", "Apparel"),
    ("Beta T-shirt", "Apparel"),
    ("Gamma Sneakers", "Footwear"),
    ("Delta Cap", "Accessories"),
    ("Epsilon Jacket", "Apparel"),
    ("Zeta Socks", "Accessories"),
    ("Eta Laptop Sleeve", "Accessories"),
    ("Theta Watch", "Electronics"),
    ("Iota Charger", "Electronics"),
    ("Kappa Backpack", "Accessories"),
]

REGIONS = ["North", "South", "East", "West", "Central"]
SALESPEOPLE = ["Ayesha", "Bilal", "Carlos", "Dina", "Ehsan", "Fatima"]

NUM_ROWS = 1200
START_DATE = datetime.now().replace(day=1) - timedelta(days=365)  # one year back

def make_row(i):
    date = START_DATE + timedelta(days=random.randint(0, 364))
    product, category = random.choice(PRODUCTS)
    unit_price = round(random.uniform(8, 250), 2)
    qty = random.choices([1,1,1,2,3,4,5,10], weights=[30,30,10,10,8,6,4,2])[0]
    revenue = round(unit_price * qty, 2)
    region = random.choice(REGIONS)
    salesperson = random.choice(SALESPEOPLE)
    customer_id = f"C{random.randint(1000,9999)}"
    return {
        "OrderID": f"O{100000+i}",
        "Date": date.strftime("%Y-%m-%d"),
        "Product": product,
        "Category": category,
        "UnitPrice": unit_price,
        "Quantity": qty,
        "Revenue": revenue,
        "Region": region,
        "Salesperson": salesperson,
        "CustomerID": customer_id
    }

def main():
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "OrderID","Date","Product","Category","UnitPrice","Quantity","Revenue","Region","Salesperson","CustomerID"
        ])
        writer.writeheader()
        for i in range(NUM_ROWS):
            writer.writerow(make_row(i))
    print(f"Wrote sample data to {OUT.resolve()} ({NUM_ROWS} rows)")

if __name__ == "__main__":
    main()
