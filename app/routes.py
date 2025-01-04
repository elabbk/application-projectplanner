from flask import Blueprint, render_template, request, jsonify
from .models import Projects, Views, Items
from datetime import datetime
from .db import db


# Define the blueprint for the main routes
main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
@main.route('/overview')
def overview():
    print('Request for index page received')
    views = Views.query.all()

    return render_template('index.html', title="Overview")

@main.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Projects.query.get_or_404(project_id)
    items = Items.query.filter_by(project_id=project_id).all()
    return render_template('project.html', title=project.project_name, project=project, items=items)


@main.route('/api/user_projects', methods=['GET'])
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

@main.route('/api/projects', methods=['POST'])
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

@main.route('/api/project_items', methods=['GET'])
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
@main.route('/api/add_item', methods=['POST'])
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
@main.route('/api/update_item/<int:item_id>', methods=['PUT'])
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
@main.route('/api/delete_item/<int:item_id>', methods=['DELETE'])
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
@main.route('/api/net_position', methods=['GET'])
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
