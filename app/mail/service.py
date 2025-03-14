import os
from typing import Optional

import aiosmtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from app.mail.success_template import get_success_template

class EmailService:
    def __init__(self):
        """
        Initialize the email service with sender credentials.
        """
        load_dotenv()
        self.sender_email = os.getenv("NO_REPLY_MAIL")
        self.sender_password = os.getenv("NO_REPLY_MAIL_PASSWORD")

    async def send_email(self, recipient_email, subject, body, download_link: Optional[str] = None):
        """
        Send a styled HTML email asynchronously using SSL on port 465.
        """
        # Example HTML content; replace with your actual template
        html_content = get_success_template(download_link)
        msg = MIMEText(html_content, 'html')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = recipient_email

        try:
            # Connect using SSL on port 465
            async with aiosmtplib.SMTP(hostname='smtp.gmail.com', port=465, use_tls=True) as server:
                await server.login(self.sender_email, self.sender_password)
                await server.sendmail(
                    self.sender_email,
                    recipient_email,
                    msg.as_string()
                )
        except aiosmtplib.SMTPException as e:
            raise aiosmtplib.SMTPException(f"Failed to send email: {str(e)}")

# Example usage
if __name__ == "__main__":
    import asyncio
    email_service = EmailService()
    asyncio.run(email_service.send_email("nikolovski.nikola42@gmail.com", "Test Subject", "Test Body"))