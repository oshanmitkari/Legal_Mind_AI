"""
Database Migration: Add Email Field and Deadline Notifications
Adds:
1. email field to users table
2. deadline_notifications table for tracking sent emails
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, DeadlineNotification
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Run the migration"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("Starting migration: Adding email field and deadline_notifications table")
            
            # Create all tables (this will create deadline_notifications if it doesn't exist)
            db.create_all()
            logger.info("✓ Tables created/verified")
            
            # Check if email column exists in users table
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'email' not in columns:
                # Add email column to existing users table
                logger.info("Adding email column to users table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text('ALTER TABLE users ADD COLUMN email VARCHAR(150)'))
                    conn.commit()
                logger.info("✓ Email column added to users table")
            else:
                logger.info("✓ Email column already exists in users table")
            
            # Verify deadline_notifications table exists
            tables = inspector.get_table_names()
            if 'deadline_notifications' in tables:
                logger.info("✓ deadline_notifications table exists")
            else:
                logger.info("✗ deadline_notifications table not created")
                return False
            
            logger.info("\n" + "="*60)
            logger.info("✓ MIGRATION COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            logger.info("\nNext steps:")
            logger.info("1. Users can now add their email in profile settings")
            logger.info("2. Deadline notifications will be sent automatically")
            logger.info("3. Configure SMTP settings in .env file")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate()
    exit(0 if success else 1)
