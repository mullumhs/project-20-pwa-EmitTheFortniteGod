# app.py
# This file creates the Flask application instance

from flask import Flask

app = Flask(__name__)

# Secret key used for forms & security features
app.secret_key = "pourtrait_secret_key"

# Import routes AFTER app is created
from views import *
