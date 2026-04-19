"""
F4 Email Notification Service
Handles deadline alert emails to advocates
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import current_app


class EmailService:
    """Service for sending deadline notification emails"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.sender_email = os.getenv('SENDER_EMAIL', self.smtp_username)
        self.enabled = bool(self.smtp_username and self.smtp_password)
    
    def send_deadline_alert(self, recipient_email, advocate_name, deadline_info):
        """
        Send deadline alert email to advocate
        
        Args:
            recipient_email (str): Advocate's email address
            advocate_name (str): Advocate's name
            deadline_info (dict): Deadline details including:
                - case_number
                - case_title
                - deadline_title
                - due_date
                - days_until
                - priority
                - deadline_type
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.enabled:
            return False, "Email service not configured (SMTP credentials missing)"
        
        if not recipient_email:
            return False, "Recipient email not provided"
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"⚠️ Urgent: Deadline Alert - {deadline_info['case_number']}"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Create plain text and HTML versions
            text_content = self._create_text_email(advocate_name, deadline_info)
            html_content = self._create_html_email(advocate_name, deadline_info)
            
            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
        
        except smtplib.SMTPAuthenticationError:
            return False, "SMTP authentication failed - check credentials"
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"
    
    def _create_text_email(self, advocate_name, deadline_info):
        """Create plain text email content"""
        days_text = self._format_days_text(deadline_info['days_until'])
        
        return f"""
Dear Advocate {advocate_name},

URGENT DEADLINE ALERT

This is an automated notification from LegalMind AI regarding an imminent deadline.

Case Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Case Number:    {deadline_info['case_number']}
Case Title:     {deadline_info.get('case_title', 'N/A')}
Deadline:       {deadline_info['deadline_title']}
Due Date:       {deadline_info['due_date'].strftime('%d %B %Y, %I:%M %p')}
Type:           {deadline_info['deadline_type']}
Priority:       {deadline_info['priority'].upper()}
Status:         {days_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMMEDIATE ACTION REQUIRED:
This deadline is within 48 hours. Please take necessary action immediately.

To view full case details and manage deadlines, log in to:
https://legalmind-ai.onrender.com/cases/{deadline_info.get('case_id', '')}

Best regards,
LegalMind AI System
Automated Deadline Monitoring Service

---
This is an automated email. Please do not reply to this message.
For support, contact: support@legalmind-ai.com
"""
    
    def _create_html_email(self, advocate_name, deadline_info):
        """Create HTML email content with professional styling"""
        days_text = self._format_days_text(deadline_info['days_until'])
        urgency_color = self._get_urgency_color(deadline_info['days_until'])
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; padding: 40px 20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1e293b; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: bold;">⚠️ URGENT DEADLINE ALERT</h1>
                            <p style="margin: 10px 0 0 0; color: #fff9e6; font-size: 14px;">LegalMind AI - Deadline Monitoring System</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="margin: 0 0 20px 0; color: #e2e8f0; font-size: 16px;">Dear Advocate <strong>{advocate_name}</strong>,</p>
                            
                            <p style="margin: 0 0 30px 0; color: #cbd5e1; font-size: 14px; line-height: 1.6;">
                                This is an automated notification regarding an <strong>imminent deadline</strong> that requires your immediate attention.
                            </p>
                            
                            <!-- Alert Box -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: {urgency_color}20; border-left: 4px solid {urgency_color}; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <p style="margin: 0 0 10px 0; color: {urgency_color}; font-size: 18px; font-weight: bold;">{days_text}</p>
                                        <p style="margin: 0; color: #94a3b8; font-size: 12px;">Action required within 48 hours</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Case Details -->
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="margin: 0 0 15px 0; color: #06b6d4; font-size: 16px;">Case Details</h3>
                                        
                                        <table width="100%" cellpadding="8" cellspacing="0">
                                            <tr>
                                                <td style="color: #94a3b8; font-size: 13px; width: 35%;">Case Number:</td>
                                                <td style="color: #e2e8f0; font-size: 13px; font-weight: 600;">{deadline_info['case_number']}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #94a3b8; font-size: 13px;">Deadline:</td>
                                                <td style="color: #e2e8f0; font-size: 13px; font-weight: 600;">{deadline_info['deadline_title']}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #94a3b8; font-size: 13px;">Due Date:</td>
                                                <td style="color: #f59e0b; font-size: 13px; font-weight: 600;">{deadline_info['due_date'].strftime('%d %B %Y, %I:%M %p')}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #94a3b8; font-size: 13px;">Type:</td>
                                                <td style="color: #e2e8f0; font-size: 13px;">{deadline_info['deadline_type']}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #94a3b8; font-size: 13px;">Priority:</td>
                                                <td style="color: #e2e8f0; font-size: 13px;"><span style="background-color: #dc2626; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px;">{deadline_info['priority'].upper()}</span></td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <a href="https://legalmind-ai.onrender.com/cases/{deadline_info.get('case_id', '')}" style="display: inline-block; background: linear-gradient(135deg, #06b6d4 0%, #0284c7 100%); color: #ffffff; text-decoration: none; padding: 14px 40px; border-radius: 8px; font-weight: bold; font-size: 14px;">
                                            View Case Details →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #0f172a; padding: 20px 30px; text-align: center; border-top: 1px solid #334155;">
                            <p style="margin: 0 0 10px 0; color: #64748b; font-size: 12px;">
                                This is an automated email from <strong>LegalMind AI</strong> Deadline Monitoring System
                            </p>
                            <p style="margin: 0; color: #475569; font-size: 11px;">
                                Please do not reply to this message. For support, contact: support@legalmind-ai.com
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    
    def _format_days_text(self, days_until):
        """Format days until text"""
        if days_until < 0:
            return f"OVERDUE by {abs(days_until)} day(s)"
        elif days_until == 0:
            return "DUE TODAY"
        elif days_until == 1:
            return "DUE TOMORROW"
        else:
            return f"DUE IN {days_until} DAY(S)"
    
    def _get_urgency_color(self, days_until):
        """Get color based on urgency"""
        if days_until < 0:
            return "#dc2626"  # Red for overdue
        elif days_until <= 1:
            return "#f59e0b"  # Amber for 0-1 days
        else:
            return "#06b6d4"  # Cyan for 2 days


# Singleton instance
_email_service = None

def get_email_service():
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
