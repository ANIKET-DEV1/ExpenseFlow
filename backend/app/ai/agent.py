from openai import AsyncOpenAI
from ..schemas import chatbot as chat_schemas
from .client import client,setting
from .tools import AGENT_TOOLS,execute_tool
SYSTEM_PROMPT = """You are ExpenseFlow AI, a concise personal finance assistant for an Indian expense & debt-tracking app (currency: ₹).
Rules:
- guide user only about application 
- Use provided tools when needed to read, add, or update expenses, settlements, and tags.
- Never invent transaction IDs or amounts or delete data.
- Keep answers under 3 sentences unless summarizing multiple transactions
"""
messages = [{"role": "system", "content": SYSTEM_PROMPT}]
history=[]

async def agent_call(user_say:chat_schemas.user_message,parameter:dict):
    if len(history) > 10:
        history.pop(0)
        history.pop(0)
    
    history.append({"role":user_say.role, "content":user_say.prompt})
    for _ in range(3):
        response = await client.chat.completions.create(
            model=setting.LLM_MODEL,
            messages=messages + history,
            tools=AGENT_TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        # Case A: Model answered directly with text -> save clean strings to history & return
        if not msg.tool_calls:
            final_reply = msg.content or "Done."
            history.append({"role": user_say.role, "content": user_say.prompt})
            history.append({"role": "assistant", "content": final_reply})
            return final_reply

        # Case B: Model requested tool(s) -> execute via tools.py and feed output back
        history.append(msg.model_dump(exclude_none=True))

        for tool_call in msg.tool_calls:
            tool_result = await execute_tool(tool_call, parameter)
            history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })
        print(history)
    return "I hit the maximum tool steps for that request. Please try again."
