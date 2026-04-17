import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import logging
from config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_contact_email(submission_data: dict) -> bool:
        try:
            if not all([
                settings.SMTP_HOST,
                settings.SMTP_USER,
                settings.SMTP_PASS,
                settings.SMTP_FROM,
                settings.ADMIN_EMAIL
            ]):
                # Log email content for development
                logger.info(f"SMTP not configured. Email content:")
                logger.info(f"To: {settings.ADMIN_EMAIL}")
                logger.info(f"From: {settings.SMTP_FROM}")
                logger.info(f"Subject: Contact Form Submission - {submission_data.get('subject', 'No Subject')}")
                logger.info(f"Name: {submission_data.get('name', 'Anonymous')}")
                logger.info(f"Email: {submission_data.get('email', 'No Email')}")
                logger.info(f"Message: {submission_data.get('message', 'No Message')}")
                
                if submission_data.get('user_data_snapshot'):
                    logger.info(f"User Data: {submission_data['user_data_snapshot']}")
                
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM
            msg['To'] = settings.ADMIN_EMAIL
            msg['Subject'] = f"Contact Form Submission - {submission_data.get('subject', 'No Subject')}"
            
            # Create HTML body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #333; margin-bottom: 20px;">New Contact Form Submission</h2>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                        <div style="margin-bottom: 15px;">
                            <strong>From:</strong> {submission_data.get('name', 'Anonymous')} &lt;{submission_data.get('email', 'no-email@example.com')}&gt;
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <strong>Subject:</strong> {submission_data.get('subject', 'No Subject')}
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <strong>Priority:</strong> {submission_data.get('priority', 'medium').upper()}
                        </div>
                        
                        <div style="margin-bottom: 20px;">
                            <strong>Message:</strong><br>
                            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 4px; margin-top: 10px; white-space: pre-wrap;">
                                {submission_data.get('message', 'No Message')}
                            </div>
                        </div>
                    </div>
                    
                    {EmailService._format_user_data(submission_data.get('user_data_snapshot'))}
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666;">
                        <p>This message was sent via the Imikino contact form.</p>
                        <p><strong>Timestamp:</strong> {submission_data.get('created_at', 'Unknown')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
                server.quit()
            
            logger.info(f"Contact email sent successfully to {settings.ADMIN_EMAIL}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(email: str, reset_token: str, user_name: str) -> bool:
        try:
            if not all([
                settings.SMTP_HOST,
                settings.SMTP_USER,
                settings.SMTP_PASS,
                settings.SMTP_FROM
            ]):
                logger.info(f"SMTP not configured. Password reset email content for {email}")
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM
            msg['To'] = email
            msg['Subject'] = "Password Reset - Imikino"
            
            # Create HTML body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #333; margin-bottom: 20px;">Password Reset Request</h2>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                        <p>Hello {user_name},</p>
                        
                        <p>You requested to reset your password for your Imikino account.</p>
                        
                        <p>Click the link below to reset your password:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{settings.FRONTEND_URL}/reset-password?token={reset_token}" 
                               style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                                Reset Password
                            </a>
                        </div>
                        
                        <p style="margin-top: 30px; font-size: 14px; color: #666;">
                            This link will expire in 1 hour for security reasons.<br>
                            If you didn't request this, please ignore this email.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
                server.quit()
            
            logger.info(f"Password reset email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(email: str, user_name: str) -> bool:
        try:
            if not all([
                settings.SMTP_HOST,
                settings.SMTP_USER,
                settings.SMTP_PASS,
                settings.SMTP_FROM
            ]):
                logger.info(f"SMTP not configured. Welcome email content for {email}")
                return True
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM
            msg['To'] = email
            msg['Subject'] = "Welcome to Imikino!"
            
            # Create HTML body
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #333; margin-bottom: 20px;">Welcome to Imikino! 🎉</h2>
                    
                    <div style="background-color: white; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                        <p>Hello {user_name},</p>
                        
                        <p>Welcome to Imikino - your platform for learning, sharing, and growing together!</p>
                        
                        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 6px; margin: 20px 0;">
                            <h3 style="color: #333; margin-top: 0;">What's Next?</h3>
                            <ul style="color: #666; line-height: 1.6;">
                                <li>📚 <strong>Explore Courses:</strong> Start learning with our interactive courses</li>
                                <li>🎯 <strong>Complete Tasks:</strong> Earn XP by completing real-world tasks</li>
                                <li>💬 <strong>Share Your Progress:</strong> Connect with the community</li>
                                <li>🏆 <strong>Level Up:</strong> Unlock badges and achievements</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 30px; font-size: 14px; color: #666;">
                            If you have any questions, reply to this email or visit our help center.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASS)
                server.send_message(msg)
                server.quit()
            
            logger.info(f"Welcome email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False
    
    @staticmethod
    def _format_user_data(user_data_snapshot: Optional[dict]) -> str:
        if not user_data_snapshot:
            return ""
        
        return f"""
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 6px; margin: 20px 0;">
                        <h3 style="color: #333; margin-top: 0;">User Information</h3>
                        <div style="color: #666; font-size: 14px;">
                            <p><strong>Email:</strong> {user_data_snapshot.get('email', 'N/A')}</p>
                            <p><strong>Display Name:</strong> {user_data_snapshot.get('display_name', 'N/A')}</p>
                            <p><strong>Role:</strong> {user_data_snapshot.get('role', 'N/A')}</p>
                            <p><strong>XP:</strong> {user_data_snapshot.get('xp', 0)}</p>
                            <p><strong>Level:</strong> {user_data_snapshot.get('level', 1)}</p>
                        </div>
                    </div>
                    """
