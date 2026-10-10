from datetime import datetime

from flask import request
from flask_restful import Resource

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from models import db, Task


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": (
            task.due_date.isoformat()
            if task.due_date
            else None
        ),
        "created_at": (
            task.created_at.isoformat()
            if task.created_at
            else None
        ),
        "updated_at": (
            task.updated_at.isoformat()
            if task.updated_at
            else None
        ),
        "user_id": task.user_id
    }


# --------------------------------------------------
# GET /api/tasks
# POST /api/tasks
# --------------------------------------------------

class TaskList(Resource):

    @jwt_required()
    def get(self):

        user_id = get_jwt_identity()

        # Pagination parameters
        page = request.args.get(
            "page",
            default=1,
            type=int
        )

        per_page = request.args.get(
            "per_page",
            default=10,
            type=int
        )

        # Prevent very large requests
        if per_page > 100:
            per_page = 100

        if page < 1:
            page = 1

        # Get only the logged-in user's tasks
        pagination = Task.query.filter_by(
            user_id=user_id
        ).order_by(
            Task.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        tasks = [
            task_to_dict(task)
            for task in pagination.items
        ]

        return {
            "tasks": tasks,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_previous": pagination.has_prev
            }
        }, 200

    # --------------------------------------------------
    # POST /api/tasks
    # --------------------------------------------------

    @jwt_required()
    def post(self):

        user_id = get_jwt_identity()

        data = request.get_json()

        if not data:
            return {
                "message": "Request body is required"
            }, 400

        title = data.get("title")
        description = data.get("description")
        status = data.get("status", "pending")
        priority = data.get("priority", "medium")
        due_date = data.get("due_date")

        # Validate title
        if not title:
            return {
                "message": "Title is required"
            }, 400

        # Validate status
        allowed_status = [
            "pending",
            "in_progress",
            "completed"
        ]

        if status not in allowed_status:
            return {
                "message": (
                    "Status must be pending, "
                    "in_progress or completed"
                )
            }, 400

        # Validate priority
        allowed_priority = [
            "low",
            "medium",
            "high"
        ]

        if priority not in allowed_priority:
            return {
                "message": (
                    "Priority must be low, "
                    "medium or high"
                )
            }, 400

        # Convert due date
        parsed_due_date = None

        if due_date:
            try:
                parsed_due_date = datetime.strptime(
                    due_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                return {
                    "message": "due_date must be YYYY-MM-DD"
                }, 400

        # Create task
        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=parsed_due_date,
            user_id=user_id
        )

        db.session.add(task)
        db.session.commit()

        return {
            "message": "Task created successfully",
            "task": task_to_dict(task)
        }, 201


# --------------------------------------------------
# GET /api/tasks/<id>
# PUT /api/tasks/<id>
# PATCH /api/tasks/<id>
# DELETE /api/tasks/<id>
# --------------------------------------------------

class TaskDetail(Resource):

    # --------------------------------------------------
    # GET SINGLE TASK
    # --------------------------------------------------

    @jwt_required()
    def get(self, task_id):

        user_id = get_jwt_identity()

        task = Task.query.filter_by(
            id=task_id,
            user_id=user_id
        ).first()

        if not task:
            return {
                "message": "Task not found"
            }, 404

        return {
            "task": task_to_dict(task)
        }, 200

    # --------------------------------------------------
    # PUT TASK
    # --------------------------------------------------

    @jwt_required()
    def put(self, task_id):

        user_id = get_jwt_identity()

        task = Task.query.filter_by(
            id=task_id,
            user_id=user_id
        ).first()

        if not task:
            return {
                "message": "Task not found"
            }, 404

        data = request.get_json()

        if not data:
            return {
                "message": "Request body is required"
            }, 400

        title = data.get("title")
        description = data.get("description")
        status = data.get("status")
        priority = data.get("priority")
        due_date = data.get("due_date")

        if not title:
            return {
                "message": "Title is required"
            }, 400

        allowed_status = [
            "pending",
            "in_progress",
            "completed"
        ]

        if status not in allowed_status:
            return {
                "message": (
                    "Invalid status"
                )
            }, 400

        allowed_priority = [
            "low",
            "medium",
            "high"
        ]

        if priority not in allowed_priority:
            return {
                "message": (
                    "Invalid priority"
                )
            }, 400

        parsed_due_date = None

        if due_date:
            try:
                parsed_due_date = datetime.strptime(
                    due_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                return {
                    "message": "due_date must be YYYY-MM-DD"
                }, 400

        task.title = title
        task.description = description
        task.status = status
        task.priority = priority
        task.due_date = parsed_due_date

        db.session.commit()

        return {
            "message": "Task updated successfully",
            "task": task_to_dict(task)
        }, 200

    # --------------------------------------------------
    # PATCH TASK
    # --------------------------------------------------

    @jwt_required()
    def patch(self, task_id):

        user_id = get_jwt_identity()

        task = Task.query.filter_by(
            id=task_id,
            user_id=user_id
        ).first()

        if not task:
            return {
                "message": "Task not found"
            }, 404

        data = request.get_json()

        if not data:
            return {
                "message": "Request body is required"
            }, 400

        # Update only fields that were provided

        if "title" in data:

            if not data["title"]:
                return {
                    "message": "Title cannot be empty"
                }, 400

            task.title = data["title"]

        if "description" in data:
            task.description = data["description"]

        if "status" in data:

            allowed_status = [
                "pending",
                "in_progress",
                "completed"
            ]

            if data["status"] not in allowed_status:
                return {
                    "message": "Invalid status"
                }, 400

            task.status = data["status"]

        if "priority" in data:

            allowed_priority = [
                "low",
                "medium",
                "high"
            ]

            if data["priority"] not in allowed_priority:
                return {
                    "message": "Invalid priority"
                }, 400

            task.priority = data["priority"]

        if "due_date" in data:

            if data["due_date"]:

                try:
                    task.due_date = datetime.strptime(
                        data["due_date"],
                        "%Y-%m-%d"
                    ).date()

                except ValueError:
                    return {
                        "message": (
                            "due_date must be YYYY-MM-DD"
                        )
                    }, 400

            else:
                task.due_date = None

        db.session.commit()

        return {
            "message": "Task updated successfully",
            "task": task_to_dict(task)
        }, 200

    # --------------------------------------------------
    # DELETE TASK
    # --------------------------------------------------

    @jwt_required()
    def delete(self, task_id):

        user_id = get_jwt_identity()

        task = Task.query.filter_by(
            id=task_id,
            user_id=user_id
        ).first()

        if not task:
            return {
                "message": "Task not found"
            }, 404

        db.session.delete(task)
        db.session.commit()

        return {
            "message": "Task deleted successfully"
        }, 200