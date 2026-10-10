
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, send_from_directory
from flask_restful import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from config import Config
from extensions import limiter

# Import your existing resource classes.
from routes.auth import (
    Register,
    Login,
    RefreshToken,
    Profile,
    ForgotPassword,
    ResetPassword,
)

from routes.tasks import TaskList, TaskDetail

# Import your existing database object.
# If your project defines db in another module,
# change this import to match that module.
from extensions import db


# --------------------------------------------------
# Application setup
# --------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

jwt = JWTManager(app)
mail = Mail(app)
migrate = Migrate(app, db)
api = Api(app)

# Allow requests from a local frontend running on port 3000.
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": ["http://localhost:3000"]
        }
    }
)

# Enable rate limiting
limiter.init_app(app)


# --------------------------------------------------
# Logging
# --------------------------------------------------

os.makedirs("logs", exist_ok=True)

file_handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=1024 * 1024,
    backupCount=3
)

file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.ERROR)


# --------------------------------------------------
# Swagger API documentation
# --------------------------------------------------

SWAGGER_URL = "/swagger"
API_URL = "/openapi.yaml"

swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Task Management REST API"
    }
)

app.register_blueprint(swagger_blueprint)


@app.route("/openapi.yaml")
def openapi_spec():
    return send_from_directory(
        app.root_path,
        "openapi.yaml",
        mimetype="application/yaml"
    )


# --------------------------------------------------
# Home endpoint
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "message": "Task Management REST API is running",
        "version": "1.0",
        "documentation": "/swagger"
    }), 200


# --------------------------------------------------
# Authentication endpoints
# --------------------------------------------------

api.add_resource(
    Register,
    "/api/auth/register"
)

api.add_resource(
    Login,
    "/api/auth/login"
)

api.add_resource(
    RefreshToken,
    "/api/auth/refresh"
)

api.add_resource(
    Profile,
    "/api/auth/profile"
)

api.add_resource(
    ForgotPassword,
    "/api/auth/forgot-password"
)

api.add_resource(
    ResetPassword,
    "/api/auth/reset-password"
)


# --------------------------------------------------
# Task endpoints - original routes
# --------------------------------------------------

api.add_resource(
    TaskList,
    "/api/tasks"
)

api.add_resource(
    TaskDetail,
    "/api/tasks/<int:task_id>"
)



# --------------------------------------------------
# Task endpoints - version 1
# --------------------------------------------------

api.add_resource(
    TaskList,
    "/api/v1/tasks",
    endpoint="tasklist_v1"
)

api.add_resource(
    TaskDetail,
    "/api/v1/tasks/<int:task_id>",
    endpoint="taskdetail_v1"
)

# --------------------------------------------------
# Error handlers
# --------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    app.logger.error("404 Not Found: %s", error)

    return jsonify({
        "success": False,
        "status": 404,
        "error": "Not Found",
        "message": "The requested resource was not found."
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(
        "500 Internal Server Error: %s",
        error,
        exc_info=True
    )

    return jsonify({
        "success": False,
        "status": 500,
        "error": "Internal Server Error",
        "message": "An unexpected server error occurred."
    }), 500


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
