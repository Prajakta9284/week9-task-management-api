from datetime import timedelta

from flask import request
from flask_restful import Resource

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from validation import get_json_data, validate_required_fields

from models import db, User

from flask_jwt_extended import get_jwt
from extensions import limiter


class Register(Resource):

    def post(self):

        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return {
                "message": "Username, email and password are required"
            }, 400

        existing_user = User.query.filter(
            (User.username == username) |
            (User.email == email)
        ).first()

        if existing_user:
            return {
                "message": "Username or email already exists"
            }, 409

        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, 201
        
class Login(Resource):

    def post(self):

        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {
                "message": "Email and password are required"
            }, 400

        user = User.query.filter_by(
            email=email
        ).first()

        if not user or not user.check_password(password):
            return {
                "message": "Invalid email or password"
            }, 401

        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=30)
        )

        refresh_token = create_refresh_token(
            identity=str(user.id)
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
        }, 200
        
class RefreshToken(Resource):

    @jwt_required(refresh=True)
    def post(self):

        user_id = get_jwt_identity()

        new_access_token = create_access_token(
            identity=str(user_id),
            expires_delta=timedelta(minutes=30)
        )

        return {
            "access_token": new_access_token
        }, 200
        
class Profile(Resource):

    @jwt_required()
    def get(self):

        user_id = get_jwt_identity()

        user = User.query.get(user_id)

        if not user:
            return {
                "message": "User not found"
            }, 404

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, 200
        
class ForgotPassword(Resource):

    def post(self):

        data = request.get_json()

        email = data.get("email")

        if not email:
            return {
                "message": "Email is required"
            }, 400

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:
            return {
                "message": "If the email exists, a reset link will be sent"
            }, 200

        reset_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(minutes=15),
            additional_claims={
                "type": "password_reset"
            }
        )

        

        return {
            "message": "Password reset token generated",
            "reset_token": reset_token
        }, 200
        

class ResetPassword(Resource):

    def post(self):

        data = request.get_json(silent=True) or {}

        reset_token = data.get("reset_token")
        new_password = data.get("new_password")

        if not reset_token:
            return {
                "message": "Password reset token is required"
            }, 400

        if not new_password:
            return {
                "message": "New password is required"
            }, 400

        if len(new_password) < 6:
            return {
                "message": "Password must be at least 6 characters"
            }, 400

        try:
            decoded_token = decode_token(reset_token)

            claims = decoded_token

            if claims.get("type") != "password_reset":
                return {
                    "message": "Invalid password reset token"
                }, 401

            user_id = claims.get("sub")

            if not user_id:
                return {
                    "message": "Invalid password reset token"
                }, 401

        except Exception:
            return {
                "message": "Invalid or expired password reset token"
            }, 401

        user = db.session.get(User, user_id)

        if not user:
            return {
                "message": "User not found"
            }, 404

        user.set_password(new_password)

        db.session.commit()

        return {
            "message": "Password reset successfully"
        }, 200
