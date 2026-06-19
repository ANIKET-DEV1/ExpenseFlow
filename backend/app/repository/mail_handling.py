from fastapi_mail import FastMail,ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr
from starlette.background import BackgroundTasks
from ..config.config import mail_config

mail=mail_config()
class NotificationService:
    def __init__(self,tasks:BackgroundTasks):
        self.tasks=tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **mail.model_dump()
            )
        )

    
    async def send_mail(
            self,
            recipients:list[EmailStr],
            subject:str,
            context_data:dict,
            template_name:str
        
    ):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                template_body=context_data,
                subtype=MessageType.html,
            ),
            template_name=template_name
        )
    
