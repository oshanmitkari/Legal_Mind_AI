"""
F4 Deadline Notification Service
Monitors deadlines and triggers email alerts for imminent deadlines
"""

from datetime import datetime, timedelta
from app.models import db, Deadline, DeadlineNotification
from app.services.email_service import get_email_service
import logging

logger = logging.getLogger(__name__)


class DeadlineNotifier:
    """Service to check and notify about imminent deadlines"""
    
    # Threshold for "imminent" deadlines (2 days = 48 hours)
    IMMINENT_THRESHOLD_DAYS = 2
    
    def __init__(self):
        self.email_service = get_email_service()
    
    def check_and_notify_deadline(self, deadline):
        """
        Check if a single deadline is within the 2-day threshold and send notification
        
        Args:
            deadline: Deadline model instance
        
        Returns:
            tuple: (notified: bool, message: str)
        """
        # Skip completed deadlines
        if deadline.is_completed:
            return False, "Deadline already completed"
        
        # Calculate days until deadline
        now = datetime.utcnow()
        time_until = deadline.due_date - now
        days_until = time_until.days
        hours_until = time_until.total_seconds() / 3600
        
        # Check if within 48 hours (2 days)
        is_imminent = hours_until <= (self.IMMINENT_THRESHOLD_DAYS * 24)
        
        if not is_imminent:
            return False, f"Deadline not imminent ({days_until} days away)"
        
        # Check if notification already sent for this deadline
        existing_notification = DeadlineNotification.query.filter_by(
            deadline_id=deadline.id,
            notification_type='2_day_alert'
        ).first()
        
        if existing_notification:
            return False, "Notification already sent for this deadline"
        
        # Get advocate email
        advocate = deadline.case.lawyer
        if not advocate.email:
            return False, f"Advocate {advocate.name} has no email configured"
        
        # Prepare deadline info for email
        deadline_info = {
            'case_id': deadline.case.id,
            'case_number': deadline.case.case_number,
            'case_title': deadline.case.client_name,
            'deadline_title': deadline.title,
            'due_date': deadline.due_date,
            'days_until': days_until,
            'priority': deadline.priority,
            'deadline_type': deadline.deadline_type
        }
        
        # Send email
        success, message = self.email_service.send_deadline_alert(
            recipient_email=advocate.email,
            advocate_name=advocate.name,
            deadline_info=deadline_info
        )
        
        if success:
            # Record notification in database
            notification = DeadlineNotification(
                deadline_id=deadline.id,
                user_id=advocate.id,
                notification_type='2_day_alert',
                sent_at=datetime.utcnow(),
                email_sent=True,
                email_address=advocate.email
            )
            db.session.add(notification)
            db.session.commit()
            
            logger.info(f"Deadline notification sent: {deadline.title} (ID: {deadline.id}) to {advocate.email}")
            return True, f"Email sent to {advocate.email}"
        else:
            logger.error(f"Failed to send notification for deadline {deadline.id}: {message}")
            return False, message
    
    def scan_and_notify_all_imminent_deadlines(self):
        """
        Scan all active deadlines and send notifications for imminent ones
        
        Returns:
            dict: Summary of notifications sent
        """
        # Get all non-completed deadlines
        active_deadlines = Deadline.query.filter_by(is_completed=False).all()
        
        summary = {
            'total_checked': len(active_deadlines),
            'notifications_sent': 0,
            'already_notified': 0,
            'not_imminent': 0,
            'no_email': 0,
            'errors': 0,
            'details': []
        }
        
        for deadline in active_deadlines:
            notified, message = self.check_and_notify_deadline(deadline)
            
            if notified:
                summary['notifications_sent'] += 1
                summary['details'].append({
                    'deadline_id': deadline.id,
                    'deadline_title': deadline.title,
                    'case_number': deadline.case.case_number,
                    'status': 'sent',
                    'message': message
                })
            else:
                # Categorize the reason for not sending
                if 'already sent' in message.lower():
                    summary['already_notified'] += 1
                elif 'not imminent' in message.lower():
                    summary['not_imminent'] += 1
                elif 'no email' in message.lower():
                    summary['no_email'] += 1
                else:
                    summary['errors'] += 1
                
                summary['details'].append({
                    'deadline_id': deadline.id,
                    'deadline_title': deadline.title,
                    'case_number': deadline.case.case_number,
                    'status': 'skipped',
                    'message': message
                })
        
        logger.info(f"Deadline scan complete: {summary['notifications_sent']} notifications sent out of {summary['total_checked']} deadlines")
        return summary
    
    def check_single_deadline_on_create_or_update(self, deadline):
        """
        Check a deadline immediately upon creation or update
        This is called from the deadline routes when deadlines are created/updated
        
        Args:
            deadline: Newly created or updated Deadline instance
        
        Returns:
            bool: True if notification was sent
        """
        notified, message = self.check_and_notify_deadline(deadline)
        
        if notified:
            logger.info(f"Immediate notification sent for deadline {deadline.id}: {message}")
        else:
            logger.debug(f"No immediate notification for deadline {deadline.id}: {message}")
        
        return notified


# Singleton instance
_deadline_notifier = None

def get_deadline_notifier():
    """Get or create deadline notifier instance"""
    global _deadline_notifier
    if _deadline_notifier is None:
        _deadline_notifier = DeadlineNotifier()
    return _deadline_notifier
