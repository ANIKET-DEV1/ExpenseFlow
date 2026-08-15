from google import genai
from ..config.config import ai_config  
settings=ai_config()
client = genai.Client(api_key=settings.GEMINI_API_KEY.get_secret_value())




    