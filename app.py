from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, logout_user
from sqlalchemy.exc import IntegrityError
from model.users import db
from form import RegisterForm, LogoutForm, UpdateEmailForm
from model.users import User



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://rootlocalhost:3306/yo'

loginmanager = LoginManager()   
loginmanager.init_app(app)
loginmanager.login_view = 'login'

@loginmanager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            error = 'Username or email already taken.'
            return render_template('register.html', form=form, error=error)

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        user.set_password(password)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            error = 'A database error occurred. The username or email may already exist.'
            return render_template('register.html', form=form, error=error)

        return render_template("login.html")
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user.id'] = user.id
            return render_template('dashboard.html', username=username, logout_form=LogoutForm(), user_id=user.id, email=user.email)
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if 'user.id' not in session:
        return render_template('login.html')
    user_id = session['user.id']
    user = User.query.get(user_id)
    if not user:
        return render_template('login.html')
    return render_template('dashboard.html', username=user.username, logout_form=LogoutForm(), user_id=user.id, email=user.email)

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete_account/<int:user_id>', methods=['POST'])
@login_required
def delete_account(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    session.pop('user.id', None)
    return redirect(url_for('login'))

@app.route('/update_email/<int:user_id>', methods=['GET', 'POST'])
def update_email(user_id):
    user = User.query.get(user_id)
    if not user:
        return render_template('login.html'), 404
    
    form = UpdateEmailForm()
    if form.validate_on_submit():
        new_email = form.new_email.data
        existing_email = User.query.filter((User.email == new_email) & (User.id != user_id)).first()
        if existing_email:
            error = 'Email already taken by another user.'
            return render_template('update_all.html', form=form, user_id=user_id, error=error)
        user.email = new_email
        db.session.commit()
        return render_template('update_all.html', form=form, user_id=user_id, success='Email updated successfully.')
    return render_template('update_all.html', form=form, user_id=user_id, email=user.email)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for('fetch_all'))

@app.route('/fetch_all')
def fetch_all():
    if 'user.id' not in session:
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('fetch_all.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)