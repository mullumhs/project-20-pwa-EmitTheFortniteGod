from flask_sqlalchemy import SQLAlchemy

from datetime import datetime



db = SQLAlchemy()



class Drink(db.Model):
    id = db.Column(db.Integer, primary_key=True)        # Its Nessasary
    title = db.Column(db.String(100), nullable=False)   # Drink name 
    type = db.Column(db.String(50), nullable=False)     # "beer", "wine", "spirit"
    brand = db.Column(db.String(100))                   # Coopers, Jim Beans , WolfBlast
    sweetness = db.Column(db.Integer)                   # 1–10 scale
    percentage = db.Column(db.Float)                    # ABV %

    def __repr__(self):

        return f'<Task {self.title}>'