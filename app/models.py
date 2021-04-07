from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extends import db

# 多对多关联表
association_table = db.Table('association',
                             db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
                             db.Column('group_id', db.Integer, db.ForeignKey('group.id', ondelete='CASCADE'))
                             )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(128))
    about = db.Column(db.Text)
    groups = db.relationship('Group', secondary=association_table, back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    users = db.relationship('User', secondary=association_table, back_populates='groups')


class MessagePeer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class MessageGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    body = db.Column(db.Text)
