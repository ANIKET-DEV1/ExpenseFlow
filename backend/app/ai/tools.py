import json
import openai
from sqlalchemy.exc import SQLAlchemyError

from ..schemas import feature
from ..repository.featureRepo import expensesRepo, tag_repo, settlementsRepo
from ..model import models


async def add_expense_tool(expense_data: feature.ExpenseCreate, parameter: dict) -> dict:
    """Log a new personal expense in INR for the user."""
    repo: expensesRepo = parameter["expense_repo"]
    user: models.User = parameter["current_user"]

    created = await repo.add_expense(expense_data, user)
    if not created:
        raise ValueError("Failed to create expense. Check input values or if the tag exists.")

    return {
        "status": "added",
        "id": created.id,
        "amount": float(created.amount),
        "tag": expense_data.tag_name,
        "payment_type": expense_data.payment_type.value,
        "date": str(expense_data.expense_date),
        "message": "Expense logged successfully",
    }

async def add_tag_tool(tag_data: feature.TagCreate, parameter: dict) -> dict:
    """Log a new tag for categorizing expenses for the user."""
    repo: tag_repo = parameter["tag_repo"]
    user: models.User = parameter["current_user"]

    created = await repo.add_tags(tag=feature.TagCreate, user_id=user)
    if not created:
        raise ValueError("Failed to create expense. Check input values or if the tag exists.")

    return {
        "status": "added",
        "id": created.id,
        "tag": tag_data.tag_name,
        "message": "tag added successfully",
    }


_REGISTRY = {
    "add_expense_tool": (feature.ExpenseCreate, add_expense_tool),
    "add_tag_tool":(feature.TagCreate,add_tag_tool)
}
AGENT_TOOLS = [
    openai.pydantic_function_tool(
        schema,
        name=tool_name,
        description=(handler.__doc__ or "").strip(),
    )
    for tool_name, (schema, handler) in _REGISTRY.items()
]

for tool in AGENT_TOOLS:
    tool["function"].pop("strict", None)


async def execute_tool(tool_call, parameter: dict) -> str:
    name = tool_call.function.name
    entry = _REGISTRY.get(name)

    if not entry:
        return json.dumps({"status": "error", "message": f"Unknown tool: {name}"})

    schema_cls, handler = entry

    try:
        validated_args = schema_cls.model_validate_json(tool_call.function.arguments)
        result = await handler(validated_args, parameter)
        return json.dumps(result, default=str)

    except ValueError as e:
        return json.dumps({"status": "error", "message": str(e)})

    except SQLAlchemyError:
        repo = parameter.get("expense_repo")
        if repo and hasattr(repo, "db"):
            await repo.db.rollback()
        return json.dumps({"status": "error", "message": "Database transaction failed."})

    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
