import os
import smtplib
from abc import ABC, abstractmethod
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, to_email, subject, html_content, text_content):
        """
        Sends an email.
        :param to_email: Recipient email address
        :param subject: Email subject
        :param html_content: HTML version of the message
        :param text_content: Plain text fallback version of the message
        :return: True if successful, raises Exception if failed
        """
        pass


class SMTPEmailProvider(EmailProvider):
    def __init__(self, server, port, username, password, from_email):
        self.server = server
        self.port = int(port or 465)
        self.username = username
        self.password = password
        self.from_email = from_email or username

    def send_email(self, to_email, subject, html_content, text_content):
        if not self.username or not self.password:
            raise ValueError("SMTP credentials not fully configured.")

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email

        # Attach text and html parts
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Connect and send via SMTP_SSL
        with smtplib.SMTP_SSL(self.server, self.port, timeout=10) as smtp:
            smtp.login(self.username, self.password)
            smtp.sendmail(self.from_email, to_email, msg.as_string())
        
        return True


class SendGridEmailProvider(EmailProvider):
    def __init__(self, api_key, from_email):
        self.api_key = api_key
        self.from_email = from_email

    def send_email(self, to_email, subject, html_content, text_content):
        if not self.api_key:
            raise ValueError("SendGrid API key not configured.")

        # Delay import to avoid hard requirement if not configured/installed
        from sendgrid import SendGridAPIClient  # type: ignore
        from sendgrid.helpers.mail import Mail  # type: ignore

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=text_content
        )

        sg = SendGridAPIClient(self.api_key)
        response = sg.send(message)
        
        # SendGrid successful response statuses are in 2xx range
        if response.status_code not in [200, 201, 202]:
            raise RuntimeError(f"SendGrid API responded with status code {response.status_code}")
        
        return True


class EmailService:
    def __init__(self):
        self.provider = self._initialize_provider()

    def _initialize_provider(self):
        # Load from active environment variables
        provider_type = os.environ.get('EMAIL_PROVIDER', 'smtp').lower()
        from_email = os.environ.get('MAIL_USERNAME') or os.environ.get('ADMIN_EMAIL') or 'no-reply@petadopt.com'

        if provider_type == 'sendgrid':
            api_key = os.environ.get('SENDGRID_API_KEY')
            return SendGridEmailProvider(api_key, from_email)
        else:
            # Fallback to SMTP
            server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
            port = os.environ.get('MAIL_PORT', 465)
            username = os.environ.get('MAIL_USERNAME')
            password = os.environ.get('MAIL_PASSWORD')
            return SMTPEmailProvider(server, port, username, password, from_email)

    def send(self, to_email, subject, html_content, text_content):
        """
        Public dispatch method utilizing the configured provider.
        """
        if not self.provider:
            raise RuntimeError("Email provider not initialized.")
        return self.provider.send_email(to_email, subject, html_content, text_content)
