# BackEnd/tests/__init__.py

import os

os.environ["APP_SECRET_KEY"] = "test-secret"
os.environ["APP_ENCRYPTION_KEY"] = "test-encryption"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["REFRESH_TOKEN_SECRET"] = "test-refresh-secret"
os.environ["TESTING"] = "True"
