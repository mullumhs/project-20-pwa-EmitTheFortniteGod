from flask import Flask
from models import db
from routes import init_routes
import os
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

with app.app_context():
    db.create_all()

init_routes(app, openai)

if __name__ == "__main__":
    app.run(debug=True)
