import os

import click
from flask import Flask

from app.blueprints.auth import auth_bp
from app.blueprints.chat import chat_bp
from app.extends import db, moment, ckediter, socketio, login_manager, bootstrap
from app.settings import config


def create_app(debug=False, config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.debug = debug

    reg_blueprints(app)
    reg_extensions(app)
    reg_commands(app)

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
        click.echo('Initialized database.')
