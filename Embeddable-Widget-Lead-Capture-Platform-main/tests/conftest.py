import os
os.environ.setdefault("DATABASE_URL","sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY","test-secret")
os.environ.setdefault("GEO_PROVIDER_A_MODE","mock_up")
os.environ.setdefault("GEO_PROVIDER_B_MODE","mock_up")
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import get_settings
from app.services import submissions as submission_module
from app.api import public as public_module

engine=create_engine("sqlite+pysqlite:///:memory:",connect_args={"check_same_thread":False},poolclass=StaticPool)
TestingSession=sessionmaker(bind=engine,autoflush=False,expire_on_commit=False)
Base.metadata.create_all(engine)

def override_db():
    db=TestingSession()
    try: yield db
    finally: db.close()
app.dependency_overrides[get_db]=override_db
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(engine);Base.metadata.create_all(engine);public_module.limiter.reset();yield
@pytest.fixture
def client(): return TestClient(app)
