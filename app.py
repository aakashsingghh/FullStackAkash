import os

from flask import Flask, flash, redirect, render_template, session, url_for
from flask_sqlalchemy import SQLAlchemy
from register import LoginForm, RegisterForm
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret_key")

db_url = os.environ.get("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if not db_url:
    raise RuntimeError("DATABASE_URL is not set.")

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Incorrect email or password. Please try again.", "error")
        else:
            session["username"] = user.username
            session["email"] = email
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("dashboard"))

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with this email already exists.", "error")
            return render_template("register.html", form=form)

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

        flash(f"Registration successful for {username}", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/dashboard")
def dashboard():
    username = session.get("username")

    if not username:
        flash("Please sign in to open the dashboard.", "error")
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=username)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
