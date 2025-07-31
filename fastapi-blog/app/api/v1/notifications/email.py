from fastapi import APIRouter, status
from app.schemas.email import EmailRequest
from app.workers.tasks import send_notification_email

router = APIRouter()

@router.post("/email", status_code=status.HTTP_202_ACCEPTED)
def send_email_notification(payload: EmailRequest):
    send_notification_email.delay(
        to_email=payload.to_email,
        subject=payload.subject,
        content=payload.content
    )
    return {"message": "Email is being sent via Celery"}
