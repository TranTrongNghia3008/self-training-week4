from celery import Celery
from app.core.config import settings
import aiosmtplib
from email.message import EmailMessage

celery = Celery(
    "worker",
    broker=settings.REDIS_BROKER_URL,
)

@celery.task
def send_notification_email(to_email: str, subject: str, content: str):
    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)

    # Use aiosmtplib to send email asynchronously
    import asyncio
    async def send_email():
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
        )
    asyncio.run(send_email())
