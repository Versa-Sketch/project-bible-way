# Bible Way API Specification

## Base URL
```
http://localhost:8000/
```

## Authentication
Most endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 1. User Authentication APIs

### 1.1 User Signup
**Endpoint:** `POST /user/signup`  
**Authentication:** Not required

**Request Body:**
```json
{
  "user_name": "string (required)",
  "email": "string (required)",
  "password": "string (required)",
  "confirm_password": "string (required)",
  "country": "string (optional)",
  "age": "integer (optional)",
  "preferred_language": "string (optional)",
  "profile_picture_url": "string (optional)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Signup successful",
  "access_token": "string",
  "refresh_token": "string"
}
```

**Error Responses:**

- **400 Bad Request** - Email already exists:
```json
{
  "success": false,
  "error": "An account with this email already exists. Please use a different email or try signing in instead.",
  "error_code": "USER_EMAIL_ALREADY_EXISTS"
}
```

- **400 Bad Request** - Username already exists:
```json
{
  "success": false,
  "error": "An account with this username already exists. Please use a different username instead.",
  "error_code": "USER_USERNAME_ALREADY_EXISTS"
}
```

- **400 Bad Request** - Password mismatch:
```json
{
  "success": false,
  "error": "Password does not match",
  "error_code": "PASSWORD_MISMATCH"
}
```

- **400 Bad Request** - Google account exists:
```json
{
  "success": false,
  "error": "An account with this email already exists using Google authentication. Please sign in with Google instead.",
  "error_code": "GOOGLE_ACCOUNT_EXISTS"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "An unexpected error occurred. Please try again later.",
  "error_code": "INTERNAL_SERVER_ERROR"
}
```

---

### 1.2 User Login
**Endpoint:** `POST /user/login`  
**Authentication:** Not required

**Request Body:**
```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "string",
  "refresh_token": "string"
}
```

**Error Responses:**

- **400 Bad Request** - Invalid credentials:
```json
{
  "success": false,
  "error": "Invalid email or password",
  "error_code": "INVALID_CREDENTIALS"
}
```

- **400 Bad Request** - Google account login:
```json
{
  "success": false,
  "error": "This account was created with Google. Please sign in with Google instead.",
  "error_code": "GOOGLE_ACCOUNT_LOGIN"
}
```

---

### 1.3 Google Signup
**Endpoint:** `POST /user/google/signup`  
**Authentication:** Not required

**Request Body:**
```json
{
  "token": "string (required)",
  "country": "string (optional)",
  "age": "integer (optional)",
  "preferred_language": "string (optional)"
}
```

**Note:** The `token` is a Firebase ID token obtained from Google Sign-In on the client side. The server verifies this token and extracts user information (google_id, email, name, profile_picture_url) from the verified token.

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Google signup successful",
  "access_token": "string",
  "refresh_token": "string"
}
```

**Note:** If a user with the same Google ID already exists, the response message will be "Login successful" instead of "Google signup successful".

**Error Responses:**

- **401 Unauthorized** - Invalid token:
```json
{
  "success": false,
  "error": "Invalid Google Token. Identity could not be verified.",
  "error_code": "INVALID_GOOGLE_TOKEN"
}
```

- **400 Bad Request** - Signup failed:
```json
{
  "success": false,
  "error": "Google signup failed. Please try again.",
  "error_code": "GOOGLE_SIGNUP_FAILED"
}
```

---

### 1.4 Google Login
**Endpoint:** `POST /user/google/login`  
**Authentication:** Not required

**Request Body:**
```json
{
  "token": "string (required)"
}
```

**Note:** The `token` is a Firebase ID token obtained from Google Sign-In on the client side. The server verifies this token and extracts user information (google_id, email) from the verified token.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "string",
  "refresh_token": "string"
}
```

**Error Responses:**

- **401 Unauthorized** - Invalid token:
```json
{
  "success": false,
  "error": "Invalid Google Token. Identity could not be verified.",
  "error_code": "INVALID_GOOGLE_TOKEN"
}
```

- **404 Not Found** - Google user not found:
```json
{
  "success": false,
  "error": "Google account not found. Please sign up first.",
  "error_code": "GOOGLE_USER_NOT_FOUND"
}
```

---

## 2. User Profile APIs

### 2.1 Get Current User Profile
**Endpoint:** `GET /user/profile/me`  
**Authentication:** Required (JWT)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "User profile retrieved successfully",
  "data": {
    "user_id": "string",
    "user_name": "string",
    "email": "string",
    "country": "string",
    "age": "integer",
    "preferred_language": "string",
    "profile_picture_url": "string"
  }
}
```

**Error Responses:**

- **404 Not Found:**
```json
{
  "success": false,
  "error": "User not found",
  "error_code": "USER_NOT_FOUND"
}
```

---

### 2.2 Get User Profile by Username
**Endpoint:** `GET /user/profile/<user_name>`  
**Authentication:** Not required

**Path Parameters:**
- `user_name` (string, required) - The username of the user

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "User profile retrieved successfully",
  "data": {
    "user_id": "string",
    "user_name": "string",
    "email": "string",
    "country": "string",
    "age": "integer",
    "preferred_language": "string",
    "profile_picture_url": "string"
  }
}
```

**Error Responses:**

- **400 Bad Request** - Invalid username:
```json
{
  "success": false,
  "error": "User name is required",
  "error_code": "INVALID_USER_NAME"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "User not found",
  "error_code": "USER_NOT_FOUND"
}
```

---

## 3. User Follow APIs

### 3.1 Follow User
**Endpoint:** `POST /user/follow`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "followed_id": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Followed successfully"
}
```

**Error Responses:**

- **400 Bad Request** - Already following:
```json
{
  "success": false,
  "error": "You are already following this user",
  "error_code": "ALREADY_FOLLOWING"
}
```

- **400 Bad Request** - Cannot follow yourself:
```json
{
  "success": false,
  "error": "You cannot follow yourself",
  "error_code": "CANNOT_FOLLOW_YOURSELF"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "User to follow not found",
  "error_code": "USER_NOT_FOUND"
}
```

---

### 3.2 Unfollow User
**Endpoint:** `POST /user/unfollow`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "followed_id": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Unfollowed successfully"
}
```

**Error Responses:**

- **404 Not Found:**
```json
{
  "success": false,
  "error": "User to unfollow not found",
  "error_code": "USER_NOT_FOUND"
}
```

---

## 4. Post APIs

### 4.1 Create Post
**Endpoint:** `POST /post/create`  
**Authentication:** Required (JWT)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `title` (string, optional) - Post title
- `description` (string, optional) - Post description
- `media` (file[], required) - One or more media files (images/videos)

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Post created successfully",
  "post_id": "string"
}
```

**Error Responses:**

- **400 Bad Request** - No media provided:
```json
{
  "success": false,
  "error": "At least one media file is required",
  "error_code": "NO_MEDIA_PROVIDED"
}
```

- **400 Bad Request** - Invalid media type:
```json
{
  "success": false,
  "error": "Invalid media type. Only images and videos are allowed",
  "error_code": "INVALID_MEDIA_TYPE"
}
```

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Failed to upload media to S3: <error_message>",
  "error_code": "S3_UPLOAD_ERROR"
}
```

---

### 4.2 Update Post
**Endpoint:** `PUT /post/update` or `PATCH /post/update`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "post_id": "string (required)",
  "title": "string (optional)",
  "description": "string (optional)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Post updated successfully"
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "post_id is required in request body",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 4.3 Delete Post
**Endpoint:** `DELETE /post/delete`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "post_id": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Post deleted successfully"
}
```

**Error Responses:**

- **400 Bad Request:**
```json
{
  "success": false,
  "error": "post_id is required in request body",
  "error_code": "ERROR"
}
```

---

## 5. Comment APIs

### 5.1 Create Comment
**Endpoint:** `POST /comment/create`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "post_id": "string (required)",
  "description": "string (required)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Comment created successfully",
  "comment_id": "string"
}
```

**Error Responses:**

- **404 Not Found** - Post not found:
```json
{
  "success": false,
  "error": "Post not found",
  "error_code": "POST_NOT_FOUND"
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "<error_message>",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 5.2 Get Comments
**Endpoint:** `GET /comment/post`  
**Authentication:** Not required

**Query Parameters:**
- `post_id` (string, required) - The ID of the post

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Comments retrieved successfully",
  "post_id": "string",
  "data": [
    {
      "comment_id": "string",
      "user_id": "string",
      "user_name": "string",
      "description": "string",
      "created_at": "datetime",
      "likes_count": "integer",
      "is_liked": "boolean"
    }
  ]
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "<error_message>",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - Post not found:
```json
{
  "success": false,
  "error": "Post not found",
  "error_code": "POST_NOT_FOUND"
}
```

---

### 5.3 Update Comment
**Endpoint:** `PUT /comment/update` or `PATCH /comment/update`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "comment_id": "string (required)",
  "description": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Comment updated successfully"
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "<error_message>",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 5.4 Delete Comment
**Endpoint:** `DELETE /comment/delete`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "comment_id": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Comment deleted successfully"
}
```

**Error Responses:**

- **400 Bad Request:**
```json
{
  "success": false,
  "error": "<error_message>",
  "error_code": "ERROR"
}
```

---

## 6. Reaction APIs

### 6.1 Like Post
**Endpoint:** `POST /reaction/post/like`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "post_id": "string (required)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Post liked successfully",
  "reaction_id": "string",
  "post_id": "string",
  "reaction_type": "like"
}
```

**Error Responses:**

- **400 Bad Request** - Already liked:
```json
{
  "success": false,
  "error": "You have already liked this post",
  "error_code": "ALREADY_LIKED"
}
```

- **404 Not Found** - Post not found:
```json
{
  "success": false,
  "error": "Post not found",
  "error_code": "POST_NOT_FOUND"
}
```

---

### 6.2 Unlike Post
**Endpoint:** `POST /reaction/post/unlike`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "post_id": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Post unliked successfully"
}
```

**Error Responses:**

- **400 Bad Request:**
```json
{
  "success": false,
  "error": "<error_message>",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 6.3 Like Comment
**Endpoint:** `POST /reaction/comment/like`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "comment_id": "string (required)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Comment liked successfully",
  "reaction_id": "string",
  "comment_id": "string",
  "reaction_type": "like"
}
```

**Error Responses:**

- **400 Bad Request** - Already liked:
```json
{
  "success": false,
  "error": "You have already liked this comment",
  "error_code": "ALREADY_LIKED"
}
```

---

### 6.4 Unlike Comment
**Endpoint:** `POST /reaction/comment/unlike`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "comment_id": "string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Comment unliked successfully"
}
```

**Error Responses:**

- **400 Bad Request:**
```json
{
  "success": false,
  "error": "<error_message>",
  "error_code": "VALIDATION_ERROR"
}
```

---

## Common Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_CREDENTIALS` | Invalid email or password |
| `USER_EMAIL_ALREADY_EXISTS` | Email already registered |
| `USER_USERNAME_ALREADY_EXISTS` | Username already taken |
| `PASSWORD_MISMATCH` | Password and confirm password don't match |
| `INVALID_GOOGLE_TOKEN` | Invalid or unverifiable Google/Firebase ID token |
| `USER_NOT_FOUND` | User does not exist |
| `POST_NOT_FOUND` | Post does not exist |
| `ALREADY_FOLLOWING` | Already following the user |
| `CANNOT_FOLLOW_YOURSELF` | Cannot follow your own account |
| `ALREADY_LIKED` | Already liked the post/comment |
| `VALIDATION_ERROR` | Request validation failed |
| `INVALID_MEDIA_TYPE` | Media file type not supported |
| `NO_MEDIA_PROVIDED` | No media files in request |
| `S3_UPLOAD_ERROR` | Failed to upload to S3 storage |
| `INTERNAL_SERVER_ERROR` | Unexpected server error |

---

## Notes

1. **JWT Token Format:** All authenticated endpoints require a JWT token in the Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```

2. **Media Upload:** The create post endpoint accepts multiple media files. Supported formats are images and videos.

3. **Base URL:** Replace `http://localhost:8000/` with your actual server URL in production.

4. **Date Formats:** All datetime fields are returned in ISO 8601 format.

5. **Error Responses:** All error responses follow a consistent format with `success: false`, `error` message, and `error_code`.

