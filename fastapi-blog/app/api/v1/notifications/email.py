from fastapi import APIRouter, status
from app.schemas.email import EmailRequest
from app.services.notifications.email_service import send_email_async

router = APIRouter()

@router.post("/email", status_code=status.HTTP_202_ACCEPTED)
def send_email_notification(payload: EmailRequest):
    send_email_async(payload)
    return {"message": "Email is being sent via Celery"}
