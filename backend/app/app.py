from fastapi.responses import JSONResponse

from .routing import auth
from .routing import expenses
from fastapi.middleware.cors import CORSMiddleware
from .routing import settlements
from .routing import tag
from .model import models
from fastapi import FastAPI,Request
# keep jwthandler import for dependency usage in routes
from .Security.deps import get_current_user
from scalar_fastapi import get_scalar_api_reference

# Rate limiting (centralized)
from .rate_limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI()
# attach limiter to app state for middleware and decorators
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request:Request,exc:RateLimitExceeded):
    response = JSONResponse(
        status_code=429,
        content={"detail":"Too many Request!"}
    )
    if hasattr(request.state, "view_rate_limit"):
        limiter._inject_headers(
            response,
            request.state.view_rate_limit
        )
    return response

app.include_router(auth.auth)
app.include_router(tag.tags)
app.include_router(expenses.expense)
app.include_router(settlements.settlement)

ORIGINS = [
    "https://expenseflow-awsmx.netlify.app",   
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,         # Only allow requests from your trusted frontend list
    allow_credentials=True,        # CRUCIAL: Must be True to accept & set HttpOnly JWT cookies
    allow_methods=["*"],  # Specify exact HTTP actions allowed
    allow_headers=["*"],  # Headers the frontend is allowed to send
)

@app.get("/")
async def home():
    return {"message":"working"}

@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )