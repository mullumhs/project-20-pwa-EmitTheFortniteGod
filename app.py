from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Drink
import openai, os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Correct way: read API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- AI FUNCTION ---
def ai_parse_drinks(drink_list):
    prompt = f"""
    You are a sommelier assistant.
    Given this list of drinks:

    {drink_list}

    Extract each drink with fields:
    - type (Beer, Wine, Spirit)
    - brand (name)
    - sweetness (1–10 scale, estimate if needed)
    - ABV percentage (numeric, estimate if needed)

    Return ONLY rows in the format:
    type | brand | sweetness | percentage
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You structure drinks for a database."},
                  {"role": "user", "content": prompt}],
        temperature=0
    )

    return response["choices"][0]["message"]["content"]

# --- HOME ROUTE ---
@app.route("/")
def home():
    return redirect(url_for("list_drinks"))

# --- ROUTE TO PROCESS AI INPUT ---
@app.route("/ai_upload", methods=["GET", "POST"])
def ai_upload():
    if request.method == "POST":
        drink_list = request.form.get("drink_list")
        file = request.files.get("file")

        if file:
            drink_list = file.read().decode("utf-8")

        ai_output = ai_parse_drinks(drink_list)

        # Parse AI output line by line
        for line in ai_output.splitlines():
            if not line.strip() or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) == 4:
                drink = Drink(
                    type=parts[0],
                    brand=parts[1],
                    sweetness=int(parts[2]) if parts[2].isdigit() else None,
                    percentage=float(parts[3]) if parts[3].replace('.', '', 1).isdigit() else None
                )
                db.session.add(drink)
        db.session.commit()

        return redirect(url_for("list_drinks"))

    return render_template("upload.html")

# --- CRUD LIST ROUTE ---
@app.route("/drinks")
def list_drinks():
    items = Drink.query.all()
    return render_template("drinks.html", items=items)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
