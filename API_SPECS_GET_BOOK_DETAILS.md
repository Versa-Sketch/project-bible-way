# API Specification: Get Book Details

## Overview
This API endpoint retrieves detailed information about a specific book, including whether it is bookmarked by the authenticated user.

---

## Endpoint Details

### URL
```
POST /api/books/details
```

### HTTP Method
`POST`

### Authentication
**Required** - JWT Bearer Token

- **Type**: Bearer Token (JWT)
- **Header**: `Authorization: Bearer <token>`
- The user ID is automatically extracted from the authenticated user's token

---

## Request

### Headers
```
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

### Request Body
```json
{
  "book_id": "string (UUID)"
}
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `book_id` | string (UUID) | Yes | The unique identifier of the book |

### Example Request
```bash
curl -X POST https://your-domain.com/api/books/details \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -d '{
    "book_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

---

## Response

### Success Response (200 OK)

#### Response Structure
```json
{
  "success": true,
  "message": "Book details retrieved successfully",
  "data": {
    "book_id": "string (UUID)",
    "title": "string",
    "description": "string",
    "category_id": "string (UUID)",
    "category_name": "string",
    "age_group_id": "string (UUID)",
    "age_group_name": "string",
    "language_id": "string (UUID)",
    "language_name": "string",
    "cover_image_url": "string (URL)",
    "book_order": "integer",
    "is_active": "boolean",
    "is_bookmarked": "boolean",
    "created_at": "string (ISO 8601 datetime)",
    "updated_at": "string (ISO 8601 datetime)"
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Indicates if the request was successful (always `true` for success) |
| `message` | string | Success message |
| `data` | object | Book details object |
| `data.book_id` | string (UUID) | Unique identifier of the book |
| `data.title` | string | Title of the book |
| `data.description` | string | Description of the book |
| `data.category_id` | string (UUID) | ID of the book category |
| `data.category_name` | string | Display name of the category (e.g., "Segregate Bibles", "BibleReader") |
| `data.age_group_id` | string (UUID) | ID of the age group |
| `data.age_group_name` | string | Display name of the age group (e.g., "Children", "Teen", "Adult 1") |
| `data.language_id` | string (UUID) | ID of the language |
| `data.language_name` | string | Display name of the language (e.g., "English", "Hindi", "Spanish") |
| `data.cover_image_url` | string (URL) | URL of the book's cover image (can be null/empty) |
| `data.book_order` | integer | Display order of the book (can be null) |
| `data.is_active` | boolean | Whether the book is currently active and visible |
| `data.is_bookmarked` | boolean | **Whether the authenticated user has bookmarked this book** |
| `data.created_at` | string (ISO 8601) | Timestamp when the book was created (can be null) |
| `data.updated_at` | string (ISO 8601) | Timestamp when the book was last updated (can be null) |

#### Example Success Response
```json
{
  "success": true,
  "message": "Book details retrieved successfully",
  "data": {
    "book_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "The Holy Bible",
    "description": "Complete text of the Holy Bible",
    "category_id": "223e4567-e89b-12d3-a456-426614174001",
    "category_name": "Segregate Bibles",
    "age_group_id": "323e4567-e89b-12d3-a456-426614174002",
    "age_group_name": "Adult 1",
    "language_id": "423e4567-e89b-12d3-a456-426614174003",
    "language_name": "English",
    "cover_image_url": "https://example.com/images/bible-cover.jpg",
    "book_order": 1,
    "is_active": true,
    "is_bookmarked": true,
    "created_at": "2024-01-15T10:30:00.000000",
    "updated_at": "2024-01-20T14:45:00.000000"
  }
}
```

---

### Error Responses

#### 1. Validation Error (400 Bad Request)

**Case: Missing or Empty book_id**
```json
{
  "success": false,
  "error": "Book ID is required",
  "error_code": "VALIDATION_ERROR"
}
```

**Case: Book Not Found**
```json
{
  "success": false,
  "error": "Book with id 'invalid-uuid' does not exist",
  "error_code": "VALIDATION_ERROR"
}
```

#### 2. Authentication Error (401 Unauthorized)

**Case: Missing or Invalid Token**
```json
{
  "detail": "Authentication credentials were not provided."
}
```
or
```json
{
  "detail": "Given token not valid for any token type"
}
```

#### 3. Internal Server Error (500 Internal Server Error)

```json
{
  "success": false,
  "error": "Failed to retrieve book details: <error message>",
  "error_code": "INTERNAL_ERROR"
}
```

---

## Business Logic

1. **Authentication**: The API requires a valid JWT token. The user ID is extracted from the authenticated user.

2. **Book Retrieval**: The book is fetched using `book_id` with related data (category, age_group, language) pre-loaded using `select_related()` for performance.

3. **Bookmark Status**: The API checks if the authenticated user has bookmarked the book by querying the bookmarks table. The `is_bookmarked` field in the response reflects this status.

4. **Null Handling**: All foreign key relationships (category, age_group, language) are checked for null values before accessing their properties to prevent errors.

---

## Data Models

### Book Model Fields Used
- `book_id` (UUID, Primary Key)
- `title` (CharField)
- `description` (TextField)
- `category` (ForeignKey → Category)
- `age_group` (ForeignKey → AgeGroup)
- `language` (ForeignKey → Language)
- `cover_image_url` (URLField, nullable)
- `book_order` (IntegerField, nullable)
- `is_active` (BooleanField)
- `created_at` (DateTimeField, auto)
- `updated_at` (DateTimeField, auto)

### Related Models
- **Category**: Provides `category_id` and `category_name` (via `get_category_name_display()`)
- **AgeGroup**: Provides `age_group_id` and `age_group_name` (via `get_age_group_name_display()`)
- **Language**: Provides `language_id` and `language_name` (via `get_language_name_display()`)
- **Bookmark**: Used to determine `is_bookmarked` status

---

## Usage Examples

### JavaScript (Fetch API)
```javascript
const getBookDetails = async (bookId, token) => {
  const response = await fetch('https://your-domain.com/api/books/details', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      book_id: bookId
    })
  });
  
  const data = await response.json();
  return data;
};

// Usage
const bookDetails = await getBookDetails('123e4567-e89b-12d3-a456-426614174000', 'your_jwt_token');
console.log(bookDetails.data.is_bookmarked); // true or false
```

### Python (requests)
```python
import requests

def get_book_details(book_id, token):
    url = 'https://your-domain.com/api/books/details'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'book_id': book_id
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Usage
book_details = get_book_details('123e4567-e89b-12d3-a456-426614174000', 'your_jwt_token')
print(book_details['data']['is_bookmarked'])  # True or False
```

---

## Implementation Files

1. **Interactor**: `bible_way/interactors/get_book_details_interactor.py`
2. **Presenter**: `bible_way/presenters/get_book_details_response.py`
3. **View**: `bible_way/views.py` (function: `get_book_details_view`)
4. **URL Route**: `bible_way_backend/urls.py` (route: `books/details`)
5. **Storage**: Uses existing methods from `bible_way/storage/storage_implementation.py`:
   - `get_book_by_id(book_id)`
   - `get_bookmark_by_user_and_book(user_id, book_id)`

---

## Notes

- The `is_bookmarked` field is dynamic and depends on the authenticated user
- All UUIDs are returned as strings
- Datetimes are returned in ISO 8601 format
- Nullable fields (category, age_group, language) will return `null` if not set
- The API follows the existing codebase patterns (Interactor-Presenter-Storage architecture)

---

## Testing Checklist

- [ ] Successfully retrieve book details with valid book_id
- [ ] Verify `is_bookmarked` is `true` when user has bookmarked the book
- [ ] Verify `is_bookmarked` is `false` when user has not bookmarked the book
- [ ] Handle missing `book_id` parameter (400 error)
- [ ] Handle empty `book_id` parameter (400 error)
- [ ] Handle invalid `book_id` (non-existent UUID) (400 error)
- [ ] Handle missing authentication token (401 error)
- [ ] Handle invalid/expired token (401 error)
- [ ] Verify all book fields are returned correctly
- [ ] Verify related model names (category_name, age_group_name, language_name) are display names, not internal values

