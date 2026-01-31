# Admin Dashboard Guide

## Overview

The admin dashboard provides god-mode access for platform administrators to manage users, content, payments, and moderate abuse.

---

## Access Control

### Admin Authentication

Admin access is controlled via environment variables:
- `ADMIN_EMAIL`: The email address with admin privileges
- `ADMIN_PASSWORD_HASH`: Bcrypt-hashed admin password

Only the user with the matching email can access admin endpoints.

### Accessing Admin Panel

1. Navigate to `/admin/` in your browser
2. Django admin interface loads
3. Login with your superuser credentials

---

## User Management

### Viewing Users

**Admin API:** `GET /api/admin/users_list/?page=1`

Features:
- Search by email or anonymous handle
- Filter by verification status
- Filter by institutional status
- View tokens balance
- See creation date

### Banning Users

**Admin API:** `POST /api/admin/ban_user/`

```json
{
  "user_id": "user-uuid",
  "reason": "Harassment"
}
```

Effects:
- User loses access to platform
- All active chats are frozen
- User cannot login
- Reason is recorded for audit

### Unbanning Users

Use Django admin to toggle `is_banned` to False.

### Deleting Users

**Admin API:** `POST /api/admin/delete_user/`

```json
{
  "user_id": "user-uuid"
}
```

Effects:
- User and all associated data removed
- Chat history deleted
- Irreversible operation

---

## Institution Management

### Approving Domains

**Django Admin:** Institutions → Institution Domains

Features:
- Add new college/university domains
- Mark as approved/unapproved
- Bulk approve/unapprove

### Email List Uploads

Upload CSV files with verified student emails:

```csv
email@college.edu
student1@college.edu
student2@college.edu
```

---

## Chat Management

### Viewing All Chats

**Django Admin:** Chats → Chat Rooms

Search by:
- User email
- Chat ID
- Creation date
- Status (locked/active)

### Locking Chats

**Admin Actions:** Lock Chat

Prevents messaging without payment.

### Unlocking Chats

**Admin Actions:** Unlock Chat

Removes lock status; users can message freely.

### Extending Chat Duration

**Admin Actions:** Extend Chat by 7 Days

Resets expiry timer for a chat room.

### Deleting Chats

**Django Admin:** Select and delete

Removes all messages and chat history.

---

## Content Management

### Managing Stickers

**Django Admin:** Stickers

Features:
- Upload new stickers
- Set as free or premium
- Assign token costs
- Organize by category
- Enable/disable stickers

### Managing Gifts

**Django Admin:** Gifts

Features:
- Upload gift images
- Configure animations (Lottie JSON)
- Set token costs
- Mark as active/inactive

### Uploading Reminder Media

**Django Admin:** Payment Reminders

Features:
- Upload reminder images
- Upload voice message audio
- Schedule automatic delivery
- Track sent/unsent status

---

## Payment Management

### Viewing Subscriptions

**Django Admin:** Payments → Subscriptions

View:
- Payment status (pending/success/failed)
- Payment amount and currency
- Subscription period
- Associated user and chat

### Processing Payments

Payments are handled by Razorpay or Stripe. Admin can:
- View payment details
- Refund transactions
- Verify successful payments

---

## Abuse Moderation

### Viewing Reports

**Django Admin:** Abuse → Abuse Reports

Filter by:
- Status (pending/reviewed/resolved)
- Reported user
- Creation date

### Reviewing Reports

1. Click on report to view details
2. Review evidence URLs
3. Decide action:
   - Ban reported user
   - Dismiss report
   - Document findings

### Taking Action

```json
POST /api/admin/ban_user/
{
  "user_id": "reported-user-uuid",
  "reason": "Report ID: abc123"
}
```

### Recording Resolution

Mark report as "resolved" with admin notes in Django admin.

---

## Admin Logs

All admin actions are logged for audit purposes.

**Django Admin:** Admin Logs

View:
- Admin who performed action
- Action type
- Target user
- Timestamp
- Action details

### Audit Trail

Logs include:
- User bans/unbans
- User deletions
- Chat modifications
- Domain approvals
- Content uploads

---

## Notifications & Reminders

### Viewing Payment Reminders

**Django Admin:** Payment Reminders

Track:
- Reminder type
- Scheduled time
- Delivery status
- Associated chat

### Sending Custom Reminders

Create new PaymentReminder:
```python
from api.models import PaymentReminder, ChatRoom
from django.utils import timezone

chat = ChatRoom.objects.get(id='room-id')
PaymentReminder.objects.create(
    chat_room=chat,
    reminder_type='custom',
    media_url='https://...',
    scheduled_at=timezone.now() + timedelta(hours=1)
)
```

---

## Statistics & Analytics

### Available Metrics

1. **User Metrics**
   - Total users
   - Verified vs unverified
   - Institutional vs non-institutional
   - Banned users

2. **Chat Metrics**
   - Total chats
   - Active chats
   - Locked chats
   - Average chat duration

3. **Payment Metrics**
   - Total revenue
   - Successful transactions
   - Failed transactions
   - Subscription status

4. **Engagement Metrics**
   - Messages per chat
   - Average response time
   - Users with matches

### Generating Reports

```bash
# Django shell
python manage.py shell

from django.db.models import Count
from api.models import User, ChatRoom, ChatMessage

# User count by status
User.objects.values('is_verified', 'is_institutional').annotate(count=Count('id'))

# Active chats
ChatRoom.objects.filter(is_locked=False, is_deleted=False).count()

# Messages statistics
ChatMessage.objects.values('room').annotate(count=Count('id'))
```

---

## Security Best Practices

1. **Protect Admin Email**
   - Use a unique email for admin account
   - Store credentials securely
   - Rotate password regularly

2. **Audit Admin Actions**
   - Review admin logs regularly
   - Monitor for unusual activity
   - Keep backups of logs

3. **Secure Uploads**
   - Validate all file uploads
   - Scan for malware
   - Use CDN for serving media

4. **Data Privacy**
   - Only view emails when necessary
   - Respect user privacy
   - Handle reports confidentially

5. **Access Control**
   - Limit admin users to necessary personnel
   - Use VPN for remote access
   - Enable 2FA when available

---

## Troubleshooting

### Cannot Login to Admin Panel

1. Verify `ADMIN_EMAIL` environment variable matches your email
2. Check `ADMIN_PASSWORD_HASH` is correctly set
3. Clear browser cookies and try again
4. Check Django logs for errors

### Payment Delays

1. Check Redis connection
2. Verify Celery worker is running
3. Monitor payment gateway status
4. Check database for stuck transactions

### Chat Lock Issues

1. Verify subscription status in database
2. Check chat expiry time
3. Manually unlock if necessary
4. Check for Celery task failures

### High Error Rate

1. Check database connection
2. Monitor Redis memory usage
3. Review application logs
4. Check for deployment issues

---

## Common Tasks

### Ban Spammer

```python
from api.models import User

user = User.objects.get(email='spammer@college.edu')
user.is_banned = True
user.ban_reason = 'Spam account'
user.save()
```

### Approve New Domain

```python
from api.models import InstitutionDomain

domain = InstitutionDomain.objects.create(
    domain='newcollege.edu',
    institution_name='New College',
    country='India',
    is_approved=True
)
```

### Create Manual Subscription

```python
from api.models import Subscription, ChatRoom
from django.utils import timezone
from datetime import timedelta

chat = ChatRoom.objects.get(id='room-id')
user = chat.user_a

Subscription.objects.create(
    user=user,
    chat_room=chat,
    payment_id='manual_' + str(timezone.now().timestamp()),
    amount_paise=5000,
    status='success',
    started_at=timezone.now(),
    expires_at=timezone.now() + timedelta(days=30)
)
```

### Generate Token Pack for User

```python
from api.models import User, TokenTransaction

user = User.objects.get(user_uuid='user-uuid')
old_balance = user.tokens_balance
user.tokens_balance += 400
user.save()

TokenTransaction.objects.create(
    user=user,
    transaction_type='bonus',
    amount=400,
    balance_before=old_balance,
    balance_after=user.tokens_balance,
    description='Admin bonus'
)
```

---

## Support & Escalation

For critical issues:
1. Check application logs
2. Review admin logs for context
3. Contact DevOps team
4. Engage technical support
