from dash import Dash, html, dcc, Input, Output, State
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import pandas as pd
from ..db import db

from ..models import Items, Projects

def init_project_dash(server):
    dash_app = Dash(
        server=server,
        name="Project Dashboard",
        url_base_pathname="/dash/project/"
    )

    # Layout for the dashboard
    dash_app.layout = html.Div([
        html.H1("Project Dashboard"),
        html.Div([
            html.Label("Adjust Start Date:"),
            dcc.Input(id="start-date-input", type="date", style={"margin-right": "10px"}),
            html.Label("Adjust End Date:"),
            dcc.Input(id="end-date-input", type="date"),
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
        dcc.Graph(id="timeline-graph"),
        #html.Div(id="net-position", style={"font-size": "18px", "margin-top": "20px"})
    ])

    # Callback to update the graph and net position
    @dash_app.callback(
        Output("timeline-graph", "figure"),

        [Input("start-date-input", "value"),
         Input("end-date-input", "value"),
         Input("category-dropdown", "value"),
         Input("group-by-category", "value")]
    )

    def update_dashboard(start_date, end_date, categories, group_by_category):
        #project_id = pathname.split("/")[-1]

        # Query all items from the database with their associated projects
        items = db.session.query(Items, Projects.project_name).join(Projects).all()

        if not items:
            return px.bar()

        # Convert items to a DataFrame
        df = pd.DataFrame([{
            "Project": project_name,
            "Item Name": item.item_name,
            "Type": item.type,
            "Amount": item.amount,
            "Category": item.category,
            "Start Date": item.item_start_date,
            "End Date": item.item_end_date
        } for item, project_name in items])
        print(df)

        # Set default date range if not provided
        if not start_date:
            start_date = df["Start Date"].min().date()
        if not end_date:
            end_date = df["End Date"].max().date()
        df = df[(df["Start Date"] >= pd.to_datetime(start_date)) & (df["End Date"] <= pd.to_datetime(end_date))]

        # Filter by categories if provided
        if categories:
            df = df[df["Category"].isin(categories)]

        # Create a timeline chart
        if "group" in group_by_category:
            y_axis = "Category"
        else:
            y_axis = "Item Name"

        figure = px.timeline(
            df,
            x_start="Start Date",
            x_end="End Date",
            y=y_axis,
            color="Category",
            title="Project Timeline"
        )

        # Update layout for better visualization
        figure.update_layout(
            xaxis_title="Time",
            yaxis_title="Items",
            yaxis=dict(
                categoryorder="total ascending"
            ),
            bargap=0.2
        )

        figure.update_yaxes(categoryorder="total ascending")
        figure.update_traces(textposition="inside", texttemplate="%{text:.2s}")

        return figure

    return dash_app


# Function to calculate net position
def compute_net_position(df, split_monthly):
    total_budget = df[df["Type"] == "budget"]["Amount"].sum()
    total_cost = df[df["Type"] == "cost"]["Amount"].sum()

    if split_monthly:
        # Logic to split budget and costs over months
        return total_budget - total_cost

    return total_budget - total_cost
