"""
Quick setup script to add email to user profile
Run this after configuring SMTP in .env
"""

from app import create_app, db
from app.models import User

def setup_emails():
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("  USER EMAIL SETUP FOR DEADLINE NOTIFICATIONS")
        print("="*60)
        print()
        
        # List all users
        users = User.query.all()
        
        if not users:
            print("✗ No users found in database")
            print("  Please create a user first via registration")
            return
        
        print(f"Found {len(users)} user(s):\n")
        
        for i, user in enumerate(users, 1):
            status = "✓" if user.email else "✗"
            email = user.email or "NOT SET"
            print(f"{i}. {status} {user.name} ({user.enrollment_number})")
            print(f"   Email: {email}")
            print()
        
        # Ask which user to update
        print("-" * 60)
        
        if len(users) == 1:
            selected_user = users[0]
            print(f"Updating email for: {selected_user.name}")
        else:
            choice = input(f"Select user (1-{len(users)}): ").strip()
            try:
                selected_user = users[int(choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice")
                return
        
        print()
        print(f"Current email: {selected_user.email or 'NOT SET'}")
        
        # Ask for new email
        new_email = input("Enter email address (or press Enter to skip): ").strip()
        
        if new_email:
            # Basic validation
            if '@' not in new_email:
                print("✗ Invalid email format (must contain @)")
                return
            
            selected_user.email = new_email
            db.session.commit()
            
            print()
            print("="*60)
            print(f"✓ SUCCESS! Email updated")
            print("="*60)
            print(f"User: {selected_user.name}")
            print(f"Email: {selected_user.email}")
            print()
            print("Next steps:")
            print("1. Make sure SMTP_PASSWORD is set in .env")
            print("2. Run test: python test_deadline_notifications.py")
            print("3. Create a deadline within 2 days to test notification")
        else:
            print("Skipped.")

if __name__ == '__main__':
    setup_emails()
