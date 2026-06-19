from datetime import datetime, timedelta, timezone
from jose import jwt,ExpiredSignatureError,JWTError
import uuid
from backend.app.model.models import User
from ..config.config import get_config
system = get_config()

SECRET_KEY = system.secret_key.get_secret_value()
ALGORITHM = system.algorithms
class password_mail_verification():
    def generate_token(user:User) -> str:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
    
        payload = {
            "sub": str(user.id),
            "exp": expire,
            "scope": "password_reset" 
        }
        
        return jwt.encode(payload,SECRET_KEY,ALGORITHM)
    
    def verify_passwaord_reset_token(token:str) -> uuid.UUID | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

            user_id:str|None = payload.get("sub")
            scope:str|None = payload.get("scope")
            if scope != "password_reset":
                return None
                
            return uuid.UUID(str(user_id))
            
        except ExpiredSignatureError:
            return None
        except JWTError:
            return None



