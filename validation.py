
from flask import request


def get_json_data():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None, ({
            "success": False,
            "status": 400,
            "error": "Bad Request",
            "message": "Request body must contain valid JSON."
        }, 400)

    return data, None


def validate_required_fields(data, fields):
    missing_fields = [
        field for field in fields
        if not isinstance(data.get(field), str)
        or not data[field].strip()
    ]

    if missing_fields:
        return {
            "success": False,
            "status": 400,
            "error": "Validation Error",
            "message": "Required fields are missing or empty.",
            "fields": missing_fields
        }, 400

    return None
