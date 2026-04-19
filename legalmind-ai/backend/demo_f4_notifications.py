"""
F4 Deadline Notification - Interactive Demo
Demonstrates the email notification system with step-by-step examples
"""

from app import create_app, db
from app.models import User, Case, Deadline
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def demo():
    """Interactive demo of F4 notification system"""
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("  F4 DEADLINE NOTIFICATION SYSTEM - INTERACTIVE DEMO")
        print("="*70 + "\n")
        
        # Step 1: Setup user with email
        print("STEP 1: Setting up advocate with email")
        print("-" * 70)
        
        user = User.query.first()
        if not user:
            print("✗ No users found. Please create a user first.")
            return
        
        print(f"Current user: {user.name} ({user.enrollment_number})")
        print(f"Current email: {user.email or 'NOT SET'}")
        
        if not user.email:
            # Ask for email
            print("\nTo enable notifications, we need an email address.")
            print("Would you like to:")
            print("  1. Enter a real email (will send actual notification)")
            print("  2. Use test email (won't send, but will log)")
            print("  3. Skip demo")
            
            choice = input("\nChoice (1/2/3): ").strip()
            
            if choice == '1':
                email = input("Enter email address: ").strip()
                user.email = email
                db.session.commit()
                print(f"✓ Email set to: {email}")
            elif choice == '2':
                user.email = 'test@example.com'
                db.session.commit()
                print(f"✓ Email set to: test@example.com (test mode)")
            else:
                print("Demo skipped.")
                return
        else:
            print(f"✓ Email already configured: {user.email}")
        
        print()
        
        # Step 2: Create or use existing case
        print("STEP 2: Finding or creating test case")
        print("-" * 70)
        
        case = Case.query.filter_by(lawyer_id=user.id).first()
        if not case:
            print("Creating new test case...")
            case = Case(
                case_number='DEMO/2026/001',
                client_name='Demo Client - F4 Test',
                case_type='Civil',
                lawyer_id=user.id
            )
            db.session.add(case)
            db.session.commit()
            print(f"✓ Created case: {case.case_number}")
        else:
            print(f"✓ Using existing case: {case.case_number}")
        
        print()
        
        # Step 3: Create deadline within 2 days
        print("STEP 3: Creating deadline within 2-day threshold")
        print("-" * 70)
        
        # Calculate a due date 1 day from now
        due_date = datetime.utcnow() + timedelta(days=1, hours=10)
        
        print(f"Creating deadline:")
        print(f"  Title: Demo Court Hearing - F4 Test")
        print(f"  Due Date: {due_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Days from now: 1 day")
        print(f"  Advocate: {user.name}")
        print(f"  Email: {user.email}")
        
        # Create deadline
        deadline = Deadline(
            case_id=case.id,
            title='Demo Court Hearing - F4 Test',
            due_date=due_date,
            deadline_type='Court Date',
            priority='high',
            is_completed=False
        )
        
        db.session.add(deadline)
        db.session.commit()
        
        print(f"✓ Deadline created (ID: {deadline.id})")
        print()
        
        # Step 4: Trigger notification check
        print("STEP 4: Checking if notification should be sent")
        print("-" * 70)
        
        from app.services.deadline_notifier import get_deadline_notifier
        
        notifier = get_deadline_notifier()
        
        # Calculate time until deadline
        now = datetime.utcnow()
        hours_until = (deadline.due_date - now).total_seconds() / 3600
        is_within_threshold = hours_until <= 48
        
        print(f"Deadline analysis:")
        print(f"  Current time: {now.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Due date: {deadline.due_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Hours until: {hours_until:.1f} hours")
        print(f"  Within 48-hour threshold: {is_within_threshold}")
        print()
        
        if is_within_threshold:
            print("✓ Deadline is within 2-day threshold!")
            print("Triggering notification check...")
            print()
            
            notified, message = notifier.check_and_notify_deadline(deadline)
            
            if notified:
                print(f"✅ NOTIFICATION SENT!")
                print(f"   {message}")
                print()
                print(f"Email details:")
                print(f"  To: {user.email}")
                print(f"  Subject: ⚠️ Urgent: Deadline Alert - {case.case_number}")
                print(f"  Content: Professional HTML email with case details")
                print()
                
                # Show notification record
                from app.models import DeadlineNotification
                notification = DeadlineNotification.query.filter_by(
                    deadline_id=deadline.id
                ).first()
                
                if notification:
                    print(f"Notification logged in database:")
                    print(f"  ID: {notification.id}")
                    print(f"  Type: {notification.notification_type}")
                    print(f"  Sent at: {notification.sent_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"  Email sent: {notification.email_sent}")
                    print(f"  Email address: {notification.email_address}")
            else:
                print(f"○ Notification not sent")
                print(f"   Reason: {message}")
        else:
            print("○ Deadline is NOT within 2-day threshold")
            print("   No notification will be sent")
        
        print()
        
        # Step 5: Show how to test manually
        print("STEP 5: Manual notification testing")
        print("-" * 70)
        print("You can manually trigger notification checks using:")
        print()
        print("API Endpoint:")
        print("  POST /api/admin/deadlines/check-all")
        print()
        print("Python Command:")
        print("  from app.services.deadline_notifier import get_deadline_notifier")
        print("  notifier = get_deadline_notifier()")
        print("  summary = notifier.scan_and_notify_all_imminent_deadlines()")
        print()
        
        # Step 6: Cleanup option
        print()
        print("="*70)
        print("DEMO COMPLETE")
        print("="*70)
        print()
        print("Would you like to:")
        print("  1. Keep the test deadline (for further testing)")
        print("  2. Delete the test deadline")
        
        cleanup = input("\nChoice (1/2): ").strip()
        
        if cleanup == '2':
            # Delete the deadline and its notifications
            from app.models import DeadlineNotification
            DeadlineNotification.query.filter_by(deadline_id=deadline.id).delete()
            db.session.delete(deadline)
            db.session.commit()
            print("✓ Test deadline deleted")
        else:
            print("✓ Test deadline preserved")
        
        print()
        print("="*70)
        print("Thank you for testing F4 Deadline Notifications!")
        print("="*70)

if __name__ == '__main__':
    demo()
