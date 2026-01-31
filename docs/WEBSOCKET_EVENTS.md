# WebSocket Events Documentation

## Connection
**URL:** `ws://localhost:8000/ws/chat/{room_id}/`

Requires authentication token in query string or header.

---

## Client → Server Events

### Message Event
Send a message to the chat room.

**Payload:**
```json
{
  "type": "message",
  "message_type": "text",
  "content": "Hello!",
  "media_url": ""
}
```

**Parameters:**
- `type`: Must be `"message"`
- `message_type`: `"text"`, `"image"`, `"voice"`, `"sticker"`, or `"gift"`
- `content`: Message text (required for text messages)
- `media_url`: URL to media file (for image/voice/sticker)

---

### Typing Event
Indicate typing status.

**Payload:**
```json
{
  "type": "typing",
  "is_typing": true
}
```

**Parameters:**
- `type`: Must be `"typing"`
- `is_typing`: `true` or `false`

---

### Seen Event
Mark a message as seen.

**Payload:**
```json
{
  "type": "seen",
  "message_id": "message-uuid"
}
```

**Parameters:**
- `type`: Must be `"seen"`
- `message_id`: UUID of the message

---

## Server → Client Events

### Message Event
Receive a new message.

**Payload:**
```json
{
  "type": "message",
  "message_id": "msg-uuid",
  "sender": "swift_tiger2345",
  "message_type": "text",
  "content": "Hello!",
  "media_url": "",
  "timestamp": "2024-01-01T12:30:00Z"
}
```

---

### Typing Indicator
User is typing.

**Payload:**
```json
{
  "type": "typing",
  "user": "bold_eagle7890",
  "is_typing": true
}
```

---

### Message Seen
Message was seen by recipient.

**Payload:**
```json
{
  "type": "seen",
  "message_id": "msg-uuid",
  "user": "bold_eagle7890"
}
```

---

### User Joined
User joined the chat.

**Payload:**
```json
{
  "type": "user_joined",
  "user": "bold_eagle7890"
}
```

---

### User Left
User left the chat.

**Payload:**
```json
{
  "type": "user_left",
  "user": "bold_eagle7890"
}
```

---

## Error Handling

Errors are sent as:
```json
{
  "error": "Error message"
}
```

### Common Errors
- `"Chat room is locked"` - Room requires active subscription
- `"Invalid JSON"` - Malformed message
- `"Unknown message type"` - Invalid event type
- `"Empty message"` - No content provided

---

## Connection Lifecycle

1. Client connects to WebSocket URL with auth token
2. Client receives connection confirmation
3. Client and server exchange events
4. Client disconnects (automatic cleanup)

---

## Implementation Example (JavaScript)

```javascript
const token = localStorage.getItem('access_token')
const ws = new WebSocket(`ws://localhost:8000/ws/chat/${roomId}/?token=${token}`)

ws.onopen = () => {
  console.log('Connected')
}

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  
  if (data.type === 'message') {
    console.log(`${data.sender}: ${data.content}`)
  } else if (data.type === 'typing') {
    console.log(`${data.user} is ${data.is_typing ? 'typing' : 'not typing'}`)
  }
}

// Send message
ws.send(JSON.stringify({
  type: 'message',
  message_type: 'text',
  content: 'Hello!'
}))

// Indicate typing
ws.send(JSON.stringify({
  type: 'typing',
  is_typing: true
}))

// Mark as seen
ws.send(JSON.stringify({
  type: 'seen',
  message_id: 'msg-uuid'
}))

ws.onclose = () => {
  console.log('Disconnected')
}
```

---

## Authentication

WebSocket connections are authenticated via:

1. **Query String Parameter:**
   ```
   ws://localhost:8000/ws/chat/{room_id}/?token=<access_token>
   ```

2. **Authorization Header (if supported):**
   ```
   Authorization: Bearer <access_token>
   ```

Token must be a valid JWT access token from login/register endpoint.

---

## Rate Limiting

- Message rate: 1 per 500ms
- Typing events: 1 per 1000ms
- Connection limit: 100 concurrent connections per user

Exceeding limits may result in temporary disconnection.

---

## Best Practices

1. **Handle Disconnections**: Implement reconnection logic with exponential backoff
2. **Message Ordering**: Client should order messages by `timestamp` field
3. **Typing Indicators**: Debounce typing events
4. **Seen Receipts**: Only mark messages from other users as seen
5. **Error Handling**: Gracefully handle and log all errors
6. **Memory Management**: Clean up old messages from memory periodically
