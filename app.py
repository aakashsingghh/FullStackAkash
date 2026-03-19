from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, logout_user, login_user
from sqlalchemy.exc import IntegrityError
from model.users import db, User
import os
from form import RegisterForm, LogoutForm, UpdateEmailForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# ================= DATABASE CONFIG (FIXED) =================

db_url = os.environ.get("DATABASE_URL")

# For local testing (optional)
if not db_url:
    db_url = "mysql+mysqlconnector://root:akash123@localhost:3306/yo"

# Fix for Render PostgreSQL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ==========================================================

db.init_app(app)

# ================= LOGIN MANAGER =================

loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.login_view = 'login'

@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =================================================

with app.app_context():
    db.create_all()

# ================= ROUTES =================

@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            return render_template('register.html', form=form, error='Username or email already taken.')

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return render_template('register.html', form=form, error='Database error.')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)   # ✅ FIXED (Flask-Login)
            session['user.id'] = user.id
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

# ---------- DASHBOARD ----------
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user.id')

    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)

    return render_template(
        'dashboard.html',
        username=user.username,
        logout_form=LogoutForm(),
        user_id=user.id,
        email=user.email
    )

# ---------- LOGOUT ----------
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('user.id', None)
    return redirect(url_for('login'))

# ---------- DELETE ACCOUNT ----------
@app.route('/delete_account/<int:user_id>', methods=['POST'])
@login_required
def delete_account(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

    session.pop('user.id', None)
    return redirect(url_for('login'))

# ---------- UPDATE EMAIL ----------
@app.route('/update_email/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_email(user_id):
    user = User.query.get(user_id)

    if not user:
        return redirect(url_for('login'))

    form = UpdateEmailForm()

    if form.validate_on_submit():
        new_email = form.new_email.data

        existing_email = User.query.filter(
            (User.email == new_email) & (User.id != user_id)
        ).first()

        if existing_email:
            return render_template('update_all.html', form=form, error='Email already taken.')

        user.email = new_email
        db.session.commit()

        return render_template('update_all.html', form=form, success='Email updated successfully.')

    return render_template('update_all.html', form=form, email=user.email)

# ---------- FETCH USERS ----------
@app.route('/fetch_all')
@login_required
def fetch_all():
    users = User.query.all()
    return render_template('fetch_all.html', users=users)

# ---------- DELETE USER ----------
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()

    return redirect(url_for('fetch_all'))

# =================================================

if __name__ == '__main__':
    app.run(debug=True)