from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Drink(db.Model):
    __tablename__ = "drinks"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(100))
    sweetness = db.Column(db.Integer)
    percentage = db.Column(db.Float)

    def __repr__(self):
        return f"<Drink {self.type} - {self.brand}, {self.percentage}% ABV>"
