"""
Task endpoints:
  POST   /api/tasks               - create a task
  GET    /api/tasks               - list tasks (supports ?project_id= and ?status= filters)
  GET    /api/tasks/<id>          - get one task
  PUT    /api/tasks/<id>          - update task fields (title, priority, due_date, assignee)
  PATCH  /api/tasks/<id>/status   - update ONLY the status (todo / in-progress / done)
  DELETE /api/tasks/<id>          - delete a task
"""

from flask import Blueprint, request, jsonify
from app import store
from app.errors import ApiError
from app.validators import require_fields, validate_choice, VALID_TASK_STATUSES, VALID_PRIORITIES

tasks_bp = Blueprint("tasks", __name__)


def _serialize_task(task):
    return {
        "id": task["id"],
        "title": task["title"],
        "project_id": task["project_id"],
        "assignee_id": task["assignee_id"],
        "status": task["status"],
        "priority": task["priority"],
        "due_date": task["due_date"],
    }


@tasks_bp.route("", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["title", "project_id"])

    project_id = data["project_id"]
    if project_id not in store.projects:
        raise ApiError("project_id does not match any existing project.", 400)

    assignee_id = data.get("assignee_id")
    if assignee_id is not None and assignee_id not in store.users:
        raise ApiError("assignee_id does not match any existing user.", 400)

    priority = data.get("priority", "medium")
    validate_choice(priority, VALID_PRIORITIES, "priority")

    task_id = store.next_task_id()
    task = {
        "id": task_id,
        "title": data["title"].strip(),
        "project_id": project_id,
        "assignee_id": assignee_id,
        "status": "todo",  # every new task always starts as "todo"
        "priority": priority,
        "due_date": data.get("due_date"),
    }
    store.tasks[task_id] = task

    return jsonify(_serialize_task(task)), 201


@tasks_bp.route("", methods=["GET"])
def list_tasks():
    result = list(store.tasks.values())

    # Optional query-string filters, e.g. GET /api/tasks?status=done
    status_filter = request.args.get("status")
    if status_filter:
        result = [t for t in result if t["status"] == status_filter]

    project_filter = request.args.get("project_id", type=int)
    if project_filter is not None:
        result = [t for t in result if t["project_id"] == project_filter]

    return jsonify([_serialize_task(t) for t in result]), 200


@tasks_bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = store.tasks.get(task_id)
    if not task:
        raise ApiError("Task not found.", 404)
    return jsonify(_serialize_task(task)), 200


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = store.tasks.get(task_id)
    if not task:
        raise ApiError("Task not found.", 404)

    data = request.get_json(silent=True) or {}

    if "title" in data:
        if not str(data["title"]).strip():
            raise ApiError("title cannot be empty.", 400)
        task["title"] = data["title"].strip()

    if "priority" in data:
        validate_choice(data["priority"], VALID_PRIORITIES, "priority")
        task["priority"] = data["priority"]

    if "due_date" in data:
        task["due_date"] = data["due_date"]

    if "assignee_id" in data:
        assignee_id = data["assignee_id"]
        if assignee_id is not None and assignee_id not in store.users:
            raise ApiError("assignee_id does not match any existing user.", 400)
        task["assignee_id"] = assignee_id

    return jsonify(_serialize_task(task)), 200


@tasks_bp.route("/<int:task_id>/status", methods=["PATCH"])
def update_task_status(task_id):
    """
    A dedicated endpoint just for changing status. Why separate
    from the general PUT above? Because status changes are the
    MOST common action in a task tracker (dragging a card between
    columns), and the task guide explicitly calls out "Task status
    management" as its own requirement — a small, focused endpoint
    is easier for a frontend to call correctly and safely.
    """
    task = store.tasks.get(task_id)
    if not task:
        raise ApiError("Task not found.", 404)

    data = request.get_json(silent=True) or {}
    require_fields(data, ["status"])
    validate_choice(data["status"], VALID_TASK_STATUSES, "status")

    task["status"] = data["status"]
    return jsonify(_serialize_task(task)), 200


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    if task_id not in store.tasks:
        raise ApiError("Task not found.", 404)
    del store.tasks[task_id]
    return "", 204
