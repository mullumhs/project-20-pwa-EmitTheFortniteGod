from flask import Flask
import models
import views

app = Flask(__name__)
app.secret_key = "dev-secret-key"

# init DB
with app.app_context():
    models.init_db()
    models.seed_db()

# register routes
views.register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
