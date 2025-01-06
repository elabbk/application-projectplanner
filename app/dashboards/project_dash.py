from dash import Dash, html, dcc, Input, Output, State
from flask_sqlalchemy import SQLAlchemy
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from urllib.parse import urlparse, parse_qs
from ..db import db
from ..models import Items, Projects

# Map category names to hex color codes
CATEGORY_COLORS = {
    "consultancy services": "#1f77b4",
    "licenses": "#ff7f0e",
    "operations": "#2ca02c",
    "business travels": "#d62728",
    "internal FTE": "#9467bd",
    "other": "#8c564b"
}

def init_project_dash(server):
    dash_app = Dash(
        server=server,
        name="Project Dashboard",
        url_base_pathname="/dash/project/"
    )

    # Layout for the dashboard
    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.H1("Project Dashboard"),
        html.Div([
            dcc.DatePickerRange(
                id="date-picker-range",
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                style={"margin-bottom": "20px"}
            ),
        ], style={"margin-bottom": "20px"}),
        dcc.Dropdown(
            id="category-dropdown",
            options=[
                {"label": "Consultancy Services", "value": "consultancy services"},
                {"label": "Licenses", "value": "licenses"},
                {"label": "Operations", "value": "operations"},
                {"label": "Business Travels", "value": "business travels"},
                {"label": "Internal FTE", "value": "internal FTE"},
                {"label": "Other", "value": "other"},
            ],
            multi=True,
            placeholder="Select Categories"
        ),
        dcc.Checklist(
            id="group-by-category",
            options=[{"label": "Group by Category", "value": "group"}],
            value=[]
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            style={"display": "inline-block", "width": "20px", "height": "20px", "backgroundColor": color, "margin-right": "10px"}
                        ),
                        html.Span(category, style={"margin-right": "20px"})
                    ],
                    style={"display": "flex", "align-items": "center", "margin-right": "20px"}
                ) for category, color in CATEGORY_COLORS.items()
            ],
            style={"margin-bottom": "20px", "display": "flex", "flex-wrap": "wrap"}
        ),
        dcc.Graph(id="timeline-graph")
    ])

    # Callback to update the graph
    @dash_app.callback(
        Output("timeline-graph", "figure"),
        [Input("url", "href"),
         Input("date-picker-range", "start_date"),
         Input("date-picker-range", "end_date"),
         Input("category-dropdown", "value"),
         Input("group-by-category", "value")]
    )
    def update_dashboard(href, start_date, end_date, categories, group_by_category):
        # Parse project ID from query string
        project_id = None
        if href:
            parsed_url = urlparse(href)
            query_params = parse_qs(parsed_url.query)
            if 'project_id' in query_params:
                project_id = int(query_params['project_id'][0])

        if not project_id:
            return go.Figure()

        # Query only items related to the specific project
        items = db.session.query(Items, Projects.project_name).join(Projects).filter(Projects.project_id == project_id).all()

        if not items:
            return go.Figure()

        # Convert items to a DataFrame
        df = pd.DataFrame([{
            "Project": project_name,
            "Item Name": f"{item.item_name} ({item.type})",
            "Type": item.type,
            "Amount": item.amount,
            "Category": item.category,
            "Start Date": item.item_start_date,
            "End Date": item.item_end_date
        } for item, project_name in items])

        # Set default values for start_date and end_date if not provided
        if not start_date:
            start_date = df["Start Date"].min()
        else:
            start_date = pd.to_datetime(start_date)

        if not end_date:
            end_date = df["End Date"].max()
        else:
            end_date = pd.to_datetime(end_date)

        # Filter cost items within date range
        cost_df = df[(df["Type"] == "cost") & (df["Start Date"] >= start_date) & (df["End Date"] <= end_date)]

        # Filter budget items that overlap with the date range
        budget_df = df[(df["Type"] == "budget") & ((df["Start Date"] <= end_date) & (df["End Date"] >= start_date))]

        # Calculate net position based on filtered budgets and costs
        net_value = budget_df["Amount"].sum() - cost_df["Amount"].sum()

        # Determine net position color
        if net_value < 0:
            net_color = "red"
        elif net_value > 0.8 * budget_df["Amount"].sum():
            net_color = "green"
        else:
            net_color = "blue"

        # Create subplots with shared x-axis
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, subplot_titles=("Cost Items", "Budget Items", "Net Position"))

        # Add cost items as horizontal bars with category-based coloring
        for _, row in cost_df.iterrows():
            color = CATEGORY_COLORS.get(row["Category"], "#333333")
            fig.add_trace(go.Bar(
                x=[row["Amount"]],
                y=[row["Item Name"]],
                orientation='h',
                name=row["Category"],
                marker_color=color,
                showlegend=False,
                legendgroup=row["Category"]
            ), row=1, col=1)

        # Add budget items as horizontal bars with category-based coloring
        for _, row in budget_df.iterrows():
            color = CATEGORY_COLORS.get(row["Category"], "#333333")
            fig.add_trace(go.Bar(
                x=[row["Amount"]],
                y=[row["Item Name"]],
                orientation='h',
                name=row["Category"],
                marker_color=color,
                showlegend=False,
                legendgroup=row["Category"]
            ), row=2, col=1)

        # Add net position as a horizontal bar
        fig.add_trace(go.Bar(
            x=[net_value],
            y=["Net Position"],
            orientation='h',
            name="Net Position",
            marker_color=net_color,
            showlegend=False
        ), row=3, col=1)

        # Update layout to ensure shared x-axis and correct ordering of subplots
        fig.update_layout(
            barmode="stack",
            xaxis_title="Amount",
            yaxis_title="Items",
            title="Project Timeline with Costs, Budgets, and Net Position",
            bargap=0.2
        )

        return fig

    return dash_app
