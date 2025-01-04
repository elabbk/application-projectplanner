from dash import Dash, html, dcc, Input, Output
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import pandas as pd
from ..db import db

from ..models import Items, Projects

def init_overview_dash(server):
    dash_app = Dash(
        server=server,
        name="Overview Dashboard",
        url_base_pathname="/dash/overview/"
    )

    # Layout for the dashboard
    dash_app.layout = html.Div([
        html.H1("Overview Dashboard"),
        dcc.DatePickerRange(
            id="date-range-picker",
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            style={"margin-bottom": "20px"}
        ),
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
            placeholder="Select Categories",
            style={"margin-bottom": "20px"}
        ),
        dcc.Dropdown(
            id="label-dropdown",
            placeholder="Select Labels",
            multi=True,
            style={"margin-bottom": "20px"}
        ),
        dcc.Checklist(
            id="group-by-category",
            options=[{"label": "Group by Category", "value": "group"}],
            value=[]
        ),
        dcc.Graph(id="timeline-graph"),
    ])

    # Callback to update the graph
    @dash_app.callback(
        Output("timeline-graph", "figure"),
        [Input("date-range-picker", "start_date"),
         Input("date-range-picker", "end_date"),
         Input("category-dropdown", "value"),
         Input("label-dropdown", "value"),
         Input("group-by-category", "value")]
    )
    def update_dashboard(start_date, end_date, categories, labels, group_by_category):
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
        # Filter by date range
        if start_date and end_date:
            df = df[(df["Start Date"] >= pd.to_datetime(start_date)) & (df["End Date"] <= pd.to_datetime(end_date))]

        # Filter by categories if provided
        if categories:
            df = df[df["Category"].isin(categories)]

        # Filter by labels if provided
        if labels:
            df = df[df["Type"].isin(labels)]

        # Sort and prepare the y-axis structure
        df['Project_Type'] = df['Project'] + ' - ' + df['Type']

        # Compute net positions for each project
        net_positions = df.groupby('Project').apply(lambda group: compute_net_position(group, False)).reset_index(name='Net Position')
        net_positions['Start Date'] = df['Start Date'].min()
        net_positions['End Date'] = df['End Date'].max()
        net_positions['Type'] = 'Net Position'

        # Append net positions to the DataFrame
        df = pd.concat([df, net_positions])

        # Create a timeline chart with horizontal bars grouped by project and type
        figure = px.timeline(
            df,
            x_start="Start Date",
            x_end="End Date",
            y="Project_Type",
            color="Category",
            text="Amount",
            title="All Projects Timeline",
            labels={"Project_Type": "Project / Type", "Category": "Categories"}
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