"""
F4 Deadline Notification System - Comprehensive Test
Tests email notification logic for 2-day threshold
"""

from app import create_app, db
from app.models import User, Case, Deadline, DeadlineNotification
from app.services.deadline_notifier import get_deadline_notifier
from app.services.email_service import get_email_service
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_deadline_notification_system():
    """Run comprehensive tests on deadline notification system"""
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("  F4 DEADLINE NOTIFICATION SYSTEM - COMPREHENSIVE TEST")
        print("="*70 + "\n")
        
        # Test 1: Check SMTP Configuration
        print("TEST 1: SMTP Configuration")
        print("-" * 70)
        email_service = get_email_service()
        print(f"✓ SMTP Enabled: {email_service.enabled}")
        print(f"✓ SMTP Server: {email_service.smtp_server}:{email_service.smtp_port}")
        print(f"✓ Sender Email: {email_service.sender_email}")
        print(f"✓ Username Configured: {bool(email_service.smtp_username)}")
        print(f"✓ Password Configured: {bool(email_service.smtp_password)}")
        
        if not email_service.enabled:
            print("\n⚠️  WARNING: SMTP not configured. Email notifications will not work.")
            print("   Configure SMTP credentials in .env file:")
            print("   - SMTP_USERNAME")
            print("   - SMTP_PASSWORD")
        print()
        
        # Test 2: Check User Email Configuration
        print("TEST 2: User Email Configuration")
        print("-" * 70)
        users_with_email = User.query.filter(User.email.isnot(None), User.email != '').count()
        total_users = User.query.count()
        print(f"✓ Total users: {total_users}")
        print(f"✓ Users with email: {users_with_email}")
        print(f"✓ Users without email: {total_users - users_with_email}")
        
        if users_with_email > 0:
            sample_user = User.query.filter(User.email.isnot(None)).first()
            print(f"✓ Sample: {sample_user.name} ({sample_user.email})")
        else:
            print("⚠️  No users have email configured yet")
        print()
        
        # Test 3: Check Deadlines Within 2-Day Threshold
        print("TEST 3: Deadlines Within 2-Day Threshold")
        print("-" * 70)
        now = datetime.utcnow()
        threshold = now + timedelta(days=2)
        
        imminent_deadlines = Deadline.query.filter(
            Deadline.is_completed == False,
            Deadline.due_date <= threshold
        ).all()
        
        print(f"✓ Total active deadlines: {Deadline.query.filter_by(is_completed=False).count()}")
        print(f"✓ Imminent deadlines (≤2 days): {len(imminent_deadlines)}")
        
        if imminent_deadlines:
            print(f"\nImminent Deadlines:")
            for d in imminent_deadlines[:5]:  # Show first 5
                days_until = (d.due_date - now).days
                hours_until = (d.due_date - now).total_seconds() / 3600
                print(f"  • {d.case.case_number}: {d.title}")
                print(f"    Due: {d.due_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"    Time until: {days_until} days ({hours_until:.1f} hours)")
                print(f"    Advocate: {d.case.lawyer.name}")
                print(f"    Email: {d.case.lawyer.email or 'NOT CONFIGURED'}")
                print()
        else:
            print("  (No imminent deadlines found)")
        print()
        
        # Test 4: Check Notification History
        print("TEST 4: Notification History")
        print("-" * 70)
        total_notifications = DeadlineNotification.query.count()
        successful_notifications = DeadlineNotification.query.filter_by(email_sent=True).count()
        
        print(f"✓ Total notifications sent: {total_notifications}")
        print(f"✓ Successful emails: {successful_notifications}")
        print(f"✓ Failed emails: {total_notifications - successful_notifications}")
        
        if total_notifications > 0:
            recent = DeadlineNotification.query.order_by(
                DeadlineNotification.sent_at.desc()
            ).limit(5).all()
            
            print(f"\nRecent Notifications:")
            for n in recent:
                status = "✓ Sent" if n.email_sent else "✗ Failed"
                print(f"  {status} - {n.sent_at.strftime('%Y-%m-%d %H:%M')}")
                print(f"    To: {n.email_address}")
                print(f"    Deadline: {n.deadline.title}")
                if n.error_message:
                    print(f"    Error: {n.error_message}")
                print()
        else:
            print("  (No notifications sent yet)")
        print()
        
        # Test 5: Create Test Deadline (if user exists)
        print("TEST 5: Create Test Deadline Within 2 Days")
        print("-" * 70)
        
        # Find a user with email
        test_user = User.query.filter(User.email.isnot(None), User.email != '').first()
        
        if test_user:
            # Find or create a test case
            test_case = Case.query.filter_by(lawyer_id=test_user.id).first()
            
            if not test_case:
                print("Creating test case...")
                test_case = Case(
                    case_number='TEST/2026/001',
                    client_name='Test Client',
                    case_type='Criminal',
                    lawyer_id=test_user.id
                )
                db.session.add(test_case)
                db.session.commit()
            
            # Create a deadline 1 day from now
            test_deadline_date = datetime.utcnow() + timedelta(days=1, hours=6)
            
            test_deadline = Deadline(
                case_id=test_case.id,
                title=f'TEST DEADLINE - Created at {datetime.now().strftime("%H:%M:%S")}',
                due_date=test_deadline_date,
                deadline_type='Test',
                priority='high',
                is_completed=False
            )
            
            db.session.add(test_deadline)
            db.session.commit()
            
            print(f"✓ Created test deadline (ID: {test_deadline.id})")
            print(f"  Case: {test_case.case_number}")
            print(f"  Due: {test_deadline_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Days until: {(test_deadline_date - datetime.utcnow()).days}")
            print(f"  Advocate: {test_user.name} ({test_user.email})")
            
            # Test immediate notification
            print(f"\nTesting immediate notification...")
            notifier = get_deadline_notifier()
            notified, message = notifier.check_and_notify_deadline(test_deadline)
            
            if notified:
                print(f"✓ Notification sent successfully!")
                print(f"  {message}")
            else:
                print(f"○ Notification not sent: {message}")
            
        else:
            print("⚠️  No users with email configured - cannot test notification")
        print()
        
        # Test 6: Manual Scan All Deadlines
        print("TEST 6: Manual Scan All Deadlines")
        print("-" * 70)
        
        notifier = get_deadline_notifier()
        summary = notifier.scan_and_notify_all_imminent_deadlines()
        
        print(f"✓ Deadlines checked: {summary['total_checked']}")
        print(f"✓ Notifications sent: {summary['notifications_sent']}")
        print(f"✓ Already notified: {summary['already_notified']}")
        print(f"✓ Not imminent: {summary['not_imminent']}")
        print(f"✓ No email: {summary['no_email']}")
        print(f"✓ Errors: {summary['errors']}")
        
        if summary['details']:
            print(f"\nDetails:")
            for detail in summary['details'][:10]:  # Show first 10
                print(f"  • {detail['case_number']}: {detail['deadline_title']}")
                print(f"    Status: {detail['status']} - {detail['message']}")
        print()
        
        # Summary
        print("="*70)
        print("  TEST SUMMARY")
        print("="*70)
        print(f"SMTP Configured: {'✓ Yes' if email_service.enabled else '✗ No'}")
        print(f"Users with Email: {users_with_email}/{total_users}")
        print(f"Imminent Deadlines: {len(imminent_deadlines)}")
        print(f"Notifications Sent (Total): {total_notifications}")
        print(f"Notifications Sent (This Run): {summary['notifications_sent']}")
        print("="*70)
        
        if not email_service.enabled:
            print("\n⚠️  ACTION REQUIRED:")
            print("1. Configure SMTP credentials in backend/.env")
            print("2. Add email addresses to user profiles")
            print("3. Re-run this test")
        elif users_with_email == 0:
            print("\n⚠️  ACTION REQUIRED:")
            print("1. Add email addresses to user profiles via /api/profile/update")
            print("2. Re-run this test")
        else:
            print("\n✅ System is ready to send deadline notifications!")

if __name__ == '__main__':
    test_deadline_notification_system()
