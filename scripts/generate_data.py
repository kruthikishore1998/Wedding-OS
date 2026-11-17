"""WeddingOS fake data generator. Day 1: seed. (Day 4 adds `simulate`.)"""
import argparse
import os
import random
from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
fake = Faker()

TAX_RATE = 0.0875  # fake rate, fine for a demo
CITIES = ["Stockton", "Lodi", "Modesto", "Tracy", "Sacramento"]
VENUE_STYLES = ["Estate", "Vineyard", "Garden", "Banquet Hall", "Ballroom", "Ranch"]
VENDOR_CATEGORIES = ["caterer", "decor", "dj", "photographer", "mehndi", "pandit"]
# (flat base range, per-guest range) by vendor category
VENDOR_PRICING = {
    "caterer": ((500, 1500), (45, 110)),
    "decor": ((2500, 9000), (0, 0)),
    "dj": ((1200, 3500), (0, 0)),
    "photographer": ((2500, 8000), (0, 0)),
    "mehndi": ((300, 900), (10, 25)),
    "pandit": ((300, 800), (0, 0)),
}


def connect():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "weddingos"),
        user=os.getenv("POSTGRES_USER", "weddingos"),
        password=os.getenv("POSTGRES_PASSWORD", "weddingos_local"),
    )


def money(lo, hi):
    return round(random.uniform(lo, hi), 2)


def build_line_items(base_range, per_guest_range, guests, is_venue):
    """Returns list of (item_type, description, unit_price, quantity, amount)."""
    items = [("base", "Base rental / package", money(*base_range), 1)]
    if per_guest_range[1] > 0:
        items.append(("per_guest", "Per-guest charge", money(*per_guest_range), guests))
    if is_venue:
        items.append(("cleaning", "Cleaning fee", money(200, 800), 1))
        if random.random() < 0.5:
            items.append(("overtime", "Overtime (2 hrs)", money(250, 600), 2))

    rows = [(t, d, p, q, round(p * q, 2)) for t, d, p, q in items]
    subtotal = sum(r[4] for r in rows)

    service_rate = random.choice([0, 0.15, 0.18, 0.20])
    gratuity_rate = random.choice([0, 0, 0.15, 0.18])
    if service_rate:
        amt = round(subtotal * service_rate, 2)
        rows.append(("service_fee", f"Service fee {service_rate:.0%}", amt, 1, amt))
    taxable = sum(r[4] for r in rows)
    tax = round(taxable * TAX_RATE, 2)
    rows.append(("tax", "Sales tax", tax, 1, tax))
    if gratuity_rate:
        amt = round(subtotal * gratuity_rate, 2)
        rows.append(("gratuity", f"Gratuity {gratuity_rate:.0%}", amt, 1, amt))
    return rows


def insert_quote(cur, venue_id, vendor_id, event, guests, status, rows, created_at):
    total = round(sum(r[4] for r in rows), 2)
    cur.execute(
        """insert into raw.quotes
           (venue_id, vendor_id, event_name, guest_count, status, quoted_total, created_at, updated_at)
           values (%s,%s,%s,%s,%s,%s,%s,%s) returning quote_id""",
        (venue_id, vendor_id, event, guests, status, total, created_at, created_at),
    )
    quote_id = cur.fetchone()[0]
    for t, d, p, q, a in rows:
        cur.execute(
            """insert into raw.quote_line_items
               (quote_id, item_type, description, unit_price, quantity, amount, updated_at)
               values (%s,%s,%s,%s,%s,%s,%s)""",
            (quote_id, t, d, p, q, a, created_at),
        )


def seed(n_venues=8, n_vendors=10):
    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "truncate raw.quote_line_items, raw.quotes, raw.vendors, raw.venues restart identity cascade"
    )
    now = datetime.now()

    venue_ids = []
    for i in range(n_venues):
        event = "dinner_party" if i >= n_venues - 2 else "wedding"
        capacity = random.choice([100, 120, 150, 200]) if event == "wedding" else random.choice([40, 50, 60])
        cur.execute(
            """insert into raw.venues
               (name, city, intended_event, capacity, overage_fee_per_guest, allows_outside_caterer,
                allows_baraat, allows_open_flame, noise_curfew, alcohol_policy, created_at, updated_at)
               values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning venue_id""",
            (
                f"The {fake.last_name()} {random.choice(VENUE_STYLES)}",
                random.choice(CITIES), event, capacity, money(10, 40),
                random.random() < 0.6, random.random() < 0.5, random.random() < 0.4,
                random.choice(["21:00", "22:00", "23:00"]),
                random.choice(["byo_allowed", "venue_bar_only", "licensed_bartender_required"]),
                now, now,
            ),
        )
        venue_ids.append((cur.fetchone()[0], event))

    vendor_ids = []
    for i in range(n_vendors):
        cat = VENDOR_CATEGORIES[i % len(VENDOR_CATEGORIES)]
        cur.execute(
            "insert into raw.vendors (name, category, city, created_at, updated_at) "
            "values (%s,%s,%s,%s,%s) returning vendor_id",
            (fake.company(), cat, random.choice(CITIES), now, now),
        )
        vendor_ids.append((cur.fetchone()[0], cat))

    statuses = ["received", "received", "negotiating", "accepted", "declined", "expired"]
    for venue_id, event in venue_ids:
        guests = 80 if event == "wedding" else 40
        for _ in range(random.choice([1, 1, 2])):
            rows = build_line_items((4000, 14000), (15, 60), guests, is_venue=True)
            insert_quote(cur, venue_id, None, event, guests, random.choice(statuses),
                         rows, now - timedelta(days=random.randint(1, 30)))

    for vendor_id, cat in vendor_ids:
        base, per_guest = VENDOR_PRICING[cat]
        rows = build_line_items(base, per_guest, 80, is_venue=False)
        insert_quote(cur, None, vendor_id, "wedding", 80, random.choice(statuses),
                     rows, now - timedelta(days=random.randint(1, 30)))

    conn.commit()
    for t in ["venues", "vendors", "quotes", "quote_line_items"]:
        cur.execute(f"select count(*) from raw.{t}")
        print(f"raw.{t}: {cur.fetchone()[0]} rows")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["seed"])
    parser.add_argument("--random-seed", type=int, default=42)
    args = parser.parse_args()
    random.seed(args.random_seed)
    Faker.seed(args.random_seed)
    seed()
