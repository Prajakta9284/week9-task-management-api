
# 1. Project Overview

This REST API allows users to register, log in, and manage their tasks securely using JWT authentication.

**Base URL:** `http://127.0.0.1:5000`

# 2. User Registration

**Endpoint:** `POST /api/auth/register`

Request body:
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "Test@123"
}

# 3. User Login

**Endpoint:** `POST /api/auth/login`

Request body:
{
  "email": "test@example.com",
  "password": "Test@123"
}

Copy the `access_token` from the response. Use your actual registered credentials.

# 4. Get User Profile

**Endpoint:** `GET /api/auth/profile`

In Postman, select **Authorization → Bearer Token** and paste your access token.

# 5. Create a Task

**Endpoint:** `POST /api/tasks`

Authorization: Bearer Token

Request body:
{
  "title": "Complete Flask API",
  "description": "Finish API documentation",
  "status": "pending",
  "priority": "high"
}

# 6. Get All Tasks

**Endpoint:** `GET /api/tasks`

Authorization: Bearer Token

# 7. Update a Task

**Endpoint:** `PUT /api/tasks/3`

Replace `3` with an existing task ID belonging to your account.

Request body:
{
  "title": "Updated Flask API",
  "description": "Documentation completed",
  "status": "in_progress",
  "priority": "high"
}

# 8. Delete a Task

**Endpoint:** `DELETE /api/tasks/3`

Replace `3` with the task ID you want to delete.

# 9. Refresh Access Token

**Endpoint:** `POST /api/auth/refresh`

Use the **refresh token** as a Bearer Token for this request. Do not use the access token here.

# 10. API Documentation

Swagger UI: `http://127.0.0.1:5000/swagger`

OpenAPI specification: `http://127.0.0.1:5000/openapi.yaml`

# 11. Important Notes

- Register a user before logging in.
- Use the access token for protected endpoints.
- Access tokens expire; log in again or refresh the token.
- Only use task IDs that exist and belong to your account.
- Never share passwords, access tokens, or refresh tokens.
