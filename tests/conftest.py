# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.app.model.models import User, UserTag, UserExpense, UserDebt
from backend.app.database.database import Base 
from backend.app.app import app
from backend.app.database.database import Base, get_db

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:localpassword@localhost:5433/expense_test_db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database():
    from backend.app.model.models import User,UserDebt,UserExpense,UserTag
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

# Function-scoped fixture (runs before/after every single test)
@pytest.fixture()
async def db_session():
    
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async with TestingSessionLocal(bind=connection) as session:
            yield session
        await transaction.rollback() 

@pytest.fixture()
async def client(db_session):
    
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="https://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()

class MockRedis:
    def __init__(self):
        self.store = {}
        
    async def set(self, name: str, value: str, ex=None, **kwargs):
        self.store[name] = value
        return True
        
    async def exists(self, name: str) -> bool:
        return name in self.store
        
    async def delete(self, name: str) -> int:
        if name in self.store:
            del self.store[name]
            return 1
        return 0

class MockSyncRedis:
    def __init__(self):
        self.store = {}
        
    def get(self, name: str):
        import json
        val = self.store.get(name)
        return val
        
    def set(self, name: str, value: str, ex=None, **kwargs):
        self.store[name] = value
        return True
        
    def delete(self, name: str):
        if name in self.store:
            del self.store[name]
            return 1
        return 0

@pytest.fixture(autouse=True)
def mock_redis_and_cache(monkeypatch):
    # Disable slowapi limiter
    from backend.app.rate_limiter import limiter
    limiter.enabled = False

    # Setup sent emails list
    sent_emails = []
    app.state.sent_emails = sent_emails

    # Mock database.redis._redis_client
    import backend.app.database.redis as redis_module
    mock_redis = MockRedis()
    monkeypatch.setattr(redis_module, "_redis_client", mock_redis)
    
    # Mock utils.cache.cache_service.client
    from backend.app.utils.cache import cache_service
    mock_sync_redis = MockSyncRedis()
    monkeypatch.setattr(cache_service, "client", mock_sync_redis)
    
    # Mock NotificationService.send_mail
    async def mock_send_mail(self, recipients, subject, context_data, template_name):
        sent_emails.append({
            "recipients": recipients,
            "subject": subject,
            "context_data": context_data,
            "template_name": template_name
        })
        return True
        
    from backend.app.repository.mail_handling import NotificationService
    monkeypatch.setattr(NotificationService, "send_mail", mock_send_mail)

@pytest.fixture()
async def auth_client(client, db_session):
    # Register a user
    payload = {
        "username": "authuser",
        "email": "authuser@example.com",
        "password": "securepassword123",
        "confirm_password": "securepassword123"
    }
    reg_resp = await client.post("/auth/register", json=payload)
    assert reg_resp.status_code == 200
    
    # Verify the user
    # Retrieve email verify token from app.state.sent_emails
    sent = app.state.sent_emails
    assert len(sent) == 1
    magic_url = sent[0]["context_data"]["url"]
    token = magic_url.split("token=")[1]
    
    verify_resp = await client.get(f"/auth/verify-email?token={token}")
    assert verify_resp.status_code == 200
    
    # Login user to set access_token cookie
    login_payload = {
        "username": "authuser",
        "password": "securepassword123"
    }
    login_resp = await client.post("/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    
    # Clear emails so tests start with a clean state
    app.state.sent_emails.clear()
    
    yield client

@pytest.fixture()
async def auth_user(db_session):
    from backend.app.model.models import User
    from sqlalchemy import select
    result = await db_session.execute(select(User).where(User.username == "authuser"))
    return result.scalar_one()