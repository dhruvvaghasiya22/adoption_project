import os
import time
import logging
from flask import render_template, current_app
from models import db, NotificationLog, AdoptionApplication, User, Pet
from services.email_service import EmailService

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class NotificationService:
    @staticmethod
    def log_to_db(application_id, recipient_id, notification_type, event_type, status, error_message=None, retry_count=0):
        """
        Creates or updates a notification history log in the database.
        """
        try:
            log_entry = NotificationLog(
                application_id=application_id,
                recipient_id=recipient_id,
                notification_type=notification_type,
                event_type=event_type,
                status=status,
                error_message=error_message,
                retry_count=retry_count
            )
            db.session.add(log_entry)
            db.session.commit()
            return log_entry
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to log notification to database: {e}")
            return None

    @staticmethod
    def send_stream_notification(application, status_choice):
        """
        Publishes a real-time notification to GetStream.
        """
        api_key = os.environ.get('STREAM_API_KEY')
        api_secret = os.environ.get('STREAM_API_SECRET')
        app_id = os.environ.get('STREAM_APP_ID')

        adopter = application.applicant
        pet = application.pet
        owner = pet.shelter

        verb = f"adoption_{status_choice}"
        message = (
            f"🎉 Your pet adoption request for {pet.name} has been accepted!"
            if status_choice == 'accepted' else
            f"Update regarding your pet adoption request for {pet.name}."
        )

        if not api_key or not api_secret:
            logger.warning("[GetStream] Credentials missing. Running in mock/dry-run mode.")
            NotificationService.log_to_db(
                application_id=application.id,
                recipient_id=adopter.id,
                notification_type="stream",
                event_type=status_choice,
                status="sent (mocked)"
            )
            return True

        try:
            import stream  # type: ignore
            # Connect to stream
            client = stream.connect(api_key, api_secret, app_id=app_id)
            # Use 'notification' feed group for adopter
            feed = client.feed('notification', str(adopter.id))
            
            activity = {
                'actor': f"user:{owner.id}",
                'verb': verb,
                'object': f"application:{application.id}",
                'message': message,
                'pet_name': pet.name,
                'status': status_choice,
                'foreign_id': f"app_{application.id}_{status_choice}",
                'time': time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            
            feed.add_activity(activity)
            logger.info(f"[GetStream] Successfully sent notification to adopter {adopter.id}")
            
            NotificationService.log_to_db(
                application_id=application.id,
                recipient_id=adopter.id,
                notification_type="stream",
                event_type=status_choice,
                status="sent"
            )
            return True
        except Exception as e:
            logger.error(f"[GetStream] Failed to send activity: {e}")
            NotificationService.log_to_db(
                application_id=application.id,
                recipient_id=adopter.id,
                notification_type="stream",
                event_type=status_choice,
                status="failed",
                error_message=str(e)
            )
            return False

    @staticmethod
    def send_email_notification(application, status_choice):
        """
        Renders templates and dispatches email using the swappable EmailService with retry logic.
        """
        adopter = application.applicant
        pet = application.pet
        owner = pet.shelter

        # Resolve subject
        if status_choice == 'accepted':
            subject = "🎉 Your Pet Adoption Request Has Been Accepted!"
            html_template = "emails/accepted_email.html"
            txt_template = "emails/accepted_email.txt"
        else:
            subject = "Update Regarding Your Pet Adoption Request"
            html_template = "emails/rejected_email.html"
            txt_template = "emails/rejected_email.txt"

        # Context variables
        context = {
            'user_name': adopter.name,
            'pet_name': pet.name,
            'breed': pet.breed or 'Unknown Breed',
            'owner_name': owner.name,
            'pet_photo': pet.photo if pet.photo else 'default_pet.png',
            'application_id': application.id
        }

        try:
            html_content = render_template(html_template, **context)
            text_content = render_template(txt_template, **context)
        except Exception as e:
            logger.error(f"Failed to render email templates: {e}")
            NotificationService.log_to_db(
                application_id=application.id,
                recipient_id=adopter.id,
                notification_type="email",
                event_type=status_choice,
                status="failed",
                error_message=f"Template render error: {str(e)}"
            )
            return False

        email_service = EmailService()
        max_retries = 3
        retry_count = 0
        success = False
        last_error = ""

        while retry_count < max_retries and not success:
            try:
                email_service.send(adopter.email, subject, html_content, text_content)
                success = True
                logger.info(f"Email successfully sent to {adopter.email} on attempt {retry_count + 1}")
            except Exception as e:
                retry_count += 1
                last_error = str(e)
                logger.warning(f"Email send attempt {retry_count} failed: {e}")
                if retry_count < max_retries:
                    time.sleep(1)  # small delay before retry

        status = "sent" if success else "failed"
        err_msg = None if success else f"SMTP/SendGrid error after {max_retries} attempts: {last_error}"

        NotificationService.log_to_db(
            application_id=application.id,
            recipient_id=adopter.id,
            notification_type="email",
            event_type=status_choice,
            status=status,
            error_message=err_msg,
            retry_count=retry_count
        )

        return success

    @classmethod
    def send_adoption_update(cls, application_id, status_choice):
        """
        Coordinates database updates, sending email (with retry), and Stream alerts.
        """
        application = AdoptionApplication.query.get(application_id)
        if not application:
            logger.error(f"Application ID {application_id} not found.")
            return False

        logger.info(f"Triggering notifications for application {application_id} (Status: {status_choice})")

        # 1. Send Email Notification
        email_sent = cls.send_email_notification(application, status_choice)

        # 2. Send Stream Notification
        stream_sent = cls.send_stream_notification(application, status_choice)

        return email_sent and stream_sent
