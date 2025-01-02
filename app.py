import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the UserViews model for the PostgreSQL table
class UserViews(db.Model):
    __tablename__ = 'user_views'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    view_name = db.Column(db.String(100), nullable=False)

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

#@app.route('/favicon.ico')
#def favicon():
#    return send_from_directory(os.path.join(app.root_path, 'static'),
#                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/views', methods=['GET'])
def get_views():
    user_id = request.args.get('userId')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    views = UserViews.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": v.id, "view_name": v.view_name} for v in views])

@app.route('/api/views', methods=['POST'])
def add_view():
    data = request.json
    user_id = data.get('userId')
    view_name = data.get('viewName')
    if not user_id or not view_name:
        return jsonify({"error": "User ID and view name are required"}), 400
    new_view = UserViews(user_id=user_id, view_name=view_name)
    db.session.add(new_view)
    db.session.commit()
    return jsonify({"id": new_view.id, "view_name": new_view.view_name})



if __name__ == '__main__':
   app.run()
