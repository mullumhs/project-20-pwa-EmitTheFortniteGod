from models import db, Beer, Wine, Spirit
from app import app

def seed():
    beers = [
        # name, brewery, style, abv, country, mid_strength, notes
        ('Peroni Nastro Azzurro', 'Peroni', 'Pale Lager', 5.1, 'Italy', False, 'Crisp, light bitterness'),
        ('Heineken', 'Heineken', 'Pale Lager', 5.0, 'Netherlands', False, 'Clean lager profile'),
        ('Guinness Draught', 'Guinness', 'Stout', 4.2, 'Ireland', True, 'Creamy, roasted malt'),
        ('Carlton Mid', 'Carlton & United', 'Mid Lager', 3.5, 'Australia', True, 'Approachable, low bitterness'),
        ('Stone IPA', 'Stone Brewing', 'IPA', 6.9, 'USA', False, 'Pine and citrus hop character'),
        ('Asahi Super Dry', 'Asahi', 'Dry Lager', 5.0, 'Japan', False, 'Very dry finish'),
        ('Pacífico', 'Grupo Modelo', 'Mexican Lager', 4.5, 'Mexico', True, 'Sessionable, mild hop'),
        ('Coopers Pale', 'Coopers', 'Pale Ale', 4.5, 'Australia', True, 'Fruity esters, bottle conditioned'),
        ('Sapporo Premium', 'Sapporo', 'Lager', 4.9, 'Japan', False, 'Smooth, slightly sweet malt'),
    ]

    wines = [
        # name, producer, varietal, region, country, abv, sweetness, vintage, notes
        ('Penfolds Bin 28', 'Penfolds', 'Shiraz', 'South Australia', 'Australia', 14.5, 'dry', 2020, 'Rich dark fruit, spice'),
        ('Cloudy Bay Sauvignon Blanc', 'Cloudy Bay', 'Sauvignon Blanc', 'Marlborough', 'New Zealand', 13.0, 'dry', 2022, 'Zesty citrus, gooseberry'),
        ('Henschke Keyneton Euphonium', 'Henschke', 'Blend', 'Eden Valley', 'Australia', 14.5, 'dry', 2019, 'Structured, cassis, spice'),
        ('Dom Pérignon', 'Moët & Chandon', 'Champagne', 'Champagne', 'France', 12.5, 'dry', 2012, 'Toasty brioche, fine mousse'),
        ('Dr Loosen Riesling', 'Dr Loosen', 'Riesling', 'Mosel', 'Germany', 8.5, 'sweet', 2021, 'Lime, slate, balanced sweetness'),
        ('Antinori Tignanello', 'Antinori', 'Sangiovese Blend', 'Tuscany', 'Italy', 13.5, 'dry', 2019, 'Cherry, cedar, elegance'),
        ('Billecart-Salmon Rosé', 'Billecart-Salmon', 'Rosé Champagne', 'Champagne', 'France', 12.0, 'dry', 2018, 'Delicate red fruit, fine bubbles'),
    ]

    spirits = [
        # name, brand, category, subtype, abv, country, flavor_notes, aging
        ('Tanqueray', 'Tanqueray', 'Gin', 'London Dry', 47.3, 'UK', 'Juniper-forward, citrus, spice', None),
        ('Hendrick\'s', 'Hendrick\'s', 'Gin', 'New Western', 41.4, 'UK', 'Cucumber and rose notes', None),
        ('Johnnie Walker Black Label', 'Johnnie Walker', 'Whisky', 'Blended Scotch', 40.0, 'UK', 'Smoke, vanilla, dried fruit', '12 years'),
        ('Lagavulin 16', 'Lagavulin', 'Whisky', 'Single Malt Scotch', 43.0, 'UK', 'Peat smoke, iodine, caramel', '16 years'),
        ('Patrón Silver', 'Patrón', 'Tequila', 'Blanco', 40.0, 'Mexico', 'Agave-forward, pepper, citrus', None),
        ('Don Julio Reposado', 'Don Julio', 'Tequila', 'Reposado', 40.0, 'Mexico', 'Vanilla, caramel, baked agave', '8 months'),
        ('Havana Club 7', 'Havana Club', 'Rum', 'Añejo', 40.0, 'Cuba', 'Molasses, oak, dried fruit', '7 years'),
        ('Grey Goose', 'Grey Goose', 'Vodka', None, 40.0, 'France', 'Clean, soft mouthfeel', None),
        ('Aperol', 'Aperol', 'Liqueur', 'Aperitivo', 11.0, 'Italy', 'Bitter orange, rhubarb, herbal', None),
        ('Campari', 'Campari', 'Liqueur', 'Aperitivo', 25.0, 'Italy', 'Bitter orange, spice', None),
        ('Hennessy VS', 'Hennessy', 'Brandy', 'Cognac', 40.0, 'France', 'Oak, vanilla, dried fruit', '2-8 years'),
    ]

    with app.app_context():
        db.create_all()
        if Beer.query.count() == 0:
            for b in beers:
                db.session.add(Beer(name=b[0], brewery=b[1], style=b[2], abv=b[3], country=b[4], mid_strength=b[5], notes=b[6]))
        if Wine.query.count() == 0:
            for w in wines:
                db.session.add(Wine(name=w[0], producer=w[1], varietal=w[2], region=w[3], country=w[4], abv=w[5], sweetness=w[6], vintage=w[7], notes=w[8]))
        if Spirit.query.count() == 0:
            for s in spirits:
                db.session.add(Spirit(name=s[0], brand=s[1], category=s[2], subtype=s[3], abv=s[4], country=s[5], flavor_notes=s[6], aging=s[7]))
        db.session.commit()
        print('Seeded initial catalog.')

if __name__ == '__main__':
    seed()
