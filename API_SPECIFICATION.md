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

### 1.3 Google Authentication
**Endpoint:** `POST /user/google/authentication`  
**Authentication:** Not required

**Request Body:**
```json
{
  "token": "string (required) - Google/Firebase ID token",
  "age": "integer (optional)",
  "preferred_language": "string (optional)",
  "country": "string (optional)"
}
```

**Note:** The `token` is a Firebase ID token obtained from Google Sign-In on the client side. The server verifies this token and extracts user information (google_id, email, name, profile_picture_url) from the verified token.

**Flow:**
- **If user exists** (by google_id or email): Returns login response (200 OK)
- **If user doesn't exist**:
  - If `age` and `preferred_language` are provided: Creates new account and returns signup response (201 Created)
  - If `age` or `preferred_language` is missing: Returns error "Account doesn't exist" (404 Not Found)

**Success Response (200 OK) - Login:**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "string",
  "refresh_token": "string"
}
```

**Success Response (201 Created) - Signup:**
```json
{
  "success": true,
  "message": "Google signup successful",
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

- **404 Not Found** - Account doesn't exist (missing age/preferred_language):
```json
{
  "success": false,
  "error": "Account doesn't exist. Please provide age and preferred_language to create an account.",
  "error_code": "ACCOUNT_NOT_FOUND"
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

### 2.3 Get Complete User Profile
**Endpoint:** `POST /user/profile/complete`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "user_id": "string (required)",
  "current_user": "string (optional) - User ID of the authenticated user (for is_following field)"
}
```

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
    "profile_picture_url": "string",
    "is_admin": "boolean",
    "followers_count": "integer",
    "following_count": "integer",
    "is_following": "boolean"
  }
}
```

**Response Fields:**
- `user_id` (string) - Unique user identifier
- `user_name` (string) - Username
- `email` (string) - User email
- `country` (string) - User country
- `age` (integer) - User age
- `preferred_language` (string) - User's preferred language
- `profile_picture_url` (string) - URL to user's profile picture
- `is_admin` (boolean) - Whether the user is an admin
- `followers_count` (integer) - Number of followers
- `following_count` (integer) - Number of users this user is following
- `is_following` (boolean) - Whether the `current_user` is following this user (only included if `current_user` is provided)

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "user_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid current_user:
```json
{
  "success": false,
  "error": "Invalid current_user",
  "error_code": "VALIDATION_ERROR"
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

### 2.4 Search Users
**Endpoint:** `GET /user/search`  
**Authentication:** Required (JWT)

**Query Parameters:**
- `q` (string, required) - Search query (minimum 2 characters, maximum 50 characters)
- `limit` (integer, optional) - Maximum number of results (default: 20, maximum: 50)

**Description:**
Search for users by username with partial matching (case-insensitive). Results are prioritized by relevance:
1. Exact match (highest priority)
2. Starts with query
3. Contains query

**Example Request:**
```
GET /user/search?q=ven&limit=20
Authorization: Bearer <access_token>
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "user_id": "abc-123-uuid",
      "user_name": "venugopal",
      "profile_picture_url": "https://s3.amazonaws.com/bucket/profile.jpg",
      "followers_count": 150,
      "is_following": false,
      "conversation_id": "1"
    },
    {
      "user_id": "def-456-uuid",
      "user_name": "venkat",
      "profile_picture_url": "https://s3.amazonaws.com/bucket/profile2.jpg",
      "followers_count": 89,
      "is_following": true,
      "conversation_id": null
    }
  ],
  "total_count": 15,
  "query": "ven"
}
```

**Response Fields:**
- `user_id` (string) - Unique user identifier
- `user_name` (string) - Username
- `profile_picture_url` (string) - URL to user's profile picture (empty string if not set)
- `followers_count` (integer) - Number of followers
- `is_following` (boolean) - Whether the authenticated user is following this user
- `conversation_id` (string or null) - The ID of the DIRECT conversation between the authenticated user and this user. Returns `null` if no conversation exists yet
- `total_count` (integer) - Total number of matching users (may be more than returned results)
- `query` (string) - The original search query

**Error Responses:**

- **400 Bad Request** - Search query required:
```json
{
  "success": false,
  "error": "Search query is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Query too short:
```json
{
  "success": false,
  "error": "Search query must be at least 2 characters",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Query too long:
```json
{
  "success": false,
  "error": "Search query must be less than 50 characters",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to search users: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Search is case-insensitive
- Results are ordered by relevance (exact matches first, then starts with, then contains)
- Maximum 50 results can be returned per request
- The `is_following` field indicates the follow relationship from the authenticated user to each result
- Empty search queries (less than 2 characters) return empty results

---

### 2.5 Get Recommended Users
**Endpoint:** `GET /user/recommended` or `POST /user/recommended`  
**Authentication:** Required (JWT)

**Description:**
Get recommended users for a specific user. Returns users that the specified user is not already following, ordered by follower count (most popular first). Excludes the user themselves.

**Request Parameters:**

For **GET** requests:
- `user_id` (string, required) - Query parameter: The user ID to get recommendations for
- `limit` (integer, optional) - Query parameter: Maximum number of results (default: 20, maximum: 20)

For **POST** requests:
- `user_id` (string, required) - Request body: The user ID to get recommendations for
- `limit` (integer, optional) - Request body: Maximum number of results (default: 20, maximum: 20)

**Example GET Request:**
```
GET /user/recommended?user_id=abc-123-uuid&limit=20
Authorization: Bearer <access_token>
```

**Example POST Request:**
```
POST /user/recommended
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "abc-123-uuid",
  "limit": 20
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "user_id": "def-456-uuid",
      "user_name": "john_doe",
      "profile_image": "https://s3.amazonaws.com/bucket/profile.jpg"
    },
    {
      "user_id": "ghi-789-uuid",
      "user_name": "jane_smith",
      "profile_image": ""
    }
  ],
  "total_count": 45
}
```

**Response Fields:**
- `success` (boolean) - Indicates if the request was successful
- `data` (array) - Array of recommended user objects
  - `user_id` (string) - Unique user identifier
  - `user_name` (string) - Username
  - `profile_image` (string) - URL to user's profile picture (empty string if not set)
- `total_count` (integer) - Total number of recommended users available (may be more than returned results)

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "user_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - User not found:
```json
{
  "success": false,
  "error": "User not found",
  "error_code": "USER_NOT_FOUND"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to get recommended users: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Results exclude users that the specified user is already following
- Results exclude the user themselves
- Results are ordered by follower count (descending), then by username (ascending)
- Maximum 20 results can be returned per request
- If `limit` is less than 1 or greater than 20, it defaults to 20
- If `limit` is not provided or invalid, it defaults to 20

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

**Note:** Following a user does not create a conversation. Conversations are created automatically when the first message is sent.

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

**Note:** Unfollowing a user does not deactivate or remove existing conversations. Users can still message each other even after unfollowing.

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
- `media` (file[], optional) - One or more media files (images/videos/audio)

**Note:** Media files are optional. Posts can be created without media.

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Post created successfully",
  "post_id": "string"
}
```

**Error Responses:**

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Invalid media type. Only images, videos, and audio files are allowed",
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

### 4.4 Get All Posts
**Endpoint:** `GET /post/all`  
**Authentication:** Required (JWT)

**Query Parameters:**
- `limit` (integer, optional, default: 10) - Number of posts to return
- `offset` (integer, optional, default: 0) - Number of posts to skip

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Posts retrieved successfully",
  "data": [
    {
      "post_id": "uuid-string",
      "user": {
        "user_id": "uuid-string",
        "user_name": "string",
        "profile_picture_url": "string"
      },
      "title": "string",
      "description": "string",
      "media": [
        {
          "media_id": "uuid-string",
          "media_type": "image|video|audio",
          "url": "string"
        }
      ],
      "likes_count": 5,
      "comments_count": 3,
      "is_liked": true,
      "is_commented": false,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 50,
    "has_next": true,
    "has_previous": false
  }
}
```

**Note:** 
- `is_liked`: Indicates if the current authenticated user has liked this post
- `is_commented`: Indicates if the current authenticated user has commented on this post

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Invalid limit:
```json
{
  "success": false,
  "error": "Limit must be greater than 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid offset:
```json
{
  "success": false,
  "error": "Offset must be greater than or equal to 0",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 4.5 Get User's Posts
**Endpoint:** `GET /post/user/me`  
**Authentication:** Required (JWT)

**Query Parameters:**
- `limit` (integer, optional, default: 10) - Number of posts to return
- `offset` (integer, optional, default: 0) - Number of posts to skip

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "User posts retrieved successfully",
  "data": [
    {
      "post_id": "uuid-string",
      "title": "string",
      "description": "string",
      "media": [
        {
          "media_id": "uuid-string",
          "media_type": "image|video|audio",
          "url": "string"
        }
      ],
      "likes_count": 5,
      "comments_count": 3,
      "is_liked": true,
      "is_commented": false,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

**Note:** 
- `is_liked`: Indicates if the current authenticated user has liked this post
- `is_commented`: Indicates if the current authenticated user has commented on this post

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Invalid limit:
```json
{
  "success": false,
  "error": "Limit must be greater than 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid offset:
```json
{
  "success": false,
  "error": "Offset must be greater than or equal to 0",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 4.6 Get Specific User's Posts
**Endpoint:** `POST /post/user`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "user_id": "string (required)"
}
```

**Query Parameters:**
- `limit` (integer, optional, default: 10) - Number of posts to return
- `offset` (integer, optional, default: 0) - Number of posts to skip

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "User posts retrieved successfully",
  "data": [
    {
      "post_id": "uuid-string",
      "title": "string",
      "description": "string",
      "media": [
        {
          "media_id": "uuid-string",
          "media_type": "image|video|audio",
          "url": "string"
        }
      ],
      "likes_count": 5,
      "comments_count": 3,
      "is_liked": true,
      "is_commented": false,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

**Note:** 
- `is_liked`: Indicates if the current authenticated user has liked this post
- `is_commented`: Indicates if the current authenticated user has commented on this post

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "user_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - User not found:
```json
{
  "success": false,
  "error": "User not found",
  "error_code": "USER_NOT_FOUND"
}
```

- **400 Bad Request** - Invalid limit:
```json
{
  "success": false,
  "error": "Limit must be greater than 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid offset:
```json
{
  "success": false,
  "error": "Offset must be greater than or equal to 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve user posts: <error_message>",
  "error_code": "INTERNAL_ERROR"
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

### 5.2 Get Comments for a Post
**Endpoint:** `GET /comment/details/<post_id>/v1`  
**Authentication:** Required (JWT)

**Path Parameters:**
- `post_id` (string, required) - The ID of the post

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Comments retrieved successfully",
  "post_id": "uuid-string",
  "data": [
    {
      "comment_id": "uuid-string",
      "user": {
        "user_id": "uuid-string",
        "user_name": "string",
        "profile_picture_url": "string"
      },
      "description": "string",
      "likes_count": 5,
      "is_liked": true,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Note:** 
- `is_liked`: Indicates if the current authenticated user has liked this comment

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Post ID is required",
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

### 5.5 Get User's Comments
**Endpoint:** `GET /comment/user/me`  
**Authentication:** Required (JWT)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "User comments retrieved successfully",
  "data": [
    {
      "comment_id": "uuid-string",
      "description": "string",
      "likes_count": 5,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve user comments: <error_message>",
  "error_code": "INTERNAL_ERROR"
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

## 7. Promotion APIs

### 7.1 Get All Promotions
**Endpoint:** `GET /promotion/all`  
**Authentication:** Required (JWT)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Promotions retrieved successfully",
  "data": [
    {
      "promotion_id": "uuid-string",
      "title": "string",
      "description": "string",
      "price": "10.00",
      "redirect_link": "https://...",
      "meta_data": {},
      "media": {
        "media_id": "uuid-string",
        "media_type": "image|video|audio",
        "url": "https://..."
      },
      "images": [
        {
          "promotion_image_id": "uuid-string",
          "image_url": "https://...",
          "image_type": "image",
          "order": 1
        }
      ],
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve promotions: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

## 8. Prayer Request APIs

### 8.1 Create Prayer Request
**Endpoint:** `POST /prayer-request/create`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "name": "string (required)",
  "email": "string (required)",
  "description": "string (required)",
  "phone_number": "string (optional)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Prayer request created successfully",
  "prayer_request_id": "uuid-string"
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Name is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Email required:
```json
{
  "success": false,
  "error": "Email is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Description required:
```json
{
  "success": false,
  "error": "Description is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to create prayer request: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 8.2 Update Prayer Request
**Endpoint:** `PUT /prayer-request/update` or `PATCH /prayer-request/update`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "prayer_request_id": "uuid-string (required)",
  "name": "string (optional)",
  "email": "string (optional)",
  "phone_number": "string (optional)",
  "description": "string (optional)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Prayer request updated successfully"
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Prayer request ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **403 Forbidden** - Unauthorized:
```json
{
  "success": false,
  "error": "You are not authorized to update this prayer request",
  "error_code": "UNAUTHORIZED"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "Prayer request not found",
  "error_code": "PRAYER_REQUEST_NOT_FOUND"
}
```

---

### 8.3 Delete Prayer Request
**Endpoint:** `DELETE /prayer-request/delete`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "prayer_request_id": "uuid-string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Prayer request deleted successfully"
}
```

**Error Responses:**

- **400 Bad Request:**
```json
{
  "success": false,
  "error": "Prayer request ID is required",
  "error_code": "ERROR"
}
```

- **403 Forbidden** - Unauthorized:
```json
{
  "success": false,
  "error": "You are not authorized to delete this prayer request",
  "error_code": "UNAUTHORIZED"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "Prayer request not found",
  "error_code": "PRAYER_REQUEST_NOT_FOUND"
}
```

---

### 8.4 Get All Prayer Requests
**Endpoint:** `GET /prayer-request/all`  
**Authentication:** Required (JWT)

**Query Parameters:**
- `limit` (integer, optional, default: 10) - Number of prayer requests to return
- `offset` (integer, optional, default: 0) - Number of prayer requests to skip

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Prayer requests retrieved successfully",
  "data": [
    {
      "prayer_request_id": "uuid-string",
      "user": {
        "user_id": "uuid-string",
        "user_name": "string",
        "profile_picture_url": "string"
      },
      "name": "string",
      "email": "string",
      "phone_number": "string",
      "description": "string",
      "comments_count": 5,
      "reactions_count": 10,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 50,
    "has_next": true,
    "has_previous": false
  }
}
```

**Error Responses:**

- **400 Bad Request** - Invalid limit:
```json
{
  "success": false,
  "error": "Limit must be greater than 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid offset:
```json
{
  "success": false,
  "error": "Offset must be greater than or equal to 0",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 8.5 Get User's Prayer Requests
**Endpoint:** `GET /prayer-request/user/me`  
**Authentication:** Required (JWT)

**Query Parameters:**
- `limit` (integer, optional, default: 10) - Number of prayer requests to return
- `offset` (integer, optional, default: 0) - Number of prayer requests to skip

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Prayer requests retrieved successfully",
  "data": [
    {
      "prayer_request_id": "uuid-string",
      "user": {
        "user_id": "uuid-string",
        "user_name": "string",
        "profile_picture_url": "string"
      },
      "name": "string",
      "email": "string",
      "phone_number": "string",
      "description": "string",
      "comments_count": 5,
      "reactions_count": 10,
      "is_liked": true,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

**Note:** 
- `is_liked`: Indicates if the current authenticated user has liked this prayer request

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Invalid limit:
```json
{
  "success": false,
  "error": "Limit must be greater than 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid offset:
```json
{
  "success": false,
  "error": "Offset must be greater than or equal to 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve prayer requests: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 8.6 Get Specific User's Prayer Requests
**Endpoint:** `POST /prayer-request/user`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "user_id": "string (required)"
}
```

**Query Parameters:**
- `limit` (integer, optional, default: 10) - Number of prayer requests to return
- `offset` (integer, optional, default: 0) - Number of prayer requests to skip

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Prayer requests retrieved successfully",
  "data": [
    {
      "prayer_request_id": "uuid-string",
      "user": {
        "user_id": "uuid-string",
        "user_name": "string",
        "profile_picture_url": "string"
      },
      "name": "string",
      "email": "string",
      "phone_number": "string",
      "description": "string",
      "comments_count": 5,
      "reactions_count": 10,
      "is_liked": true,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

**Note:** 
- `is_liked`: Indicates if the current authenticated user has liked this prayer request

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "user_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - User not found:
```json
{
  "success": false,
  "error": "User not found",
  "error_code": "USER_NOT_FOUND"
}
```

- **400 Bad Request** - Invalid limit:
```json
{
  "success": false,
  "error": "Limit must be greater than 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid offset:
```json
{
  "success": false,
  "error": "Offset must be greater than or equal to 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve prayer requests: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 8.7 Create Comment on Prayer Request
**Endpoint:** `POST /prayer-request/comment/create`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "prayer_request_id": "uuid-string (required)",
  "description": "string (required)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Comment created successfully",
  "comment_id": "uuid-string"
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Prayer request ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "Prayer request not found",
  "error_code": "PRAYER_REQUEST_NOT_FOUND"
}
```

---

### 8.8 Get Comments for Prayer Request
**Endpoint:** `GET /prayer-request/comment/details/<prayer_request_id>/v1`  
**Authentication:** Required (JWT)

**Path Parameters:**
- `prayer_request_id` (string, required) - The prayer request ID

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Comments retrieved successfully",
  "prayer_request_id": "uuid-string",
  "data": [
    {
      "comment_id": "uuid-string",
      "user": {
        "user_id": "uuid-string",
        "user_name": "string",
        "profile_picture_url": "string"
      },
      "description": "string",
      "likes_count": 5,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Prayer request ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "Prayer request not found",
  "error_code": "PRAYER_REQUEST_NOT_FOUND"
}
```

---

### 8.9 Like Prayer Request
**Endpoint:** `POST /prayer-request/reaction/like`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "prayer_request_id": "uuid-string (required)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Prayer request liked successfully",
  "reaction_id": "uuid-string",
  "prayer_request_id": "uuid-string",
  "reaction_type": "like"
}
```

**Error Responses:**

- **400 Bad Request** - Already liked:
```json
{
  "success": false,
  "error": "You have already liked this prayer request",
  "error_code": "ALREADY_LIKED"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "Prayer request not found",
  "error_code": "PRAYER_REQUEST_NOT_FOUND"
}
```

---

### 8.10 Unlike Prayer Request
**Endpoint:** `POST /prayer-request/reaction/unlike`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "prayer_request_id": "uuid-string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Prayer request unliked successfully"
}
```

**Error Responses:**

- **400 Bad Request** - Not liked:
```json
{
  "success": false,
  "error": "You have not liked this prayer request",
  "error_code": "NOT_LIKED"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "Prayer request not found",
  "error_code": "PRAYER_REQUEST_NOT_FOUND"
}
```

---

## 9. Verse APIs

### 9.1 Get Daily Verse
**Endpoint:** `GET /verse/daily`  
**Authentication:** Required (JWT)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Verse retrieved successfully",
  "data": {
    "verse_id": "uuid-string",
    "title": "Quote of the day",
    "description": "string",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **404 Not Found** - No verse found:
```json
{
  "success": false,
  "error": "Verse not found",
  "error_code": "VERSE_NOT_FOUND"
}
```

---

### 9.2 Get All Verses
**Endpoint:** `GET /verse/all`  
**Authentication:** Required (JWT)

**Description:**
This endpoint retrieves all verses with their like counts. For authenticated users, it also includes whether the user has liked each verse.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Verses retrieved successfully",
  "data": [
    {
      "verse_id": "uuid-string",
      "title": "Quote of the day",
      "description": "string",
      "likes_count": 15,
      "is_liked": true,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ],
  "total_count": 10
}
```

**Response Fields:**
- `verse_id` (string) - Unique verse identifier
- `title` (string) - Verse title (default: "Quote of the day")
- `description` (string) - Verse description/content
- `likes_count` (integer) - Number of likes for this verse
- `is_liked` (boolean) - Whether the authenticated user has liked this verse
- `created_at` (string) - Creation timestamp in ISO 8601 format
- `updated_at` (string) - Last update timestamp in ISO 8601 format
- `total_count` (integer) - Total number of verses

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - User not found (if user_id validation fails):
```json
{
  "success": false,
  "error": "User not found",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve verses: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Verses are ordered by creation date (newest first)
- The `is_liked` field indicates if the authenticated user has liked each verse
- All verses are returned (no pagination)

---

### 9.3 Like Verse
**Endpoint:** `POST /verse/like`  
**Authentication:** Required (JWT)

**Description:**
Allows an authenticated user to like a verse. Each user can only like a verse once.

**Request Body:**
```json
{
  "verse_id": "uuid-string (required)"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Verse liked successfully",
  "reaction_id": "uuid-string",
  "verse_id": "uuid-string",
  "reaction_type": "like"
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Missing verse_id:
```json
{
  "success": false,
  "error": "Verse ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - Verse not found:
```json
{
  "success": false,
  "error": "Verse not found",
  "error_code": "VERSE_NOT_FOUND"
}
```

- **400 Bad Request** - Already liked:
```json
{
  "success": false,
  "error": "You have already liked this verse",
  "error_code": "ALREADY_LIKED"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to like verse: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- A user can only like a verse once
- The like count is updated automatically
- The reaction is stored with the user and verse relationship

---

### 9.4 Unlike Verse
**Endpoint:** `POST /verse/unlike`  
**Authentication:** Required (JWT)

**Description:**
Allows an authenticated user to remove their like from a verse.

**Request Body:**
```json
{
  "verse_id": "uuid-string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Verse unliked successfully",
  "verse_id": "uuid-string"
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Missing verse_id:
```json
{
  "success": false,
  "error": "Verse ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - Verse not found:
```json
{
  "success": false,
  "error": "Verse not found",
  "error_code": "VERSE_NOT_FOUND"
}
```

- **400 Bad Request** - Not liked:
```json
{
  "success": false,
  "error": "You haven't liked this verse",
  "error_code": "NOT_LIKED"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to unlike verse: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- User must have previously liked the verse to unlike it
- The like count is decremented automatically
- User can like the verse again after unliking

---

## 10. Admin APIs

### 10.1 Admin Create Verse
**Endpoint:** `POST /admin/verse/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Request Body:**
```json
{
  "title": "string (optional, default: 'Quote of the day')",
  "description": "string (required)"
}
```

**Note:** This endpoint clears all existing verses before creating a new one (24-hour clearing mechanism).

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Verse created successfully",
  "verse_id": "uuid-string"
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Description is required",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 10.2 Admin Create Promotion
**Endpoint:** `POST /admin/promotion/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `title` (string, required) - Promotion title
- `description` (string, optional) - Promotion description
- `price` (decimal, required) - Promotion price
- `redirect_link` (string, required) - URL to redirect to
- `meta_data` (string, optional) - JSON string for metadata
- `media` (file, optional) - Single media file (image/video/audio)
- `images` (file[], optional) - Multiple image files

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Promotion created successfully",
  "promotion_id": "uuid-string"
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Title is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid JSON format:
```json
{
  "success": false,
  "error": "Invalid JSON format for meta_data",
  "error_code": "VALIDATION_ERROR"
}
```

---

### 10.3 Admin Create Category
**Endpoint:** `POST /admin/category/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `category_name` (string, required) - Category name (must be a valid CategoryChoices value)
- `cover_image` (file, optional) - Cover image file for the category
- `description` (string, optional) - Category description
- `display_order` (integer, optional, default: 0) - Display order for sorting categories

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Category created successfully",
  "data": {
    "category_id": "uuid-string",
    "category_name": "SEGREGATE_BIBLES",
    "display_name": "Segregated Bibles",
    "cover_image_url": "https://s3.amazonaws.com/bucket/categories/cover_images/...",
    "description": "Bibles with age-specific content",
    "display_order": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Category name is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid category name:
```json
{
  "success": false,
  "error": "Invalid category name. Must be one of: SEGREGATE_BIBLES, ...",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Category already exists:
```json
{
  "success": false,
  "error": "Category 'SEGREGATE_BIBLES' already exists",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Failed to upload cover image: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 10.4 Admin Get Categories
**Endpoint:** `GET /admin/categories`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Categories retrieved successfully",
  "data": [
    {
      "category_id": "uuid-string",
      "category_name": "SEGREGATE_BIBLES",
      "display_name": "Segregated Bibles",
      "cover_image_url": "https://s3.amazonaws.com/bucket/categories/cover_images/...",
      "description": "Bibles with age-specific content",
      "display_order": 0,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve categories: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 10.5 Admin Create Age Group
**Endpoint:** `POST /admin/age-group/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `age_group_name` (string, required) - Age group name (must be a valid AgeGroupChoices value)
- `cover_image` (file, optional) - Cover image file for the age group
- `description` (string, optional) - Age group description
- `display_order` (integer, optional, default: 0) - Display order for sorting age groups

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Age group created successfully",
  "data": {
    "age_group_id": "uuid-string",
    "age_group_name": "CHILD",
    "display_name": "Child",
    "cover_image_url": "https://s3.amazonaws.com/bucket/age_groups/cover_images/...",
    "description": "Books for children",
    "display_order": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Age group name is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Failed to upload cover image: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 10.6 Admin Get Age Groups
**Endpoint:** `GET /admin/age-groups`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Age groups retrieved successfully",
  "data": [
    {
      "age_group_id": "uuid-string",
      "age_group_name": "CHILD",
      "display_name": "Child",
      "cover_image_url": "https://s3.amazonaws.com/bucket/age_groups/cover_images/...",
      "description": "Books for children",
      "display_order": 0,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve age groups: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 10.7 Admin Get Languages
**Endpoint:** `GET /admin/languages`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Languages retrieved successfully",
  "data": [
    {
      "language_id": "uuid-string",
      "language_name": "ENGLISH",
      "display_name": "English",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve languages: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 10.8 Admin Create Book
**Endpoint:** `POST /admin/book/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `title` (string, required) - Book title
- `category` (string, required) - Category ID (UUID)
- `agegroup` (string, required) - Age group ID (UUID)
- `language` (string, required) - Language ID (UUID)
- `cover_image` (file, optional) - Cover image file for the book
- `description` (string, optional) - Book description

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Book created successfully",
  "book_id": "uuid-string"
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Title is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing required field:
```json
{
  "success": false,
  "error": "Category is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid category/age group/language:
```json
{
  "success": false,
  "error": "Category with id '<category_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Failed to upload cover image: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 10.9 Admin Create Chapters
**Endpoint:** `POST /admin/book/chapters/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `book_id` (string, required) - Book UUID
- `bookdata` (JSON string, required) - Array of chapter objects:
  ```json
  [
    {
      "title": "string (required)",
      "description": "string (required)",
      "metadata": {} // optional JSON object per chapter
    }
  ]
  ```
- `file_0`, `file_1`, `file_2`, ... (files, required) - Files indexed to match bookdata array order

**Note:** Files are sent as separate fields (`file_0`, `file_1`, etc.) and matched by index to the bookdata array.

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Chapters uploaded successfully",
  "chaptersCount": 3,
  "book_id": "uuid-string"
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Book ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid JSON:
```json
{
  "success": false,
  "error": "Invalid JSON format for bookdata",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Book not found:
```json
{
  "success": false,
  "error": "Book with id '<book_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing chapter fields:
```json
{
  "success": false,
  "error": "Title is required for chapter at index 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - File count mismatch:
```json
{
  "success": false,
  "error": "Number of files (2) must match number of chapters (3)",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Failed to upload file for chapter at index 0: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 10.10 Admin Update Book Metadata
**Endpoint:** `POST /admin/book/update-metadata`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Request Body:**
```json
{
  "book_id": "string (required)",
  "metadata": "string (required) - JSON string containing metadata"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Book metadata updated successfully"
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "book_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing metadata:
```json
{
  "success": false,
  "error": "metadata is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "Book not found",
  "error_code": "BOOK_NOT_FOUND"
}
```

---

### 10.11 Admin Get All Books
**Endpoint:** `GET /admin/books`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Query Parameters:**
- `limit` (integer, optional) - Maximum number of books to return (if not provided, returns all)
- `offset` (integer, optional, default: 0) - Number of books to skip

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Books retrieved successfully",
  "data": [
    {
      "book_id": "uuid-string",
      "title": "The Book of Genesis",
      "description": "string",
      "category_id": "uuid-string",
      "age_group_id": "uuid-string",
      "language_id": "uuid-string",
      "cover_image_url": "https://s3.amazonaws.com/bucket/books/cover_images/...",
      "source_file_url": "https://s3.amazonaws.com/bucket/books/.../source_files/...",
      "book_order": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 50,
    "has_next": true,
    "has_previous": false
  }
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve books: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `book_id` (string, required) - Book ID (UUID)
- `bookdata` (JSON string, required) - Array of chapter objects:
  ```json
  [
    {
      "title": "string (required)",
      "description": "string (required)",
      "metadata": {} // optional JSON object per chapter
    }
  ]
  ```
- `file_0`, `file_1`, `file_2`, ... (files, required) - Files indexed to match bookdata array order

**Note:** Files are sent as separate fields (`file_0`, `file_1`, etc.) and matched by index to the bookdata array.

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Chapters uploaded successfully",
  "chaptersCount": 3,
  "book_id": "uuid-string"
}
```

**Error Responses:**

- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Book ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid JSON:
```json
{
  "success": false,
  "error": "Invalid JSON format for bookdata",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Book not found:
```json
{
  "success": false,
  "error": "Book with id '<book_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing chapter fields:
```json
{
  "success": false,
  "error": "Title is required for chapter at index 0",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - File count mismatch:
```json
{
  "success": false,
  "error": "Number of files (2) must match number of chapters (3)",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Failed to upload file for chapter at index 0: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

- **500 Internal Server Error** - Chapter creation error:
```json
{
  "success": false,
  "error": "Failed to create chapter at index 0: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Chapter numbers are auto-incremented starting from max existing chapter_number + 1
- Files are uploaded to S3 in path: `books/{sanitized_book_title}/chapters/{original_filename}`
- Each chapter can have its own metadata JSON object
- Files must use indexed keys: `file_0`, `file_1`, `file_2`, etc.

---

## 11. Books APIs

### 11.1 Get All Categories
**Endpoint:** `GET /books/categories/`  
**Authentication:** Required (JWT)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Categories retrieved successfully",
  "data": [
    {
      "category_id": "uuid-string",
      "category_name": "SEGREGATE_BIBLES",
      "display_name": "Segregated Bibles",
      "cover_image_url": "https://s3.amazonaws.com/bucket/categories/cover_images/...",
      "description": "Bibles with age-specific content",
      "display_order": 0,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve categories: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 11.2 Get All Age Groups
**Endpoint:** `GET /books/age-groups/`  
**Authentication:** Required (JWT)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Age groups retrieved successfully",
  "data": [
    {
      "age_group_id": "uuid-string",
      "age_group_name": "CHILD",
      "display_name": "Child",
      "cover_image_url": "https://s3.amazonaws.com/bucket/age_groups/cover_images/...",
      "description": "Books for children",
      "display_order": 0,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve age groups: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 11.3 Get Books by Category and Age Group (POST)
**Endpoint:** `POST /books/get`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "category_id": "uuid-string (required)",
  "age_group": "uuid-string (required)"  // OR "age_group_id": "uuid-string"
}
```

**Note:** The endpoint accepts either `age_group` or `age_group_id` in the request body.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Books retrieved successfully",
  "data": [
    {
      "book_id": "uuid-string",
      "title": "The Book of Genesis",
      "description": "string",
      "category_id": "uuid-string",
      "age_group_id": "uuid-string",
      "language_id": "uuid-string",
      "cover_image_url": "https://s3.amazonaws.com/bucket/books/cover_images/...",
      "book_order": 0,
      "is_active": true,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Missing category:
```json
{
  "success": false,
  "error": "Category is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing age group:
```json
{
  "success": false,
  "error": "Age group is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Category not found:
```json
{
  "success": false,
  "error": "Category with id '<category_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Age group not found:
```json
{
  "success": false,
  "error": "Age group with id '<age_group_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve books: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 11.3.1 Get Books by Category and Age Group (GET)
**Endpoint:** `GET /books/?category_id=<uuid>&age_group_id=<uuid>`  
**Authentication:** Required (JWT)

**Query Parameters:**
- `category_id` (string, required) - UUID of the category
- `age_group_id` (string, required) - UUID of the age group

**Example Request:**
```
GET /books/?category_id=123e4567-e89b-12d3-a456-426614174000&age_group_id=123e4567-e89b-12d3-a456-426614174001
Headers: Authorization: Bearer <access_token>
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Books retrieved successfully",
  "data": [
    {
      "book_id": "uuid-string",
      "title": "The Book of Genesis",
      "description": "string",
      "category_id": "uuid-string",
      "age_group_id": "uuid-string",
      "language_id": "uuid-string",
      "cover_image_url": "https://s3.amazonaws.com/bucket/books/cover_images/...",
      "book_order": 0,
      "is_active": true,
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Missing category:
```json
{
  "success": false,
  "error": "Category is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing age group:
```json
{
  "success": false,
  "error": "Age group is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Category not found:
```json
{
  "success": false,
  "error": "Category with id '<category_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Age group not found:
```json
{
  "success": false,
  "error": "Age group with id '<age_group_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve books: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---


### 11.4 Get Book Chapters
**Endpoint:** `POST /books/chapters/get`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "book_id": "uuid-string (required)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Chapters retrieved successfully",
  "data": [
    {
      "chapter_id": "uuid-string",
      "book_id": "uuid-string",
      "title": "string",
      "description": "string",
      "chapter_number": 1,
      "chapter_name": "string or null",
      "chapter_url": "string or null",
      "metadata": {},
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "Book ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Book not found:
```json
{
  "success": false,
  "error": "Book with id '<book_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve chapters: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Chapters are returned ordered by `chapter_number` (ascending)
- Returns empty array `[]` if no chapters found for the book

---

### 11.5 Search Chapters
**Endpoint:** `POST /books/search`  
**Authentication:** Required (JWT)

**Description:**  
Search for text within chapter blocks using Elasticsearch. Returns matching text blocks with their associated chapter information, including highlighted matched text. Supports fuzzy matching for typo tolerance.

**Request Body:**
```json
{
  "book_id": "uuid-string (required)",
  "language_id": "uuid-string (required)",
  "search_text": "string (required)"
}
```

**Example Request:**
```json
{
  "book_id": "123e4567-e89b-12d3-a456-426614174000",
  "language_id": "123e4567-e89b-12d3-a456-426614174001",
  "search_text": "town"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Search completed successfully",
  "data": {
    "results": [
      {
        "block_id": "block-0",
        "text": "At dawn, the town of Bracken Hollow",
        "highlighted_text": "At dawn, the <mark>town</mark> of Bracken Hollow",
        "chapter_id": "d442a669-d96d-46a2-8b90-5b1beefb795a",
        "chapter_name": "Untitled document (1)"
      },
      {
        "block_id": "block-289",
        "text": "And Jehovah came down to see the city and the tower, which the children of men builded",
        "highlighted_text": "And Jehovah came down to see the <mark>city</mark> and the tower, which the children of men builded",
        "chapter_id": "ddb8fbdc-6f46-40ee-8388-c2f9374fe1e0",
        "chapter_name": "Genesis"
      }
    ],
    "total_results": 64
  }
}
```

**Response Fields:**
- `block_id` (string) - Unique identifier of the text block
- `text` (string) - Original text content without highlighting
- `highlighted_text` (string, optional) - Text with `<mark>` tags around matched portions. Only present when matches are found.
- `chapter_id` (string) - UUID of the chapter containing this block
- `chapter_name` (string) - Name of the chapter
- `total_results` (number) - Total number of matching results

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Missing book_id:
```json
{
  "success": false,
  "error": "book_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing language_id:
```json
{
  "success": false,
  "error": "language_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing search_text:
```json
{
  "success": false,
  "error": "search_text is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to perform search: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Uses Elasticsearch for fast full-text search across chapter metadata blocks
- Supports fuzzy matching with automatic typo tolerance
- Results are returned with relevance scoring
- Search is case-insensitive
- Searches within the `text` field of chapter blocks
- **Highlighting**: Matched text is wrapped in `<mark>` tags in the `highlighted_text` field
- Highlighting shows up to 3 fragments of 150 characters each around matches
- Multiple matches in the same block are separated by " ... "
- Frontend should render `<mark>` tags with CSS styling (e.g., yellow background)
- If no highlighting is available, use the `text` field as fallback
- Both `book_id` and `language_id` are used as filters to narrow down search scope
- Maximum 100 results returned per request (pagination can be added if needed)

**Search Features:**
- **Full-text search:** Matches words within block text content
- **Fuzzy matching:** Tolerates typos (e.g., "twon" will match "town")
- **Fast performance:** Optimized for large datasets using Elasticsearch inverted index
- **Relevance ranking:** Results sorted by relevance to search query

---

### 11.6 Get All Books
**Endpoint:** `GET /books/all`  
**Authentication:** Required (JWT)

**Description:**  
Retrieves all active books with their IDs and titles. This is a simplified endpoint for populating dropdowns or selection lists.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Books retrieved successfully",
  "data": [
    {
      "book_id": "uuid-string",
      "title": "Genesis"
    },
    {
      "book_id": "uuid-string",
      "title": "Exodus"
    },
    {
      "book_id": "uuid-string",
      "title": "Leviticus"
    }
  ],
  "total_count": 66
}
```

**Response Fields:**
- `book_id` (string) - Unique book identifier (UUID)
- `title` (string) - Book title
- `total_count` (integer) - Total number of active books

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve books: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Returns only active books (`is_active=True`)
- Books are ordered by `book_order` and `title`
- Returns minimal data (only ID and title) for efficiency
- Accessible to any authenticated user (not admin-only)
- Perfect for dropdown menus and selection lists in frontend

---

### 11.7 Get All Languages
**Endpoint:** `GET /languages/all`  
**Authentication:** Required (JWT)

**Description:**  
Retrieves all available languages with their IDs and display names. This is a public endpoint accessible to any authenticated user.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Languages retrieved successfully",
  "data": [
    {
      "language_id": "uuid-string",
      "language_name": "EN",
      "display_name": "English"
    },
    {
      "language_id": "uuid-string",
      "language_name": "ES",
      "display_name": "Spanish"
    },
    {
      "language_id": "uuid-string",
      "language_name": "FR",
      "display_name": "French"
    }
  ]
}
```

**Response Fields:**
- `language_id` (string) - Unique language identifier (UUID)
- `language_name` (string) - Language code (e.g., "EN", "ES", "FR")
- `display_name` (string) - Human-readable language name (e.g., "English", "Spanish")

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve languages: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Returns all languages ordered by `language_name`
- Accessible to any authenticated user (not admin-only)
- The admin equivalent endpoint (`GET /admin/languages`) still exists for admin panel use
- Perfect for language selection dropdowns in frontend
- Includes both language code and display name for flexibility

---

## 12. Highlight APIs

### 12.1 Create Highlight
**Endpoint:** `POST /highlight/create`  
**Authentication:** Required (JWT)

**Description:**
Creates a highlight for a specific text selection within a chapter. The highlight is associated with a book, chapter, and optional block, allowing users to mark and save important passages.

**Request Body:**
```json
{
  "book_id": "uuid-string (required)",
  "chapter_id": "uuid-string (required)",
  "block_id": "uuid-string (optional)",
  "start_offset": "string (required)",
  "end_offset": "string (required)",
  "color": "string (optional, default: 'yellow')"
}
```

**Example Request:**
```json
{
  "book_id": "123e4567-e89b-12d3-a456-426614174000",
  "chapter_id": "d442a669-d96d-46a2-8b90-5b1beefb795a",
  "block_id": "block-5",
  "start_offset": "10",
  "end_offset": "50",
  "color": "yellow"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Highlight created successfully",
  "highlight_id": "uuid-string"
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Missing book_id:
```json
{
  "success": false,
  "error": "book_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing chapter_id:
```json
{
  "success": false,
  "error": "chapter_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing start_offset:
```json
{
  "success": false,
  "error": "start_offset is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing end_offset:
```json
{
  "success": false,
  "error": "end_offset is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - Book not found:
```json
{
  "success": false,
  "error": "Book not found",
  "error_code": "BOOK_NOT_FOUND"
}
```

- **404 Not Found** - Chapter not found:
```json
{
  "success": false,
  "error": "Chapter not found",
  "error_code": "CHAPTER_NOT_FOUND"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to create highlight: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- The `block_id` is optional and can be used to specify a particular block within the chapter
- Default highlight color is 'yellow' if not specified
- `start_offset` and `end_offset` define the text selection boundaries
- The response includes the unique `highlight_id` which can be used for future operations

---

### 12.2 Get Highlights
**Endpoint:** `GET /highlight/book/<book_id>`  
**Authentication:** Required (JWT)

**Description:**
Retrieves all highlights created by the authenticated user for a specific book.

**Path Parameters:**
- `book_id` (string, required) - The UUID of the book

**Example Request:**
```
GET /highlight/book/123e4567-e89b-12d3-a456-426614174000
Authorization: Bearer <jwt_token>
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Highlights retrieved successfully",
  "data": [
    {
      "highlight_id": "uuid-string",
      "book_id": "uuid-string",
      "block_id": "uuid-string or null",
      "start_offset": "string",
      "end_offset": "string",
      "color": "yellow",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Missing book_id:
```json
{
  "success": false,
  "error": "book_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - Book not found:
```json
{
  "success": false,
  "error": "Book not found",
  "error_code": "BOOK_NOT_FOUND"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve highlights: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Returns highlights **only for the authenticated user**
- Returns an empty array `[]` if no highlights are found
- Highlights are ordered by creation date (newest first)
- `block_id` will be `null` if the highlight is not associated with a specific block

---

### 12.3 Delete Highlight
**Endpoint:** `DELETE /highlight/delete`  
**Authentication:** Required (JWT)

**Description:**
Deletes a specific highlight. Users can only delete their own highlights.

**Request Body:**
```json
{
  "highlight_id": "uuid-string (required)"
}
```

**Example Request:**
```json
{
  "highlight_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Highlight deleted successfully"
}
```

**Error Responses:**

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **400 Bad Request** - Missing highlight_id:
```json
{
  "success": false,
  "error": "highlight_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - Highlight not found:
```json
{
  "success": false,
  "error": "Highlight not found",
  "error_code": "HIGHLIGHT_NOT_FOUND"
}
```

- **403 Forbidden** - Not authorized to delete:
```json
{
  "success": false,
  "error": "You are not authorized to delete this highlight",
  "error_code": "UNAUTHORIZED"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to delete highlight: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Users can only delete their own highlights
- Returns `403 Forbidden` if attempting to delete another user's highlight
- Deletion is permanent and cannot be undone

---

## 13. Reading Note APIs

### 13.1 Create Reading Note
**Endpoint:** `POST /reading-note/create`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "book_id": "string (required)",
  "content": "string (required)",
  "chapter_id": "string (optional)",
  "block_id": "string (required)"
}
```

**Note:** If `chapter_id` is not provided, a new UUID will be automatically generated.

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Reading note created successfully",
  "note_id": "uuid-string"
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "book_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing required field:
```json
{
  "success": false,
  "error": "content is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing block_id:
```json
{
  "success": false,
  "error": "block_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - Book not found:
```json
{
  "success": false,
  "error": "Book not found",
  "error_code": "BOOK_NOT_FOUND"
}
```

- **404 Not Found** - User not found:
```json
{
  "success": false,
  "error": "User not found",
  "error_code": "USER_NOT_FOUND"
}
```

- **401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to create reading note: <error_message>",
  "error": "Failed to create share link: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 13.2 Get Reading Notes
**Endpoint:** `GET /reading-note/book/<book_id>`  
**Authentication:** Required (JWT)

**Path Parameters:**
- `book_id` (string, required) - The ID of the book

**Query Parameters:**
- `user_id` (string, optional) - User ID to get reading notes for. If not provided, returns reading notes for the authenticated user.
### 12.3 View Shared Post
**Endpoint:** `GET /s/p/<token>`  
**Authentication:** Required (JWT)

**Path Parameters:**
- `token` (string, required) - The share token from the share link

**Description:**
View a shared post using the short share link. Users must be authenticated to view shared content. If a user is not authenticated, they will receive a 401 error and should be redirected to signup/login, then redirected back to the share link.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Reading notes retrieved successfully",
  "data": [
    {
      "note_id": "uuid-string",
      "book_id": "uuid-string",
      "user_id": "uuid-string",
      "content": "string",
      "chapter_id": "uuid-string or null",
      "block_id": "uuid-string"
    }
  ]
  "message": "Post retrieved successfully",
  "data": {
    "post_id": "uuid-string",
    "user": {
      "user_id": "uuid-string",
      "user_name": "string",
      "profile_picture_url": "string"
    },
    "title": "string",
    "description": "string",
    "media": [
      {
        "media_id": "uuid-string",
        "media_type": "image|video|audio",
        "url": "string"
      }
    ],
    "likes_count": 10,
    "comments_count": 5,
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "book_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - User ID required:
```json
{
  "success": false,
  "error": "user_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found** - Book not found:
```json
{
  "success": false,
  "error": "Book not found",
  "error_code": "BOOK_NOT_FOUND"
- **401 Unauthorized** - Not authenticated:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Note:** Frontend should redirect unauthenticated users to signup/login with `return_url` parameter, then redirect back after authentication.

- **404 Not Found** - Invalid token:
```json
{
  "success": false,
  "error": "Invalid or expired share link",
  "error_code": "INVALID_SHARE_TOKEN"
}
```

- **404 Not Found** - Post deleted:
```json
{
  "success": false,
  "error": "Post no longer available",
  "error_code": "POST_NOT_FOUND"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve reading notes: <error_message>",
  "error": "Failed to retrieve shared post: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 13.3 Update Reading Note
**Endpoint:** `PUT /reading-note/update` or `PATCH /reading-note/update`  
**Authentication:** Required (JWT)

**Request Body:**
```json
{
  "note_id": "string (required)",
  "content": "string (required)"
}
```
### 12.4 View Shared Profile
**Endpoint:** `GET /s/u/<token>`  
**Authentication:** Required (JWT)

**Path Parameters:**
- `token` (string, required) - The share token from the share link

**Description:**
View a shared user profile using the short share link. Users must be authenticated to view shared content. If a user is not authenticated, they will receive a 401 error and should be redirected to signup/login, then redirected back to the share link.

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Reading note updated successfully",
  "note_id": "uuid-string"
  "message": "Profile retrieved successfully",
  "data": {
    "user_id": "uuid-string",
    "user_name": "string",
    "email": "string",
    "country": "string",
    "age": "integer",
    "preferred_language": "string",
    "profile_picture_url": "string",
    "is_admin": "boolean",
    "followers_count": "integer",
    "following_count": "integer"
  }
}
```

**Error Responses:**

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "note_id is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Missing content:
```json
{
  "success": false,
  "error": "content is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **404 Not Found:**
```json
{
  "success": false,
  "error": "Reading note not found",
  "error_code": "NOTE_NOT_FOUND"
}
```

- **403 Forbidden** - Unauthorized:
```json
{
  "success": false,
  "error": "You are not authorized to update this reading note",
  "error_code": "UNAUTHORIZED"
- **401 Unauthorized** - Not authenticated:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Note:** Frontend should redirect unauthenticated users to signup/login with `return_url` parameter, then redirect back after authentication.

- **404 Not Found** - Invalid token:
```json
{
  "success": false,
  "error": "Invalid or expired share link",
  "error_code": "INVALID_SHARE_TOKEN"
}
```

- **404 Not Found** - User deleted or deactivated:
```json
{
  "success": false,
  "error": "Profile no longer available",
  "error_code": "USER_NOT_FOUND"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to update reading note: <error_message>",
  "error": "Failed to retrieve shared profile: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Share links are short URLs (e.g., `/s/p/{token}` for posts, `/s/u/{token}` for profiles)
- All share link endpoints require authentication to encourage user signups
- If a share link already exists for the same content and user, the existing link is returned
- Share links do not expire (unless manually deactivated by admin)
- Frontend should handle authentication redirects: detect 401 → redirect to login with `return_url` → redirect back after auth

---

## Common Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_CREDENTIALS` | Invalid email or password |
| `USER_EMAIL_ALREADY_EXISTS` | Email already registered |
| `USER_USERNAME_ALREADY_EXISTS` | Username already taken |
| `PASSWORD_MISMATCH` | Password and confirm password don't match |
| `INVALID_GOOGLE_TOKEN` | Invalid or unverifiable Google/Firebase ID token |
| `ACCOUNT_NOT_FOUND` | Account doesn't exist, requires age and preferred_language for signup |
| `USER_NOT_FOUND` | User does not exist |
| `POST_NOT_FOUND` | Post does not exist |
| `PRAYER_REQUEST_NOT_FOUND` | Prayer request does not exist |
| `VERSE_NOT_FOUND` | Verse not found in database |
| `BOOK_NOT_FOUND` | Book does not exist |
| `HIGHLIGHT_NOT_FOUND` | Highlight does not exist |
| `NOTE_NOT_FOUND` | Reading note does not exist |
| `ALREADY_FOLLOWING` | Already following the user |
| `CANNOT_FOLLOW_YOURSELF` | Cannot follow your own account |
| `ALREADY_LIKED` | Already liked the post/comment/prayer request |
| `NOT_LIKED` | Prayer request has not been liked |
| `UNAUTHORIZED` | Not authorized to perform this action |
| `VALIDATION_ERROR` | Request validation failed |
| `INVALID_MEDIA_TYPE` | Media file type not supported |
| `NO_MEDIA_PROVIDED` | No media files in request |
| `S3_UPLOAD_ERROR` | Failed to upload to S3 storage |
| `INVALID_SHARE_TOKEN` | Invalid or expired share link token |
| `INTERNAL_ERROR` | Internal server error |
| `INTERNAL_SERVER_ERROR` | Unexpected server error |

---

## Notes

1. **JWT Token Format:** All authenticated endpoints require a JWT token in the Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```

2. **Media Upload:** The create post endpoint accepts multiple media files (optional). Supported formats are images, videos, and audio files. Media files are determined by filename extension (no magic library validation).

3. **Base URL:** Replace `http://localhost:8000/` with your actual server URL in production.

4. **Date Formats:** All datetime fields are returned in ISO 8601 format.

5. **Error Responses:** All error responses follow a consistent format with `success: false`, `error` message, and `error_code`.

6. **User Interaction Flags:** Posts include `is_liked` and `is_commented` flags indicating if the current authenticated user has liked or commented. Comments include `is_liked` flag indicating if the current authenticated user has liked the comment.

7. **Share Links:** Share links require authentication to view shared content. This encourages user signups and growth. Unauthenticated users receive 401 errors and should be redirected to signup/login with the share link as the return URL. Share links use short URLs (`/s/p/{token}` for posts, `/s/u/{token}` for profiles) for easy sharing.

