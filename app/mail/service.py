import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

from app.mail.success_template import get_success_template


class EmailService:
    def __init__(self):
        """
        Initialize the email service with sender credentials

        Args:
            sender_email (str): Sender's Gmail address
            sender_password (str): Sender's Gmail password or app-specific password
        """
        load_dotenv()
        self.sender_email = os.getenv("NO_REPLY_MAIL")
        self.sender_password = os.getenv("NO_REPLY_MAIL_PASSWORD")

    def send_email(self, recipient_email, subject, body):
        """
        Send styled HTML email with visible checkmark
        """
        html_content = get_success_template()
        msg = MIMEText(html_content, 'html')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        # Rest of the email sending code remains the same


        # Rest of the code remains the same...
        try:
            # Connect to Gmail's SMTP server
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Secure the connection
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    recipient_email,
                    msg.as_string()
                )
        except smtplib.SMTPException as e:
            raise smtplib.SMTPException(f"Failed to send email: {str(e)}")
#
# email_service = EmailService()
# email_service.send_email(recipient_email="nikolovski.nikola42@gmail.com", subject="Барање за возачка", body="Подоле ти го праќам барањето за возачка.")