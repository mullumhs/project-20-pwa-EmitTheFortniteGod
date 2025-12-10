import re, unicodedata
from difflib import SequenceMatcher
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, UserDrink, Beer, Wine, Spirit

bp = Blueprint('main', __name__)

# ---------- Auth ----------
@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        pw = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already registered','error')
            return redirect(url_for('main.register'))
        user = User(email=email, password_hash=generate_password_hash(pw))
        db.session.add(user); db.session.commit()
        flash('Account created. Please log in.','success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        pw = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, pw):
            login_user(user); return redirect(url_for('main.dashboard'))
        flash('Invalid credentials','error')
        return redirect(url_for('main.login'))
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('main.login'))

# ---------- Dashboard ----------
@bp.route('/')
@login_required
def dashboard():
    count = UserDrink.query.filter_by(user_id=current_user.id).count()
    return render_template('dashboard.html', drink_count=count)

# ---------- Upload ----------
@bp.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        raw_text = request.form['drink_list']
        UserDrink.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        for line in [l.strip() for l in raw_text.splitlines() if l.strip()]:
            table, mid, status = match_drink(line)
            db.session.add(UserDrink(user_id=current_user.id,
                                     raw_name=line,
                                     matched_table=table,
                                     matched_id=mid,
                                     correction_status=status))
        db.session.commit()
        flash('Drinks processed','success')
        return redirect(url_for('main.dashboard'))
    return render_template('upload.html')

# ---------- Posters ----------
@bp.route('/posters')
@login_required
def posters():
    beers,wines,spirits,unknowns = build_grouped(current_user.id)
    return render_template('posters.html',
                           beers=beers,wines=wines,spirits=spirits,unknowns=unknowns)

# ---------- Unknowns export ----------
@bp.route('/unknowns.txt')
@login_required
def unknowns_txt():
    _,_,_,unknowns = build_grouped(current_user.id)
    content = "# Unknown drinks\n"
    content += f"# Exported {datetime.utcnow().isoformat()} UTC\n\n"
    for u in unknowns: content += u.raw_name + "\n"
    return Response(content,
                    mimetype="text/plain",
                    headers={"Content-Disposition":"attachment;filename=unknown_drinks.txt"})

# ---------- Helpers ----------
def normalize_name(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode()
    s = re.sub(r'[^a-z0-9\s]','',s.lower())
    return re.sub(r'\s+',' ',s).strip()

def token_score(a,b):
    ratio = SequenceMatcher(None,a,b).ratio()
    overlap = len(set(a.split()) & set(b.split())) / max(1,len(set(a.split())|set(b.split())))
    return ratio*0.7 + overlap*0.3

def match_catalog(name, table, field='name', brand_field=None):
    n = normalize_name(name)
    best,best_score=None,0
    for c in table.query.all():
        fields=[getattr(c,field) or '']
        if brand_field: fields.append(getattr(c,brand_field) or '')
        joined=normalize_name(' '.join(fields))
        score=token_score(n,joined)
        if score>best_score: best,best_score=c,score
    if best and best_score>=0.80: return best,"exact"
    elif best and best_score>=0.65: return best,"corrected"
    else: return None,None

def match_drink(raw):
    for t,table,f,b in [('beer',Beer,'name',None),
                        ('wine',Wine,'name','producer'),
                        ('spirit',Spirit,'name','brand')]:
        m,status=match_catalog(raw,table,f,b)
        if m: return t,m.id,status
    return None,None,None

def build_grouped(uid):
    items=UserDrink.query.filter_by(user_id=uid).all()
    beers,wines,spirits,unknowns=[],[],[],[]
    for it in items:
        if it.matched_table=='beer' and it.matched_id: beers.append(Beer.query.get(it.matched_id))
        elif it.matched_table=='wine' and it.matched_id: wines.append(Wine.query.get(it.matched_id))
        elif it.matched_table=='spirit' and it.matched_id: spirits.append(Spirit.query.get(it.matched_id))
        else: unknowns.append(it)
    return beers,wines,spirits,unknowns
