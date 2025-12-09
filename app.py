from flask import Flask
from flask_login import LoginManager
from models import db, User
from views import bp as main_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-to-a-long-random-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pourtrait.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(main_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
