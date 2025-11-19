from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Drink(db.Model):
    __tablename__ = "drinks"

    id = db.Column(db.Integer, primary_key=True)        # Primary key
    type = db.Column(db.String(50), nullable=False)     # "beer", "wine", "spirit"
    brand = db.Column(db.String(100))                   # Coopers, Jim Beam, Wolf Blass
    sweetness = db.Column(db.Integer)                   # 1–10 scale
    percentage = db.Column(db.Float)                    # ABV %

    def __repr__(self):
        return f"<Drink {self.type} - {self.brand}, {self.percentage}% ABV>"