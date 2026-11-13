from openai import AsyncOpenAI
from ..config.config import get_ai_config
setting = get_ai_config()
client = AsyncOpenAI(base_url=setting.LLM_BASE_URL, api_key=setting.LLM_API_KEY)



