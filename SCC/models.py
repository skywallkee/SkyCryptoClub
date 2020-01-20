from .extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publicId = db.Column(db.String(64))
    username = db.Column(db.String(35))
    password = db.Column(db.String(64))
    email = db.Column(db.String(64))
    otp_token = db.Column(db.String(64))