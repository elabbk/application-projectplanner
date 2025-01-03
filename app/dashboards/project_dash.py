from dash import Dash, html, dcc
from flask import request

def init_project_dash(server):
    dash_app = Dash(
        server=server,
        name="Project Dashboard",
        url_base_pathname="/dash/project/"
    )

    dash_app.layout = html.Div([
        html.H1("Project Dashboard"),
        dcc.Graph(
            id="project-graph",
            figure={
                "data": [{"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "Project Example"}],
                "layout": {"title": "Project Example"}
            }
        )
    ])
