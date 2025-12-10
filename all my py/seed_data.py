import csv
from models import db, Beer, Wine, Spirit
from app import app

def load_csv(filename, model, fieldnames):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, fieldnames=fieldnames)
        next(reader)  # skip header row
        for row in reader:
            # Convert types
            if 'abv' in row: row['abv'] = float(row['abv']) if row['abv'] else None
            if 'mid_strength' in row: row['mid_strength'] = row['mid_strength'].lower() == 'true'
            if 'vintage' in row: row['vintage'] = int(row['vintage']) if row['vintage'] else None
            db.session.add(model(**row))
        db.session.commit()

def seed():
    with app.app_context():
        db.create_all()
        load_csv('beers.csv', Beer,
                 ['name','brewery','style','abv','country','mid_strength','notes'])
        load_csv('wines.csv', Wine,
                 ['name','producer','varietal','region','country','abv','sweetness','vintage','notes'])
        load_csv('spirits.csv', Spirit,
                 ['name','brand','category','subtype','abv','country','flavor_notes','aging'])
        print("Database seeded from CSV files.")

if __name__ == '__main__':
    seed()
