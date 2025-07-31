from app.schemas.email import EmailRequest
from app.workers.tasks import send_notification_email

def send_email_async(payload: EmailRequest):
    send_notification_email.delay(
        to_email=payload.to_email,
        subject=payload.subject,
        content=payload.content
    )
