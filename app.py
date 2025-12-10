# app.py
import os
import json
import sqlite3
from difflib import get_close_matches
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

APP_NAME = "Pourtrait"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-pourtrait')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'drinks.db')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- DB helpers ---
def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    # users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # drinks (unified)
    c.execute("""
    CREATE TABLE IF NOT EXISTS drinks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,            -- beer | wine | spirit
        category TEXT,                 -- e.g., Lager, IPA, Red, White, Gin, Whisky
        abv REAL,                      -- ABV for beers/spirits; can be null for wines
        sweetness TEXT,                -- e.g., Dry, Off-dry, Sweet (commonly for wines)
        strength TEXT,                 -- e.g., Light, Mid, Heavy (commonly for beers)
        notes TEXT
    )
    """)

    # user stock inputs (raw and resolved)
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        raw_input TEXT NOT NULL,       -- original text or filename
        parsed_json TEXT NOT NULL,     -- list of entered lines
        matched_json TEXT NOT NULL,    -- list of matched drink dicts
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # posters saved per user
    c.execute("""
    CREATE TABLE IF NOT EXISTS posters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        options_json TEXT NOT NULL,    -- poster style/sorting options
        drinks_json TEXT NOT NULL,     -- final list used to render
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

init_db()

# --- Flask-Login user model ---
class User(UserMixin):
    def __init__(self, id_, email, password_hash, created_at):
        self.id = id_
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def get_by_id(uid):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (uid,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(row["id"], row["email"], row["password_hash"], row["created_at"])
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(row["id"], row["email"], row["password_hash"], row["created_at"])
        return None

    @staticmethod
    def create(email, password):
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users (email, password_hash, created_at) VALUES (?,?,?)",
                (email, generate_password_hash(password), datetime.utcnow().isoformat())
            )
            conn.commit()
            uid = c.lastrowid
        except sqlite3.IntegrityError:
            conn.close()
            return None
        conn.close()
        return User.get_by_id(uid)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# --- Fuzzy matching ---
def fetch_all_drink_names(conn):
    c = conn.cursor()
    c.execute("SELECT id, name FROM drinks")
    rows = c.fetchall()
    id_to_name = {row["id"]: row["name"] for row in rows}
    names = [row["name"] for row in rows]
    return id_to_name, names

def find_best_match(conn, input_name, cutoff=0.72):
    # Try exact match first
    c = conn.cursor()
    c.execute("SELECT * FROM drinks WHERE LOWER(name) = LOWER(?)", (input_name.strip(),))
    exact = c.fetchone()
    if exact:
        return dict(exact)

    # Fuzzy match
    id_to_name, names = fetch_all_drink_names(conn)
    matches = get_close_matches(input_name.strip(), names, n=1, cutoff=cutoff)
    if matches:
        best = matches[0]
        c.execute("SELECT * FROM drinks WHERE name = ?", (best,))
        row = c.fetchone()
        if row:
            return dict(row)
    return None

# --- Utility: sort for poster ---
def sort_drinks(drinks, sort_by):
    if sort_by == "type":
        return sorted(drinks, key=lambda d: (d.get("type",""), d.get("category","") or "", d.get("name","")))
    if sort_by == "abv":
        return sorted(drinks, key=lambda d: (d.get("abv") if d.get("abv") is not None else -1, d.get("name","")), reverse=True)
    if sort_by == "sweetness":
        order = {"Dry": 0, "Off-dry": 1, "Medium": 2, "Sweet": 3}
        return sorted(drinks, key=lambda d: (order.get(d.get("sweetness"), 99), d.get("name","")))
    return sorted(drinks, key=lambda d: d.get("name",""))

# --- Routes ---

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("login.html", app_name=APP_NAME)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        confirm = request.form.get("confirm","")
        if not email or not password:
            flash("Please enter email and password.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif User.get_by_email(email):
            flash("Email is already registered.", "error")
        else:
            user = User.create(email, password)
            if user:
                login_user(user)
                flash("Welcome to Pourtrait.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Registration failed.", "error")
    return render_template("register.html", app_name=APP_NAME)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = User.get_by_email(email)
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
        else:
            login_user(user)
            flash("Logged in.", "success")
            return redirect(url_for("dashboard"))
    return render_template("login.html", app_name=APP_NAME)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM user_stocks WHERE user_id = ? ORDER BY updated_at DESC", (current_user.id,))
    stocks = [dict(row) for row in c.fetchall()]
    c.execute("SELECT * FROM posters WHERE user_id = ? ORDER BY updated_at DESC", (current_user.id,))
    posters = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template("dashboard.html", app_name=APP_NAME, stocks=stocks, posters=posters)

@app.route("/upload", methods=["GET","POST"])
@login_required
def upload():
    if request.method == "POST":
        title = request.form.get("title","").strip() or f"Stock {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        input_mode = request.form.get("input_mode","paste")
        raw_input = ""
        parsed = []

        if input_mode == "paste":
            raw_input = request.form.get("pasted","").strip()
            parsed = [line.strip() for line in raw_input.splitlines() if line.strip()]
        elif input_mode == "file":
            file = request.files.get("file")
            if file and file.filename:
                raw_input = file.filename
                content = file.stream.read().decode("utf-8", errors="ignore")
                parsed = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                flash("No file selected.", "error")
                return redirect(url_for("upload"))

        # Fuzzy resolve
        conn = get_db()
        matched = []
        for item in parsed:
            m = find_best_match(conn, item)
            if m:
                matched.append({
                    "id": m["id"],
                    "name": m["name"],
                    "type": m["type"],
                    "category": m.get("category"),
                    "abv": m.get("abv"),
                    "sweetness": m.get("sweetness"),
                    "strength": m.get("strength"),
                    "notes": m.get("notes"),
                    "input": item
                })
            else:
                matched.append({
                    "id": None,
                    "name": item,
                    "type": "unknown",
                    "category": None,
                    "abv": None,
                    "sweetness": None,
                    "strength": None,
                    "notes": None,
                    "input": item,
                    "unmatched": True
                })

        # Save stock record
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute("""
        INSERT INTO user_stocks (user_id, title, raw_input, parsed_json, matched_json, created_at, updated_at)
        VALUES (?,?,?,?,?,?,?)
        """, (current_user.id, title, raw_input, json.dumps(parsed), json.dumps(matched), now, now))
        conn.commit()
        stock_id = c.lastrowid
        conn.close()

        flash("Stock processed. Unmatched items are flagged—you can edit before poster.", "success")
        return redirect(url_for("poster_preview", stock_id=stock_id))

    return render_template("upload.html", app_name=APP_NAME)

@app.route("/poster/preview/<int:stock_id>", methods=["GET","POST"])
@login_required
def poster_preview(stock_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM user_stocks WHERE id = ? AND user_id = ?", (stock_id, current_user.id))
    row = c.fetchone()
    if not row:
        conn.close()
        flash("Stock not found.", "error")
        return redirect(url_for("dashboard"))

    matched = json.loads(row["matched_json"])
    sort_by = request.form.get("sort_by") or "type"
    poster_title = request.form.get("poster_title") or f"Pourtrait Poster - {row['title']}"
    style = request.form.get("style") or "classic"

    # Allow inline edits for unmatched or corrections
    if request.method == "POST":
        edits = request.form.getlist("edit_name")
        # Reresolve edited names
        new_list = []
        for idx, item in enumerate(matched):
            new_input = edits[idx].strip() if idx < len(edits) else item["name"]
            m = find_best_match(conn, new_input)
            if m:
                new_list.append({
                    "id": m["id"],
                    "name": m["name"],
                    "type": m["type"],
                    "category": m.get("category"),
                    "abv": m.get("abv"),
                    "sweetness": m.get("sweetness"),
                    "strength": m.get("strength"),
                    "notes": m.get("notes"),
                    "input": new_input
                })
            else:
                new_list.append({
                    "id": None,
                    "name": new_input,
                    "type": "unknown",
                    "category": None,
                    "abv": None,
                    "sweetness": None,
                    "strength": None,
                    "notes": None,
                    "input": new_input,
                    "unmatched": True
                })
        matched = new_list
        # Update stock
        c.execute("UPDATE user_stocks SET matched_json = ?, updated_at = ? WHERE id = ?",
                  (json.dumps(matched), datetime.utcnow().isoformat(), stock_id))
        conn.commit()

    sorted_drinks = sort_drinks(matched, sort_by)
    conn.close()

    return render_template("poster_preview.html",
                           app_name=APP_NAME,
                           stock_id=stock_id,
                           poster_title=poster_title,
                           sort_by=sort_by,
                           style=style,
                           drinks=sorted_drinks)

@app.route("/poster/save/<int:stock_id>", methods=["POST"])
@login_required
def poster_save(stock_id):
    sort_by = request.form.get("sort_by") or "type"
    poster_title = request.form.get("poster_title") or "Pourtrait Poster"
    style = request.form.get("style") or "classic"

    # Load latest matched for this stock
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM user_stocks WHERE id = ? AND user_id = ?", (stock_id, current_user.id))
    row = c.fetchone()
    if not row:
        conn.close()
        flash("Stock not found.", "error")
        return redirect(url_for("dashboard"))

    drinks = sort_drinks(json.loads(row["matched_json"]), sort_by)
    options = {"title": poster_title, "sort_by": sort_by, "style": style}

    now = datetime.utcnow().isoformat()
    c.execute("""
    INSERT INTO posters (user_id, title, options_json, drinks_json, created_at, updated_at)
    VALUES (?,?,?,?,?,?)
    """, (current_user.id, poster_title, json.dumps(options), json.dumps(drinks), now, now))
    conn.commit()
    conn.close()

    flash("Poster saved.", "success")
    return redirect(url_for("posters_list"))

@app.route("/posters")
@login_required
def posters_list():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM posters WHERE user_id = ? ORDER BY updated_at DESC", (current_user.id,))
    posters = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template("posters_list.html", app_name=APP_NAME, posters=posters)

@app.route("/poster/view/<int:poster_id>")
@login_required
def poster_view(poster_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM posters WHERE id = ? AND user_id = ?", (poster_id, current_user.id))
    row = c.fetchone()
    conn.close()
    if not row:
        flash("Poster not found.", "error")
        return redirect(url_for("posters_list"))
    options = json.loads(row["options_json"])
    drinks = json.loads(row["drinks_json"])
    return render_template("poster_pdf.html",
                           app_name=APP_NAME,
                           poster_title=options.get("title","Pourtrait Poster"),
                           sort_by=options.get("sort_by","type"),
                           style=options.get("style","classic"),
                           drinks=drinks)
if __name__ == "__main__":
    app.run(debug=True)
