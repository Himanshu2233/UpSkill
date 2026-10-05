from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db

STATUSES = ('Applied', 'Interviewing', 'Offered', 'Rejected')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    company = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    posting_url = db.Column(db.String(2048), nullable=True)
    application_date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Applied')
    notes = db.Column(db.Text, nullable=False, default='')
    __table_args__ = (db.CheckConstraint("status IN ('Applied', 'Interviewing', 'Offered', 'Rejected')"),)
