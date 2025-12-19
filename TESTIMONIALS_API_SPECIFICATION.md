# Testimonials API Specification

**Version:** 1.0  
**Last Updated:** December 19, 2025  
**Base URL:** `http://localhost:8000` (or your server URL)

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [User Endpoints](#user-endpoints)
4. [Admin Endpoints](#admin-endpoints)
5. [Data Models](#data-models)
6. [Error Responses](#error-responses)
7. [Status Codes](#status-codes)

---

## Overview

The Testimonials API allows users to submit testimonials with ratings and media files. Testimonials require admin approval before being visible to the public. Admins can view, approve, or reject testimonials.

### Key Features

- Users can create testimonials with description, rating (1-5), and optional media files
- Testimonials are hidden from public until admin approval
- Users can view their own testimonials (including pending ones)
- Admins can view all testimonials with filtering options
- Admins can approve or reject testimonials
- Media files (images, videos, audio) are supported

---

## Authentication

### JWT Token Authentication

Most endpoints require authentication using JWT Bearer tokens. Include the token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

### Getting an Access Token

Login endpoint: `POST /user/login`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## User Endpoints

### 1. Create Testimonial

**Endpoint:** `POST /testimonial/create`  
**Authentication:** Required (JWT)  
**Content-Type:** `multipart/form-data` or `application/json`

#### Description

Creates a new testimonial with description, rating, and optional media files. The testimonial will be in `pending` status (`is_verified=false`) until admin approval.

#### Request Body

**Form Data Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Testimonial description/text content |
| `rating` | integer | Yes | Rating value (1-5) |
| `media` | file(s) | No | Media files (images, videos, or audio). Can upload multiple files |

**JSON Alternative:**

```json
{
  "description": "This is an amazing app! Highly recommend it.",
  "rating": 5
}
```

**Note:** When using JSON, media files cannot be included. Use `multipart/form-data` for media uploads.

#### Request Example (cURL)

```bash
# Without media
curl -X POST http://localhost:8000/testimonial/create \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "This app has changed my life! Amazing features and user-friendly interface.",
    "rating": 5
  }'

# With media (multipart/form-data)
curl -X POST http://localhost:8000/testimonial/create \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "description=Great app with excellent features!" \
  -F "rating=5" \
  -F "media=@/path/to/image.jpg" \
  -F "media=@/path/to/video.mp4"
```

#### Success Response (201 Created)

```json
{
  "success": true,
  "message": "Testimonial created successfully",
  "testimonial_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Error Responses

**400 Bad Request - Missing Description:**
```json
{
  "success": false,
  "error": "Description is required",
  "error_code": "VALIDATION_ERROR"
}
```

**400 Bad Request - Missing Rating:**
```json
{
  "success": false,
  "error": "Rating is required",
  "error_code": "VALIDATION_ERROR"
}
```

**400 Bad Request - Invalid Rating:**
```json
{
  "success": false,
  "error": "Rating must be between 1 and 5",
  "error_code": "VALIDATION_ERROR"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to create testimonial: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 2. Get All Verified Testimonials (Public)

**Endpoint:** `GET /testimonials/all`  
**Authentication:** Not Required (Public Endpoint)

#### Description

Retrieves all verified testimonials that are visible to the public. Only testimonials with `is_verified=true` are returned.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Maximum number of testimonials to return |
| `offset` | integer | No | 0 | Number of testimonials to skip |

#### Request Example (cURL)

```bash
# Get first 10 testimonials
curl -X GET "http://localhost:8000/testimonials/all?limit=10&offset=0"

# Get next 10 testimonials
curl -X GET "http://localhost:8000/testimonials/all?limit=10&offset=10"
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Testimonials retrieved successfully",
  "data": [
    {
      "testimonial_id": "550e8400-e29b-41d4-a716-446655440000",
      "user": {
        "user_id": "78109efa-c758-4245-8f42-631ec5e6243e",
        "user_name": "john_doe",
        "profile_picture_url": "https://bucket.s3.region.amazonaws.com/..."
      },
      "description": "This is an amazing app! It has helped me so much in my spiritual journey. Highly recommend to everyone!",
      "rating": 5,
      "media": [
        {
          "media_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
          "media_type": "image",
          "url": "https://bucket.s3.region.amazonaws.com/bible_way/user/testimonial/user_id/testimonial_id/image.jpg",
          "created_at": "2025-12-19T10:30:00.000000+00:00"
        },
        {
          "media_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
          "media_type": "video",
          "url": "https://bucket.s3.region.amazonaws.com/bible_way/user/testimonial/user_id/testimonial_id/video.mp4",
          "created_at": "2025-12-19T10:30:00.000000+00:00"
        }
      ],
      "created_at": "2025-12-19T10:30:00.000000+00:00",
      "updated_at": "2025-12-19T10:30:00.000000+00:00"
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

#### Response Fields

- `testimonial_id` (string): Unique identifier for the testimonial
- `user` (object): User information
  - `user_id` (string): User's unique identifier
  - `user_name` (string): Username
  - `profile_picture_url` (string): URL to user's profile picture (empty string if not set)
- `description` (string): Testimonial text content
- `rating` (integer): Rating value (1-5)
- `media` (array): Array of media objects (empty if no media)
  - `media_id` (string): Unique identifier for the media
  - `media_type` (string): Type of media (`image`, `video`, or `audio`)
  - `url` (string): S3 URL to the media file
  - `created_at` (string): ISO 8601 timestamp
- `created_at` (string): ISO 8601 timestamp when testimonial was created
- `updated_at` (string): ISO 8601 timestamp when testimonial was last updated
- `pagination` (object): Pagination information
  - `limit` (integer): Current limit
  - `offset` (integer): Current offset
  - `total_count` (integer): Total number of verified testimonials
  - `has_next` (boolean): Whether there are more testimonials
  - `has_previous` (boolean): Whether there are previous testimonials

**Note:** The `is_verified` field is NOT included in this response since all returned testimonials are verified.

---

### 3. Get User's Testimonials

**Endpoint:** `GET /testimonial/user/me`  
**Authentication:** Required (JWT)

#### Description

Retrieves all testimonials created by the authenticated user, including both verified and pending testimonials. Users can see their own testimonials regardless of verification status.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Maximum number of testimonials to return |
| `offset` | integer | No | 0 | Number of testimonials to skip |

#### Request Example (cURL)

```bash
curl -X GET "http://localhost:8000/testimonial/user/me?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Testimonials retrieved successfully",
  "data": [
    {
      "testimonial_id": "550e8400-e29b-41d4-a716-446655440000",
      "user": {
        "user_id": "78109efa-c758-4245-8f42-631ec5e6243e",
        "user_name": "john_doe",
        "profile_picture_url": ""
      },
      "description": "This is an amazing app!",
      "rating": 5,
      "is_verified": false,
      "media": [],
      "created_at": "2025-12-19T10:30:00.000000+00:00",
      "updated_at": "2025-12-19T10:30:00.000000+00:00"
    },
    {
      "testimonial_id": "660e8400-e29b-41d4-a716-446655440001",
      "user": {
        "user_id": "78109efa-c758-4245-8f42-631ec5e6243e",
        "user_name": "john_doe",
        "profile_picture_url": ""
      },
      "description": "Great features!",
      "rating": 4,
      "is_verified": true,
      "media": [],
      "created_at": "2025-12-18T10:30:00.000000+00:00",
      "updated_at": "2025-12-18T15:30:00.000000+00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 2,
    "has_next": false,
    "has_previous": false
  }
}
```

#### Response Fields

Same as public endpoint, but includes:
- `is_verified` (boolean): Whether the testimonial has been approved by admin

#### Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve testimonials: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

## Admin Endpoints

All admin endpoints require:
- JWT Authentication
- Admin privileges (`is_staff=True`)

### 4. Get All Testimonials (Admin)

**Endpoint:** `GET /admin/testimonials`  
**Authentication:** Required (JWT + Admin)

#### Description

Retrieves all testimonials with optional status filtering. Admins can see all testimonials regardless of verification status.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Maximum number of testimonials to return |
| `offset` | integer | No | 0 | Number of testimonials to skip |
| `status` | string | No | `all` | Filter by status: `all`, `pending`, or `verified` |

#### Request Example (cURL)

```bash
# Get all testimonials
curl -X GET "http://localhost:8000/admin/testimonials?limit=10&offset=0&status=all" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"

# Get only pending testimonials
curl -X GET "http://localhost:8000/admin/testimonials?limit=10&offset=0&status=pending" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"

# Get only verified testimonials
curl -X GET "http://localhost:8000/admin/testimonials?limit=10&offset=0&status=verified" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Testimonials retrieved successfully",
  "data": [
    {
      "testimonial_id": "550e8400-e29b-41d4-a716-446655440000",
      "user": {
        "user_id": "78109efa-c758-4245-8f42-631ec5e6243e",
        "user_name": "john_doe",
        "profile_picture_url": ""
      },
      "description": "This is an amazing app!",
      "rating": 5,
      "is_verified": false,
      "media": [],
      "created_at": "2025-12-19T10:30:00.000000+00:00",
      "updated_at": "2025-12-19T10:30:00.000000+00:00"
    }
  ],
  "pagination": {
    "limit": 10,
    "offset": 0,
    "total_count": 15,
    "has_next": true,
    "has_previous": false
  }
}
```

#### Response Fields

Same as user endpoint, always includes `is_verified` field.

#### Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden (Not Admin):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**400 Bad Request - Invalid Status Filter:**
```json
{
  "success": false,
  "error": "Status filter must be 'all', 'pending', or 'verified'",
  "error_code": "VALIDATION_ERROR"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve testimonials: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 5. Approve Testimonial (Admin)

**Endpoint:** `POST /admin/testimonial/approve`  
**Authentication:** Required (JWT + Admin)  
**Content-Type:** `application/json`

#### Description

Approves a testimonial, making it visible to the public. Sets `is_verified=true` for the testimonial.

#### Request Body

```json
{
  "testimonial_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `testimonial_id` | string (UUID) | Yes | Unique identifier of the testimonial to approve |

#### Request Example (cURL)

```bash
curl -X POST http://localhost:8000/admin/testimonial/approve \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "testimonial_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Testimonial approved successfully"
}
```

#### Error Responses

**400 Bad Request - Missing testimonial_id:**
```json
{
  "success": false,
  "error": "Testimonial ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden (Not Admin):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": "Testimonial not found",
  "error_code": "TESTIMONIAL_NOT_FOUND"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to approve testimonial: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

### 6. Reject Testimonial (Admin)

**Endpoint:** `POST /admin/testimonial/reject`  
**Authentication:** Required (JWT + Admin)  
**Content-Type:** `application/json`

#### Description

Rejects and permanently deletes a testimonial. The testimonial will be removed from the database and cannot be recovered.

#### Request Body

```json
{
  "testimonial_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `testimonial_id` | string (UUID) | Yes | Unique identifier of the testimonial to reject |

#### Request Example (cURL)

```bash
curl -X POST http://localhost:8000/admin/testimonial/reject \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "testimonial_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Testimonial rejected and deleted successfully"
}
```

#### Error Responses

**400 Bad Request - Missing testimonial_id:**
```json
{
  "success": false,
  "error": "Testimonial ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden (Not Admin):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": "Testimonial not found",
  "error_code": "TESTIMONIAL_NOT_FOUND"
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to reject testimonial: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

## Data Models

### Testimonial Object

```json
{
  "testimonial_id": "550e8400-e29b-41d4-a716-446655440000",
  "user": {
    "user_id": "78109efa-c758-4245-8f42-631ec5e6243e",
    "user_name": "john_doe",
    "profile_picture_url": "https://..."
  },
  "description": "Testimonial text content",
  "rating": 5,
  "is_verified": false,
  "media": [
    {
      "media_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "media_type": "image",
      "url": "https://bucket.s3.region.amazonaws.com/...",
      "created_at": "2025-12-19T10:30:00.000000+00:00"
    }
  ],
  "created_at": "2025-12-19T10:30:00.000000+00:00",
  "updated_at": "2025-12-19T10:30:00.000000+00:00"
}
```

### Field Descriptions

- `testimonial_id` (string, UUID): Unique identifier for the testimonial
- `user` (object): User who created the testimonial
  - `user_id` (string, UUID): User's unique identifier
  - `user_name` (string): Username
  - `profile_picture_url` (string): URL to profile picture (empty string if not set)
- `description` (string): Testimonial text content (required, non-empty)
- `rating` (integer): Rating value from 1 to 5 (required)
- `is_verified` (boolean): Whether testimonial has been approved by admin
  - `false`: Pending approval (not visible to public)
  - `true`: Approved (visible to public)
- `media` (array): Array of media objects (empty array if no media)
  - `media_id` (string, UUID): Unique identifier for the media
  - `media_type` (string): Type of media (`image`, `video`, or `audio`)
  - `url` (string): S3 URL to the media file
  - `created_at` (string): ISO 8601 timestamp
- `created_at` (string): ISO 8601 timestamp when testimonial was created
- `updated_at` (string): ISO 8601 timestamp when testimonial was last updated

---

## Error Responses

### Standard Error Format

All error responses follow this format:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE"
}
```

### Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `VALIDATION_ERROR` | Request validation failed | 400 |
| `TESTIMONIAL_NOT_FOUND` | Testimonial not found | 404 |
| `INTERNAL_ERROR` | Server error | 500 |

### DRF Error Format

Some errors (like authentication) use Django REST Framework's standard format:

```json
{
  "detail": "Error message"
}
```

---

## Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Validation error or invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions (admin required) |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

---

## Media File Support

### Supported Media Types

- **Images:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`
- **Videos:** `.mp4`, `.mov`, `.avi`, `.mkv`
- **Audio:** `.mp3`, `.wav`, `.m4a`, `.aac`

### Media Storage

- All media files are uploaded to AWS S3
- S3 path structure: `bible_way/user/testimonial/{user_id}/{testimonial_id}/{filename}`
- Media URLs are returned in the response and are publicly accessible

### Media Upload Limits

- Maximum file size: Check server configuration (typically 10-50MB)
- Multiple files can be uploaded in a single request
- Each file is processed independently

---

## Workflow Example

### Complete Testimonial Lifecycle

1. **User creates testimonial:**
   ```bash
   POST /testimonial/create
   ```
   - Testimonial created with `is_verified=false`
   - Not visible in public endpoint

2. **User views their testimonials:**
   ```bash
   GET /testimonial/user/me
   ```
   - User can see their testimonial with `is_verified=false`

3. **Admin views all testimonials:**
   ```bash
   GET /admin/testimonials?status=pending
   ```
   - Admin sees pending testimonials

4. **Admin approves testimonial:**
   ```bash
   POST /admin/testimonial/approve
   ```
   - Testimonial `is_verified` set to `true`

5. **Public can now see testimonial:**
   ```bash
   GET /testimonials/all
   ```
   - Approved testimonial is now visible

---

## Rate Limiting

Rate limiting may be applied to prevent abuse. Check server configuration for specific limits.

---

## Versioning

Current API version: **v1.0**

Future versions may introduce breaking changes. Version information will be included in response headers or URL paths if versioning is implemented.

---

## Support

For issues or questions, contact the API support team or refer to the main API documentation.

---

**Document Version:** 1.0  
**Last Updated:** December 19, 2025

