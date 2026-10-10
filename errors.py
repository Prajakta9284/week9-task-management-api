
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):

    # Configure error logging
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    def error_response(status_code, error, message):
        return jsonify({
            "success": False,
            "status": status_code,
            "error": error,
            "message": message
        }), status_code

    @app.errorhandler(400)
    def bad_request(error):
        return error_response(
            400, "Bad Request",
            "The request contains invalid or missing data."
        )

    @app.errorhandler(401)
    def unauthorized(error):
        return error_response(
            401, "Unauthorized",
            "Authentication is required or the credentials are invalid."
        )

    @app.errorhandler(403)
    def forbidden(error):
        return error_response(
            403, "Forbidden",
            "You do not have permission to perform this action."
        )

    @app.errorhandler(404)
    def not_found(error):
        app.logger.error("404 Not Found: %s", error)
        
        return jsonify({
            "success": False,
            "status": 404,
            "error": "Not Found",
            "message": "The requested resource was not found."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response(
            405, "Method Not Allowed",
            "This HTTP method is not supported for this endpoint."
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(
            "Internal server error: %s", error,
            exc_info=(type(error), error, error.__traceback__)
        )
        return error_response(
            500, "Internal Server Error",
            "An unexpected server error occurred."
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        # Preserve the actual HTTP status code.
        return error_response(
            error.code or 500,
            error.name,
            error.description
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        app.logger.exception("Unhandled application exception")
        return error_response(
            500, "Internal Server Error",
            "An unexpected server error occurred."
        )
