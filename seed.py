# seed.py
import os
import csv
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'drinks.db')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def ensure_schema(conn):
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS drinks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        category TEXT,
        abv REAL,
        sweetness TEXT,
        strength TEXT,
        notes TEXT
    )
    """)
    conn.commit()

def load_csv(path, expected_headers):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = [h.strip() for h in reader.fieldnames or []]
        missing = [h for h in expected_headers if h not in headers]
        if missing:
            raise ValueError(f"CSV {os.path.basename(path)} missing headers: {missing}")
        for r in reader:
            rows.append({k: (r.get(k) or "").strip() for k in expected_headers})
    return rows

def seed():
    conn = sqlite3.connect(DB_PATH)
    ensure_schema(conn)
    c = conn.cursor()

    # Clear existing data for fresh seed (optional: comment out to append)
    c.execute("DELETE FROM drinks")

    beers_csv = os.path.join(DATA_DIR, 'beers.csv')
    wines_csv = os.path.join(DATA_DIR, 'wines.csv')
    spirits_csv = os.path.join(DATA_DIR, 'spirits.csv')

    beers = load_csv(beers_csv, ["name","category","abv","strength","notes"])
    wines = load_csv(wines_csv, ["name","category","sweetness","notes"])
    spirits = load_csv(spirits_csv, ["name","category","abv","notes"])

    for b in beers:
        abv = float(b["abv"]) if b["abv"] else None
        c.execute("""INSERT INTO drinks (name,type,category,abv,sweetness,strength,notes)
                     VALUES (?,?,?,?,?,?,?)""",
                  (b["name"], "beer", b["category"], abv, None, b["strength"] or None, b["notes"] or None))

    for w in wines:
        c.execute("""INSERT INTO drinks (name,type,category,abv,sweetness,strength,notes)
                     VALUES (?,?,?,?,?,?,?)""",
                  (w["name"], "wine", w["category"], None, w["sweetness"] or None, None, w["notes"] or None))

    for s in spirits:
        abv = float(s["abv"]) if s["abv"] else None
        c.execute("""INSERT INTO drinks (name,type,category,abv,sweetness,strength,notes)
                     VALUES (?,?,?,?,?,?,?)""",
                  (s["name"], "spirit", s["category"], abv, None, None, s["notes"] or None))

    conn.commit()
    conn.close()
    print("Seed complete.")

if __name__ == "__main__":
    seed()
