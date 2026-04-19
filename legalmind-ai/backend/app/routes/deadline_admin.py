"""
F4 Admin Routes: Deadline Notification Management
Admin tools for testing and monitoring deadline notifications
"""

from flask import Blueprint, jsonify, request
from app.utils.auth_utils import login_required, get_current_user
from app.models import db, Deadline, DeadlineNotification, User
from app.services.deadline_notifier import get_deadline_notifier
from app.services.email_service import get_email_service
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
deadline_admin_bp = Blueprint('deadline_admin', __name__)


@deadline_admin_bp.route('/api/admin/deadlines/check-all', methods=['POST'])
@login_required
def check_all_deadlines():
    """
    Manually trigger deadline check for all active deadlines
    Admin tool for testing
    """
    user = get_current_user()
    
    # Only admins can trigger manual checks
    if not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    notifier = get_deadline_notifier()
    summary = notifier.scan_and_notify_all_imminent_deadlines()
    
    logger.info(f"Manual deadline check triggered by {user.name}")
    
    return jsonify({
        'success': True,
        'message': f'Checked {summary["total_checked"]} deadlines',
        'summary': summary
    }), 200


@deadline_admin_bp.route('/api/admin/deadlines/notifications', methods=['GET'])
@login_required
def get_notification_history():
    """
    Get history of sent deadline notifications
    """
    user = get_current_user()
    
    # Get all notifications (admin) or user's notifications (non-admin)
    if user.is_admin:
        notifications = DeadlineNotification.query.order_by(
            DeadlineNotification.sent_at.desc()
        ).limit(100).all()
    else:
        notifications = DeadlineNotification.query.filter_by(
            user_id=user.id
        ).order_by(
            DeadlineNotification.sent_at.desc()
        ).limit(50).all()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'deadline_title': n.deadline.title,
            'case_number': n.deadline.case.case_number,
            'notification_type': n.notification_type,
            'sent_at': n.sent_at.isoformat(),
            'email_sent': n.email_sent,
            'email_address': n.email_address,
            'error_message': n.error_message
        } for n in notifications],
        'total': len(notifications)
    }), 200


@deadline_admin_bp.route('/api/admin/deadlines/test-email', methods=['POST'])
@login_required
def test_email():
    """
    Send a test email to verify SMTP configuration
    """
    user = get_current_user()
    
    data = request.get_json()
    recipient = data.get('email', user.email)
    
    if not recipient:
        return jsonify({'error': 'No email address provided'}), 400
    
    # Create test deadline info
    test_deadline_info = {
        'case_id': 1,
        'case_number': 'TEST/2026/001',
        'case_title': 'Test Case for Email Verification',
        'deadline_title': 'Test Deadline - Email Configuration Check',
        'due_date': datetime.utcnow() + timedelta(days=1),
        'days_until': 1,
        'priority': 'high',
        'deadline_type': 'Test'
    }
    
    email_service = get_email_service()
    success, message = email_service.send_deadline_alert(
        recipient_email=recipient,
        advocate_name=user.name,
        deadline_info=test_deadline_info
    )
    
    if success:
        logger.info(f"Test email sent to {recipient}")
        return jsonify({
            'success': True,
            'message': f'Test email sent to {recipient}'
        }), 200
    else:
        logger.error(f"Test email failed: {message}")
        return jsonify({
            'success': False,
            'error': message
        }), 500


@deadline_admin_bp.route('/api/admin/deadlines/smtp-status', methods=['GET'])
@login_required
def smtp_status():
    """
    Check SMTP configuration status
    """
    email_service = get_email_service()
    
    return jsonify({
        'smtp_configured': email_service.enabled,
        'smtp_server': email_service.smtp_server,
        'smtp_port': email_service.smtp_port,
        'sender_email': email_service.sender_email,
        'username_configured': bool(email_service.smtp_username),
        'password_configured': bool(email_service.smtp_password)
    }), 200


@deadline_admin_bp.route('/api/admin/deadlines/upcoming', methods=['GET'])
@login_required
def get_upcoming_deadlines():
    """
    Get all upcoming deadlines within 2 days (for testing notification logic)
    """
    user = get_current_user()
    
    # Get deadlines within 2 days
    threshold_date = datetime.utcnow() + timedelta(days=2)
    
    if user.is_admin:
        # Admin sees all deadlines
        deadlines = Deadline.query.filter(
            Deadline.is_completed == False,
            Deadline.due_date <= threshold_date
        ).order_by(Deadline.due_date.asc()).all()
    else:
        # Users see only their deadlines
        deadlines = Deadline.query.join(Deadline.case).filter(
            Deadline.is_completed == False,
            Deadline.due_date <= threshold_date,
            Deadline.case.has(lawyer_id=user.id)
        ).order_by(Deadline.due_date.asc()).all()
    
    return jsonify({
        'deadlines': [{
            'id': d.id,
            'title': d.title,
            'case_number': d.case.case_number,
            'due_date': d.due_date.isoformat(),
            'days_until': (d.due_date - datetime.utcnow()).days,
            'hours_until': (d.due_date - datetime.utcnow()).total_seconds() / 3600,
            'priority': d.priority,
            'deadline_type': d.deadline_type,
            'has_notification': len(d.notifications) > 0,
            'notification_count': len(d.notifications)
        } for d in deadlines],
        'total': len(deadlines)
    }), 200
