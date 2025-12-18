# Notifications API Specification

## Overview

The Notifications API provides real-time WebSocket-based notifications for user activities including follows, likes, comments, and prayer requests. All notifications are delivered instantly via WebSocket connections with automatic aggregation support. Notifications are delivered through the unified `ws/user/` WebSocket connection along with chat messages.

**Base WebSocket URL:**
```
ws://localhost:8000/ws/user/
```

**Production URL:**
```
wss://your-domain.com/ws/user/
```

**REST API Base URL:**
```
http://localhost:8000/api/notifications/
```

---

## Table of Contents

1. [Authentication](#authentication)
2. [WebSocket Connection](#websocket-connection)
3. [REST API Endpoints](#rest-api-endpoints)
4. [Message Formats](#message-formats)
5. [Notification Types](#notification-types)
6. [Client Actions](#client-actions)
7. [Error Handling](#error-handling)
8. [Read/Unread Tracking](#readunread-tracking)

---

## Authentication

All WebSocket connections require JWT authentication via query parameter.

**WebSocket Connection URL Format:**
```
ws://domain/ws/user/?token=<access_token>
```

**REST API Authentication:**
- Include JWT access token in `Authorization` header: `Bearer <access_token>`
- Token must be valid and not expired
- User must be authenticated and active

**WebSocket Authentication:**
- Include JWT access token in the `token` query parameter
- Token must be valid and not expired
- User must be authenticated and active

**Example:**
```
ws://localhost:8000/ws/user/?token=eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## WebSocket Connection

### Connection Flow

1. Client initiates WebSocket connection to unified `ws/user/` endpoint with JWT token
2. Server validates token and authenticates user
3. Server accepts connection and sends connection confirmation
4. Client automatically joins both chat groups and notification group (`user_{user_id}_notifications`)
5. Client receives both chat messages and notifications in real-time through the same connection
6. Client calls `GET /api/notifications/missed/` to fetch unread notifications created while offline

### Connection Established Message

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

Note: This is the same connection message used for chat, as notifications are delivered through the unified WebSocket connection.

### Connection Rejection

If authentication fails, the connection is closed with code `4008` (Policy violation - authentication required).

---

## REST API Endpoints

### GET /api/notifications/missed/

Fetch unread notifications that were created while the user was offline.

**Authentication:** JWT token in `Authorization` header

**Query Parameters:**
- `limit` (optional): Number of notifications to return (default: 50, max: 100)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "type": "notification",
        "notification_id": "uuid-string",
        "notification_type": "POST_LIKE",
        "message": "john_doe liked your post",
        "target_id": "post-uuid",
        "target_type": "post",
        "actor": {
          "user_id": "uuid-string",
          "user_name": "john_doe",
          "profile_picture_url": "https://..."
        },
        "metadata": {...},
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "count": 5,
    "last_fetch_at": "2024-01-15T10:30:00Z"
  }
}
```

**Behavior:**
- Only returns notifications where `is_read = False`
- Filters by `created_at > last_fetch_at` (or last 24 hours if first time)
- Updates `last_fetch_at` after successful fetch
- Notifications are ordered by `created_at` (oldest first)

**Error Responses:**
- `401 Unauthorized`: Invalid or missing JWT token
- `500 Internal Server Error`: Server error

### POST /api/notifications/markread/

Mark all notifications as read for the authenticated user.

**Authentication:** JWT token in `Authorization` header

**Request Body:** Empty (no body required)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "All notifications marked as read",
    "marked_count": 10
  }
}
```

**Behavior:**
- Marks ALL notifications for the authenticated user as `is_read = True`
- Uses bulk update for performance
- Returns count of notifications that were marked

**Error Responses:**
- `401 Unauthorized`: Invalid or missing JWT token
- `500 Internal Server Error`: Server error

---

## Read/Unread Tracking

All notifications default to `is_read = False` when created. The system tracks read/unread status:

- **New notifications:** Created with `is_read = False`
- **WebSocket delivery:** Real-time notifications are delivered with `is_read = False`
- **Missed notifications:** Only unread notifications are returned by `GET /api/notifications/missed/`
- **Mark as read:** `POST /api/notifications/markread/` marks all user's notifications as read

**Best Practice:**
1. Connect to `ws/user/` WebSocket for real-time notifications
2. On app startup/reconnect, call `GET /api/notifications/missed/` to fetch unread missed notifications
3. When user views notifications, call `POST /api/notifications/markread/` to mark all as read
4. Subsequent calls to `GET /api/notifications/missed/` will only return new unread notifications

---

## Message Formats

### Incoming Messages (Server → Client)

All notification messages follow this structure:

```json
{
  "type": "notification",
  "notification_id": "uuid-string",
  "notification_type": "FOLLOW|POST_LIKE|COMMENT_LIKE|PRAYER_REQUEST_LIKE|COMMENT_ON_POST|COMMENT_ON_PRAYER_REQUEST|PRAYER_REQUEST_CREATED",
  "message": "Human-readable notification message",
  "target_id": "uuid-string",
  "target_type": "user|post|comment|prayer_request",
  "actor": {
    "user_id": "uuid-string",
    "user_name": "string",
    "profile_picture_url": "string"
  },
  "metadata": {
    "actors_count": 1,
    "actors": ["uuid-string"],
    "last_actor_id": "uuid-string",
    "last_actor_name": "string",
    "is_aggregated": false
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Outgoing Messages (Client → Server)

Clients can send the following actions:

#### Ping (Heartbeat)

```json
{
  "action": "ping",
  "request_id": "optional-request-id"
}
```

**Response:**
```json
{
  "type": "pong",
  "request_id": "optional-request-id"
}
```

---

## Notification Types

### 1. Follow Notification

**Type:** `FOLLOW`

**Trigger:** When a user follows another user

**Message Format:**
- Single: `"{actor_name} started following you"`

**Payload:**
```json
{
  "type": "notification",
  "notification_id": "uuid-string",
  "notification_type": "FOLLOW",
  "message": "john_doe started following you",
  "target_id": "user-uuid",
  "target_type": "user",
  "actor": {
    "user_id": "uuid-string",
    "user_name": "john_doe",
    "profile_picture_url": "https://..."
  },
  "metadata": {},
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Aggregation:** Not applicable (one follow per user)

---

### 2. Post Like Notification

**Type:** `POST_LIKE`

**Trigger:** When a user likes a post

**Message Format:**
- Single: `"{actor_name} liked your post"`
- Aggregated (2): `"{actor_name} and 1 other liked your post"`
- Aggregated (3+): `"{actor_name} and {count-1} others liked your post"`

**Payload (Single):**
```json
{
  "type": "notification",
  "notification_id": "uuid-string",
  "notification_type": "POST_LIKE",
  "message": "john_doe liked your post",
  "target_id": "post-uuid",
  "target_type": "post",
  "actor": {
    "user_id": "uuid-string",
    "user_name": "john_doe",
    "profile_picture_url": "https://..."
  },
  "metadata": {
    "actors_count": 1,
    "actors": ["user-uuid"],
    "last_actor_id": "user-uuid",
    "last_actor_name": "john_doe"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Payload (Aggregated):**
```json
{
  "type": "notification",
  "notification_id": "uuid-string",
  "notification_type": "POST_LIKE",
  "message": "jane_smith and 2 others liked your post",
  "target_id": "post-uuid",
  "target_type": "post",
  "actor": {
    "user_id": "uuid-string",
    "user_name": "jane_smith",
    "profile_picture_url": "https://..."
  },
  "metadata": {
    "actors_count": 3,
    "actors": ["user-uuid-1", "user-uuid-2", "user-uuid-3"],
    "last_actor_id": "user-uuid-3",
    "last_actor_name": "jane_smith",
    "is_aggregated": true
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Aggregation:** 
- Multiple likes on the same post within 24 hours are aggregated
- `actors_count` indicates total number of users who liked
- `last_actor_name` is the most recent user who liked

---

### 3. Comment Like Notification

**Type:** `COMMENT_LIKE`

**Trigger:** When a user likes a comment

**Message Format:**
- Single: `"{actor_name} liked your comment"`
- Aggregated: `"{actor_name} and {count-1} others liked your comment"`

**Payload:** Similar to Post Like notification, but `target_type` is `"comment"`

**Aggregation:** Same as Post Like (24-hour window)

---

### 4. Prayer Request Like Notification

**Type:** `PRAYER_REQUEST_LIKE`

**Trigger:** When a user likes a prayer request

**Message Format:**
- Single: `"{actor_name} liked your prayer request"`
- Aggregated: `"{actor_name} and {count-1} others liked your prayer request"`

**Payload:** Similar to Post Like notification, but `target_type` is `"prayer_request"`

**Aggregation:** Same as Post Like (24-hour window)

---

### 5. Comment on Post Notification

**Type:** `COMMENT_ON_POST`

**Trigger:** When a user comments on a post

**Message Format:**
- Single: `"{actor_name} commented on your post"`
- Aggregated (2): `"{actor_name} and 1 other commented on your post"`
- Aggregated (3+): `"{actor_name} and {count-1} others commented on your post"`

**Payload:**
```json
{
  "type": "notification",
  "notification_id": "uuid-string",
  "notification_type": "COMMENT_ON_POST",
  "message": "john_doe commented on your post",
  "target_id": "post-uuid",
  "target_type": "post",
  "actor": {
    "user_id": "uuid-string",
    "user_name": "john_doe",
    "profile_picture_url": "https://..."
  },
  "metadata": {
    "actors_count": 1,
    "actors": ["user-uuid"],
    "last_actor_id": "user-uuid",
    "last_actor_name": "john_doe"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Aggregation:** Same as Post Like (24-hour window)

---

### 6. Comment on Prayer Request Notification

**Type:** `COMMENT_ON_PRAYER_REQUEST`

**Trigger:** When a user comments on a prayer request

**Message Format:**
- Single: `"{actor_name} commented on your prayer request"`
- Aggregated: `"{actor_name} and {count-1} others commented on your prayer request"`

**Payload:** Similar to Comment on Post, but `target_type` is `"prayer_request"`

**Aggregation:** Same as Post Like (24-hour window)

---

### 7. Prayer Request Created Notification

**Type:** `PRAYER_REQUEST_CREATED`

**Trigger:** When a user you follow creates a prayer request

**Message Format:**
- Single: `"{actor_name} created a prayer request"`

**Payload:**
```json
{
  "type": "notification",
  "notification_id": "uuid-string",
  "notification_type": "PRAYER_REQUEST_CREATED",
  "message": "john_doe created a prayer request",
  "target_id": "prayer-request-uuid",
  "target_type": "prayer_request",
  "actor": {
    "user_id": "uuid-string",
    "user_name": "john_doe",
    "profile_picture_url": "https://..."
  },
  "metadata": {},
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Aggregation:** Not applicable (one notification per prayer request per follower)

**Note:** Only sent to users who follow the creator

---

## Client Actions

### Ping (Heartbeat)

Send a ping message to keep the connection alive and verify connectivity.

**Request:**
```json
{
  "action": "ping",
  "request_id": "optional-unique-id"
}
```

**Response:**
```json
{
  "type": "pong",
  "request_id": "optional-unique-id"
}
```

**Usage:**
- Recommended to send ping every 30-60 seconds
- Helps detect connection issues
- Server responds with pong immediately

---

## Error Handling

### Connection Errors

**Authentication Failed:**
- Connection is closed with code `4008`
- No error message sent (connection rejected)

**Invalid Token:**
- Connection is closed with code `4008`
- User should refresh their access token

### Message Errors

**Invalid JSON:**
```json
{
  "type": "error",
  "error": "Invalid JSON format",
  "error_code": "VALIDATION_ERROR"
}
```

**Unknown Action:**
```json
{
  "type": "error",
  "error": "Unknown action: invalid_action",
  "error_code": "INVALID_ACTION",
  "request_id": "optional-request-id"
}
```

---

## Aggregation Logic

### How Aggregation Works

1. **Time Window:** Notifications of the same type for the same target are aggregated within a 24-hour window
2. **Grouping:** Aggregated by:
   - `notification_type` (e.g., POST_LIKE)
   - `target_id` (e.g., post UUID)
   - `recipient` (user receiving notification)
3. **Update:** When a new event occurs within the window:
   - Existing notification is updated (not replaced)
   - `actors_count` is incremented
   - `last_actor_id` and `last_actor_name` are updated
   - New actor is added to `actors` array if not already present
4. **New Notification:** If no notification exists or the last one is older than 24 hours, a new notification is created

### Aggregation Examples

**Scenario:** 3 users like the same post within 2 hours

1. **First Like (User A):**
   ```json
   {
     "message": "alice liked your post",
     "metadata": {
       "actors_count": 1,
       "last_actor_name": "alice"
     }
   }
   ```

2. **Second Like (User B) - Aggregated:**
   ```json
   {
     "message": "bob and 1 other liked your post",
     "metadata": {
       "actors_count": 2,
       "last_actor_name": "bob",
       "is_aggregated": true
     }
   }
   ```

3. **Third Like (User C) - Aggregated:**
   ```json
   {
     "message": "charlie and 2 others liked your post",
     "metadata": {
       "actors_count": 3,
       "last_actor_name": "charlie",
       "is_aggregated": true
     }
   }
   ```

---

## Self-Notification Prevention

Users **do not** receive notifications for their own actions:

- ❌ Liking your own post
- ❌ Commenting on your own post
- ❌ Liking your own comment
- ❌ Liking your own prayer request
- ❌ Commenting on your own prayer request

**Note:** Following yourself is also prevented at the model level.

---

## Notification Flow Diagram

```
User Action (Follow/Like/Comment)
         ↓
Django Signal Triggered
         ↓
Signal Handler Executes
         ↓
Check: Self-action? → No
         ↓
Check: Existing notification? → Yes/No
         ↓
Create or Update Notification
         ↓
Format Notification (with aggregation)
         ↓
Send via Channel Layer
         ↓
Broadcast to user_{user_id}_notifications group
         ↓
WebSocket Consumer Receives
         ↓
Send to Connected Client
         ↓
Client Displays Notification
```

---

## Field Descriptions

### Notification Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"notification"` for notification messages |
| `notification_id` | UUID | Unique identifier for the notification |
| `notification_type` | string | Type of notification (FOLLOW, POST_LIKE, etc.) |
| `message` | string | Human-readable notification message |
| `target_id` | UUID string | ID of the target object (post, comment, etc.) |
| `target_type` | string | Type of target (`post`, `comment`, `prayer_request`, `user`) |
| `actor` | object | User who triggered the notification |
| `actor.user_id` | UUID string | Actor's user ID |
| `actor.user_name` | string | Actor's username |
| `actor.profile_picture_url` | string | Actor's profile picture URL (empty string if not set) |
| `metadata` | object | Additional notification data |
| `metadata.actors_count` | integer | Number of users who performed the action |
| `metadata.actors` | array | List of user IDs who performed the action |
| `metadata.last_actor_id` | UUID string | Most recent actor's user ID |
| `metadata.last_actor_name` | string | Most recent actor's username |
| `metadata.is_aggregated` | boolean | Whether this is an aggregated notification |
| `created_at` | ISO 8601 string | When the notification was created |

---

## Best Practices

### Client Implementation

1. **Reconnection Logic:**
   - Implement exponential backoff for reconnection
   - Reconnect automatically on connection loss
   - Refresh JWT token if connection fails with 4008

2. **Heartbeat:**
   - Send ping every 30-60 seconds
   - Detect connection issues if pong not received

3. **Notification Display:**
   - Show notifications in real-time as they arrive
   - Group notifications by type if needed
   - Display aggregated count clearly

4. **Error Handling:**
   - Handle all error types gracefully
   - Log errors for debugging
   - Provide user feedback on connection issues

5. **Token Management:**
   - Refresh access token before expiration
   - Reconnect with new token when refreshed
   - Handle token expiration gracefully

### Performance Considerations

1. **Connection Management:**
   - Maintain single WebSocket connection per user
   - Avoid multiple simultaneous connections
   - Close connection when app goes to background (mobile)

2. **Notification Handling:**
   - Process notifications asynchronously
   - Don't block UI thread with notification processing
   - Implement notification queue if needed

---

## Testing

### Manual Testing

1. **Connect to Unified WebSocket:**
   ```bash
   wscat -c "ws://localhost:8000/ws/user/?token=YOUR_TOKEN"
   ```
   
2. **Fetch Missed Notifications:**
   ```bash
   curl -X GET "http://localhost:8000/api/notifications/missed/?limit=50" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```
   
3. **Mark All as Read:**
   ```bash
   curl -X POST "http://localhost:8000/api/notifications/markread/" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

4. **Trigger Notifications:**
   - Follow a user (via REST API)
   - Like a post (via REST API)
   - Comment on a post (via REST API)
   - Create a prayer request (via REST API)

5. **Verify:**
   - Notifications appear in unified WebSocket connection
   - Aggregation works correctly
   - Self-notifications are prevented
   - Missed notifications endpoint returns only unread notifications
   - Mark as read endpoint marks all notifications correctly

### Automated Testing

See `test_notifications.py` for comprehensive test suite covering all notification types.
