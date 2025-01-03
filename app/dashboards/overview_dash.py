from dash import Dash, html, dcc

def init_overview_dash(server):
    dash_app = Dash(
        server=server,
        name="Overview Dashboard",
        url_base_pathname="/dash/overview/"
    )

    dash_app.layout = html.Div([
        html.H1("Overview Dashboard"),
        dcc.Graph(
            id="example-graph",
            figure={
                "data": [{"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "Example"}],
                "layout": {"title": "Overview Example"}
            }
        )
    ])
