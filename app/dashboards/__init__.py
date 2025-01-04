from .overview_dash import init_overview_dash
from .project_dash import init_project_dash

def register_dash_apps(app):
    init_overview_dash(app)
    init_project_dash(app)

