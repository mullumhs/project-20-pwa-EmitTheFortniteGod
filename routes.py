from flask import render_template, request, redirect, url_for, flash
from models import db, Drink

def init_routes(app, openai):

    @app.route("/")
    def home():
        return redirect(url_for("list_drinks"))

    @app.route("/drinks")
    def list_drinks():
        drinks = Drink.query.all()
        return render_template("drinks.html", items=drinks)

    @app.route("/add", methods=["POST"])
    def add_drink():
        s = request.form.get("sweetness")
        p = request.form.get("percentage")
        drink = Drink(
            type=request.form["type"],
            brand=request.form.get("brand") or None,
            sweetness=int(s) if s else None,
            percentage=float(p) if p else None
        )
        db.session.add(drink)
        db.session.commit()
        flash("Added", "success")
        return redirect(url_for("list_drinks"))

    @app.route("/update/<int:id>", methods=["POST"])
    def update_drink(id):
        drink = Drink.query.get_or_404(id)
        s = request.form.get("sweetness")
        p = request.form.get("percentage")
        drink.type = request.form["type"]
        drink.brand = request.form.get("brand") or None
        drink.sweetness = int(s) if s else None
        drink.percentage = float(p) if p else None
        db.session.commit()
        flash("Updated", "success")
        return redirect(url_for("list_drinks"))

    @app.route("/delete/<int:id>", methods=["POST"])
    def delete_drink(id):
        drink = Drink.query.get_or_404(id)
        db.session.delete(drink)
        db.session.commit()
        flash("Deleted", "success")
        return redirect(url_for("list_drinks"))

    @app.route("/ai_upload", methods=["GET", "POST"])
    def ai_upload():
        if request.method == "POST":
            drink_list = request.form.get("drink_list") or ""
            file = request.files.get("file")
            if file and file.filename:
                drink_list = file.read().decode("utf-8")

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

            resp = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You structure drinks for a database."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0
            )
            ai_output = resp["choices"][0]["message"]["content"]

            for line in ai_output.splitlines():
                if "|" not in line:
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

        return render_template("upload.html")
