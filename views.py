from flask import render_template, request
import models

def register_routes(app):

    @app.teardown_appcontext
    def close_db(exception):
        models.close_db(exception)

    @app.route("/", methods=["GET","POST"])
    def index():
        if request.method=="POST":
            drinks = [l.strip() for l in request.form.get("drinks","").splitlines() if l.strip()]

            matched, unmatched = [], []
            for d in drinks:
                m = models.match_drink(d)
                (matched if m else unmatched).append(m or d)

            return render_template("poster.html", matched=matched, unmatched=unmatched)

        return render_template("index.html")
