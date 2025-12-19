# views.py
# Handles all routes, database queries, and app logic

from app import app
from flask import render_template, request, redirect, url_for
import sqlite3
import difflib


# DATABASE HELPER

def get_db():
    """
    Opens a connection to the SQLite database.
    Using a function avoids repeating code - Chat gpts idea
    """
    conn = sqlite3.connect("drinks.db")
    conn.row_factory = sqlite3.Row
    return conn



# HOME PAGE – GENERATE POSTER

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main page where managers paste their drink list.
    Handles fuzzy matching and poster generation.
    """
    if request.method == "POST":
        raw_input = request.form["drinks"]

        # Split pasted text into lines
        entered_drinks = [
            d.strip() for d in raw_input.split("\n") if d.strip()
        ]

        conn = get_db()
        c = conn.cursor()

        # Get all drink names from DB
        c.execute("SELECT name FROM drinks")
        db_names = [row["name"] for row in c.fetchall()]

        matched_names = []

        # Word match each entered drink like if the word is spelt wrong or similar
        for drink in entered_drinks:
            match = difflib.get_close_matches(
                drink, db_names, n=1, cutoff=0.6
            )
            if match:
                matched_names.append(match[0])

        drinks = []
        if matched_names:
            placeholders = ",".join("?" for _ in matched_names)
            c.execute(
                f"SELECT * FROM drinks WHERE name IN ({placeholders})",
                matched_names
            )
            drinks = c.fetchall()

        conn.close()

        return render_template("poster.html", drinks=drinks)

    return render_template("index.html")



#  VIEW ALL DRINKS

@app.route("/admin")
def admin():
    """
    Admin dashboard to view all drinks.
    Demonstrates READ functionality.
    """
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM drinks ORDER BY category, name")
    drinks = c.fetchall()
    conn.close()
    return render_template("admin.html", drinks=drinks)



# EDIT DRINK

@app.route("/edit/<int:drink_id>", methods=["GET", "POST"])
def edit_drink(drink_id):
    """
    Allows editing an existing drink.
    Demonstrates UPDATE functionality.
    """
    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        c.execute("""
            UPDATE drinks
            SET name=?, category=?, abv=?, sweetness=?, strength=?, style=?
            WHERE id=?
        """, (
            request.form["name"],
            request.form["category"],
            request.form["abv"],
            request.form["sweetness"],
            request.form["strength"],
            request.form["style"],
            drink_id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("admin"))

    c.execute("SELECT * FROM drinks WHERE id=?", (drink_id,))
    drink = c.fetchone()
    conn.close()

    return render_template("edit.html", drink=drink)



# DELETE DRINK

@app.route("/delete/<int:drink_id>")
def delete_drink(drink_id):
    """
    Deletes a drink from the database.
    Demonstrates DELETE functionality.
    """
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM drinks WHERE id=?", (drink_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))
