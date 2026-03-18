from flask_sqlalchemy import SQLAlchemy
import bcrypt
db= SQLAlchemy()
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)   

    def set_password(self, password):
        self.password_hash= bcrypt.hashpw(
            password.encode('utf-8'),
              bcrypt.gensalt()).decode('utf-8')
    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8'))
