from flask import Flask, jsonify, request, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- In-memory Data Store ---

users = [
    {"id": 1, "name": "Alice", "age": 25},
    {"id": 2, "name": "Bob", "age": 30},
]

# 3.1.3 Initial Data for Tasks
tasks = [
    {"id": 1, "title": "Learn REST", "description": "Study REST principles", "user_id": 1, "completed": True},
    {"id": 2, "title": "Build API", "description": "Complete the assignment", "user_id": 2, "completed": False},
]

# --- Root & Health Routes ---

@app.route('/')
def index():
    return "Welcome to Flask REST API Demo! Access /users or /tasks to see data."

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# --- User Endpoints ---

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if user is None:
        abort(404)
    return jsonify(user), 200

# 3.2 Part 2: Add a User-Tasks Endpoint
@app.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    # Check if user exists first
    user_exists = any(u['id'] == user_id for u in users)
    if not user_exists:
        abort(404) # Return 404 if user doesn't exist
    
    # Filter tasks for this user
    user_specific_tasks = [t for t in tasks if t['user_id'] == user_id]
    return jsonify(user_specific_tasks), 200

# --- Task Endpoints (Part 1) ---

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks), 200

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        abort(404)
    return jsonify(task), 200

@app.route('/tasks', methods=['POST'])
def create_task():
    # 3.1.2 Validation: Invalid JSON
    if not request.json:
        abort(400)
    
    # 3.1.2 Validation: Missing required fields (title or user_id)
    if 'title' not in request.json or 'user_id' not in request.json:
        abort(400)
        
    # 3.1.2 Validation: Invalid user_id (user doesn't exist)
    user_id = request.json['user_id']
    if not any(u['id'] == user_id for u in users):
        return jsonify({"error": "User ID does not exist"}), 400

    # 3.1.1 Task Data Structure
    new_task = {
        'id': tasks[-1]['id'] + 1 if tasks else 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""), # Default to ""
        'user_id': user_id,
        'completed': request.json.get('completed', False) # Default to false
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        abort(404)
    if not request.json:
        abort(400)

    # If updating user_id, ensure the new user actually exists
    if 'user_id' in request.json:
        if not any(u['id'] == request.json['user_id'] for u in users):
            abort(400)

    task['title'] = request.json.get('title', task['title'])
    task['description'] = request.json.get('description', task['description'])
    task['user_id'] = request.json.get('user_id', task['user_id'])
    task['completed'] = request.json.get('completed', task['completed'])
    
    return jsonify(task), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    # 3.1.2: Check if exists to return 404 or just filter
    task_exists = any(t['id'] == task_id for t in tasks)
    if not task_exists:
        abort(404)
        
    tasks = [t for t in tasks if t['id'] != task_id]
    return '', 204

if __name__ == '__main__':
    # Running on port 8000 as per original script
    app.run(debug=True, host='0.0.0.0', port=8000)