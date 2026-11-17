"""Simulate a week of planning: revise some quotes and add a new venue.
Never truncates. Run after `generate_data.py seed`."""
import os
import random
import sys
from datetime import datetime

from generate_data import build_line_items, connect, insert_quote, money

if "private" in os.getenv("POSTGRES_DB", "weddingos"):
    sys.exit("Refusing to run against a private database.")

conn = connect()
cur = conn.cursor()
now = datetime.now()

# 1. Negotiate: cut base 5-15% on up to 3 open quotes, move status forward.
cur.execute("select quote_id, status from raw.quotes where status in ('received', 'negotiating')")
open_quotes = cur.fetchall()
next_status = {"received": "negotiating", "negotiating": "accepted"}
for quote_id, status in random.sample(open_quotes, min(3, len(open_quotes))):
    cut = round(random.uniform(0.85, 0.95), 2)
    cur.execute(
        """update raw.quote_line_items
           set unit_price = round(unit_price * %s, 2), amount = round(amount * %s, 2), updated_at = %s
           where quote_id = %s and item_type = 'base'""",
        (cut, cut, now, quote_id),
    )
    cur.execute(
        """update raw.quotes
           set status = %s, updated_at = %s,
               quoted_total = (select sum(amount) from raw.quote_line_items where quote_id = %s)
           where quote_id = %s""",
        (next_status[status], now, quote_id, quote_id),
    )
    print(f"quote {quote_id}: base x{cut}, {status} -> {next_status[status]}")

# 2. A new wedding venue shows up, with one quote.
cur.execute(
    """insert into raw.venues
       (name, city, intended_event, capacity, overage_fee_per_guest, allows_outside_caterer,
        allows_baraat, allows_open_flame, noise_curfew, alcohol_policy, created_at, updated_at)
       values (%s,'Stockton','wedding',150,%s,true,true,false,'22:00','byo_allowed',%s,%s)
       returning venue_id""",
    (f"New Venue {now:%m%d-%H%M}", money(10, 40), now, now),
)
venue_id = cur.fetchone()[0]
insert_quote(cur, venue_id, None, "wedding", 80, "received",
             build_line_items((4000, 14000), (15, 60), 80, is_venue=True), now)
print(f"new venue {venue_id} with 1 quote")

conn.commit()
conn.close()
