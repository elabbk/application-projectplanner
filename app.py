import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_folder='static')
#app.config['SECRET_KEY'] = 'your-secure-random-secret-key'
#csrf = CSRFProtect(app)

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

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Views, Items, Projects


@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    views = Views.query.all()
    return render_template('index.html', views=views)

@app.route('/api/user_projects', methods=['GET'])
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

@app.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json
    username = data.get('username')  # Get the username from the request body
    try:
        # Create a new project object
        new_project = Projects(
            project_name=data['name'],
            status=data['status'],
            tag=data['tag'],
            start_date=datetime.strptime(data['startDate'], '%Y-%m-%d')
        )
        # Add the project to the database
        db.session.add(new_project)
        db.session.flush()  # Flush to get the project ID before committing

        # Create a new entry in the views table
        new_view = Views(
            user_id=username,
            project_id=new_project.project_id,
            Bookmark=True
        )
        db.session.add(new_view)

        # Commit the transaction
        db.session.commit()

        return jsonify({"message": "Project created successfully!", "project": data}), 201
    except Exception as e:
        db.session.rollback()  # Roll back the transaction in case of error
        return jsonify({"error": str(e)}), 400

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
    app.run()
