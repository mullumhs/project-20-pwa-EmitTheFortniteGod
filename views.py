import re
import unicodedata
from difflib import SequenceMatcher
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from io import StringIO
from datetime import datetime
from models import db, User, UserDrink, Beer, Wine, Spirit

bp = Blueprint('main', __name__)

# ---------- Auth ----------

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('main.register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('main.register'))
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials.', 'error')
        return redirect(url_for('main.login'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# ---------- Dashboard ----------

@bp.route('/')
@login_required
def dashboard():
    count = UserDrink.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', drink_count=count)

# ---------- Upload / Paste ----------

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        raw_text = request.form.get('drink_list', '').strip()
        lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
        # Clear previous
        UserDrink.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        for ln in lines:
            matched_table, matched_id = match_drink(ln)
            ud = UserDrink(user_id=current_user.id, raw_name=ln,
                           matched_table=matched_table, matched_id=matched_id)
            db.session.add(ud)
        db.session.commit()
        flash('Drinks processed. See posters or edit stock.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('upload.html')

# ---------- Edit Stock ----------

@bp.route('/edit-stock', methods=['GET', 'POST'])
@login_required
def edit_stock():
    items = UserDrink.query.filter_by(user_id=current_user.id).all()
    if request.method == 'POST':
        # Replace all with new entries
        UserDrink.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        new_text = request.form.get('drink_list', '').strip()
        for ln in [l.strip() for l in new_text.splitlines() if l.strip()]:
            matched_table, matched_id = match_drink(ln)
            db.session.add(UserDrink(user_id=current_user.id, raw_name=ln,
                                     matched_table=matched_table, matched_id=matched_id))
        db.session.commit()
        flash('Stock updated.', 'success')
        return redirect(url_for('main.edit_stock'))
    return render_template('edit_stock.html', items=items)

# ---------- Posters ----------

@bp.route('/posters')
@login_required
def posters():
    beers, wines, spirits, unknowns = build_grouped(current_user.id)
    sort_by = request.args.get('sort', 'name')
    # Sorting logic
    beers = sort_beers(beers, sort_by)
    wines = sort_wines(wines, sort_by)
    spirits = sort_spirits(spirits, sort_by)
    return render_template('posters.html',
                           beers=beers, wines=wines, spirits=spirits,
                           unknowns=unknowns, sort_by=sort_by)

# ---------- Unknowns export ----------

@bp.route('/unknowns.txt')
@login_required
def unknowns_txt():
    _, _, _, unknowns = build_grouped(current_user.id)
    buf = StringIO()
    buf.write('# Unknown drinks for catalog enrichment\n')
    buf.write(f'# Exported {datetime.utcnow().isoformat()} UTC\n\n')
    for u in unknowns:
        buf.write(u.raw_name + '\n')
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='unknown_drinks.txt', mimetype='text/plain')

# ---------- Helpers ----------

def normalize_name(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9\s\-]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def token_score(a, b):
    # Balanced score combining ratio and common tokens
    ratio = SequenceMatcher(None, a, b).ratio()
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    overlap = len(a_tokens & b_tokens) / max(1, len(a_tokens | b_tokens))
    return (ratio * 0.7) + (overlap * 0.3)

def match_catalog(name, table, field='name', brand_field=None):
    n = normalize_name(name)
    # Exact match first
    exact = table.query.filter(getattr(table, field).ilike(name)).first()
    if exact:
        return exact
    # Fuzzy across full table
    candidates = table.query.all()
    best, best_score = None, 0.0
    for c in candidates:
        fields = [getattr(c, field) or '']
        if brand_field:
            fields.append(getattr(c, brand_field) or '')
        joined = normalize_name(' '.join(fields))
        score = token_score(n, joined)
        if score > best_score:
            best, best_score = c, score
    if best and best_score >= 0.62:  # threshold tuned to catch common misspellings
        return best
    return None

def match_drink(raw):
    # Heuristic route: if contains style keywords, try that table first.
    n = normalize_name(raw)
    beer_hint = any(k in n for k in ['lager', 'ale', 'ipa', 'stout', 'porter', 'pils', 'draught'])
    wine_hint = any(k in n for k in ['cabernet', 'merlot', 'shiraz', 'chardonnay', 'pinot', 'sauvignon', 'riesling', 'rosé', 'rose'])
    spirit_hint = any(k in n for k in ['gin', 'whisky', 'whiskey', 'rum', 'vodka', 'tequila', 'mezcal', 'brandy', 'cognac', 'liqueur', 'amaro'])

    # Try hinted table first, then fallbacks
    order = []
    if beer_hint: order.append('beer')
    if wine_hint: order.append('wine')
    if spirit_hint: order.append('spirit')
    order += [t for t in ['beer', 'wine', 'spirit'] if t not in order]

    for t in order:
        if t == 'beer':
            m = match_catalog(raw, Beer, field='name')
            if m: return 'beer', m.id
        elif t == 'wine':
            m = match_catalog(raw, Wine, field='name', brand_field='producer')
            if m: return 'wine', m.id
        else:
            m = match_catalog(raw, Spirit, field='name', brand_field='brand')
            if m: return 'spirit', m.id
    return None, None

def build_grouped(user_id):
    items = UserDrink.query.filter_by(user_id=user_id).all()
    beers, wines, spirits, unknowns = [], [], [], []
    for it in items:
        if it.matched_table == 'beer' and it.matched_id:
            beers.append(Beer.query.get(it.matched_id))
        elif it.matched_table == 'wine' and it.matched_id:
            wines.append(Wine.query.get(it.matched_id))
        elif it.matched_table == 'spirit' and it.matched_id:
            spirits.append(Spirit.query.get(it.matched_id))
        else:
            unknowns.append(it)
    return beers, wines, spirits, unknowns

def sort_beers(beers, key):
    if key == 'abv':
        return sorted(beers, key=lambda x: (x.abv or 0))
    elif key == 'mid':
        return sorted(beers, key=lambda x: (not x.mid_strength, x.name or ''))
    else:
        return sorted(beers, key=lambda x: (x.name or ''))

def sort_wines(wines, key):
    if key == 'abv':
        return sorted(wines, key=lambda x: (x.abv or 0))
    elif key == 'sweetness':
        order = {'dry': 0, 'medium': 1, 'sweet': 2}
        return sorted(wines, key=lambda x: order.get((x.sweetness or 'dry').lower(), 0))
    else:
        return sorted(wines, key=lambda x: (x.name or ''))

def sort_spirits(spirits, key):
    if key == 'abv':
        return sorted(spirits, key=lambda x: (x.abv or 0))
    elif key == 'category':
        return sorted(spirits, key=lambda x: (x.category or '', x.name or ''))
    else:
        return sorted(spirits, key=lambda x: (x.name or ''))
