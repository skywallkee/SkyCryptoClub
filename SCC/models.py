from .extensions import db

class User(db.Model):
    # User login table, unseen by users
    id = db.Column(db.Integer, primary_key=True)
    publicId = db.Column(db.String(64))
    username = db.Column(db.String(35))
    password = db.Column(db.String(64))
    email = db.Column(db.String(64))
    otp_token = db.Column(db.String(64))

class Platform(db.Model):
    # Partnered platforms available on SCC
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(35), nullable=False)