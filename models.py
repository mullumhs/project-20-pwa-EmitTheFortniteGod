import sqlite3, os, re
from flask import g
from difflib import get_close_matches

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
        # Beers
        ("Coopers Red", "beer", 4.5, 2.5, "Bitter taste", "Australia", "Classic Aussie ale"),
        ("Guinness Draught", "beer", 4.2, 1.7, "Roasted malt, creamy", "Ireland", "Stout"),
        ("Heineken", "beer", 5.0, 1.8, "Crisp, light", "Netherlands", "Pale lager"),
        ("Corona Extra", "beer", 4.6, 1.6, "Light, refreshing", "Mexico", "Serve with lime"),
        ("Asahi Super Dry", "beer", 5.0, 1.8, "Dry, crisp", "Japan", "Popular lager"),
        ("Peroni Nastro Azzurro", "beer", 5.1, 1.9, "Smooth, light", "Italy", "Premium lager"),
        ("VB Victoria Bitter", "beer", 4.9, 1.7, "Bitter lager", "Australia", "Classic Aussie beer"),
        ("Tooheys New", "beer", 4.6, 1.6, "Clean lager", "Australia", "Easy drinking"),

        # Wines
        ("Shiraz", "wine", 14.5, 8.6, "Bold, peppery", "Australia", "Dark fruit"),
        ("Cabernet Sauvignon", "wine", 14.0, 8.2, "Rich, tannic", "France", "Blackcurrant"),
        ("Pinot Noir", "wine", 13.0, 7.6, "Light, cherry", "France", "Elegant red"),
        ("Sauvignon Blanc", "wine", 12.5, 7.0, "Zesty, citrus", "New Zealand", "Herbal white"),
        ("Chardonnay", "wine", 13.5, 7.8, "Buttery, stone fruit", "Australia", "Classic white"),
        ("Prosecco", "wine", 11.0, 6.2, "Sparkling, apple", "Italy", "Light bubbles"),
        ("Riesling", "wine", 11.5, 6.5, "Sweet, floral", "Germany", "Honey notes"),

        # Spirits
        ("Jack Daniel's", "spirit", 40.0, 1.0, "Vanilla, caramel", "USA", "Tennessee whiskey"),
        ("Jameson Irish Whiskey", "spirit", 40.0, 1.0, "Smooth, light spice", "Ireland", "Triple distilled"),
        ("Johnnie Walker Black Label", "spirit", 40.0, 1.0, "Smoky, rich", "Scotland", "Blended Scotch"),
        ("Tanqueray Gin", "spirit", 43.1, 1.0, "Juniper, citrus", "UK", "London Dry"),
        ("Bombay Sapphire Gin", "spirit", 40.0, 1.0, "Botanical, bright", "UK", "Popular gin"),
        ("Patrón Silver Tequila", "spirit", 40.0, 1.0, "Agave, pepper", "Mexico", "Premium tequila"),
        ("Belvedere Vodka", "spirit", 40.0, 1.0, "Clean, crisp", "Poland", "Luxury vodka"),
        ("Bundaberg Rum", "spirit", 37.0, 1.0, "Molasses, spice", "Australia", "Dark rum"),
    ]
