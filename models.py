from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False)
    long_url = db.Column(db.String(500), nullable=False)
