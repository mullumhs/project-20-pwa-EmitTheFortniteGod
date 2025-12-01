from flask import render_template, request, redirect, url_for, flash, session
from models import db, Drink

def init_routes(app, openai):

    # --- LOGIN REQUIRED DECORATOR ---
    def login_required(func):
        def wrapper(*args, **kwargs):
            if "user" not in session:
                flash("Please log in first.", "danger")
                return redirect(url_for("login"))
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper

    @app.route("/")
    @login_required
    def home():
        return redirect(url_for("list_drinks"))

    @app.route("/drinks")
    @login_required
    def list_drinks():
        drinks = Drink.query.all()
        return render_template("drinks.html", items=drinks)

    # --- NEW MULTI-STEP ADD FLOW ---
    @app.route("/add_choice")
    @login_required
    def add_choice():
        return render_template("add_choice.html")

    @app.route("/add_form/<drink_type>", methods=["GET", "POST"])
    @login_required
    def add_form(drink_type):
        if request.method == "POST":
            brand = request.form.get("brand")
            sweetness = request.form.get("sweetness")
            percentage = request.form.get("percentage")
            strength = request.form.get("strength")
            smoothness = request.form.get("smoothness")

            if drink_type == "beer":
                new_drink = Drink(
                    type="Beer",
                    brand=brand,
                    percentage=float(strength) if strength else None
                )
            elif drink_type == "wine":
                new_drink = Drink(
                    type="Wine",
                    brand=brand,
                    sweetness=int(sweetness) if sweetness else None,
                    percentage=float(percentage) if percentage else None
                )
            elif drink_type == "spirit":
                new_drink = Drink(
                    type="Spirit",
                    brand=brand,
                    percentage=float(percentage) if percentage else None,
                    sweetness=int(smoothness) if smoothness else None
                )
            else:
                flash("Unknown drink type", "danger")
                return redirect(url_for("add_choice"))

            db.session.add(new_drink)
            db.session.commit()
            flash(f"{drink_type.capitalize()} added!", "success")
            return redirect(url_for("list_drinks"))

        return render_template("add_form.html", drink_type=drink_type)

    # --- UPDATE / DELETE EXISTING ---
    @app.route("/update/<int:id>", methods=["POST"])
    @login_required
    def update_drink(id):
        drink = Drink.query.get_or_404(id)
        drink.type = request.form["type"]
        drink.brand = request.form.get("brand") or None
        s = request.form.get("sweetness")
        p = request.form.get("percentage")
        drink.sweetness = int(s) if s else None
        drink.percentage = float(p) if p else None
        db.session.commit()
        flash("Updated", "success")
        return redirect(url_for("list_drinks"))

    @app.route("/delete/<int:id>", methods=["POST"])
    @login_required
    def delete_drink(id):
        drink = Drink.query.get_or_404(id)
        db.session.delete(drink)
        db.session.commit()
        flash("Deleted", "success")
        return redirect(url_for("list_drinks"))

    # --- AI UPLOAD ---
    @app.route("/ai_upload", methods=["GET", "POST"])
    @login_required
    def ai_upload():
        if request.method == "POST":
            drink_list = request.form.get("drink_list") or ""
            file = request.files.get("file")
            if file and file.filename:
                try:
                    drink_list = file.read().decode("utf-8")
                except Exception:
                    flash("Could not read file", "danger")
                    return redirect(url_for("ai_upload"))

            if not drink_list.strip():
                flash("No drink list provided.", "warning")
                return redirect(url_for("ai_upload"))

            prompt = f"""
            You are a sommelier assistant. Given this list of drinks:
            {drink_list}
            Extract each drink with fields:
            - type (Beer, Wine, Spirit)
            - brand (name)
            - sweetness (1–10 scale)
            - ABV percentage
            Return ONLY rows:
            type | brand | sweetness | percentage
            """

            try:
                resp = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You structure drinks for a database."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )
                ai_output = resp["choices"][0]["message"]["content"]
            except Exception as e:
                flash(f"AI error: {e}", "danger")
                return redirect(url_for("ai_upload"))

            for line in ai_output.splitlines():
                if "|" not in line or line.lower().startswith("type"):
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) != 4:
                    continue
                t, b, sv, pv = parts
                sweetness = int(sv) if sv.isdigit() else None
                try:
                    percentage = float(pv)
                except:
                    percentage = None
                d = Drink(type=t, brand=b or None, sweetness=sweetness, percentage=percentage)
                db.session.add(d)
            db.session.commit()
            flash("AI processed", "success")
            return redirect(url_for("list_drinks"))

        return render_template("ai_upload.html")

    @app.route("/poster")
    @login_required
    def poster():
        poster_html = "<ul><li>Beer - Example</li><li>Wine - Example</li></ul>"
        return render_template("poster.html", poster_html=poster_html)

    # --- LOGIN / LOGOUT ---
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if username == "admin" and password == "password":
                session["user"] = username
                flash("Login successful!", "success")
                return redirect(url_for("list_drinks"))
            else:
                flash("Invalid credentials.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("user", None)
        flash("Logged out.", "info")
        return redirect(url_for("login"))
