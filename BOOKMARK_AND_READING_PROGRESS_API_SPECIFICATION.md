# Bookmark and Reading Progress API Specification

## Base URL
All endpoints require JWT authentication via `JWTAuthentication` and `IsAuthenticated` permission.

---

## 1. Create Bookmark

**Endpoint:** `POST /bookmark/create`

**Description:** Creates a bookmark for a book. A user can only have one bookmark per book. If a bookmark already exists, returns an error.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
    "book_id": "string (required)"
}
```

**Request Parameters:**
- `book_id` (string, required): The UUID of the book to bookmark

**Success Response (201 Created):**
```json
{
    "success": true,
    "message": "Bookmark created successfully",
    "bookmark_id": "uuid-string"
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**
```json
{
    "success": false,
    "error": "book_id is required",
    "error_code": "VALIDATION_ERROR"
}
```

**400 Bad Request - Already Bookmarked:**
```json
{
    "success": false,
    "error": "already book_marked",
    "error_code": "ALREADY_BOOKMARKED"
}
```

**404 Not Found - Book Not Found:**
```json
{
    "success": false,
    "error": "Book not found",
    "error_code": "BOOK_NOT_FOUND"
}
```

**400 Bad Request - User Not Found:**
```json
{
    "success": false,
    "error": "User not found",
    "error_code": "VALIDATION_ERROR"
}
```

**500 Internal Server Error:**
```json
{
    "success": false,
    "error": "Failed to create bookmark: <error_message>",
    "error_code": "INTERNAL_ERROR"
}
```

---

## 2. Get All Bookmarks

**Endpoint:** `GET /bookmark/all`

**Description:** Retrieves all bookmarks for the authenticated user, including book details and reading progress.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Bookmarks retrieved successfully",
    "bookmarks": [
        {
            "bookmark_id": "uuid-string",
            "book_id": "uuid-string",
            "book_title": "string",
            "progress_percentage": "0.00",
            "block_id": "uuid-string or null",
            "book_details": {
                "book_id": "uuid-string",
                "title": "string",
                "description": "string",
                "cover_image_url": "string",
                "category_id": "uuid-string or null",
                "category_name": "string or null",
                "age_group_id": "uuid-string or null",
                "age_group_name": "string or null",
                "language_id": "uuid-string or null",
                "language_name": "string or null",
                "book_order": 0,
                "is_active": true
            },
            "created_at": "ISO 8601 datetime string",
            "updated_at": "ISO 8601 datetime string"
        }
    ]
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**
```json
{
    "success": false,
    "error": "user_id is required",
    "error_code": "VALIDATION_ERROR"
}
```

**500 Internal Server Error:**
```json
{
    "success": false,
    "error": "Failed to retrieve bookmarks: <error_message>",
    "error_code": "INTERNAL_ERROR"
}
```

---

## 3. Delete Bookmark

**Endpoint:** `POST /bookmark/delete`

**Description:** Deletes a bookmark. Only the owner of the bookmark can delete it.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
    "bookmark_id": "string (required)"
}
```

**Request Parameters:**
- `bookmark_id` (string, required): The UUID of the bookmark to delete

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Bookmark deleted successfully"
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**
```json
{
    "success": false,
    "error": "bookmark_id is required",
    "error_code": "VALIDATION_ERROR"
}
```

**404 Not Found - Bookmark Not Found:**
```json
{
    "success": false,
    "error": "Bookmark not found",
    "error_code": "BOOKMARK_NOT_FOUND"
}
```

**403 Forbidden - Unauthorized:**
```json
{
    "success": false,
    "error": "You are not authorized to delete this bookmark",
    "error_code": "UNAUTHORIZED"
}
```

**500 Internal Server Error:**
```json
{
    "success": false,
    "error": "Failed to delete bookmark: <error_message>",
    "error_code": "INTERNAL_ERROR"
}
```

---

## 4. Create/Update Reading Progress

**Endpoint:** `POST /reading-progress/create`

**Description:** Creates or updates reading progress for a book. If progress already exists for the user and book, it will be updated.

**Request Headers:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Request Body:**
```json
{
    "book_id": "string (required)",
    "chapter_id": "string (optional)",
    "progress_percentage": 0.0,
    "block_id": "string (optional)"
}
```

**Request Parameters:**
- `book_id` (string, required): The UUID of the book
- `chapter_id` (string, optional): The UUID of the chapter
- `progress_percentage` (float, required): Progress percentage (0.0 to 100.0)
- `block_id` (string, optional): The UUID of the block

**Success Response (200 OK):**
```json
{
    "success": true,
    "message": "Reading progress updated successfully",
    "progress_percentage": "0.0"
}
```

**Error Responses:**

**400 Bad Request - Validation Error:**
```json
{
    "success": false,
    "error": "book_id is required",
    "error_code": "VALIDATION_ERROR"
}
```

**400 Bad Request - Progress Percentage Validation:**
```json
{
    "success": false,
    "error": "progress_percentage is required",
    "error_code": "VALIDATION_ERROR"
}
```

or

```json
{
    "success": false,
    "error": "progress_percentage must be between 0 and 100",
    "error_code": "VALIDATION_ERROR"
}
```

or

```json
{
    "success": false,
    "error": "progress_percentage must be a valid number",
    "error_code": "VALIDATION_ERROR"
}
```

**404 Not Found - Book Not Found:**
```json
{
    "success": false,
    "error": "Book not found",
    "error_code": "BOOK_NOT_FOUND"
}
```

**404 Not Found - Chapter Not Found:**
```json
{
    "success": false,
    "error": "Chapter not found",
    "error_code": "CHAPTER_NOT_FOUND"
}
```

**400 Bad Request - User Not Found:**
```json
{
    "success": false,
    "error": "User not found",
    "error_code": "VALIDATION_ERROR"
}
```

**500 Internal Server Error:**
```json
{
    "success": false,
    "error": "Failed to update reading progress: <error_message>",
    "error_code": "INTERNAL_ERROR"
}
```

---

## Notes

1. **Authentication:** All endpoints require JWT authentication. The user ID is automatically extracted from the JWT token.

2. **Bookmark Uniqueness:** Each user can only have one bookmark per book. Attempting to create a duplicate bookmark will return an `ALREADY_BOOKMARKED` error.

3. **Reading Progress:** The reading progress endpoint creates a new progress record if one doesn't exist, or updates the existing one if it does.

4. **Authorization:** Users can only delete their own bookmarks. Attempting to delete another user's bookmark will return an `UNAUTHORIZED` error.

5. **Data Types:**
   - UUIDs are represented as strings
   - Progress percentage is a float between 0.0 and 100.0
   - Datetime fields are in ISO 8601 format
   - Optional fields may be `null` in responses

