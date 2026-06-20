import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

def send_adoption_emails(user_name, user_email, pet_name, admin_email=None):
    """
    Sends adoption application confirmation emails:
    1. To the adopter confirming their request.
    2. To the administrator notifying them of the new request.
    
    Uses SMTP_SSL with configuration values retrieved from current_app.config.
    """
    # Fetch settings from Flask app configuration
    server = current_app.config.get('MAIL_SERVER')
    port = current_app.config.get('MAIL_PORT')
    username = current_app.config.get('MAIL_USERNAME')
    password = current_app.config.get('MAIL_PASSWORD')
    default_admin = current_app.config.get('ADMIN_EMAIL')
    
    # If admin_email is not provided, fallback to standard configured admin email
    if not admin_email:
        admin_email = default_admin

    # If no credentials are set, print a clear log/warning to console and bypass
    if not username or not password:
        print("\n[WARNING] Email credentials are not configured in the .env file!")
        print(f"Skipping sending email to {user_email} and {admin_email}.")
        print("Please configure MAIL_USERNAME and MAIL_PASSWORD to enable emails.\n")
        return False

    try:
        # Create user confirmation email
        user_msg = MIMEMultipart()
        user_msg['From'] = username
        user_msg['To'] = user_email
        user_msg['Subject'] = 'Adoption Request Received'

        user_body = f"""Hello {user_name},

Thank you for submitting an adoption application for {pet_name}!

We have successfully received your request, and our team is currently reviewing it. We will get in touch with you soon with details on the next steps of the adoption process.

Best regards,
Pet Adoption Team
"""
        user_msg.attach(MIMEText(user_body, 'plain'))

        # Create admin notification email
        admin_msg = MIMEMultipart()
        admin_msg['From'] = username
        admin_msg['To'] = admin_email
        admin_msg['Subject'] = 'Adoption Request Received'

        admin_body = f"""Hello Admin,

A new adoption request has been submitted on the Pet Adoption platform.

Details:
- Applicant Name: {user_name}
- Applicant Email: {user_email}
- Pet Name: {pet_name}

Please log in to the admin dashboard to review and process this application.

Best regards,
Pet Adoption System
"""
        admin_msg.attach(MIMEText(admin_body, 'plain'))

        # Send emails using SMTP_SSL
        print(f"Connecting to SMTP server {server}:{port}...")
        with smtplib.SMTP_SSL(server, port, timeout=10) as smtp_server:
            smtp_server.login(username, password)
            
            # Send to user
            smtp_server.sendmail(username, user_email, user_msg.as_string())
            print(f"Adoption confirmation email sent to user: {user_email}")
            
            # Send to admin
            smtp_server.sendmail(username, admin_email, admin_msg.as_string())
            print(f"Adoption notification email sent to admin: {admin_email}")
            
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to send email confirmation: {e}")
        print("Ensure SMTP configurations in .env are correct and SMTP SSL traffic is allowed.\n")
        return False
