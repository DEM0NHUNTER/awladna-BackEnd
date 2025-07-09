# BackEnd/main.py
import json

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.middleware import Middleware
from BackEnd.middleware.security_headers import security_headers
from fastapi.middleware import Middleware
from sqlalchemy.orm import Session

from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv
from BackEnd.Models.user import User, UserRole
from BackEnd.Routes import admin, auth, child_profile, recommendation, analytics, settings as Settings
from BackEnd.Utils.auth_utils import get_current_user
from BackEnd.Utils.config import settings
from BackEnd.Utils.database import Base, check_database_health, engine
from BackEnd.Utils.mongo_client import ensure_indexes
from BackEnd.Utils.rate_limiter import init_rate_limiter
# from BackEnd.Utils.sanitization import SanitizationMiddleware
from pydantic import BaseModel
from typing import Optional
from BackEnd.Utils.ai_integration import get_ai_response
from BackEnd.Models.child_profile import ChildProfile
from BackEnd.Utils.database import get_db
from BackEnd.Routes import chat as ChatRoutes

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)
logger = logging.getLogger(__name__)
logging.info(f"CORS origins loaded: {settings.ALLOWED_ORIGINS}")


# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        for k, v in headers.items():
            if k not in response.headers:
                response.headers[k] = v
        return response


def require_role(role: UserRole):
    def wrapper(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user

    return wrapper


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup")
    try:
        await init_rate_limiter()

        db_health = await check_database_health()
        logger.info(f"Database health: {db_health}")

        # Only fail startup if PostgreSQL is unreachable
        if not db_health["postgresql"]["status"]:
            raise Exception(f"PostgreSQL health check failed: {db_health['postgresql']}")

        # Allow MongoDB failure during startup
        if not db_health["mongodb"]["status"]:
            logger.warning(f"MongoDB health check failed: {db_health['mongodb'].get('error')}")

        Base.metadata.create_all(bind=engine)
        await ensure_indexes()

    except Exception as e:
        logger.error("Startup errors", exc_info=e)
        raise e

    yield

    engine.dispose()
    logger.info("App shutdown")


# Initialize FastAPI
app = FastAPI(
    title="Awladna Parenting Chatbot API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_REDOC else None,
    redirect_slashes=False,
)

# ─── 1) CORS middleware MUST come first ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_credentials=(True if "*" not in settings.ALLOWED_ORIGINS else False),
)

# ─── 2) Then your security‐headers middleware ───────────────────────────────────
app.add_middleware(BaseHTTPMiddleware, dispatch=security_headers)

# ─── 3) Now include your routers ───────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth")
app.include_router(admin.router, prefix="/api/auth/admin")
app.include_router(ChatRoutes.router, prefix="/api/auth/chat")
app.include_router(child_profile.router, prefix="/api/auth/child")
app.include_router(recommendation.router, prefix="/api/auth/recommendation")
app.include_router(analytics.router, prefix="/api/auth/analytics")
app.include_router(Settings.router, prefix="/api/auth/settings")


class AIRequest(BaseModel):
    user_input: str
    child_id: int
    child_age: int
    child_name: str
    context: Optional[str] = None
    hf_model_name: Optional[str] = None


# @app.options("/api/auth/child")
# async def options_child_profile():
#     return {"status": "OK"}


@app.get("/api/cors-debug")
async def cors_debug():
    return {"message": "CORS is working!"}


@app.get("/api/ping")
def ping():
    return {"pong": True}


@app.get("/api/test-db")
async def test_db():
    return await check_database_health()


@app.get("/api")
async def root():
    return {
        "status": "Awladna API is running",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.ENABLE_DOCS else "disabled",
        "redoc": "/redoc" if settings.ENABLE_REDOC else "disabled"
    }


# def mock_get_current_user():
#     return User(email="demo@example.com", role=UserRole.PARENT)


@app.get("/api/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "role": current_user.role,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at.isoformat()
    }


@app.post("/ai/respond")
async def ai_respond(
        request: AIRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    child = db.query(ChildProfile).filter_by(child_id=request.child_id, user_id=current_user.user_id).first()
    if not child:
        raise HTTPException(status_code=403, detail="Access to child denied.")

    return await get_ai_response(
        user_input=request.user_input,
        child_age=request.child_age,
        child_name=request.child_name,
        context=request.context,
    )


class HealthCheck(BaseModel):
    status: str = "OK"


@app.get("/health", summary="Health check", status_code=status.HTTP_200_OK, response_model=HealthCheck, )
def health():
    try:
        return HealthCheck(status="OK")
    except Exception as e:
        logger.error("Health check failed", exc_info=e)
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/api/security-info", dependencies=[Depends(require_role(UserRole.ADMIN))])
async def security_info(request: Request):
    return {
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "headers": dict(request.headers),
        "security_headers": {
            "content_security_policy": "enabled",
            "strict_transport_security": "enabled",
            "x_frame_options": "enabled"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.status_code}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )


# Debug endpoint for environment variables
@app.get("/env")
async def get_env_vars():
    return dict(os.environ.items())
