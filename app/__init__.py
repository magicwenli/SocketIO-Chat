import os
import uuid

import click
from flask import Flask, url_for

from app.blueprints.auth import auth_bp
from app.blueprints.chat import chat_bp
from app.extends import db, moment, ckediter, socketio, login_manager, bootstrap, jsglue
from app.models import User
from app.settings import config


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    reg_blueprints(app)
    reg_extensions(app)
    reg_commands(app)
    reg_jinja2(app)
    return app


def reg_blueprints(app):
    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')


def reg_extensions(app):
    db.init_app(app)
    moment.init_app(app)
    ckediter.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    jsglue.init_app(app)


def reg_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')

        db.create_all()

        user = User(username='magicwenli', email='yxra3603@outlook.com', about='123')
        user.set_password('123456')
        user.generate_email_hash()
        db.session.add(user)
        db.session.commit()
        click.echo('Initialized database.')


def reg_jinja2(app):
    @app.context_processor
    def utility_processor():
        def chat_url(user):
            return url_for('chat.chat_url', uuid=uuid.uuid3(uuid.NAMESPACE_DNS, user.username))

        return dict(chat_url=chat_url)
