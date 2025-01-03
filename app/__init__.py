import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .dashboards import register_dash_apps
from .routes import main
from .db import db

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # WEBSITE_HOSTNAME exists only in production environment
    if 'WEBSITE_HOSTNAME' not in os.environ:
        # local development, where we'll use environment variables
        print("Loading config.development and environment variables from .env file.")
        app.config.from_object('azureproject.development')
    else:
        # production
        print("Loading config.production.")
        app.config.from_object('azureproject.production')

    app.config.update(
        SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    app.register_blueprint(main)

    try:
        db.init_app(app)
        migrate.init_app(app, db)

    except Exception as e:
        print(f"Error initializing the database: {e}")

    try:
        register_dash_apps(app)
    except Exception as e:
        print(f"Error registering Dash apps: {e}")

    # Register shell context processor
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'app': app}

    return app

