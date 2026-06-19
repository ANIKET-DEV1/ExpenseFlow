from pydantic import EmailStr

from .Base import BaseRepository
from fastapi import HTTPException,status,Response
from ..schemas import user
from ..Security import jwthandler
from ..database import crud_auth 
from ..model.models import User
from ..config.config import get_config
from .mail_handling import NotificationService
from ..utils.email_verification import email_verification
from ..utils.passwrod_reset import password_mail_verification
from ..database.redis import mail_send,is_mail_send

class for_Auth(BaseRepository,NotificationService):
    async def login_user(self, credential: user.UserLogin):
        user= await crud_auth.login(self.db,user_data=credential)
        if not user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST ,detail="Invalid Credential")
        token_payload = {
            "sub": str(user.id),
            "verified":user.verified_status
        }
        access_token= jwthandler.create_access_token(data=token_payload)
        if not user.verified_status:
            if not await is_mail_send(user.email):
                email_verify_token = email_verification.generate_token(user)

                magic_url = f"{get_config().base_url}/verify-email.html?token={email_verify_token}"
            
                await NotificationService(self.tasks).send_mail(
                    recipients=[user.email],
                    subject="Hello! Please Verify Your Email Account",
                    context_data={
                        "username":user.username,
                        "url":magic_url
                    },
                    template_name="mail_register.html"
                )
                raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, 
                        detail="Please verify your email address before logging in."
                    )
            else:
                raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, 
                        detail="Please verify your email address before logging in."
                    )
        

        return {"token":access_token,"message":"Login Successful"}
    
    async def create_user(self,cred: user.UserCreate):
        data = await crud_auth.register_user(self.db,user_data=cred)
        if not data:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Error hai thik kardo")
        
        email_verify_token = email_verification.generate_token(data)

        magic_url = f"{get_config().base_url}/verify-email.html?token={email_verify_token}"
        
        await NotificationService(self.tasks).send_mail(
            recipients=[cred.email],
            subject="Welcome! Please Verify Your Expense Tracker Account",
            context_data={
                "username":cred.username,
                "url":magic_url
            },
            template_name="mail_register.html"
        )
        await mail_send(data.email)
        
        return data

    async def password_reset(self,email:user.ResetPasswordRequest):
        user=await crud_auth.get_user(db=self.db,email=email)
        if not await is_mail_send(user.email):
                email_verify_token = password_mail_verification.generate_token(user)

                magic_url = f"{get_config().base_url}/reset-password.html?token={email_verify_token}"
            
                await NotificationService(self.tasks).send_mail(
                    recipients=[user.email],
                    subject="Hello! Change Your Email Account passowrd?",
                    context_data={
                        "username":user.username,
                        "url":magic_url
                    },
                    template_name="mail_password_reset.html"
                )
        else:
            return {"message":"Email Already Sended Please verify. "}
        
        return{"message":"Email Sended"}

        