"""
User management endpoints:
  POST   /api/users        - create a user
  GET    /api/users        - list all users
  GET    /api/users/<id>   - get one user
  DELETE /api/users/<id>   - delete a user
"""

from flask import Blueprint, request, jsonify
from app import store
from app.errors import ApiError
from app.validators import require_fields, validate_email

# A Blueprint groups related routes together. We register this
# whole group under the prefix "/api/users" in app/__init__.py.
users_bp = Blueprint("users", __name__)


def _serialize_user(user):
    """Converts our internal dict into the shape we send to clients."""
    return {"id": user["id"], "name": user["name"], "email": user["email"]}


@users_bp.route("", methods=["POST"])
def create_user():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name", "email"])
    validate_email(data["email"])

    # Prevent duplicate emails — a common, realistic validation rule
    if any(u["email"] == data["email"] for u in store.users.values()):
        raise ApiError("A user with this email already exists.", 409)

    user_id = store.next_user_id()
    user = {"id": user_id, "name": data["name"].strip(), "email": data["email"].strip()}
    store.users[user_id] = user

    return jsonify(_serialize_user(user)), 201


@users_bp.route("", methods=["GET"])
def list_users():
    return jsonify([_serialize_user(u) for u in store.users.values()]), 200


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = store.users.get(user_id)
    if not user:
        raise ApiError("User not found.", 404)
    return jsonify(_serialize_user(user)), 200


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if user_id not in store.users:
        raise ApiError("User not found.", 404)
    del store.users[user_id]
    return "", 204
