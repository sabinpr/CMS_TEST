# 🧑‍💼 User Management & Authentication API

Comprehensive API module for handling **user registration, authentication (JWT)**, and **password management** in the Django REST Framework–based CMS backend.

---

## 🔐 Authentication Endpoints

### 1. **Login**

**URL:** `/api/auth/login/`  
**Method:** `POST`  
**Description:** Authenticates a user and returns a JWT access and refresh token.

#### Request Body:

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

#### Response Body:

```json
{
  "refresh": "your_refresh_token",
  "access": "your_access_token"
}
```

### 2. **Refresh Token**

**URL:** `/api/auth/refresh/`  
**Method:** `POST`  
**Description:** Returns a new access token using the refresh token.

#### Request Body:

```json
{
  "refresh": "your_refresh_token"
}
```

#### Response Body:

```json
{
  "access": "new_access_token"
}
```

### 3. **Logout (Blacklist Token)**

**URL:** `/api/auth/logout/`  
**Method:** `POST`  
**Description:** Blacklists the refresh token, effectively logging out the user.

#### Request Body:

```json
{
  "refresh": "your_refresh_token"
}
```

#### Response Body:

```json
{
  "detail": "Token blacklisted"
}
```

## 👤 User Management Endpoints

### 4. **List / Create Users**

**URL:** `/api/users/`  
**Method:**

- `GET`: List all users
- `POST`: Create a new user (Admin only)

#### Example Request (POST):

```json
{
  "full_name": "sabin prajapati",
  "email": "sabinprajapati1@gmail.com",
  "password": "password",
  "role": "procurement_officer"
}
```

#### Response:

```json
{
  "id": 5,
  "full_name": "sabin prajapati",
  "email": "sabinprajapati1@gmail.com",
  "role": "procurement_officer",
  "department": null,
  "status": true,
  "last_active": "2025-10-12T17:49:48.698424+05:45",
  "created_at": "2025-10-12T17:49:48.594055+05:45"
}
```

### 5. **Retrieve / Update / Delete User**

**URL:** `/api/users/<id>/`  
**Method:**

- `GET`: Retrieve user details
- `PUT / PATCH`: Update user info (Admin only)
- `DELETE`: Remove user (Admin only)

## 🔑 Password Management

### 6. **Change Password**

**URL:** `/api/auth/change-password/`
**Method:** `PUT`
**Authentication:** Required
**Description:** Allows logged-in users to change their password.

#### Request Body:

```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

#### Response Body:

```json
{
  "detail": "Password updated successfully"
}
```

### 7. **Forgot Password**

**URL:** `/api/auth/forgot-password/`
**Method:** `POST`
**Description:** Sends a password reset link to the user’s email.

#### Request Body:

```json
{
  "email": "user@example.com"
}
```

#### Response Body:

```json
{
  "detail": "If this email exists, a reset link will be sent."
}
```

### 8. **Reset Password**

**URL:** `/api/auth/reset-password/`
**Method:** `POST`
**Description:** Resets the password using a valid token.

#### Request Body:

```json
{
  "uid": "1",
  "token": "generated_token",
  "new_password": "newpassword456"
}
```

#### Response Body:

```json
{
  "detail": "Password reset successfully."
}
```

## ⚙️ Notes

- JWT authentication is implemented using `djangorestframework-simplejwt`.
- Only admins can create, update, or delete users.
- When a user is created, a password reset link is automatically sent to their email.
- All sensitive endpoints require authentication unless stated otherwise.

## 🧾 Example Setup

In `settings.py`, configure your email backend and JWT settings before using password reset features:

```
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"
```

## 📘 Author: Sabin Prajapati

## 🗓️ Last Updated: October 2025

### To view API docs (Swagger):

👉 **Swagger UI:** [http://127.0.0.1:8000/api/schema/swagger-ui/](http://127.0.0.1:8000/api/schema/swagger-ui/)
