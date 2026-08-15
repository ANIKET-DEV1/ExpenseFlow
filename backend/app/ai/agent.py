from .client import client
from ..config.config import ai_config
from google import genai
async def ask_gemini_with_tools(message: str):
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=message,
        config={
            "system_instruction":ai_config().SYSTEM_INTRUCTION
        }
    )
    part = response.candidates[0].content.parts[0]
    
    if part.function_call:
        print(f"→ TOOL CALL detected: {part.function_call.name}({part.function_call.args})")
        if part.function_call.name == "add_expense":
            # result = add_expense(**part.function_call.args)
            print(f"→ EXECUTED: {part}")
        elif part.function_call.name == "delete_expense":
            # delete_expense()
            print(f"→ EXECUTED: Deleted")
        
    else:
        return part.text

