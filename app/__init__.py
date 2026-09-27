"""
The "application factory" pattern: instead of creating the Flask
app as a bare global variable, we wrap creation in a function.
This is the professional standard because it lets us create
multiple instances of the app with different configs (e.g. one
for running the real server, a separate one for automated tests)
without them interfering with each other.
"""

from flask import Flask, jsonify
from app.config import Config
from app.errors import ApiError


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---- Register route groups (blueprints) ----
    from app.routes.users import users_bp
    from app.routes.projects import projects_bp
    from app.routes.tasks import tasks_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")

    # ---- Centralized error handling ----
    # This ONE handler catches every ApiError raised ANYWHERE in
    # the app (any route) and turns it into a consistent JSON
    # response. This is what "centralized error handling" means.
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify(error.to_dict()), error.status_code

    # Catch-all handlers for errors Flask raises itself, so the
    # API always responds with JSON — never Flask's default HTML
    # error page.
    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({"error": "Method not allowed on this endpoint."}), 405

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({"error": "Internal server error."}), 500

    # ---- A simple root route so visiting the base URL isn't a dead end ----
    @app.route("/")
    def index():
        return jsonify(
            {
                "service": "Users, Projects & Tasks API",
                "status": "running",
                "docs": "See README.md for all endpoints.",
            }
        )

    return app
