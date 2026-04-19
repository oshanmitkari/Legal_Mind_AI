"""
F4 Background Task: Deadline Monitoring
Periodic task to scan deadlines and send email notifications
"""

import logging
import threading
import time
from datetime import datetime
from app import create_app
from app.services.deadline_notifier import get_deadline_notifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeadlineMonitor:
    """Background task to monitor deadlines and send notifications"""
    
    def __init__(self, check_interval_minutes=60):
        """
        Initialize deadline monitor
        
        Args:
            check_interval_minutes: How often to check for deadlines (default: 60 minutes)
        """
        self.check_interval_minutes = check_interval_minutes
        self.running = False
        self.thread = None
        self.app = None
    
    def start(self):
        """Start the background monitoring task"""
        if self.running:
            logger.warning("Deadline monitor already running")
            return
        
        self.running = True
        self.app = create_app()
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info(f"Deadline monitor started (check interval: {self.check_interval_minutes} minutes)")
    
    def stop(self):
        """Stop the background monitoring task"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Deadline monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_deadlines()
            except Exception as e:
                logger.error(f"Error in deadline monitoring loop: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Sleep for the configured interval
            sleep_seconds = self.check_interval_minutes * 60
            for _ in range(sleep_seconds):
                if not self.running:
                    break
                time.sleep(1)
    
    def _check_deadlines(self):
        """Check all deadlines and send notifications"""
        with self.app.app_context():
            logger.info(f"Starting deadline check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            notifier = get_deadline_notifier()
            summary = notifier.scan_and_notify_all_imminent_deadlines()
            
            logger.info(f"Deadline check complete:")
            logger.info(f"  • Total checked: {summary['total_checked']}")
            logger.info(f"  • Notifications sent: {summary['notifications_sent']}")
            logger.info(f"  • Already notified: {summary['already_notified']}")
            logger.info(f"  • Not imminent: {summary['not_imminent']}")
            logger.info(f"  • No email: {summary['no_email']}")
            logger.info(f"  • Errors: {summary['errors']}")
            
            if summary['notifications_sent'] > 0:
                logger.info(f"Sent {summary['notifications_sent']} deadline alert emails")
                for detail in summary['details']:
                    if detail['status'] == 'sent':
                        logger.info(f"  → {detail['case_number']}: {detail['deadline_title']}")


# Global monitor instance
_monitor = None

def get_deadline_monitor():
    """Get or create deadline monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = DeadlineMonitor(check_interval_minutes=60)  # Check every hour
    return _monitor

def start_deadline_monitor():
    """Start the deadline monitoring background task"""
    monitor = get_deadline_monitor()
    monitor.start()
    return monitor

def stop_deadline_monitor():
    """Stop the deadline monitoring background task"""
    monitor = get_deadline_monitor()
    monitor.stop()
