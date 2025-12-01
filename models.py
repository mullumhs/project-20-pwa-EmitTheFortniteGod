import sqlite3, os, re
from flask import g

DB_PATH = os.path.join(os.path.dirname(__file__), "drinks.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(exception):
    db = g.pop("db", None)
    if db: db.close()

def init_db():
    db = get_db()
    db.execute("""
    CREATE TABLE IF NOT EXISTS drinks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        type TEXT,
        abv REAL,
        std_drinks REAL,
        taste TEXT,
        origin TEXT,
        notes TEXT
    );
    """)
    db.commit()

def seed_db():
    db = get_db()
    cur = db.execute("SELECT COUNT(*) AS c FROM drinks")
    if cur.fetchone()["c"] > 0: return
    sample = [
        ("Coopers Red", "beer", 4.5, 2.5, "Bitter taste", "Australia", "Classic Aussie ale"),
        ("Guinness Draught", "beer", 4.2, 1.7, "Roasted malt, creamy", "Ireland", "Stout"),
        ("Shiraz", "wine", 14.5, 8.6, "Bold, peppery", "Australia", "Dark fruit"),
        ("Jack Daniel's", "spirit", 40.0, 1.0, "Vanilla, caramel", "USA", "Tennessee whiskey"),
    ]
    db.executemany("INSERT INTO drinks (name,type,abv,std_drinks,taste,origin,notes) VALUES (?,?,?,?,?,?,?)", sample)
    db.commit()

def normalize(s): return re.sub(r"[^a-z0-9\s]", "", s.lower()).strip()

def match_drink(name, dtype):
    db = get_db()
    cur = db.execute("SELECT * FROM drinks WHERE LOWER(name)=?", (normalize(name),))
    row = cur.fetchone()
    if row and row["type"] == dtype: return row
    cur = db.execute("SELECT * FROM drinks WHERE LOWER(name) LIKE ? AND type=?", (f"%{normalize(name)}%", dtype))
    return cur.fetchone()
