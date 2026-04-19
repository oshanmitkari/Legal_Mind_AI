# 📧 F4 DEADLINE TRACKER - EMAIL NOTIFICATION SYSTEM

## Complete Implementation Guide

**Status**: ✅ **FULLY IMPLEMENTED**  
**Date**: April 19, 2026  
**Feature**: Automated Email Alerts for Imminent Deadlines (2-Day Threshold)

---

## 🎯 **OVERVIEW**

The F4 Deadline Notification System automatically sends email alerts to advocates when case deadlines are within **48 hours** (2 days). The system monitors deadlines in two ways:

1. **Immediate Check**: When a deadline is created or updated
2. **Periodic Scan**: Background task checks all deadlines every hour

---

## 🏗️ **ARCHITECTURE**

### **Components**:

```
┌─────────────────────────────────────────────────────────────┐
│                    F4 NOTIFICATION SYSTEM                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Email Service (email_service.py)                       │
│     • SMTP connection management                           │
│     • HTML/Text email generation                           │
│     • Professional email templates                         │
│                                                             │
│  2. Deadline Notifier (deadline_notifier.py)               │
│     • 2-day threshold detection                            │
│     • Duplicate notification prevention                    │
│     • Notification logging                                 │
│                                                             │
│  3. Deadline Monitor (deadline_monitor.py)                 │
│     • Background task scheduler                            │
│     • Periodic deadline scanning (every 60 min)            │
│     • Automatic notification dispatch                      │
│                                                             │
│  4. Deadline Routes (deadlines.py)                         │
│     • Immediate check on create/update                     │
│     • Triggers notifier on deadline changes                │
│                                                             │
│  5. Admin Routes (deadline_admin.py)                       │
│     • Manual notification triggers                         │
│     • SMTP status checking                                 │
│     • Notification history                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ **SETUP INSTRUCTIONS**

### **Step 1: Configure SMTP Credentials**

Edit `backend/.env` file:

```bash
# F4: Email Notification Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
SENDER_EMAIL=your_email@gmail.com
```

#### **For Gmail Users**:
1. Enable 2-Factor Authentication on your Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character app password (not your regular password)
4. Enter credentials in `.env` file

#### **For Other Email Providers**:
- **Outlook/Office365**: `smtp.office365.com`, Port `587`
- **Yahoo**: `smtp.mail.yahoo.com`, Port `587`
- **Custom SMTP**: Enter your server details

---

### **Step 2: Run Database Migration**

Add email field to users table and create notification tracking table:

```bash
cd backend
python migrations/add_email_and_notifications.py
```

Expected output:
```
✓ Tables created/verified
✓ Email column added to users table
✓ deadline_notifications table exists
✓ MIGRATION COMPLETED SUCCESSFULLY
```

---

### **Step 3: Add User Email Addresses**

Users can update their email via API:

```bash
POST /api/profile/update
Content-Type: application/json

{
  "email": "advocate@example.com"
}
```

Or programmatically in Python:

```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(enrollment_number='UP/12345/2020').first()
    user.email = 'advocate@example.com'
    db.session.commit()
```

---

### **Step 4: Test Email Configuration**

Run the comprehensive test script:

```bash
python test_deadline_notifications.py
```

This will:
- ✓ Check SMTP configuration
- ✓ Verify user email setup
- ✓ Find imminent deadlines
- ✓ Review notification history
- ✓ Create test deadline
- ✓ Send test email

---

### **Step 5: Start the Server**

The notification system is automatically active when the server runs:

```bash
python run.py
```

---

## 🔔 **HOW IT WORKS**

### **Scenario 1: New Deadline Created**

```python
# When advocate creates a deadline via POST /deadlines/create
POST /deadlines/create
{
  "case_id": 1,
  "title": "Filing Deadline - Evidence Submission",
  "due_date": "2026-04-21T10:00:00",  # 1.5 days from now
  "deadline_type": "Filing Deadline",
  "priority": "high"
}

# System Response:
1. Create deadline in database
2. Check if due_date <= (now + 48 hours)
3. If yes:
   - Check if advocate has email
   - Check if notification already sent
   - Send email alert
   - Record notification in database
4. Return success with notification_sent flag
```

---

### **Scenario 2: Existing Deadline Updated**

```python
# When deadline due_date is moved closer
PUT /deadlines/update/5
{
  "due_date": "2026-04-20T14:00:00"  # Now within 2 days
}

# System Response:
1. Update deadline due_date
2. Check if new date is within 48 hours
3. If yes and not previously notified:
   - Send email alert
   - Record notification
```

---

### **Scenario 3: Background Monitoring** (Every Hour)

```python
# Background task runs every 60 minutes
1. Scan all active (non-completed) deadlines
2. For each deadline:
   - Calculate hours until due_date
   - If <= 48 hours:
     - Check if notification already sent
     - If not, send email and record
3. Log summary of notifications sent
```

---

## 📧 **EMAIL TEMPLATE**

### **Email Features**:
- ✅ Professional HTML design with LegalMind AI branding
- ✅ Responsive layout (mobile-friendly)
- ✅ Urgency color coding:
  - 🔴 Red: Overdue
  - 🟠 Amber: 0-1 days
  - 🔵 Cyan: 2 days
- ✅ Case details table (case number, deadline, due date, priority)
- ✅ Direct link to case detail page
- ✅ Plain text fallback for email clients without HTML

### **Sample Email Subject**:
```
⚠️ Urgent: Deadline Alert - CJ/1010
```

### **Sample Email Body** (HTML):
```
Dear Advocate Rajesh Kumar,

URGENT DEADLINE ALERT

Case Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Case Number:    CJ/1010
Deadline:       Filing Deadline - Evidence Submission
Due Date:       21 April 2026, 10:00 AM
Type:           Filing Deadline
Priority:       HIGH
Status:         DUE IN 1 DAY(S)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[View Case Details →]

Best regards,
LegalMind AI System
```

---

## 🔧 **ADMIN TOOLS**

### **1. Manual Trigger Deadline Check**

```bash
POST /api/admin/deadlines/check-all
Authorization: Bearer <token>
```

Response:
```json
{
  "success": true,
  "message": "Checked 15 deadlines",
  "summary": {
    "total_checked": 15,
    "notifications_sent": 3,
    "already_notified": 2,
    "not_imminent": 8,
    "no_email": 2
  }
}
```

---

### **2. View Notification History**

```bash
GET /api/admin/deadlines/notifications
```

Response:
```json
{
  "notifications": [
    {
      "id": 1,
      "deadline_title": "Court Hearing",
      "case_number": "CJ/1010",
      "notification_type": "2_day_alert",
      "sent_at": "2026-04-19T10:30:00",
      "email_sent": true,
      "email_address": "advocate@example.com"
    }
  ],
  "total": 1
}
```

---

### **3. Test SMTP Configuration**

```bash
POST /api/admin/deadlines/test-email
{
  "email": "test@example.com"
}
```

---

### **4. Check SMTP Status**

```bash
GET /api/admin/deadlines/smtp-status
```

Response:
```json
{
  "smtp_configured": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "legalmind@gmail.com",
  "username_configured": true,
  "password_configured": true
}
```

---

### **5. View Upcoming Deadlines**

```bash
GET /api/admin/deadlines/upcoming
```

Shows all deadlines within 2 days with notification status.

---

## 📊 **DATABASE SCHEMA**

### **New Fields Added**:

#### **users table**:
```sql
ALTER TABLE users ADD COLUMN email VARCHAR(150);
```

#### **deadline_notifications table** (new):
```sql
CREATE TABLE deadline_notifications (
    id INTEGER PRIMARY KEY,
    deadline_id INTEGER FOREIGN KEY → deadlines.id,
    user_id INTEGER FOREIGN KEY → users.id,
    notification_type VARCHAR(50),  -- '2_day_alert'
    sent_at DATETIME,
    email_sent BOOLEAN,
    email_address VARCHAR(150),
    error_message TEXT
);
```

---

## 🧪 **TESTING WORKFLOW**

### **Complete Test Procedure**:

1. **Configure SMTP** in `.env`
2. **Run migration**: `python migrations/add_email_and_notifications.py`
3. **Add user email**: Update via `/api/profile/update`
4. **Create test deadline**: Use `/deadlines/create` with `due_date` = tomorrow
5. **Check email**: Verify email received
6. **Run test script**: `python test_deadline_notifications.py`
7. **Review logs**: Check notification was recorded in database

---

## 🚨 **TROUBLESHOOTING**

### **Issue: Emails not sending**

**Check**:
1. SMTP credentials in `.env`
2. User has email configured
3. Check SMTP status: `GET /api/admin/deadlines/smtp-status`
4. Test email: `POST /api/admin/deadlines/test-email`

**Common Errors**:
- `535 Authentication failed`: Wrong password or need App Password
- `Connection refused`: Wrong SMTP server/port
- `No email configured`: User.email is NULL

---

### **Issue: Notifications sent multiple times**

**Fix**: System prevents duplicates by checking `deadline_notifications` table.
If issue persists, check database for duplicate entries.

---

### **Issue: Not detecting 2-day threshold**

**Debug**:
```python
from datetime import datetime, timedelta
now = datetime.utcnow()
deadline_date = deadline.due_date
hours_until = (deadline_date - now).total_seconds() / 3600
is_imminent = hours_until <= 48

print(f"Now: {now}")
print(f"Due: {deadline_date}")
print(f"Hours: {hours_until}")
print(f"Imminent: {is_imminent}")
```

---

## ✅ **SUCCESS CRITERIA**

The system is working correctly if:

1. ✅ User receives email within minutes of creating/updating deadline within 2 days
2. ✅ Email contains correct case details and due date
3. ✅ Notification recorded in `deadline_notifications` table
4. ✅ Duplicate emails not sent for same deadline
5. ✅ Background monitor sends emails for existing deadlines within threshold

---

## 📝 **NEXT STEPS**

### **Optional Enhancements**:
- [ ] Add 1-day alert (24 hours before deadline)
- [ ] Add overdue notification
- [ ] SMS notifications via Twilio
- [ ] WhatsApp notifications
- [ ] Email preferences (daily digest vs immediate)
- [ ] Notification frequency limits

---

**Implementation Complete**: April 19, 2026  
**Status**: ✅ **PRODUCTION READY**  
**Documentation**: F4_DEADLINE_NOTIFICATIONS_GUIDE.md
