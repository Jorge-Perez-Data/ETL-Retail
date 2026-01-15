from __future__ import annotations

import os, random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

# -------------------- Config --------------------
@dataclass(frozen=True)
class Cfg:
    seed: int = 42
    n_customers: int = 8000
    n_products: int = 1200
    n_stores: int = 60
    n_orders: int = 120000
    max_lines: int = 5
    start: date = date(2024, 1, 1)
    end: date = date(2025, 12, 31)
    out_dir: str = "data/raw"
    null_ship_rate: float = 0.002
    dup_frac: float = 0.001

CFG = Cfg()
fake = Faker()
RNG = np.random.default_rng(CFG.seed)
random.seed(CFG.seed)
Faker.seed(CFG.seed)

PAYMENT = {
    "Online": (["Credit Card", "Debit Card", "Digital Wallet", "Bank Transfer"], [0.45, 0.25, 0.22, 0.08]),
    "Store":  (["Credit Card", "Debit Card", "Cash"], [0.45, 0.35, 0.20]),
}
SHIP = {
    "Online": (["Standard", "Express", "Pickup"], [0.70, 0.18, 0.12]),
    "Store":  (["In-Store"], [1.0]),
}

CATS = {
    "Electronics":   dict(sub=["Audio","Chargers & Cables","Mobile Accessories","Smart Home"], online=1.7,  mu=3.9, sig=0.6,  qty=(1,2), ret=0.055),
    "Personal Care": dict(sub=["Skincare","Hair","Hygiene"],                      online=1.35, mu=3.2, sig=0.45, qty=(1,4), ret=0.03),
    "Grocery":       dict(sub=["Snacks","Beverages","Pantry"],                    online=0.95, mu=2.6, sig=0.35, qty=(1,6), ret=0.015),
    "Home":          dict(sub=["Cleaning","Kitchen","Decor"],                     online=1.15, mu=3.3, sig=0.5,  qty=(1,5), ret=0.025),
}

TOP = [
    ("USB-C Cable 1m","Electronics","Chargers & Cables"),
    ("Fast Charger 20W","Electronics","Chargers & Cables"),
    ("Wireless Earbuds","Electronics","Audio"),
    ("Phone Case","Electronics","Mobile Accessories"),
    ("Screen Protector","Electronics","Mobile Accessories"),
    ("Liquid Detergent 3L","Home","Cleaning"),
    ("Diapers Pack","Personal Care","Hygiene"),
    ("Shampoo 750ml","Personal Care","Hair"),
    ("Chocolate Bar","Grocery","Snacks"),
    ("Sparkling Water 6-pack","Grocery","Beverages"),
]

# -------------------- Helpers --------------------
def ensure_out() -> Path:
    out = Path(CFG.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    return out

def iso(d: date) -> str:
    return d.isoformat()

def rand_date() -> date:
    days = (CFG.end - CFG.start).days
    return CFG.start + timedelta(days=int(RNG.integers(0, days + 1)))

def seasonal_keep_prob(d: date, channel: str) -> float:
    m = 1.0
    if d.month in (11, 12): m *= 1.35
    if d.month in (1, 2):   m *= 0.90
    keep = min(1.0, m / 1.35)
    wd = datetime(d.year, d.month, d.day).weekday()
    if channel == "Online" and wd >= 5: keep *= 1.10
    return keep

def channel_for(d: date) -> str:
    wd = datetime(d.year, d.month, d.day).weekday()
    p_online = 0.62 if wd >= 5 else 0.48
    return "Online" if RNG.random() < p_online else "Store"

def choice_weighted(values, p):
    return values[int(RNG.choice(len(values), p=p))]

def lognormal_price(cat: str) -> float:
    meta = CATS[cat]
    return round(min(float(RNG.lognormal(meta["mu"], meta["sig"])), 1500.0), 2)

def discount(channel: str, d: date) -> float:
    base = (0.12 if channel == "Online" else 0.08) + (0.05 if d.month in (11, 12) else 0.0)
    r = RNG.random()
    if r < 0.55: return 0.0
    if r < 0.90: return round(float(RNG.uniform(0.03, base)), 3)
    return round(float(RNG.uniform(base, min(0.35, base + 0.18))), 3)

def delivery_days(channel: str, ship_type: str) -> int:
    if channel == "Store": return 0
    if ship_type == "Pickup":  return int(RNG.integers(0, 2))
    if ship_type == "Express": return int(RNG.integers(1, 3))
    return int(RNG.integers(2, 8))

def ret_prob(channel: str, cat: str) -> float:
    p = CATS[cat]["ret"] * (1.35 if channel == "Online" else 1.0)
    return float(min(p, 0.12))

def lines_per_order(activity: str, channel: str) -> int:
    base = {"Low": 1.4, "Medium": 2.0, "High": 2.6}[activity] + (0.2 if channel == "Online" else 0.0)
    return int(np.clip(RNG.poisson(lam=base) + 1, 1, CFG.max_lines))

# -------------------- Build dims --------------------
def build_customers() -> pd.DataFrame:
    seg = ["Consumer", "Corporate", "Small Business"]
    reg = ["North", "Central", "South"]
    return pd.DataFrame({
        "customer_id": range(1, CFG.n_customers + 1),
        "segment": RNG.choice(seg, size=CFG.n_customers, p=[0.68, 0.20, 0.12]),
        "region": RNG.choice(reg, size=CFG.n_customers, p=[0.30, 0.45, 0.25]),
        "activity_level": RNG.choice(["Low", "Medium", "High"], size=CFG.n_customers, p=[0.62, 0.28, 0.10]),
    })

def build_stores() -> pd.DataFrame:
    reg = ["North", "Central", "South"]
    typ = ["Mall", "Street", "Outlet", "Dark Store"]
    return pd.DataFrame({
        "store_id": range(1, CFG.n_stores + 1),
        "store_region": RNG.choice(reg, size=CFG.n_stores, p=[0.30, 0.45, 0.25]),
        "store_type": RNG.choice(typ, size=CFG.n_stores, p=[0.42, 0.30, 0.18, 0.10]),
    })

def build_products() -> pd.DataFrame:
    rows, pid = [], 1
    for name, cat, sub in TOP:
        rows.append(dict(product_id=pid, product_name=name, category=cat, sub_category=sub, brand="Generic", is_top_seller=True))
        pid += 1
    while pid <= CFG.n_products:
        cat = random.choice(list(CATS.keys()))
        sub = random.choice(CATS[cat]["sub"])
        rows.append(dict(product_id=pid, product_name=f"{sub} Item {pid}", category=cat, sub_category=sub, brand=f"Brand_{random.randint(1,120)}", is_top_seller=False))
        pid += 1
    df = pd.DataFrame(rows)

    base = RNG.zipf(a=1.35, size=len(df)).astype(float)
    base /= base.sum()
    boost = np.where(df["is_top_seller"].to_numpy(), 18.0, 1.0)
    w = (base * boost); w /= w.sum()
    df["purchase_weight"] = w
    return df

def sample_product(products: pd.DataFrame, channel: str) -> int:
    w = products["purchase_weight"].to_numpy().copy()
    if channel == "Online":
        cats = products["category"].to_numpy()
        for c, meta in CATS.items():
            w *= np.where(cats == c, meta["online"], 1.0)
        w *= np.where(products["is_top_seller"].to_numpy(), 1.15, 1.0)
    w /= w.sum()
    return int(RNG.choice(products["product_id"].to_numpy(), p=w))

# -------------------- Sales --------------------
def build_sales(customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    activity = customers.set_index("customer_id")["activity_level"].to_dict()
    prod_cat = products.set_index("product_id")["category"].to_dict()
    rows = []

    for order_id in range(1, CFG.n_orders + 1):
        d = rand_date()
        channel = channel_for(d)
        if RNG.random() > seasonal_keep_prob(d, channel):
            continue

        customer_id = int(RNG.integers(1, CFG.n_customers + 1))
        store_id = int(RNG.integers(1, CFG.n_stores + 1))

        pm, pp = PAYMENT[channel]
        payment_method = str(RNG.choice(pm, p=pp))

        st, sp = SHIP[channel]
        shipping_type = str(RNG.choice(st, p=sp))
        ddays = delivery_days(channel, shipping_type)

        for line_id in range(1, lines_per_order(activity[customer_id], channel) + 1):
            product_id = sample_product(products, channel)
            cat = prod_cat[product_id]
            unit_price = lognormal_price(cat)

            qmin, qmax = CATS[cat]["qty"]
            quantity = int(RNG.integers(qmin, qmax + 1))

            disc = discount(channel, d)
            net = round(unit_price * quantity * (1 - disc), 2)

            is_ret = RNG.random() < ret_prob(channel, cat)
            ret_amt = net if (is_ret and RNG.random() < 0.85) else (round(net * float(RNG.uniform(0.2, 0.8)), 2) if is_ret else 0.0)

            rows.append(dict(
                order_id=order_id, line_id=line_id, order_date=iso(d),
                customer_id=customer_id, store_id=store_id, product_id=product_id,
                channel=channel, quantity=quantity, unit_price=unit_price,
                discount_pct=disc, net_sales=net, payment_method=payment_method,
                shipping_type=shipping_type, delivery_days=ddays,
                is_returned=int(is_ret), return_amount=ret_amt
            ))

    return pd.DataFrame(rows)

def add_small_issues(sales: pd.DataFrame) -> pd.DataFrame:
    if sales.empty: return sales
    mask = (sales["channel"] == "Online") & (RNG.random(len(sales)) < CFG.null_ship_rate)
    sales.loc[mask, "shipping_type"] = None
    dup = sales.sample(frac=CFG.dup_frac, random_state=CFG.seed)
    return pd.concat([sales, dup], ignore_index=True)

# -------------------- Run --------------------
def main():
    print("Working directory:", os.getcwd())
    out = ensure_out()

    customers = build_customers()
    stores = build_stores()
    products = build_products()
    sales = add_small_issues(build_sales(customers, products))

    customers.to_csv(out / "customers.csv", index=False)
    stores.to_csv(out / "stores.csv", index=False)
    products.drop(columns=["purchase_weight"]).to_csv(out / "products.csv", index=False)
    sales.to_csv(out / "sales.csv", index=False)

    print("Saved CSVs to:", out.resolve())
    print("Rows:", f"customers={len(customers):,}, stores={len(stores):,}, products={len(products):,}, sales_lines={len(sales):,}")

if __name__ == "__main__":
    main()
