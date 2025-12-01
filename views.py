from flask import render_template, request
import models

def register_routes(app):

    @app.teardown_appcontext
    def close_db(exception):
        models.close_db(exception)

    @app.route("/", methods=["GET","POST"])
    def index():
        if request.method=="POST":
            beers = [l.strip() for l in request.form.get("beers","").splitlines() if l.strip()]
            wines = [l.strip() for l in request.form.get("wines","").splitlines() if l.strip()]
            spirits = [l.strip() for l in request.form.get("spirits","").splitlines() if l.strip()]

            matched = {"beer":[], "wine":[], "spirit":[]}
            unmatched = {"beer":[], "wine":[], "spirit":[]}

            for b in beers:
                m = models.match_drink(b,"beer")
                (matched["beer"] if m else unmatched["beer"]).append(m or b)
            for w in wines:
                m = models.match_drink(w,"wine")
                (matched["wine"] if m else unmatched["wine"]).append(m or w)
            for s in spirits:
                m = models.match_drink(s,"spirit")
                (matched["spirit"] if m else unmatched["spirit"]).append(m or s)

            return render_template("poster.html", matched=matched, unmatched=unmatched)

        return render_template("index.html")
