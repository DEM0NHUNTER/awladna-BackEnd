# BackEnd/monitoring/health.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from BackEnd.Utils.database import get_db
from BackEnd.Utils.redis import get_redis_client
from BackEnd.Utils.mongo_client import MongoDBClient
import shutil

router = APIRouter()


def check_database(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return "OK"
    except Exception as e:
        return f"DOWN: {str(e)}"


def check_redis():
    try:
        redis_cli = get_redis_client()
        return "OK" if redis_cli.ping() else "DOWN"
    except Exception as e:
        return f"DOWN: {str(e)}"


def check_mongodb():
    try:
        mongo = MongoDBClient()
        client = mongo.client
        result = client.admin.command('ping')
        return "OK" if result.get('ok') == 1 else "DOWN"
    except Exception as e:
        return f"DOWN: {str(e)}"


def check_storage():
    try:
        total, used, free = shutil.disk_usage("/")
        return "OK" if free > 1024 ** 3 else "LOW_SPACE"
    except Exception as e:
        return f"DOWN: {str(e)}"


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    return {
        "database": check_database(db),
        "redis": check_redis(),
        "mongodb": check_mongodb(),
        "storage": check_storage(),
        "status": "OK"
    }
