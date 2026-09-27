"""
Project endpoints:
  POST   /api/projects        - create a project
  GET    /api/projects        - list all projects
  GET    /api/projects/<id>   - get one project (with its tasks)
"""

from flask import Blueprint, request, jsonify
from app import store
from app.errors import ApiError
from app.validators import require_fields

projects_bp = Blueprint("projects", __name__)


def _serialize_project(project):
    return {
        "id": project["id"],
        "name": project["name"],
        "description": project["description"],
        "owner_id": project["owner_id"],
    }


@projects_bp.route("", methods=["POST"])
def create_project():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name"])

    owner_id = data.get("owner_id")
    if owner_id is not None and owner_id not in store.users:
        raise ApiError("owner_id does not match any existing user.", 400)

    project_id = store.next_project_id()
    project = {
        "id": project_id,
        "name": data["name"].strip(),
        "description": data.get("description", "").strip(),
        "owner_id": owner_id,
    }
    store.projects[project_id] = project

    return jsonify(_serialize_project(project)), 201


@projects_bp.route("", methods=["GET"])
def list_projects():
    return jsonify([_serialize_project(p) for p in store.projects.values()]), 200


@projects_bp.route("/<int:project_id>", methods=["GET"])
def get_project(project_id):
    project = store.projects.get(project_id)
    if not project:
        raise ApiError("Project not found.", 404)

    project_tasks = [
        t for t in store.tasks.values() if t["project_id"] == project_id
    ]

    result = _serialize_project(project)
    result["task_count"] = len(project_tasks)
    result["tasks_done"] = sum(1 for t in project_tasks if t["status"] == "done")
    return jsonify(result), 200
