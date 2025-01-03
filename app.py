import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime

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

# The import must be done after db initialization due to circular import issue
from models import Views, Items, Projects

# Layout
app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.Button("Add Item", id="add-item-btn", color="primary", className="me-2"),
        ],
        brand="Project Dashboard",
        brand_href="/",
        color="dark",
        dark=True,
    ),
    dcc.Graph(id='timeline-graph'),
    dcc.Checklist(
        id='category-checklist',
        options=[
            {'label': 'Group by Category', 'value': 'group_by_category'},
            {'label': 'Split Budget Monthly', 'value': 'split_monthly'}
        ],
        value=[]
    ),
    html.Div(id='net-position', style={'margin-top': '20px'}),
])

@server.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    views = Views.query.all()
    return render_template('index.html', views=views)

@server.route('/api/user_projects', methods=['GET'])
def get_user_projects():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        # Query projects associated with the user via the views table
        user_projects = db.session.query(Projects).join(Views).filter(Views.user_id == username).all()

        # Serialize the project data
        projects_data = [
            {"id": project.project_id, "name": project.project_name}
            for project in user_projects
        ]

        return jsonify({"projects": projects_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@server.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    username = data.get('username')  # Get the username from the request

    try:
        # Set default values for optional fields if not provided
        project_status = data.get('status', 'Pending')
        project_tag = data.get('tag', '')

        # Create a new project object
        new_project = Projects(
            project_name=data['name'],
            status=project_status,
            tag=project_tag,
            proj_start_date=datetime.strptime(data['startDate'], '%Y-%m-%d'),
            proj_end_date=datetime.strptime(data.get('endDate', data['startDate']), '%Y-%m-%d')
        )
        db.session.add(new_project)
        db.session.flush()  # Get the project ID before committing

        # Create a new entry in the views table
        new_view = Views(
            user_id=username,
            project_id=new_project.project_id,
            bookmark=True,
            read=True,
            write=True,
            delete=False,
            archive=False
        )
        db.session.add(new_view)
        db.session.commit()

        return jsonify({"message": "Project created successfully!", "project": data}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@server.route('/api/project_items', methods=['GET'])
def get_project_items():
    project_id = request.args.get('projectId')
    if not project_id:
        return jsonify({"error": "Project ID is required"}), 400

    items = Items.query.filter_by(project_id=project_id).all()
    items_data = [
        {
            "id": item.item_id,
            "name": item.item_name,
            "type": item.type,
            "amount": item.amount,
            "category": item.category,
            "start_date": item.item_start_date.strftime('%Y-%m-%d'),
            "end_date": item.item_end_date.strftime('%Y-%m-%d'),
        }
        for item in items
    ]
    return jsonify({"items": items_data}), 200

# 2. Add a new item
@server.route('/api/add_item', methods=['POST'])
def add_item():
    data = request.json
    try:
        new_item = Items(
            project_id=data['projectId'],
            item_name=data['name'],
            type=data['type'],
            amount=data['amount'],
            category=data['category'],
            item_start_date=datetime.strptime(data['startDate'], '%Y-%m-%d'),
            item_end_date=datetime.strptime(data['endDate'], '%Y-%m-%d')
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Item added successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# 3. Update an existing item
@server.route('/api/update_item/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    item = Items.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    try:
        item.item_name = data.get('name', item.item_name)
        item.type = data.get('type', item.type)
        item.amount = data.get('amount', item.amount)
        item.category = data.get('category', item.category)
        item.item_start_date = datetime.strptime(data['startDate'], '%Y-%m-%d')
        item.item_end_date = datetime.strptime(data['endDate'], '%Y-%m-%d')
        db.session.commit()
        return jsonify({"message": "Item updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# 4. Delete an item
@server.route('/api/delete_item/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Items.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# 5. Compute net position
@server.route('/api/net_position', methods=['GET'])
def get_net_position():
    project_id = request.args.get('projectId')
    split_monthly = request.args.get('splitMonthly') == 'true'

    items = Items.query.filter_by(project_id=project_id).all()
    total_budget = sum(item.amount for item in items if item.type == 'budget')
    total_cost = sum(item.amount for item in items if item.type == 'cost')

    if split_monthly:
        # Logic to calculate monthly split
        net_position = total_budget - total_cost  # Example logic
    else:
        net_position = total_budget - total_cost

    return jsonify({"net_position": net_position}), 200


"""
@app.route('/<int:id>', methods=['GET'])
def details(id):
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant == id)
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
    except (KeyError):
        # Redisplay the question voting form.
        return render_template('add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        db.session.add(restaurant)
        db.session.commit()

        return redirect(url_for('details', id=restaurant.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        review_text = request.values.get('review_text')
    except (KeyError):
        #Redisplay the question voting form.
        return render_template('add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        review = Review()
        review.restaurant = id
        review.review_date = datetime.now()
        review.user_name = user_name
        review.rating = int(rating)
        review.review_text = review_text
        db.session.add(review)
        db.session.commit()

    return redirect(url_for('details', id=id))

@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = Review.query.where(Review.restaurant == id)

        ratings = []
        review_count = 0
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)
"""

if __name__ == '__main__':
    server.run(debug=True)
