# main.py
# This is the entry point that actually runs the server

from app import app

if __name__ == "__main__":
    app.run(debug=True)
