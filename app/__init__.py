from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app(config_name):
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False, static_url_path='/static')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    app.config.from_object('config.Config')

    with app.app_context():
        # Imports
        from . import routes

        # Create tables for our models
        # db.create_all()

        return app
