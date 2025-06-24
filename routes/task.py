from flask import Blueprint, jsonify, request
from utils.db import execute_query, get_all_tasks

task_bp = Blueprint('tasks', __name__)

@task_bp.route("/add-task", methods=["POST"])
def add_task():
    data = request.json
    execute_query(
        "INSERT IGNORE INTO scraping_tasks (task_name, domain, status) VALUES (%s, %s, %s)",
        (data["task_name"], data["domain"], "Pending")
    )
    return jsonify({"message": "Task added successfully."})

@task_bp.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(get_all_tasks())
