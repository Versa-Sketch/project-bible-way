# Books API Specification

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

## 1. Category APIs

### 1.1 Admin Create Category
**Endpoint:** `POST /admin/category/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `category_name` (string, required) - Category name. Must be one of: `SEGREGATE_BIBLES`, `NORMAL_BIBLES`
- `cover_image` (file, optional) - Cover image file for the category
- `description` (string, optional) - Description of the category
- `display_order` (integer, optional, default: 0) - Order for displaying categories in dashboard

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
  "error": "Invalid category name. Must be one of: SEGREGATE_BIBLES, NORMAL_BIBLES",
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

### 1.2 Admin Get All Categories
**Endpoint:** `GET /admin/categories`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Description:**
This endpoint allows admins to retrieve all categories. Returns all categories regardless of their status, ordered by `display_order` and then by `category_name`.

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
    },
    {
      "category_id": "uuid-string",
      "category_name": "NORMAL_BIBLES",
      "display_name": "Normal Bibles",
      "cover_image_url": "https://s3.amazonaws.com/bucket/categories/cover_images/...",
      "description": "Bibles with same content for all age groups",
      "display_order": 1,
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

**Note:** Categories are ordered by `display_order` and then by `category_name`. This endpoint returns all categories, including those that may not be active.

---

### 1.3 Get All Categories
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
    },
    {
      "category_id": "uuid-string",
      "category_name": "NORMAL_BIBLES",
      "display_name": "Normal Bibles",
      "cover_image_url": "https://s3.amazonaws.com/bucket/categories/cover_images/...",
      "description": "Bibles with same content for all age groups",
      "display_order": 1,
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

**Note:** Categories are ordered by `display_order` and then by `category_name`.

---

## 2. Age Group APIs

### 2.1 Admin Create Age Group
**Endpoint:** `POST /admin/age-group/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
- `age_group_name` (string, required) - Age group name. Must be one of: `CHILD`, `TEEN`, `ADULT`, `SENIOR`, `ALL`
- `cover_image` (file, optional) - Cover image file for the age group
- `description` (string, optional) - Description of the age group
- `display_order` (integer, optional, default: 0) - Order for displaying age groups in dashboard

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

- **400 Bad Request** - Invalid age group name:
```json
{
  "success": false,
  "error": "Invalid age group name. Must be one of: CHILD, TEEN, ADULT, SENIOR, ALL",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Age group already exists:
```json
{
  "success": false,
  "error": "Age group 'CHILD' already exists",
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

### 2.2 Admin Get All Age Groups
**Endpoint:** `GET /admin/age-groups`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Description:**
This endpoint allows admins to retrieve all age groups. Returns all age groups regardless of their status, ordered by `display_order` and then by `age_group_name`.

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
    },
    {
      "age_group_id": "uuid-string",
      "age_group_name": "TEEN",
      "display_name": "Teen",
      "cover_image_url": "https://s3.amazonaws.com/bucket/age_groups/cover_images/...",
      "description": "Books for teenagers",
      "display_order": 1,
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

**Note:** Age groups are ordered by `display_order` and then by `age_group_name`. This endpoint returns all age groups, including those that may not be active.

---

### 2.3 Get All Age Groups
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
    },
    {
      "age_group_id": "uuid-string",
      "age_group_name": "TEEN",
      "display_name": "Teen",
      "cover_image_url": "https://s3.amazonaws.com/bucket/age_groups/cover_images/...",
      "description": "Books for teenagers",
      "display_order": 1,
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

**Note:** Age groups are ordered by `display_order` and then by `age_group_name`.

---

## 3. Language APIs

### 3.1 Admin Get All Languages
**Endpoint:** `GET /admin/languages`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Description:**
This endpoint allows admins to retrieve all available languages. Languages are used to categorize books by their language.

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

**Note:** Languages are typically predefined in the system. This endpoint returns all available languages that can be used when creating books.

---

## 4. Book APIs

### 4.1 Admin Create Book
**Endpoint:** `POST /admin/book/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Description:**
This endpoint allows admins to create a book by uploading a source file (markdown file). The system uploads the source file and cover image to S3 and creates a book record in the database.

**Request Body (Form Data):**
- `title` (string, required) - Book title
- `category` (string, required) - UUID of the category
- `age_group` (string, required) - UUID of the age group
- `language` (string, required) - UUID of the language
- `source_file` (file, required) - Source file (.md markdown file) containing the book content
- `cover_image` (file, optional) - Cover image file for the book
- `description` (string, optional) - Description of the book
- `book_order` (integer, optional, default: 0) - Order for displaying books

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Book created successfully",
  "data": {
    "book_id": "uuid-string",
    "source_file_url": "https://s3.amazonaws.com/bucket/books/{book_id_preview}/source_files/...",
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
  "error": "Title is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Source file required:
```json
{
  "success": false,
  "error": "Source file (.md file) is required",
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

- **400 Bad Request** - Language not found:
```json
{
  "success": false,
  "error": "Language with id '<language_id>' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Failed to upload source file: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

- **500 Internal Server Error** - Cover image upload error:
```json
{
  "success": false,
  "error": "Failed to upload cover image: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

- **500 Internal Server Error** - Book creation error:
```json
{
  "success": false,
  "error": "Failed to create book: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Source file and cover image are uploaded to S3
- Source files are stored in: `books/{book_id_preview}/source_files/`
- Cover images are stored in: `books/{book_id_preview}/cover_images/`
- The `book_id_preview` is a randomly generated hex string used for S3 folder structure
- The `book_order` parameter is automatically converted to an integer (defaults to 0 if invalid)
- After creation, you can update book metadata using the update metadata endpoint
- The `source_file_name` field is automatically extracted from the uploaded file and stored in the database

---

### 4.2 Get Books by Category and Age Group
**Endpoint:** `GET /books/category/<category_id>/age-group/<age_group_id>/books/`  
**Authentication:** Required (JWT)

**Path Parameters:**
- `category_id` (string, required) - UUID of the category
- `age_group_id` (string, required) - UUID of the age group

**Query Parameters:**
- `language_id` (string, optional) - UUID of the language (filters books by language)

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Books retrieved successfully",
  "data": [
    {
      "book_id": "uuid-string",
      "title": "The Book of Genesis",
      "cover_image_url": "https://s3.amazonaws.com/bucket/books/cover_images/...",
      "book_order": 1
    },
    {
      "book_id": "uuid-string",
      "title": "The Book of Exodus",
      "cover_image_url": "https://s3.amazonaws.com/bucket/books/cover_images/...",
      "book_order": 2
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

- **400 Bad Request** - Category not found:
```json
{
  "success": false,
  "error": "Category with id '<category_id>' not found",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Age group not found:
```json
{
  "success": false,
  "error": "Age group with id '<age_group_id>' not found",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Language not found:
```json
{
  "success": false,
  "error": "Language with id '<language_id>' not found",
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

**Notes:**
- Only active books (`is_active=true`) are returned
- Books are ordered by `book_order` and then by `title`
- If `language_id` is provided, only books in that language are returned
- Response does not include pagination
- Response includes minimal book information (book_id, title, cover_image_url, book_order)

---

### 4.3 Admin Update Book Metadata
**Endpoint:** `POST /admin/book/update-metadata`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Description:**
This endpoint allows admins to update the metadata field of an existing book. The metadata field is a JSON object that can store additional information about the book.

**Request Body:**
```json
{
  "book_id": "uuid-string (required)",
  "metadata": {
    "key1": "value1",
    "key2": "value2"
  }
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

- **400 Bad Request** - Book ID required:
```json
{
  "success": false,
  "error": "Book ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Metadata required:
```json
{
  "success": false,
  "error": "Metadata is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid metadata format:
```json
{
  "success": false,
  "error": "Metadata must be a valid JSON object",
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
  "error": "Failed to update book metadata: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- The `metadata` field must be a valid JSON object (dictionary)
- The metadata is stored as a JSON field in the database
- This endpoint only updates the metadata field; other book fields are not modified
- Use this endpoint to store additional structured information about the book

---

### 4.4 Admin Get All Books
**Endpoint:** `GET /admin/books`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)

**Description:**
This endpoint allows admins to retrieve all books with complete details. Returns all books regardless of their active status, ordered by creation date (newest first). Includes full book information with related category, age group, and language details.

**Query Parameters:**
- `limit` (integer, optional, max: 100) - Number of books to return. If not provided or invalid, returns all books
- `offset` (integer, optional, default: 0) - Number of books to skip for pagination

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Books retrieved successfully",
  "data": [
    {
      "book_id": "uuid-string",
      "title": "The Book of Genesis",
      "description": "First book of the Bible",
      "category_id": "uuid-string",
      "category_name": "NORMAL_BIBLES",
      "category_display_name": "Normal Bibles",
      "age_group_id": "uuid-string",
      "age_group_name": "ALL",
      "age_group_display_name": "All",
      "language_id": "uuid-string",
      "language_name": "EN",
      "language_display_name": "English",
      "cover_image_url": "https://s3.amazonaws.com/bucket/books/cover_images/...",
      "book_order": 1,
      "is_active": true,
      "source_file_url": "https://s3.amazonaws.com/bucket/books/source_files/...",
      "metadata": {},
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 50,
  "pagination": {
    "limit": 20,
    "offset": 0,
    "has_next": true,
    "has_previous": false
  }
}
```

**Response Fields:**
- `book_id` (string) - Unique book identifier
- `title` (string) - Book title
- `description` (string) - Book description (empty string if not set)
- `category_id` (string) - UUID of the category
- `category_name` (string) - Category name (e.g., "NORMAL_BIBLES", "SEGREGATE_BIBLES")
- `category_display_name` (string) - Human-readable category name (e.g., "Normal Bibles")
- `age_group_id` (string) - UUID of the age group
- `age_group_name` (string) - Age group name (e.g., "ALL", "CHILD", "TEEN", "ADULT", "SENIOR")
- `age_group_display_name` (string) - Human-readable age group name (e.g., "All", "Child")
- `language_id` (string) - UUID of the language
- `language_name` (string) - Language code (e.g., "EN", "ES", "FR")
- `language_display_name` (string) - Human-readable language name (e.g., "English", "Spanish")
- `cover_image_url` (string) - URL to book cover image (empty string if not set)
- `book_order` (integer) - Display order for the book
- `is_active` (boolean) - Whether the book is active
- `source_file_url` (string) - URL to the source file (empty string if not set)
- `metadata` (object) - Additional metadata as JSON object (empty object if not set)
- `created_at` (string) - Creation timestamp in ISO 8601 format
- `updated_at` (string) - Last update timestamp in ISO 8601 format
- `total_count` (integer) - Total number of books available
- `pagination` (object, optional) - Pagination information (only included if `limit` is provided)
  - `limit` (integer) - Number of books per page
  - `offset` (integer) - Current offset
  - `has_next` (boolean) - Whether there are more books after the current page
  - `has_previous` (boolean) - Whether there are books before the current page

**Error Responses:**
- **403 Forbidden** - Not admin:
```json
{
  "detail": "You do not have permission to perform this action."
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
  "error": "Failed to retrieve books: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Books are ordered by creation date (newest first) by default
- Returns all books including inactive ones (for admin management purposes)
- If `limit` is not provided, all books are returned
- Maximum `limit` is 100; values greater than 100 are automatically capped at 100
- Pagination information is only included in the response if `limit` is provided
- All related objects (category, age_group, language) are included in the response
- This endpoint is optimized with `select_related()` to avoid N+1 query issues

---

## 5. Highlight APIs

### 5.1 Create Highlight
**Endpoint:** `POST /highlight/create`  
**Authentication:** Required (JWT)

**Description:**
This endpoint allows users to create a highlight for a specific book. Highlights can be associated with a chapter (optional) and have start and end offsets to mark specific text ranges.

**Request Body:**
```json
{
  "book_id": "uuid-string (required)",
  "chapter_id": "uuid-string (optional)",
  "start_offset": "string (required)",
  "end_offset": "string (required)",
  "color": "string (optional, default: 'yellow')"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Highlight saved successfully",
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

- **400 Bad Request** - Validation error:
```json
{
  "success": false,
  "error": "book_id is required",
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
  "error": "Failed to create highlight: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- The `user_id` is automatically extracted from the authenticated user's token
- `chapter_id` is optional; highlights can be created without a specific chapter
- `color` defaults to "yellow" if not provided
- `start_offset` and `end_offset` are required to mark the text range

---

### 5.2 Update Highlight
**Endpoint:** `PUT /highlight/update` or `PATCH /highlight/update`  
**Authentication:** Required (JWT)

**Description:**
This endpoint allows users to update an existing highlight. Only the highlight owner can update their highlights. If a chapter_id is provided and doesn't exist, it will be created.

**Request Body:**
```json
{
  "highlight_id": "uuid-string (required)",
  "book_id": "uuid-string (required)",
  "chapter_id": "uuid-string (optional)",
  "start_offset": "string (optional)",
  "end_offset": "string (optional)"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Highlight updated successfully"
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

- **403 Forbidden** - Unauthorized:
```json
{
  "success": false,
  "error": "You are not authorized to update this highlight",
  "error_code": "UNAUTHORIZED"
}
```

- **500 Internal Server Error:**
```json
{
  "success": false,
  "error": "Failed to update highlight: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- The `user_id` is automatically extracted from the authenticated user's token
- Only the highlight owner can update their highlights
- All fields except `highlight_id` and `book_id` are optional
- If `chapter_id` is provided and doesn't exist, it will be created
- Only provided fields will be updated; omitted fields remain unchanged

---

### 5.3 Get Highlights by Book
**Endpoint:** `GET /highlight/book/<book_id>`  
**Authentication:** Required (JWT)

**Description:**
This endpoint retrieves all highlights for a specific book. Optionally, you can filter highlights by a specific user ID using a query parameter. If no user_id is provided, it returns highlights for the authenticated user.

**Path Parameters:**
- `book_id` (string, required) - UUID of the book

**Query Parameters:**
- `user_id` (string, optional) - UUID of the user to filter highlights. If not provided, defaults to the authenticated user

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Highlights retrieved successfully",
  "data": [
    {
      "highlight_id": "uuid-string",
      "book_id": "uuid-string",
      "chapter_id": "uuid-string",
      "start_offset": "string",
      "end_offset": "string",
      "color": "yellow",
      "created_at": "2024-01-01T12:00:00",
      "updated_at": "2024-01-01T12:00:00"
    }
  ]
}
```

**Response Fields:**
- `highlight_id` (string) - Unique highlight identifier
- `book_id` (string) - UUID of the book
- `chapter_id` (string or null) - UUID of the chapter (null if not associated with a chapter)
- `start_offset` (string) - Start position of the highlighted text
- `end_offset` (string) - End position of the highlighted text
- `color` (string) - Color of the highlight
- `created_at` (string) - Creation timestamp in ISO 8601 format
- `updated_at` (string) - Last update timestamp in ISO 8601 format

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
- Highlights are ordered by creation date (newest first)
- If `user_id` query parameter is not provided, highlights for the authenticated user are returned
- If `user_id` is provided, highlights for that specific user are returned
- `chapter_id` may be null if the highlight is not associated with a specific chapter

---

## Common Error Codes

| Error Code | Description |
|------------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `CATEGORY_NOT_FOUND` | Category does not exist |
| `AGE_GROUP_NOT_FOUND` | Age group does not exist |
| `LANGUAGE_NOT_FOUND` | Language does not exist |
| `BOOK_NOT_FOUND` | Book does not exist |
| `S3_UPLOAD_ERROR` | Failed to upload file to S3 storage |
| `INTERNAL_ERROR` | Internal server error |

---

## Notes

1. **JWT Token Format:** All authenticated endpoints require a JWT token in the Authorization header:
   ```
   Authorization: Bearer <access_token>
   ```

2. **File Uploads:** 
   - Cover images and source files are uploaded to S3
   - Cover images are stored in: `categories/cover_images/`, `age_groups/cover_images/`, `books/{book_id_preview}/cover_images/`
   - Source files are stored in: `books/{book_id_preview}/source_files/`
   - The `book_id_preview` is a randomly generated hex string used for organizing files in S3

4. **Category Types:**
   - `SEGREGATE_BIBLES`: Different content for different age groups (child, teen, adult, senior)
   - `NORMAL_BIBLES`: Same content for all age groups (age_group='ALL')

5. **Age Groups:**
   - `CHILD`: Books for children
   - `TEEN`: Books for teenagers
   - `ADULT`: Books for adults
   - `SENIOR`: Books for seniors
   - `ALL`: Books for all age groups (used in normal Bibles)

6. **Base URL:** Replace `http://localhost:8000/` with your actual server URL in production.

7. **Date Formats:** All datetime fields are returned in ISO 8601 format.

8. **Error Responses:** All error responses follow a consistent format with `success: false`, `error` message, and `error_code`.

9. **Chapter Content:** Use a separate endpoint (to be implemented) to fetch full chapter content by `book_content_id`.

10. **Book Creation:** When creating a book, only the basic book record is created. The source file is uploaded to S3, but parsing and chapter extraction are handled separately (if needed).

11. **Metadata Field:** The book metadata field is a JSON object that can store additional structured information. Use the Update Book Metadata endpoint to modify this field.

