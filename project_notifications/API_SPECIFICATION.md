# Project Notifications - Complete API Specification

## Overview

The Project Notifications API provides notification functionality for user interactions (follows, likes, messages, comments). Notifications are automatically created via Django signals when events occur, and can be retrieved via REST API or received in real-time via WebSocket.

**HTTP Base URL:** `http://your-domain/api/notifications/`

**WebSocket Base URL:** `ws://your-domain/ws/user/` (shared with chat WebSocket)

**Authentication:** JWT token required for all endpoints
- HTTP: `Authorization: Bearer <JWT_TOKEN>` header
- WebSocket: `?token=<JWT_TOKEN>` query parameter

---

## Table of Contents

1. [REST API](#rest-api)
2. [WebSocket Integration](#websocket-integration)
3. [Notification Types](#notification-types)
4. [Data Models](#data-models)
5. [Notification Creation](#notification-creation)
6. [Fetch Tracking](#fetch-tracking)
7. [Aggregation](#aggregation)
8. [Error Handling](#error-handling)
9. [Examples](#examples)

---

## REST API

### GET `/api/notifications/`

Retrieve notifications for the authenticated user. The endpoint uses fetch tracking to determine which notifications to return.

**Authentication:** Required (JWT token in Authorization header)

**Request:**
- Method: `GET`
- Headers:
  - `Authorization: Bearer <JWT_TOKEN>`
- Query Parameters: None (all parameters are handled automatically)

**Behavior:**
- **First Call:** Returns all notifications the user has ever received
- **Subsequent Calls:** Returns only notifications created after the last fetch time
- **Automatic Tracking:** The last fetch time is automatically updated after each successful call

**Response (Success - 200 OK):**

```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "notification_id": "550e8400-e29b-41d4-a716-446655440000",
        "type": "POST_LIKE",
        "actor": {
          "user_id": "123e4567-e89b-12d3-a456-426614174000",
          "user_name": "John Doe",
          "profile_picture_url": "https://example.com/profile.jpg"
        },
        "actors_count": 5,
        "actors": [
          "123e4567-e89b-12d3-a456-426614174000",
          "223e4567-e89b-12d3-a456-426614174001",
          "323e4567-e89b-12d3-a456-426614174002",
          "423e4567-e89b-12d3-a456-426614174003",
          "523e4567-e89b-12d3-a456-426614174004"
        ],
        "target_id": "post-uuid-123",
        "target_type": "post",
        "conversation_id": null,
        "message_id": null,
        "created_at": "2024-01-15T10:30:00Z",
        "metadata": {
          "actors_count": 5,
          "actors": [
            "123e4567-e89b-12d3-a456-426614174000",
            "223e4567-e89b-12d3-a456-426614174001",
            "323e4567-e89b-12d3-a456-426614174002",
            "423e4567-e89b-12d3-a456-426614174003",
            "523e4567-e89b-12d3-a456-426614174004"
          ],
          "last_actor_id": "523e4567-e89b-12d3-a456-426614174004"
        }
      },
      {
        "notification_id": "660e8400-e29b-41d4-a716-446655440001",
        "type": "FOLLOW",
        "actor": {
          "user_id": "789e4567-e89b-12d3-a456-426614174005",
          "user_name": "Jane Smith",
          "profile_picture_url": "https://example.com/jane.jpg"
        },
        "actors_count": 1,
        "actors": ["789e4567-e89b-12d3-a456-426614174005"],
        "target_id": "user-uuid-456",
        "target_type": "user",
        "conversation_id": null,
        "message_id": null,
        "created_at": "2024-01-15T09:15:00Z",
        "metadata": {
          "actors_count": 1,
          "actors": ["789e4567-e89b-12d3-a456-426614174005"],
          "last_actor_id": "789e4567-e89b-12d3-a456-426614174005"
        }
      },
      {
        "notification_id": "770e8400-e29b-41d4-a716-446655440002",
        "type": "NEW_MESSAGE",
        "actor": {
          "user_id": "999e4567-e89b-12d3-a456-426614174006",
          "user_name": "Bob Wilson",
          "profile_picture_url": "https://example.com/bob.jpg"
        },
        "actors_count": 1,
        "actors": ["999e4567-e89b-12d3-a456-426614174006"],
        "target_id": "conversation-123",
        "target_type": "conversation",
        "conversation_id": 123,
        "message_id": 456,
        "created_at": "2024-01-15T08:00:00Z",
        "metadata": {
          "actors_count": 1,
          "actors": ["999e4567-e89b-12d3-a456-426614174006"],
          "last_actor_id": "999e4567-e89b-12d3-a456-426614174006"
        }
      }
    ],
    "total_count": 3
  }
}
```

**Response (Error - 401 Unauthorized):**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Response (Error - 500 Internal Server Error):**

```json
{
  "success": false,
  "error": "Internal server error message",
  "error_code": "SERVER_ERROR"
}
```

**Notes:**
- Notifications are ordered by `created_at` in descending order (newest first)
- The `total_count` represents the number of notifications returned in this response
- On first call, `total_count` equals the total number of notifications the user has ever received
- On subsequent calls, `total_count` equals the number of new notifications since last fetch
- The fetch tracker is automatically updated after a successful response

---

## WebSocket Integration

### Connection

Notifications are delivered in real-time via the existing chat WebSocket connection. When a user connects to the chat WebSocket, they automatically join their notification group.

**WebSocket Endpoint:** `ws://your-domain/ws/user/?token=<JWT_TOKEN>`

**Connection Details:**
- Same WebSocket connection used for chat functionality
- User automatically joins `notification_{user_id}` group on connection
- No additional connection setup required

### Receiving Notifications

When a notification is created, it is automatically broadcast to the recipient's WebSocket group. The client receives a message with type `notification.new`.

**WebSocket Message Format:**

```json
{
  "type": "notification.new",
  "data": {
    "notification": {
      "notification_id": "550e8400-e29b-41d4-a716-446655440000",
      "type": "POST_LIKE",
      "actor": {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "user_name": "John Doe",
        "profile_picture_url": "https://example.com/profile.jpg"
      },
      "actors_count": 3,
      "actors": [
        "123e4567-e89b-12d3-a456-426614174000",
        "223e4567-e89b-12d3-a456-426614174001",
        "323e4567-e89b-12d3-a456-426614174002"
      ],
      "target_id": "post-uuid-123",
      "target_type": "post",
      "conversation_id": null,
      "message_id": null,
      "created_at": "2024-01-15T10:30:00Z",
      "metadata": {
        "actors_count": 3,
        "actors": [
          "123e4567-e89b-12d3-a456-426614174000",
          "223e4567-e89b-12d3-a456-426614174001",
          "323e4567-e89b-12d3-a456-426614174002"
        ],
        "last_actor_id": "323e4567-e89b-12d3-a456-426614174002"
      }
    }
  }
}
```

**Client Implementation Example (JavaScript):**

```javascript
const ws = new WebSocket('ws://your-domain/ws/user/?token=' + jwtToken);

ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  
  if (message.type === 'notification.new') {
    const notification = message.data.notification;
    console.log('New notification:', notification);
    // Handle notification display
    displayNotification(notification);
  }
  
  // Handle other message types (chat messages, etc.)
};
```

**Notes:**
- Notifications are broadcast immediately when created (via Django signals)
- If the user is not connected to WebSocket, the notification will still be available via REST API
- WebSocket notifications are the same format as REST API notifications
- Aggregated notifications (e.g., multiple likes) are broadcast when updated

---

## Notification Types

The following notification types are supported:

| Type | Description | Target Type | Example |
|------|-------------|-------------|---------|
| `FOLLOW` | User followed another user | `user` | "John Doe started following you" |
| `POST_LIKE` | Post was liked | `post` | "5 people liked your post" |
| `COMMENT_LIKE` | Comment was liked | `comment` | "3 people liked your comment" |
| `PRAYER_REQUEST_LIKE` | Prayer request was liked | `prayer_request` | "2 people liked your prayer request" |
| `VERSE_LIKE` | Verse was liked | `verse` | "1 person liked your verse" |
| `NEW_MESSAGE` | New message in conversation | `conversation` | "Bob Wilson sent you a message" |
| `COMMENT_ON_POST` | Comment added to post | `post` | "Jane Smith commented on your post" |
| `COMMENT_ON_PRAYER_REQUEST` | Comment added to prayer request | `prayer_request` | "John Doe commented on your prayer request" |

**Notification Type Values:**
- `FOLLOW`
- `POST_LIKE`
- `COMMENT_LIKE`
- `PRAYER_REQUEST_LIKE`
- `VERSE_LIKE`
- `NEW_MESSAGE`
- `COMMENT_ON_POST`
- `COMMENT_ON_PRAYER_REQUEST`

---

## Data Models

### Notification Object

```typescript
interface Notification {
  notification_id: string;        // UUID
  type: string;                   // Notification type (see Notification Types)
  actor: Actor | null;            // User who triggered the notification
  actors_count: number;           // Number of actors (for aggregated notifications)
  actors: string[];               // Array of actor user IDs (for aggregated notifications)
  target_id: string;              // ID of the target object (post_id, comment_id, etc.)
  target_type: string;            // Type of target (post, comment, message, etc.)
  conversation_id: number | null; // For message notifications
  message_id: number | null;      // For message notifications
  created_at: string;             // ISO 8601 datetime
  metadata: {                     // Additional metadata
    actors_count: number;
    actors: string[];
    last_actor_id: string;
  };
}

interface Actor {
  user_id: string;                // UUID
  user_name: string;              // Display name
  profile_picture_url: string;    // Profile picture URL (empty string if none)
}
```

### API Response Structure

```typescript
interface GetNotificationsResponse {
  success: boolean;
  data: {
    notifications: Notification[];
    total_count: number;
  };
}

interface ErrorResponse {
  success: false;
  error: string;
  error_code: string;
}
```

---

## Notification Creation

Notifications are **automatically created** via Django signals when events occur. There is **no HTTP endpoint** for creating notifications.

### Automatic Creation Triggers

1. **Follow Notification (`FOLLOW`)**
   - Triggered when: `UserFollowers` model is created
   - Recipient: The user being followed
   - Actor: The user who initiated the follow
   - Self-follows are skipped

2. **Like Notifications (`POST_LIKE`, `COMMENT_LIKE`, `PRAYER_REQUEST_LIKE`, `VERSE_LIKE`)**
   - Triggered when: `Reaction` model is created with `reaction_type = 'LIKE'`
   - Recipient: The owner of the liked content
   - Actor: The user who liked the content
   - Self-likes are skipped
   - **Aggregation:** Multiple likes on the same content are aggregated into a single notification

3. **Message Notification (`NEW_MESSAGE`)**
   - Triggered when: `Message` model is created
   - Recipient: All members of the conversation (except the sender)
   - Actor: The message sender
   - Self-messages are skipped

4. **Comment Notifications (`COMMENT_ON_POST`, `COMMENT_ON_PRAYER_REQUEST`)**
   - Triggered when: Comment is created on a post or prayer request
   - Recipient: The owner of the post/prayer request
   - Actor: The user who commented
   - Self-comments are skipped

---

## Fetch Tracking

The system automatically tracks when each user last fetched their notifications using the `NotificationFetchTracker` model.

### How It Works

1. **First API Call:**
   - No `NotificationFetchTracker` exists for the user
   - System creates a tracker with `last_fetch_at = null`
   - Returns all notifications the user has ever received
   - Updates `last_fetch_at` to current timestamp

2. **Subsequent API Calls:**
   - `NotificationFetchTracker` exists with `last_fetch_at` timestamp
   - Returns only notifications where `created_at > last_fetch_at`
   - Updates `last_fetch_at` to current timestamp

### Benefits

- **Efficient:** Only new notifications are returned on subsequent calls
- **Automatic:** No client-side tracking required
- **Reliable:** Server-side tracking ensures consistency
- **Simple:** Single endpoint, no query parameters needed

### Implementation Details

- Each user has a one-to-one relationship with `NotificationFetchTracker`
- Tracker is automatically created on first API call
- `last_fetch_at` is updated after each successful API call
- Timestamps are timezone-aware (UTC)

---

## Aggregation

Certain notification types are automatically aggregated to reduce notification spam.

### Aggregated Types

- `POST_LIKE`
- `COMMENT_LIKE`
- `PRAYER_REQUEST_LIKE`
- `VERSE_LIKE`

### How Aggregation Works

1. **First Like:** Creates a new notification with `actors_count = 1`
2. **Subsequent Likes:** Updates the existing notification instead of creating a new one
   - Increments `actors_count`
   - Adds new actor to `actors` array
   - Updates `last_actor_id` to the latest actor
   - Updates `actor` field to the latest actor (for display)

3. **Aggregation Criteria:**
   - Same `recipient`
   - Same `notification_type`
   - Same `target_id` and `target_type`
   - Notification must exist (only aggregates existing notifications)

### Example

**Initial Notification:**
```json
{
  "notification_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "POST_LIKE",
  "actor": {
    "user_id": "user-1",
    "user_name": "Alice"
  },
  "actors_count": 1,
  "actors": ["user-1"]
}
```

**After 4 More Likes:**
```json
{
  "notification_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "POST_LIKE",
  "actor": {
    "user_id": "user-5",
    "user_name": "Eve"
  },
  "actors_count": 5,
  "actors": ["user-1", "user-2", "user-3", "user-4", "user-5"]
}
```

**Note:** The `actor` field always shows the most recent actor, while `actors` contains all actors who triggered the notification.

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized (missing or invalid JWT token) |
| 500 | Internal server error |

### Error Response Format

```json
{
  "success": false,
  "error": "Error message description",
  "error_code": "ERROR_CODE"
}
```

### Common Error Codes

- `SERVER_ERROR`: Internal server error
- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_ERROR`: Authentication failed

### WebSocket Errors

WebSocket errors follow the same format as chat WebSocket errors:

```json
{
  "type": "error",
  "error": "Error message",
  "error_code": "ERROR_CODE"
}
```

---

## Examples

### Example 1: First API Call (Get All Notifications)

**Request:**
```http
GET /api/notifications/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "notification_id": "550e8400-e29b-41d4-a716-446655440000",
        "type": "POST_LIKE",
        "actor": {
          "user_id": "123e4567-e89b-12d3-a456-426614174000",
          "user_name": "John Doe",
          "profile_picture_url": "https://example.com/john.jpg"
        },
        "actors_count": 3,
        "actors": [
          "123e4567-e89b-12d3-a456-426614174000",
          "223e4567-e89b-12d3-a456-426614174001",
          "323e4567-e89b-12d3-a456-426614174002"
        ],
        "target_id": "post-123",
        "target_type": "post",
        "conversation_id": null,
        "message_id": null,
        "created_at": "2024-01-15T10:30:00Z",
        "metadata": {
          "actors_count": 3,
          "actors": [
            "123e4567-e89b-12d3-a456-426614174000",
            "223e4567-e89b-12d3-a456-426614174001",
            "323e4567-e89b-12d3-a456-426614174002"
          ],
          "last_actor_id": "323e4567-e89b-12d3-a456-426614174002"
        }
      }
    ],
    "total_count": 1
  }
}
```

**Note:** After this call, `last_fetch_at` is set to `2024-01-15T10:30:00Z` (or current time).

### Example 2: Subsequent API Call (Get Only New Notifications)

**Request (5 minutes later):**
```http
GET /api/notifications/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (if 2 new notifications were created):**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "notification_id": "660e8400-e29b-41d4-a716-446655440001",
        "type": "FOLLOW",
        "actor": {
          "user_id": "789e4567-e89b-12d3-a456-426614174005",
          "user_name": "Jane Smith",
          "profile_picture_url": ""
        },
        "actors_count": 1,
        "actors": ["789e4567-e89b-12d3-a456-426614174005"],
        "target_id": "user-456",
        "target_type": "user",
        "conversation_id": null,
        "message_id": null,
        "created_at": "2024-01-15T10:33:00Z",
        "metadata": {
          "actors_count": 1,
          "actors": ["789e4567-e89b-12d3-a456-426614174005"],
          "last_actor_id": "789e4567-e89b-12d3-a456-426614174005"
        }
      },
      {
        "notification_id": "770e8400-e29b-41d4-a716-446655440002",
        "type": "NEW_MESSAGE",
        "actor": {
          "user_id": "999e4567-e89b-12d3-a456-426614174006",
          "user_name": "Bob Wilson",
          "profile_picture_url": "https://example.com/bob.jpg"
        },
        "actors_count": 1,
        "actors": ["999e4567-e89b-12d3-a456-426614174006"],
        "target_id": "conversation-123",
        "target_type": "conversation",
        "conversation_id": 123,
        "message_id": 789,
        "created_at": "2024-01-15T10:35:00Z",
        "metadata": {
          "actors_count": 1,
          "actors": ["999e4567-e89b-12d3-a456-426614174006"],
          "last_actor_id": "999e4567-e89b-12d3-a456-426614174006"
        }
      }
    ],
    "total_count": 2
  }
}
```

**Note:** Only notifications created after the last fetch time are returned.

### Example 3: WebSocket Notification Reception

**Client Code:**
```javascript
const ws = new WebSocket('ws://your-domain/ws/user/?token=' + jwtToken);

ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  
  if (message.type === 'notification.new') {
    const notification = message.data.notification;
    
    // Display notification
    showNotificationToast(notification);
    
    // Update notification badge
    updateNotificationBadge();
    
    // Optionally, refresh notification list
    fetchNotifications();
  }
};
```

**Received WebSocket Message:**
```json
{
  "type": "notification.new",
  "data": {
    "notification": {
      "notification_id": "880e8400-e29b-41d4-a716-446655440003",
      "type": "POST_LIKE",
      "actor": {
        "user_id": "111e4567-e89b-12d3-a456-426614174007",
        "user_name": "Alice Brown",
        "profile_picture_url": "https://example.com/alice.jpg"
      },
      "actors_count": 1,
      "actors": ["111e4567-e89b-12d3-a456-426614174007"],
      "target_id": "post-456",
      "target_type": "post",
      "conversation_id": null,
      "message_id": null,
      "created_at": "2024-01-15T10:40:00Z",
      "metadata": {
        "actors_count": 1,
        "actors": ["111e4567-e89b-12d3-a456-426614174007"],
        "last_actor_id": "111e4567-e89b-12d3-a456-426614174007"
      }
    }
  }
}
```

### Example 4: Aggregated Like Notification

**Initial State (1 like):**
```json
{
  "notification_id": "990e8400-e29b-41d4-a716-446655440004",
  "type": "POST_LIKE",
  "actor": {
    "user_id": "user-1",
    "user_name": "First User"
  },
  "actors_count": 1,
  "actors": ["user-1"],
  "target_id": "post-789",
  "target_type": "post",
  "created_at": "2024-01-15T10:00:00Z"
}
```

**After 4 More Likes (WebSocket update):**
```json
{
  "type": "notification.new",
  "data": {
    "notification": {
      "notification_id": "990e8400-e29b-41d4-a716-446655440004",
      "type": "POST_LIKE",
      "actor": {
        "user_id": "user-5",
        "user_name": "Fifth User"
      },
      "actors_count": 5,
      "actors": ["user-1", "user-2", "user-3", "user-4", "user-5"],
      "target_id": "post-789",
      "target_type": "post",
      "created_at": "2024-01-15T10:00:00Z",
      "metadata": {
        "actors_count": 5,
        "actors": ["user-1", "user-2", "user-3", "user-4", "user-5"],
        "last_actor_id": "user-5"
      }
    }
  }
}
```

**Note:** The same `notification_id` is used, but `actors_count` and `actors` are updated. The `actor` field shows the most recent actor.

---

## Best Practices

### Client Implementation

1. **Initial Load:**
   - Call `GET /api/notifications/` on app startup to get all existing notifications
   - Display notifications in UI

2. **Real-time Updates:**
   - Connect to WebSocket to receive new notifications in real-time
   - Update UI when `notification.new` message is received
   - Optionally refresh notification list periodically

3. **Periodic Refresh:**
   - Call `GET /api/notifications/` periodically (e.g., every 5 minutes) to catch any missed notifications
   - Subsequent calls will only return new notifications

4. **Error Handling:**
   - Handle WebSocket disconnections gracefully
   - Implement retry logic for failed API calls
   - Show user-friendly error messages

### Server-Side Notes

- Notifications are created automatically via Django signals
- No manual notification creation is required
- Self-actions (liking your own post, following yourself) are automatically skipped
- Aggregation happens automatically for like notifications
- Fetch tracking is handled automatically

---

## Summary

- **Single REST Endpoint:** `GET /api/notifications/` - Returns all notifications on first call, only new ones on subsequent calls
- **WebSocket Integration:** Real-time notifications via existing chat WebSocket connection
- **Automatic Creation:** Notifications created via Django signals (no HTTP endpoint for creation)
- **Fetch Tracking:** Automatic server-side tracking of last fetch time
- **Aggregation:** Like notifications are automatically aggregated
- **No Read Status:** No mark-as-read functionality (simplified system)

---

**Last Updated:** 2024-01-15
