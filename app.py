import os
from app import create_app, db
from flask_migrate import upgrade
app = create_app()

# Push the app context when starting the server
with app.app_context():
    db.create_all()
    upgrade()

"""
import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from projectplanner.app.dashboards import register_dash_apps

server = Flask(__name__, static_folder='static')

# Dash app
app = Dash(__name__, server=server, url_base_pathname='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP])


# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    server.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    server.config.from_object('azureproject.production')

server.config.update(
    SQLALCHEMY_DATABASE_URI=server.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(server)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(server, db)

register_dash_apps(server)

# The import must be done after db initialization due to circular import issue

"""