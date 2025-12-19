# seeder.py
# This script creates the database and loads drink data from CSV files

import sqlite3
import csv

# Connect to (or create) the database
conn = sqlite3.connect("drinks.db")
c = conn.cursor()

# Create one unified drinks table
c.execute("""
CREATE TABLE IF NOT EXISTS drinks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    abv REAL,
    sweetness TEXT,
    strength TEXT,
    style TEXT
)
""")

def load_csv(path, category):
    """
    Loads a CSV file and inserts its rows into the drinks table.
    Each CSV has slightly different columns, so .get() is used safely.
    """
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            c.execute("""
                INSERT INTO drinks (name, category, abv, sweetness, strength, style)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row.get("name"),
                category,
                row.get("abv"),
                row.get("sweetness"),
                row.get("strength"),
                row.get("style")
            ))

# Load all three drink categories
load_csv("data/beers.csv", "beer")
load_csv("data/wines.csv", "wine")
load_csv("data/spirits.csv", "spirit")

conn.commit()
conn.close()

print("✅ Database created and seeded")
