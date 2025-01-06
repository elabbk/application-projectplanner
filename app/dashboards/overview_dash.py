from dash import Dash, html, dcc, Input, Output, no_update, State
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
NET_COLORS = {
    "Net Position Negative": "red",
    "Net Position within 80-100% of budget": "green",
    "Net Position <80% of budget": "blue"
}

def init_overview_dash(server):
    dash_app = Dash(
        server=server,
        name="Overview Dashboard",
        url_base_pathname="/dash/overview/"
    )

    # Layout for the dashboard
    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.H1("Project Dashboard"),
        html.Div([
            dcc.Dropdown(
                id="project-dropdown",
                options=[
                    {"label": "All Projects", "value": "all"}
                ],
                multi=True,
                placeholder="Select Projects",
                style={"margin-bottom": "20px"}
            ),
            dcc.DatePickerRange(
                id="date-picker-range",
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
            value=["group"]
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
            ] + [
                html.Div(
                    [
                        html.Div(
                            style={"display": "inline-block", "width": "20px", "height": "20px",
                                   "backgroundColor": color, "margin-right": "10px"}
                        ),
                        html.Span(net_label, style={"margin-right": "20px"})
                    ],
                    style={"display": "flex", "align-items": "center", "margin-right": "20px"}
                ) for net_label, color in NET_COLORS.items()
            ],
            style={"margin-bottom": "20px", "display": "flex", "flex-wrap": "wrap"}
        ),
        dcc.Graph(id="timeline-graph")
    ])

    # Callback to update the project dropdown
    @dash_app.callback(
        Output("project-dropdown", "options"),
        Input("url", "href")
    )
    def update_project_dropdown(href):
        projects = db.session.query(Projects.project_id, Projects.project_name).all()
        return [{"label": name, "value": project_id} for project_id, name in projects]

    # Callback to update the graph
    @dash_app.callback(
        [Output("timeline-graph", "figure"),
         Output("date-picker-range", "start_date"),
         Output("date-picker-range", "end_date")],
        [Input("project-dropdown", "value"),
         Input("date-picker-range", "start_date"),
         Input("date-picker-range", "end_date"),
         Input("category-dropdown", "value"),
         Input("label-dropdown", "value"),
         Input("group-by-category", "value")]
    )
    def update_dashboard(project_ids, start_date, end_date, categories, labels, group_by_category):
        if not project_ids or "all" in project_ids:
            project_ids = [project.project_id for project in db.session.query(Projects.project_id).all()]

        # Query only items related to the selected projects
        items = db.session.query(Items, Projects.project_name).join(Projects).filter(Projects.project_id.in_(project_ids)).all()

        # Get min and max project dates
        project_dates = db.session.query(
            db.func.min(Projects.proj_start_date),
            db.func.max(Projects.proj_end_date)
        ).first()

        # Set default start and end dates if not provided
        if not start_date:
            start_date = project_dates[0] if project_dates else "2025-01-01"
        if not end_date:
            end_date = project_dates[1] if project_dates else "2026-12-31"

        if not items:
            return go.Figure(), start_date, end_date


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

        # Apply category filter if categories are selected
        if categories:
            filtered_df = df[df["Category"].isin(categories)]
        else:
            filtered_df = df

        # Group by category if the group-by-category option is selected
        if "group" in group_by_category:
            cost_df = filtered_df[filtered_df["Type"] == "cost"].groupby("Category").agg({
                "Amount": "sum",
                "Start Date": "min",
                "End Date": "max"
            }).reset_index()

            budget_df = filtered_df[filtered_df["Type"] == "budget"].groupby("Category").agg({
                "Amount": "sum",
                "Start Date": "min",
                "End Date": "max"
            }).reset_index()

            # Modify item names for grouped data
            cost_df["Item Name"] = cost_df["Category"] + " (Cost)"
            budget_df["Item Name"] = budget_df["Category"] + " (Budget)"
        else:
            cost_df = filtered_df[(filtered_df["Type"] == "cost") & ((filtered_df["Start Date"] <= end_date) & (filtered_df["End Date"] >= start_date))]
            budget_df = filtered_df[(filtered_df["Type"] == "budget") & ((filtered_df["Start Date"] <= end_date) & (filtered_df["End Date"] >= start_date))]

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
        # Fixed bar height and dynamic figure height calculation
        fixed_bar_height = 100  # Set a fixed height for each bar
        num_items = len(cost_df) + len(budget_df) + 1  # +1 for Net Position bar
        fig_height = max(400, num_items * fixed_bar_height)

        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            subplot_titles=("Cost Items", "Budget Items", "Net Position"),
            vertical_spacing=0.1  # Adjust spacing between subplots
        )
        # Filter by labels if provided
        if labels:
            df = df[df["Type"].isin(labels)]

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
                legendgroup=row["Category"],
                text=f"{row['Start Date'].strftime('%Y-%m-%d')} - {row['End Date'].strftime('%Y-%m-%d')}",
                textposition='inside'
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
                legendgroup=row["Category"],
                text=f"{row['Start Date'].strftime('%Y-%m-%d')} - {row['End Date'].strftime('%Y-%m-%d')}",
                textposition='inside'
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
            height=fig_height,  # Set dynamic figure height based on the number of items
            barmode="stack",
            xaxis_title="Amount",
            yaxis_title="Items",
            title="Project Costs, Budgets, and Net Position",
            bargap=0.2,
            font=dict(size=12),
            yaxis1=dict(
                tickmode='array',
                tickvals=list(range(len(cost_df))),
                automargin=True,
                dtick=1
            ),
            yaxis2=dict(
                tickmode='array',
                tickvals=list(range(len(budget_df))),
                automargin=True,
                dtick=1
            ),
            yaxis3=dict(
                tickmode='array',
                tickvals=[0],
                automargin=True,
                dtick=1
            )
        )

        # Only return project start and end dates if start_date or end_date is not provided
        if not start_date or not end_date:
            return fig, project_start_date, project_end_date

        # Otherwise, keep the manually selected date range
        return fig, no_update, no_update

    return dash_app
