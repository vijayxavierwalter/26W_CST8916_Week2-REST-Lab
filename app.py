# Import necessary modules from Flask
# Flask: the core framework for the web app
# jsonify: to convert Python dictionaries to JSON responses
# request: to access incoming request data (e.g., POST data)
# abort: to handle errors and send error status codes
# Import necessary modules from Flask
from flask import Flask, jsonify, request, abort
from flask_cors import CORS  # Enable Cross-Origin Resource Sharing for client apps

# Initialize the Flask app
app = Flask(__name__)

# Enable CORS so the HTML client can connect from a browser
CORS(app)

# ----------------------------
# In-memory "database" of users
# ----------------------------
users = [
    {"id": 1, "name": "Alice", "age": 25},
    {"id": 2, "name": "Bob", "age": 30},
]

# ----------------------------
# In-memory "database" of tasks (Required initial data)
# ----------------------------
tasks = [
    {"id": 1, "title": "Learn REST", "description": "Study REST principles", "user_id": 1, "completed": True},
    {"id": 2, "title": "Build API", "description": "Complete the assignment", "user_id": 2, "completed": False},
]

# ----------------------------
# Helper functions
# ----------------------------
def user_exists(user_id: int) -> bool:
    return any(u["id"] == user_id for u in users)

def find_task(task_id: int):
    return next((t for t in tasks if t["id"] == task_id), None)

def get_next_task_id() -> int:
    return max((t["id"] for t in tasks), default=0) + 1


# ----------------------------
# Basic routes
# ----------------------------
@app.route('/')
def index():
    return "Welcome to Flask REST API Demo! Try accessing /users to see all users."

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


# ----------------------------
# USERS RESOURCE (existing)
# ----------------------------
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if user is None:
        abort(404)
    return jsonify(user), 200

@app.route('/users', methods=['POST'])
def create_user():
    if not request.json or 'name' not in request.json:
        abort(400)

    new_user = {
        'id': users[-1]['id'] + 1 if users else 1,
        'name': request.json['name'],
        'age': request.json.get('age', 0)
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if user is None:
        abort(404)

    if not request.json:
        abort(400)

    user['name'] = request.json.get('name', user['name'])
    user['age'] = request.json.get('age', user['age'])
    return jsonify(user), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    users = [user for user in users if user['id'] != user_id]
    return '', 204


# ----------------------------
# TASKS RESOURCE (Part 1)
# ----------------------------
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks), 200

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task), 200

@app.route('/tasks', methods=['POST'])
def create_task():
    # Invalid JSON must return 400
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON in request body"}), 400

    title = data.get("title")
    user_id = data.get("user_id")

    # Missing required fields -> 400
    if title is None or not str(title).strip():
        return jsonify({"error": "Missing required field: title"}), 400
    if user_id is None:
        return jsonify({"error": "Missing required field: user_id"}), 400

    # user_id must exist -> 400
    if not isinstance(user_id, int):
        return jsonify({"error": "user_id must be an integer"}), 400
    if not user_exists(user_id):
        return jsonify({"error": "Invalid user_id (user doesn't exist)"}), 400

    new_task = {
        "id": get_next_task_id(),
        "title": str(title).strip(),
        "description": str(data.get("description", "")),
        "user_id": user_id,
        "completed": bool(data.get("completed", False)),
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    # Invalid JSON must return 400
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON in request body"}), 400

    # Update fields only if provided
    if "title" in data:
        if not str(data["title"]).strip():
            return jsonify({"error": "title cannot be empty"}), 400
        task["title"] = str(data["title"]).strip()

    if "description" in data:
        task["description"] = str(data["description"])

    if "user_id" in data:
        if not isinstance(data["user_id"], int):
            return jsonify({"error": "user_id must be an integer"}), 400
        if not user_exists(data["user_id"]):
            return jsonify({"error": "Invalid user_id (user doesn't exist)"}), 400
        task["user_id"] = data["user_id"]

    if "completed" in data:
        task["completed"] = bool(data["completed"])

    return jsonify(task), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = find_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404

    tasks.remove(task)
    return '', 204


# ----------------------------
# USER-TASKS ENDPOINT (Part 2)
# ----------------------------
@app.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_tasks_for_user(user_id):
    # Return 404 if user does not exist
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404

    # Return [] if user exists but has no tasks
    user_tasks = [t for t in tasks if t["user_id"] == user_id]
    return jsonify(user_tasks), 200


# Entry point for running the Flask app
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
