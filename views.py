from flask import render_template, request, redirect, url_for, flash
from models import db, Drink

def init_routes(app):

    # --- LIST ALL DRINKS ---
    @app.route('/', methods=['GET'])
    def get_items():
        drinks = Drink.query.all()
        return render_template('drinks.html', items=drinks)

    # --- CREATE NEW DRINK ---
    @app.route('/add', methods=['POST'])
    def create_item():
        try:
            new_drink = Drink(
                type=request.form['type'],        # match input name in drinks.html
                brand=request.form.get('brand'),
                sweetness=request.form.get('sweetness'),
                percentage=request.form.get('percentage')
            )
            # convert numeric fields safely
            if new_drink.sweetness:
                new_drink.sweetness = int(new_drink.sweetness)
            if new_drink.percentage:
                new_drink.percentage = float(new_drink.percentage)

            db.session.add(new_drink)
            db.session.commit()
            flash("Drink added successfully!", "success")
        except Exception as e:
            flash(f"Error adding drink: {e}", "danger")

        return redirect(url_for('get_items'))

    # --- UPDATE EXISTING DRINK ---
    @app.route('/update/<int:drink_id>', methods=['POST'])
    def update_item(drink_id):
        drink = Drink.query.get_or_404(drink_id)
        try:
            drink.type = request.form['type']
            drink.brand = request.form.get('brand')
            drink.sweetness = request.form.get('sweetness')
            drink.percentage = request.form.get('percentage')

            if drink.sweetness:
                drink.sweetness = int(drink.sweetness)
            if drink.percentage:
                drink.percentage = float(drink.percentage)

            db.session.commit()
            flash("Drink updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating drink: {e}", "danger")

        return redirect(url_for('get_items'))

    # --- DELETE DRINK ---
    @app.route('/delete/<int:drink_id>', methods=['POST'])
    def delete_item(drink_id):
        drink = Drink.query.get_or_404(drink)