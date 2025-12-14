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

### 1.2 Get All Categories
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

### 2.2 Get All Age Groups
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

## 3. Book APIs

### 3.1 Admin Create Book
**Endpoint:** `POST /admin/book/create`  
**Authentication:** Required (JWT)  
**Permission:** Admin only (`is_staff=True`)  
**Content-Type:** `multipart/form-data`

**Description:**
This endpoint allows admins to create a book by uploading a markdown file. The system automatically:
- Detects the book title from the markdown file (if not provided)
- Parses chapters from the markdown file using multiple pattern detection
- Extracts chapter numbers, titles, and content
- Uploads the markdown file and cover image to S3
- Creates book and chapter records in the database

**Request Body (Form Data):**
- `markdown_file` (file, required) - Markdown file (.md) containing the book content
- `category_id` (string, required) - UUID of the category
- `age_group_id` (string, required) - UUID of the age group
- `language_id` (string, required) - UUID of the language
- `title` (string, optional) - Book title (if not provided, will be auto-detected from markdown)
- `cover_image` (file, optional) - Cover image file for the book
- `description` (string, optional) - Description of the book
- `author` (string, optional) - Author of the book
- `book_order` (integer, optional, default: 0) - Order for displaying books
- `metadata` (string, optional) - JSON string for additional metadata

**Markdown File Format:**
The parser supports multiple markdown formats and automatically detects:
- Bible format: `__[Chapter Name]__ {verse:number} content...`
- Standard headings: `# Chapter 1` or `## Chapter 1`
- Numbered headings: `## 1. Chapter Title`
- Bracketed format: `[Chapter 1]` or `[1] Chapter Title`
- Generic numbered lists

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Book created successfully",
  "data": {
    "book_id": "uuid-string",
    "title": "The Book of Genesis",
    "description": "First book of the Bible",
    "category_id": "uuid-string",
    "category_name": "NORMAL_BIBLES",
    "age_group_id": "uuid-string",
    "age_group_name": "ALL",
    "language_id": "uuid-string",
    "language_name": "EN",
    "cover_image_url": "https://s3.amazonaws.com/bucket/books/cover_images/...",
    "author": "Moses",
    "book_order": 1,
    "total_chapters": 50,
    "is_parsed": true,
    "is_active": true,
    "source_file_name": "genesis.md",
    "source_file_url": "https://s3.amazonaws.com/bucket/books/markdown/...",
    "metadata": {},
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "parsing_info": {
      "detected_title": "The Book of Genesis",
      "detected_pattern": "BIBLE_FORMAT",
      "total_chapters": 50,
      "parsing_method": "auto_detection"
    }
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
  "error": "Markdown file is required",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid file type:
```json
{
  "success": false,
  "error": "File must be a .md (markdown) file",
  "error_code": "VALIDATION_ERROR"
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

- **400 Bad Request** - No chapters detected:
```json
{
  "success": false,
  "error": "No chapters detected in markdown file. Please ensure the file contains chapter markers.",
  "error_code": "VALIDATION_ERROR"
}
```

- **400 Bad Request** - Invalid metadata JSON:
```json
{
  "success": false,
  "error": "Invalid JSON format for metadata",
  "error_code": "VALIDATION_ERROR"
}
```

- **500 Internal Server Error** - S3 upload error:
```json
{
  "success": false,
  "error": "Failed to upload markdown file to S3: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

- **500 Internal Server Error** - Parsing error:
```json
{
  "success": false,
  "error": "Failed to parse markdown file: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- The markdown parser automatically detects book title and chapter patterns
- Chapters are extracted and stored as separate `BookContent` records
- The book's `is_parsed` flag is set to `true` after successful parsing
- `total_chapters` is automatically calculated and stored
- Markdown file and cover image are stored in separate S3 folders

---

### 3.2 Get Books by Category and Age Group
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
      "book_order": 1,
      "total_chapters": 50,
      "is_active": true
    },
    {
      "book_id": "uuid-string",
      "title": "The Book of Exodus",
      "cover_image_url": "https://s3.amazonaws.com/bucket/books/cover_images/...",
      "book_order": 2,
      "total_chapters": 40,
      "is_active": true
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
  "error": "Category not found",
  "error_code": "CATEGORY_NOT_FOUND"
}
```

- **400 Bad Request** - Age group not found:
```json
{
  "success": false,
  "error": "Age group not found",
  "error_code": "AGE_GROUP_NOT_FOUND"
}
```

- **400 Bad Request** - Language not found:
```json
{
  "success": false,
  "error": "Language not found",
  "error_code": "LANGUAGE_NOT_FOUND"
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

---

### 3.3 Get Book Details
**Endpoint:** `GET /books/<book_id>/`  
**Authentication:** Required (JWT)

**Path Parameters:**
- `book_id` (string, required) - UUID of the book

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Book details retrieved successfully",
  "data": {
    "book": {
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
      "author": "Moses",
      "book_order": 1,
      "total_chapters": 50,
      "is_parsed": true,
      "is_active": true,
      "source_file_name": "genesis.md",
      "source_file_url": "https://s3.amazonaws.com/bucket/books/markdown/...",
      "metadata": {},
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "chapters": [
      {
        "book_content_id": "uuid-string",
        "chapter_number": 1,
        "chapter_title": "Genesis 1",
        "content_order": 1,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      },
      {
        "book_content_id": "uuid-string",
        "chapter_number": 2,
        "chapter_title": "Genesis 2",
        "content_order": 2,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ]
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
  "error": "Failed to retrieve book details: <error_message>",
  "error_code": "INTERNAL_ERROR"
}
```

**Notes:**
- Only active books are returned (inactive books return 404)
- Chapters list includes metadata only (no full content)
- Chapters are ordered by `content_order` and then by `chapter_number`
- Use `book_content_id` from chapters to fetch individual chapter content (separate endpoint)
- Related objects (category, age_group, language) are included with display names

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
   - Cover images and markdown files are uploaded to S3
   - Cover images are stored in: `categories/cover_images/`, `age_groups/cover_images/`, `books/cover_images/`
   - Markdown files are stored in: `books/markdown/{book_id}/`

3. **Markdown Parsing:**
   - The parser automatically detects book titles and chapter patterns
   - Supports multiple markdown formats (Bible format, standard headings, numbered headings, etc.)
   - Chapters are extracted and stored as separate database records
   - Book's `is_parsed` flag indicates successful parsing

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

9. **Chapter Content:** The book details endpoint returns chapter metadata only. Use a separate endpoint (to be implemented) to fetch full chapter content by `book_content_id`.

