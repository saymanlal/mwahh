# REST API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
All authenticated endpoints require:
```
Authorization: Bearer <access_token>
```

---

## Authentication Endpoints

### Register User
**POST** `/auth/register/`

**Request:**
```json
{
  "email": "user@college.edu",
  "password": "securepassword123",
  "gender": "M",
  "age": 20
}
```

**Response:** (201 Created)
```json
{
  "message": "OTP sent to email",
  "email": "user@college.edu"
}
```

---

### Verify OTP
**POST** `/auth/verify-otp/`

**Request:**
```json
{
  "email": "user@college.edu",
  "otp": "123456"
}
```

**Response:** (200 OK)
```json
{
  "user": {
    "user_uuid": "uuid-string",
    "anonymous_handle": "swift_tiger2345",
    "email": "user@college.edu",
    "gender": "M",
    "age": 20,
    "is_verified": true,
    "tokens_balance": 200,
    "created_at": "2024-01-01T12:00:00Z"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Resend OTP
**POST** `/auth/resend-otp/`

**Request:**
```json
{
  "email": "user@college.edu"
}
```

**Response:** (200 OK)
```json
{
  "message": "OTP resent"
}
```

---

## User Endpoints

### Get Profile
**GET** `/users/`

**Response:** (200 OK)
```json
{
  "user_uuid": "uuid-string",
  "anonymous_handle": "swift_tiger2345",
  "gender": "M",
  "age": 20,
  "height_cm": 175,
  "degree": "B.Tech Computer Science",
  "profession": "Student",
  "city": "Bangalore",
  "state": "Karnataka",
  "bio": "Love tech and hiking",
  "interests": ["Technology", "Hiking", "Music"],
  "photos": ["url1", "url2"],
  "tokens_balance": 200,
  "is_verified": true,
  "created_at": "2024-01-01T12:00:00Z",
  "match_profile": {
    "preferred_mode": "friend",
    "scope": "global",
    "age_range_min": 18,
    "age_range_max": 30,
    "is_active": true
  }
}
```

---

### Update Profile
**PATCH** `/users/`

**Request:**
```json
{
  "bio": "New bio text",
  "interests": ["Technology", "Hiking"],
  "city": "Delhi"
}
```

**Response:** (200 OK)
```json
{
  "user_uuid": "uuid-string",
  "anonymous_handle": "swift_tiger2345",
  ...
}
```

---

### Update Match Preferences
**POST** `/users/update_match_preferences/`

**Request:**
```json
{
  "preferred_mode": "hookup",
  "scope": "city",
  "age_range_min": 20,
  "age_range_max": 28,
  "height_range_min_cm": 160,
  "height_range_max_cm": 185,
  "preferred_interests": ["Sports", "Technology"]
}
```

**Response:** (200 OK)
```json
{
  "preferred_mode": "hookup",
  "scope": "city",
  ...
}
```

---

## Matching Endpoints

### Get Candidates
**GET** `/matching/`

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 50)

**Response:** (200 OK)
```json
[
  {
    "id": "match-uuid",
    "user_a_handle": "swift_tiger2345",
    "user_b_handle": "bold_eagle7890",
    "mode": "friend",
    "created_at": "2024-01-01T12:00:00Z",
    "expires_at": "2024-02-01T12:00:00Z"
  }
]
```

---

### Create Match
**POST** `/matching/create_match/`

**Request:**
```json
{
  "target_user_id": "target-uuid",
  "mode": "friend"
}
```

**Response:** (201 Created)
```json
{
  "id": "match-uuid",
  "user_a_handle": "swift_tiger2345",
  "user_b_handle": "bold_eagle7890",
  "mode": "friend",
  "created_at": "2024-01-01T12:00:00Z",
  "expires_at": "2024-02-01T12:00:00Z"
}
```

---

## Chat Endpoints

### List Chat Rooms
**GET** `/chat-rooms/`

**Query Parameters:**
- `page`: Page number (default: 1)

**Response:** (200 OK)
```json
[
  {
    "id": "room-uuid",
    "user_a_handle": "swift_tiger2345",
    "user_b_handle": "bold_eagle7890",
    "created_at": "2024-01-01T12:00:00Z",
    "expires_at": "2024-01-08T12:00:00Z",
    "is_locked": false,
    "days_remaining": 5,
    "last_activity": "2024-01-02T10:30:00Z"
  }
]
```

---

### Get Chat Room
**GET** `/chat-rooms/{room_id}/`

**Response:** (200 OK)
```json
{
  "id": "room-uuid",
  "user_a_handle": "swift_tiger2345",
  "user_b_handle": "bold_eagle7890",
  "created_at": "2024-01-01T12:00:00Z",
  "expires_at": "2024-01-08T12:00:00Z",
  "is_locked": false,
  "days_remaining": 5
}
```

---

### Get Messages
**GET** `/chat-rooms/{room_id}/messages/?page=1`

**Response:** (200 OK)
```json
[
  {
    "id": "msg-uuid",
    "sender_handle": "swift_tiger2345",
    "message_type": "text",
    "content": "Hello!",
    "media_url": "",
    "is_seen": true,
    "is_deleted": false,
    "created_at": "2024-01-01T12:30:00Z"
  }
]
```

---

### Send Message
**POST** `/chat-rooms/{room_id}/send_message/`

**Request:**
```json
{
  "message_type": "text",
  "content": "Hello there!",
  "media_url": ""
}
```

**Response:** (201 Created)
```json
{
  "id": "msg-uuid",
  "sender_handle": "swift_tiger2345",
  "message_type": "text",
  "content": "Hello there!",
  "media_url": "",
  "is_seen": false,
  "is_deleted": false,
  "created_at": "2024-01-01T12:30:00Z"
}
```

---

## Stickers & Gifts

### Get Stickers
**GET** `/stickers/?tier=free&category=emotions`

**Query Parameters:**
- `tier`: `free` or `premium`
- `category`: Sticker category

**Response:** (200 OK)
```json
[
  {
    "id": "sticker-uuid",
    "name": "Smiling Face",
    "tier": "free",
    "image_url": "https://...",
    "thumbnail_url": "https://...",
    "token_cost": 0,
    "category": "emotions",
    "tags": ["happy", "friendly"]
  }
]
```

---

### Get Gifts
**GET** `/gifts/`

**Response:** (200 OK)
```json
[
  {
    "id": "gift-uuid",
    "name": "Flower Bouquet",
    "image_url": "https://...",
    "animation_url": "https://...",
    "token_cost": 50,
    "is_active": true
  }
]
```

---

### Send Gift
**POST** `/gifts/send/`

**Request:**
```json
{
  "gift_id": "gift-uuid",
  "recipient_uuid": "user-uuid",
  "room_id": "room-uuid",
  "message": "For you!"
}
```

**Response:** (201 Created)
```json
{
  "id": "sent-gift-uuid",
  "gift_details": {
    "id": "gift-uuid",
    "name": "Flower Bouquet",
    ...
  },
  "sender_handle": "swift_tiger2345",
  "message": "For you!",
  "created_at": "2024-01-01T12:45:00Z"
}
```

---

## Notifications

### Get Notifications
**GET** `/notifications/?page=1`

**Response:** (200 OK)
```json
[
  {
    "id": "notif-uuid",
    "notification_type": "match",
    "title": "New Match!",
    "body": "You have a new match!",
    "related_room_id": "room-uuid",
    "is_read": false,
    "is_dismissed": false,
    "created_at": "2024-01-01T11:00:00Z"
  }
]
```

---

### Mark as Read
**POST** `/notifications/mark_as_read/`

**Request:**
```json
{
  "notification_id": "notif-uuid"
}
```

**Response:** (200 OK)
```json
{
  "status": "marked as read"
}
```

---

## Abuse Reporting

### Report Abuse
**POST** `/abuse/report/`

**Request:**
```json
{
  "reported_user_id": "user-uuid",
  "reason": "Harassment",
  "evidence_urls": ["url1", "url2"]
}
```

**Response:** (201 Created)
```json
{
  "message": "Report submitted"
}
```

---

## Admin Endpoints

All admin endpoints require `ADMIN_EMAIL` matching request user.

### List Users
**GET** `/admin/users_list/?page=1`

**Response:** (200 OK)
```json
[
  {
    "user_uuid": "uuid",
    "email": "user@college.edu",
    "anonymous_handle": "swift_tiger2345",
    "age": 20,
    "is_verified": true,
    "is_institutional": true,
    "is_banned": false,
    "created_at": "2024-01-01T12:00:00Z",
    "tokens_balance": 200
  }
]
```

---

### Ban User
**POST** `/admin/ban_user/`

**Request:**
```json
{
  "user_id": "user-uuid",
  "reason": "Policy violation"
}
```

**Response:** (200 OK)
```json
{
  "status": "user banned"
}
```

---

### Delete User
**POST** `/admin/delete_user/`

**Request:**
```json
{
  "user_id": "user-uuid"
}
```

**Response:** (200 OK)
```json
{
  "status": "user deleted"
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "code": "error_code"
}
```

### Common Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Server Error
