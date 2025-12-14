# Project Chat - Complete API Specification

## Overview

The Project Chat API provides real-time chat functionality via WebSocket connections. All communication is done through WebSocket messages using JSON format. File uploads are handled via HTTP REST API endpoints.

**WebSocket Base URL:** `ws://your-domain/ws/user/`

**HTTP Base URL:** `http://your-domain/`

**Authentication:** JWT token passed as query parameter for WebSocket: `?token=<JWT_TOKEN>` or in Authorization header for HTTP endpoints: `Bearer <JWT_TOKEN>`

---

## Table of Contents

1. [Connection](#connection)
2. [File Upload (HTTP)](#file-upload-http)
3. [Message Format](#message-format)
4. [Actions](#actions)
5. [Broadcasts](#broadcasts)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Data Models](#data-models)

---

## Connection

### WebSocket Endpoint

**URL:** `ws://your-domain/ws/user/?token=<JWT_TOKEN>`

**Authentication:**
- JWT token must be provided in the query string
- Token must be valid and not expired
- User must exist in the system

### Connection Established

Upon successful connection, the server sends:

```json
{
  "type": "connection.established",
  "data": {
    "user_id": "uuid-string",
    "message": "WebSocket connection established"
  }
}
```

### Connection Errors

- **401 Unauthorized**: Invalid or missing token
- **403 Forbidden**: Token expired or user not found
- **Connection Closed**: Server closes connection on authentication failure

---

## File Upload (HTTP)

### HTTP POST `/api/chat/upload/`

Upload files (images, videos, audio) for chat messages via HTTP before sending them in WebSocket messages.

**Request:**
- Method: POST
- Content-Type: `multipart/form-data`
- Authentication: JWT token in `Authorization` header: `Bearer <JWT_TOKEN>`
- Body:
  - `file` (required): File to upload (image, video, or audio)
  - `conversation_id` (optional): Conversation ID for organizing files

**Response (Success - 200 OK):**
```json
{
  "success": true,
  "data": {
    "file_url": "https://bucket.s3.region.amazonaws.com/chat/files/user-uuid/uuid/filename.jpg",
    "file_type": "IMAGE",
    "file_size": 245678,
    "file_name": "photo.jpg"
  }
}
```

**Response (Error - 400 Bad Request):**
```json
{
  "success": false,
  "error": "File size exceeds 10 MB limit",
  "error_code": "FILE_TOO_LARGE"
}
```

**Supported File Types:**
- **Images:** jpg, jpeg, png, gif, webp, bmp
- **Videos:** mp4, mov, avi, mkv, webm, flv, wmv, m4v
- **Audio:** mp3, wav, ogg, m4a, aac, flac, wma

**File Size Limit:** 10 MB (10,485,760 bytes)

**Error Codes:**
- `VALIDATION_ERROR`: Missing or invalid file
- `FILE_TOO_LARGE`: File size exceeds 10 MB limit
- `INVALID_FILE_TYPE`: File type not supported
- `FILE_UPLOAD_FAILED`: Failed to upload file to S3
- `SERVER_ERROR`: Internal server error

**Example Usage:**
```bash
curl -X POST http://your-domain/api/chat/upload/ \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "file=@photo.jpg" \
  -F "conversation_id=1"
```

**S3 Storage Structure:**
Files are stored at: `chat/files/{user_id}/{uuid}/{filename}`

---

## Message Format

### Request Format

All client requests must follow this format:

```json
{
  "action": "action_name",
  "request_id": "unique-uuid-string",
  "field1": "value1",
  "field2": "value2"
}
```

**Required Fields:**
- `action` (string): The action to perform
- `request_id` (string): Unique identifier for this request (UUID format recommended)

### Response Format

**Success Acknowledgment:**
```json
{
  "type": "ack",
  "action": "action_name",
  "request_id": "same-as-request",
  "ok": true,
  "data": {
    // Action-specific data
  }
}
```

**Error Response:**
```json
{
  "type": "error",
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "request_id": "same-as-request"
}
```

---

## Actions

### 1. Send Message

Send a text message, reply, share a post, or send a file (image, video, audio) in a conversation.

**Request (Existing Conversation):**
```json
{
  "action": "send_message",
  "request_id": "uuid",
  "conversation_id": "1",
  "content": "Hello! This is my message.",
  "parent_message_id": "123",  // Optional: for replies
  "shared_post_id": "post-uuid",  // Optional: to share a post
  "file_url": "https://bucket.s3.region.amazonaws.com/chat/files/user-uuid/uuid/photo.jpg",  // Optional: S3 URL from HTTP upload
  "file_type": "IMAGE",  // Optional: IMAGE, VIDEO, or AUDIO
  "file_size": 245678,  // Optional: File size in bytes
  "file_name": "photo.jpg"  // Optional: Original filename
}
```

**Request (New Conversation):**
```json
{
  "action": "send_message",
  "request_id": "uuid",
  "receiver_id": "user-uuid",
  "content": "Hello! This is my message.",
  "parent_message_id": "123",  // Optional: for replies
  "shared_post_id": "post-uuid",  // Optional: to share a post
  "file_url": "https://bucket.s3.region.amazonaws.com/chat/files/user-uuid/uuid/photo.jpg",  // Optional: S3 URL from HTTP upload
  "file_type": "IMAGE",  // Optional: IMAGE, VIDEO, or AUDIO
  "file_size": 245678,  // Optional: File size in bytes
  "file_name": "photo.jpg"  // Optional: Original filename
}
```

**Required Fields:**
- Either `conversation_id` (integer) OR `receiver_id` (string): 
  - `conversation_id`: ID of existing conversation
  - `receiver_id`: User ID to create new DIRECT conversation with
- `content` (string): Message text (can be empty if `file_url` or `shared_post_id` is provided)

**Optional Fields:**
- `parent_message_id` (integer): ID of message being replied to
- `shared_post_id` (UUID): ID of post to share in message
- `file_url` (string): S3 URL of uploaded file (obtained from HTTP upload endpoint)
- `file_type` (string): File type - "IMAGE", "VIDEO", or "AUDIO"
- `file_size` (integer): File size in bytes
- `file_name` (string): Original filename

**File Upload:**
- Files must be uploaded via HTTP POST to `/api/chat/upload/` first
- The endpoint returns a `file_url` which should be used in WebSocket messages
- Supported formats:
  - **Images:** jpg, jpeg, png, gif, webp, bmp
  - **Videos:** mp4, mov, avi, mkv, webm, flv, wmv, m4v
  - **Audio:** mp3, wav, ogg, m4a, aac, flac, wma
- Maximum file size: 10 MB
- File type is automatically detected from filename extension

**Success Response:**
```json
{
  "type": "ack",
  "action": "send_message",
  "request_id": "uuid",
  "ok": true,
  "data": {
    "message_id": "123",
    "created_at": "2025-12-13T12:00:00Z"
  }
}
```

**Broadcast (to other users):**
```json
{
  "type": "message.sent",
  "data": {
    "message_id": "123",
    "conversation_id": "1",
    "sender_id": "user-uuid",
    "sender_name": "John Doe",
    "sender_email": "john@example.com",
    "text": "Hello! This is my message.",
    "file": {
      "url": "https://bucket.s3.region.amazonaws.com/chat/files/user-uuid/uuid/photo.jpg",
      "type": "IMAGE",
      "size": 245678,
      "name": "photo.jpg"
    },
    "reply_to_id": "122",
    "created_at": "2025-12-13T12:00:00Z",
    "edited_at": null,
    "is_deleted_for_everyone": false,
    "shared_post": {  // If post was shared
      "post_id": "post-uuid",
      "title": "Post Title",
      "description": "Post description preview...",
      "created_at": "2025-12-13T11:00:00Z",
      "media": [
        {
          "media_id": "media-uuid",
          "media_type": "IMAGE",
          "url": "https://..."
        }
      ]
    }
  }
}
```

**File Object Structure:**
- `file` is `null` if no file is attached
- If file is present, it contains:
  - `url` (string): Public S3 URL to access the file
  - `type` (string): File type - "IMAGE", "VIDEO", or "AUDIO"
  - `size` (integer): File size in bytes
  - `name` (string): Original filename

**Validation Rules:**
- Either `conversation_id` (integer) OR `receiver_id` (string) must be provided
- If `receiver_id` is provided, it must be a valid user UUID
- Cannot send message to yourself
- `content` cannot be empty unless `file_url` or `shared_post_id` is provided
- `parent_message_id` must exist in the conversation
- `shared_post_id` must be a valid UUID and post must exist
- `file_url` must be a valid HTTP/HTTPS URL if provided
- User must be a member of the conversation (or will be added automatically for new conversations)
- **No follow requirement**: Users can message anyone, even without following
- Conversation must be active (or will be created automatically for new conversations)

**File Upload Rules:**
- Files must be uploaded via HTTP POST to `/api/chat/upload/` before sending message
- `file_url` must be a valid S3 URL obtained from the upload endpoint
- Maximum file size: 10 MB (10,485,760 bytes)
- File type must be one of: IMAGE, VIDEO, or AUDIO

**Error Codes:**
- `VALIDATION_ERROR`: Missing or invalid fields (e.g., missing both conversation_id and receiver_id, invalid receiver_id, trying to message yourself)
- `CONVERSATION_NOT_FOUND`: Conversation doesn't exist (when using conversation_id)
- `NOT_MEMBER`: User is not a member of the conversation
- `POST_NOT_FOUND`: Shared post doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many messages sent
- `FILE_TOO_LARGE`: File size exceeds 10 MB limit
- `INVALID_FILE_TYPE`: File type not supported
- `FILE_UPLOAD_FAILED`: Failed to upload file to S3

**Notes:**
- When `receiver_id` is provided, a new DIRECT conversation is automatically created if one doesn't exist
- Both users are automatically added as members of the conversation
- No follow relationship is required to send messages
- Conversations are created lazily (only when first message is sent)

---

### 2. Edit Message

Edit an existing message. Can only be edited within 24 hours of creation.

**Request:**
```json
{
  "action": "edit_message",
  "request_id": "uuid",
  "message_id": "123",
  "content": "Updated message text"
}
```

**Required Fields:**
- `message_id` (integer): ID of message to edit
- `content` (string): New message text

**Success Response:**
```json
{
  "type": "ack",
  "action": "edit_message",
  "request_id": "uuid",
  "ok": true,
  "data": {
    "message_id": "123",
    "text": "Updated message text",
    "edited_at": "2025-12-13T12:30:00Z"
  }
}
```

**Broadcast (to all users):**
```json
{
  "type": "message.edited",
  "data": {
    "message_id": "123",
    "conversation_id": "1",
    "text": "Updated message text",
    "edited_at": "2025-12-13T12:30:00Z"
  }
}
```

**Validation Rules:**
- Message must exist
- User must be the owner of the message
- Message must be less than 24 hours old
- Message must not be deleted
- `content` cannot be empty

**Error Codes:**
- `VALIDATION_ERROR`: Missing or invalid fields (including empty content)
- `MESSAGE_NOT_FOUND`: Message doesn't exist
- `UNAUTHORIZED`: User is not the message owner
- `EDIT_TIME_EXPIRED`: Message is older than 24 hours

---

### 3. Delete Message

Delete a message. Can only be deleted within 7 days of creation. Messages are soft-deleted (marked as deleted, not removed from database).

**Request:**
```json
{
  "action": "delete_message",
  "request_id": "uuid",
  "message_id": "123"
}
```

**Required Fields:**
- `message_id` (integer): ID of message to delete

**Success Response:**
```json
{
  "type": "ack",
  "action": "delete_message",
  "request_id": "uuid",
  "ok": true,
  "data": {
    "message_id": "123",
    "conversation_id": "1"
  }
}
```

**Broadcast (to all users):**
```json
{
  "type": "message.deleted",
  "data": {
    "message_id": "123",
    "conversation_id": "1"
  }
}
```

**Validation Rules:**
- Message must exist
- User must be the owner of the message
- Message must be less than 7 days old
- Message must not already be deleted

**Error Codes:**
- `VALIDATION_ERROR`: Missing or invalid fields
- `MESSAGE_NOT_FOUND`: Message doesn't exist
- `UNAUTHORIZED`: User is not the message owner
- `DELETE_TIME_EXPIRED`: Message is older than 7 days

---

### 4. Mark Read

Mark messages in a conversation as read. Can mark entire conversation or a specific message.

**Request:**
```json
{
  "action": "mark_read",
  "request_id": "uuid",
  "conversation_id": "1",
  "message_id": "123"  // Optional: mark specific message
}
```

**Required Fields:**
- `conversation_id` (integer): ID of the conversation

**Optional Fields:**
- `message_id` (integer): Specific message to mark as read

**Success Response:**
```json
{
  "type": "ack",
  "action": "mark_read",
  "request_id": "uuid",
  "ok": true,
  "data": {
    "conversation_id": "1",
    "last_read_at": "2025-12-13T12:30:00Z"
  }
}
```

**Broadcast (to all users):**
```json
{
  "type": "read_receipt.updated",
  "data": {
    "user_id": "user-uuid",
    "conversation_id": "1",
    "last_read_at": "2025-12-13T12:30:00Z"
  }
}
```

**Validation Rules:**
- User must be a member of the conversation
- Conversation must exist
- If `message_id` provided, message must exist in the conversation

**Error Codes:**
- `VALIDATION_ERROR`: Missing or invalid fields
- `CONVERSATION_NOT_FOUND`: Conversation doesn't exist
- `NOT_MEMBER`: User is not a member of the conversation
- `MESSAGE_NOT_FOUND`: Message doesn't exist (if message_id provided)

---

### 5. Join Conversation

Join a conversation group to receive broadcasts. Automatically called when sending messages, but can be called explicitly.

**Request:**
```json
{
  "action": "join_conversation",
  "request_id": "uuid",
  "conversation_id": "1"
}
```

**Required Fields:**
- `conversation_id` (integer): ID of the conversation

**Success Response:**
```json
{
  "type": "conversation.joined",
  "request_id": "uuid",
  "data": {
    "conversation_id": "1",
    "type": "DIRECT",
    "name": "Group Name"  // For GROUP conversations
  }
}
```

**Validation Rules:**
- User must be a member of the conversation
- Conversation must exist and be active

**Error Codes:**
- `VALIDATION_ERROR`: Missing or invalid fields (conversation_id required)
- `NOT_MEMBER`: User is not a member of the conversation

**Note:** If conversation doesn't exist, `NOT_MEMBER` error is returned.

---

### 6. Leave Conversation

Leave a conversation group to stop receiving broadcasts.

**Request:**
```json
{
  "action": "leave_conversation",
  "request_id": "uuid",
  "conversation_id": "1"
}
```

**Required Fields:**
- `conversation_id` (integer): ID of the conversation

**Success Response:**
```json
{
  "type": "conversation.left",
  "request_id": "uuid",
  "data": {
    "conversation_id": "1"
  }
}
```

**Note:** This does not remove the user from the conversation, only stops receiving broadcasts. User remains a member.

---

### 7. Typing Indicator

Send typing indicator to other users in the conversation.

**Request:**
```json
{
  "action": "typing",
  "request_id": "uuid",
  "conversation_id": "1",
  "is_typing": true
}
```

**Required Fields:**
- `conversation_id` (integer): ID of the conversation
- `is_typing` (boolean): `true` to start typing, `false` to stop

**Response:** No acknowledgment sent (silent action)

**Broadcast (to other users):**
```json
{
  "type": "typing",
  "data": {
    "user_id": "user-uuid",
    "user_name": "John Doe",
    "conversation_id": "1",
    "is_typing": true
  }
}
```

**Validation Rules:**
- User must be a member of the conversation
- If `conversation_id` is missing or user is not a member, action is silently ignored (no error sent)

**Note:** This is a silent action - no acknowledgment or error is sent. Invalid requests are simply ignored.

---

### 8. Get Presence

Get online/offline status of all members in a conversation.

**Request:**
```json
{
  "action": "get_presence",
  "request_id": "uuid",
  "conversation_id": "1"
}
```

**Required Fields:**
- `conversation_id` (integer): ID of the conversation

**Success Response:**
```json
{
  "type": "presence.status",
  "request_id": "uuid",
  "data": {
    "conversation_id": "1",
    "users": [
      {
        "user_id": "user-uuid-1",
        "user_name": "John Doe",
        "is_online": true,
        "last_seen": "2025-12-13T12:00:00Z"  // Only if online
      },
      {
        "user_id": "user-uuid-2",
        "user_name": "Jane Smith",
        "is_online": false,
        "last_seen": null
      }
    ]
  }
}
```

**Validation Rules:**
- User must be a member of the conversation

**Error Codes:**
- `VALIDATION_ERROR`: Missing or invalid fields (conversation_id required)
- `NOT_MEMBER`: User is not a member of the conversation (also returned if conversation doesn't exist)

**Note:** Presence is tracked in-memory. Users show as online only while connected via WebSocket.

---

### 9. Pong (Heartbeat)

Heartbeat response. Used to keep connection alive.

**Request:**
```json
{
  "action": "pong",
  "request_id": "uuid"
}
```

**Response:** No response (silent action)

---

## Broadcasts

Broadcasts are messages sent to all members of a conversation (except the sender) when certain events occur.

### Broadcast Types

1. **message.sent** - New message sent
2. **message.edited** - Message edited
3. **message.deleted** - Message deleted
4. **read_receipt.updated** - Read receipt updated
5. **typing** - Typing indicator
6. **presence.updated** - Presence status changed (on connect/disconnect)

### Receiving Broadcasts

To receive broadcasts, users must:
1. Be a member of the conversation
2. Have joined the conversation group (via `join_conversation` action or automatically when sending messages)

**Note:** The sender of an action does NOT receive the broadcast for that action (they already got the acknowledgment).

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "type": "error",
  "error": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "request_id": "same-as-request"
}
```

### Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_TOKEN` | Invalid or missing JWT token |
| `TOKEN_EXPIRED` | JWT token has expired |
| `USER_NOT_FOUND` | User not found |
| `CONVERSATION_NOT_FOUND` | Conversation doesn't exist |
| `NOT_MEMBER` | User is not a member of the conversation |
| `MESSAGE_NOT_FOUND` | Message doesn't exist |
| `UNAUTHORIZED` | User not authorized for this action |
| `VALIDATION_ERROR` | Invalid or missing required fields |
| `RATE_LIMIT_EXCEEDED` | Too many requests in time window |
| `EDIT_TIME_EXPIRED` | Message is older than 24 hours |
| `DELETE_TIME_EXPIRED` | Message is older than 7 days |
| `INVALID_ACTION` | Unknown or invalid action |
| `SERVER_ERROR` | Internal server error |
| `NO_FOLLOW_RELATIONSHIP` | Sender doesn't follow receiver (DIRECT conversations) |
| `POST_NOT_FOUND` | Post not found |
| `POST_SHARING_NOT_ALLOWED` | Post sharing not allowed |
| `FILE_TOO_LARGE` | File size exceeds 10 MB limit |
| `INVALID_FILE_TYPE` | File type not supported (must be image, video, or audio) |
| `FILE_UPLOAD_FAILED` | Failed to upload file to S3 |

### Common Error Scenarios

**Invalid JSON:**
```json
{
  "type": "error",
  "error": "Invalid JSON format",
  "error_code": "VALIDATION_ERROR",
  "request_id": ""
}
```

**Missing Action:**
```json
{
  "type": "error",
  "error": "Invalid action",
  "error_code": "INVALID_ACTION",
  "request_id": "uuid"
}
```

**Rate Limit Exceeded:**
```json
{
  "type": "error",
  "error": "Rate limit exceeded. Please try again later.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "request_id": "uuid"
}
```

---

## Rate Limiting

### Limits

- **Default:** 30 requests per 30 seconds per user per action
- **Applies to:** All actions (except `pong` and `typing`)

### Rate Limit Exceeded

When rate limit is exceeded:
- Request is rejected
- Error response with `RATE_LIMIT_EXCEEDED` code is sent
- User must wait for the time window to reset

### Rate Limit Storage

Rate limiting is tracked in-memory per user per action. Limits reset after the time window expires.

---

## Data Models

### Conversation

```typescript
{
  id: number;  // Integer primary key
  type: "DIRECT" | "GROUP";
  name: string;  // Optional, for GROUP conversations
  description: string;  // Optional
  image: string | null;  // URL to image
  created_by: User | null;
  created_at: ISO8601DateTime;
  updated_at: ISO8601DateTime;
  is_active: boolean;
}
```

### Message

```typescript
{
  id: number;  // Integer primary key
  conversation_id: number;
  sender: User;
  text: string;
  file: string | null;  // URL to file
  reply_to: Message | null;
  shared_post: Post | null;
  created_at: ISO8601DateTime;
  edited_at: ISO8601DateTime | null;
  is_deleted_for_everyone: boolean;
}
```

### ConversationMember

```typescript
{
  conversation: Conversation;
  user: User;
  is_admin: boolean;
  joined_at: ISO8601DateTime;
  left_at: ISO8601DateTime | null;
  last_read_at: ISO8601DateTime | null;
}
```

### User (from bible_way app)

```typescript
{
  user_id: UUID;
  user_name: string;
  email: string;
  // ... other fields
}
```

---

## Business Rules

### Follow Relationship

For **DIRECT** conversations:
- Sender must follow receiver (one-way follow check)
- If sender unfollows receiver, conversation is deactivated
- Messages cannot be sent to inactive conversations
- Conversation is automatically created when User A follows User B
- Conversation is deactivated (not deleted) when User A unfollows User B

### Message Time Limits

- **Edit:** Messages can only be edited within 24 hours of creation
- **Delete:** Messages can only be deleted within 7 days of creation
- After time limits, actions return `EDIT_TIME_EXPIRED` or `DELETE_TIME_EXPIRED` errors

### Message Ownership

- Only the message sender can edit or delete their messages
- Other users receive broadcasts but cannot modify messages

### Conversation Membership

- Users must be members of a conversation to:
  - Send messages
  - Join conversation group
  - Get presence status
  - Receive broadcasts

### Presence Status

- Users show as **online** only while connected via WebSocket
- Presence is tracked in-memory (lost on server restart)
- `last_seen` timestamp is only provided for online users

---

## Example Flows

### Sending a Message

1. Client connects: `ws://domain/ws/user/?token=JWT`
2. Server sends: `connection.established`
3. Client sends: `send_message` action
4. Server sends: ACK with `message_id`
5. Server broadcasts: `message.sent` to other users

### Sending a File

1. Client uploads file via HTTP POST to `/api/chat/upload/`
2. Server validates:
   - File size ≤ 10 MB
   - File type is supported (image/video/audio)
   - Filename has valid extension
3. Server uploads file to S3: `chat/files/{user_id}/{uuid}/{filename}`
4. Server returns file URL and metadata
5. Client sends WebSocket message: `send_message` with `file_url`, `file_type`, `file_size`, `file_name`
6. Server validates file URL format (must be valid HTTP/HTTPS URL)
7. Server creates message with S3 URL
8. Server sends: ACK with `message_id`
9. Server broadcasts: `message.sent` with file object containing URL, type, size, name
10. Other users receive file URL and can directly access from S3

### Replying to a Message

1. Client sends: `send_message` with `parent_message_id`
2. Server sends: ACK
3. Server broadcasts: `message.sent` with `reply_to_id` field

### Sharing a Post

1. Client sends: `send_message` with `shared_post_id`
2. Server validates post exists
3. Server sends: ACK
4. Server broadcasts: `message.sent` with `shared_post` preview

### Editing a Message

1. Client sends: `edit_message` action
2. Server validates:
   - Message exists
   - User is owner
   - Message < 24 hours old
3. Server sends: ACK with updated text
4. Server broadcasts: `message.edited` to all users

---

## Client Implementation Notes

### Request ID Matching

Always match responses to requests using `request_id`:

```javascript
const requestId = generateUUID();
ws.send(JSON.stringify({
  action: "send_message",
  request_id: requestId,
  // ...
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.request_id === requestId) {
    // This is the response to our request
    if (data.ok) {
      // Success - message sent
      console.log("Message ID:", data.data.message_id);
    } else {
      // Error
      console.error("Error:", data.error, data.error_code);
    }
  } else if (data.type === "message.sent") {
    // This is a broadcast from another user
    if (data.data.file) {
      // Message contains a file
      console.log("File received:", data.data.file.url);
      // Display file using the S3 URL
    }
  }
};
```

### Sending a File

```javascript
// Step 1: Upload file via HTTP
const fileInput = document.getElementById('fileInput');
const file = fileInput.files[0];

const formData = new FormData();
formData.append('file', file);
formData.append('conversation_id', '1');

fetch('http://your-domain/api/chat/upload/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${jwtToken}`
  },
  body: formData
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    // Step 2: Send WebSocket message with file URL
    const requestId = generateUUID();
    ws.send(JSON.stringify({
      action: "send_message",
      request_id: requestId,
      conversation_id: "1",
      content: "Check out this image!",
      file_url: data.data.file_url,
      file_type: data.data.file_type,
      file_size: data.data.file_size,
      file_name: data.data.file_name
    }));
    
    // Handle response
    ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.request_id === requestId) {
        if (response.ok) {
          console.log("Message sent successfully!");
          console.log("Message ID:", response.data.message_id);
        } else {
          console.error("Failed:", response.error);
        }
      }
    };
  } else {
    console.error("File upload failed:", data.error);
  }
})
.catch(error => {
  console.error("Upload error:", error);
});

### Handling Broadcasts

Filter broadcasts from acknowledgments:

```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  // Check if it's a broadcast
  if (data.type && !data.request_id) {
    // Handle broadcast
    switch (data.type) {
      case "message.sent":
        // New message from other user
        break;
      case "message.edited":
        // Message was edited
        break;
      case "typing":
        // User is typing
        break;
    }
  } else if (data.request_id) {
    // Handle acknowledgment
    handleAck(data);
  }
};
```

### Connection Management

- Reconnect on connection close
- Re-authenticate on reconnect
- Handle connection errors gracefully
- Implement exponential backoff for reconnection

### Error Handling

- Always check `ok` field in ACK responses
- Handle all error codes appropriately
- Show user-friendly error messages
- Log errors for debugging

---

## Version Information

**API Version:** 1.0.0  
**Last Updated:** December 13, 2025  
**Protocol:** WebSocket (JSON messages) + HTTP REST (file uploads)  
**Authentication:** JWT (query parameter for WebSocket, Bearer token for HTTP)

---

## Support

For issues or questions, refer to the project documentation or contact the development team.

