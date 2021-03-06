import hashlib
from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extends import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(128))
    email_hash = db.Column(db.String(128))
    about = db.Column(db.String(128))
    messages = db.relationship('Message', back_populates='author', cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_email_hash()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_email_hash(self):
        if self.email is not None and self.email_hash is None:
            self.email_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    def __repr__(self):
        return u"<User: {}>".format(self.username)

    @property
    def gravatar(self):
        return 'https://gravatar.loli.net/avatar/%s?d=monsterid' % self.email_hash


class Guest(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'


login_manager.anonymous_user = Guest


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    in_room = db.Column(db.Boolean, default=1)
    room_name = db.Column(db.String(30))
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow(), index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', back_populates='messages')


class Room():
    users = []
    name = "chat"

    def __init__(self, name):
        self.name = name

    def add_user(self, user):
        if user not in self.users:
            self.users.append(user)

    def remove_user(self, user):
        if user in self.users:
            self.users.remove(user)

    def length(self):
        return len(self.users)

    def __repr__(self):
        return u'<Room: {}>'.format(self.name)
