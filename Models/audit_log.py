# BackEnd/Models/audit_log.py (or wherever it's defined)

from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from BackEnd.Utils.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)  # matches your existing PK
    action = Column(String, nullable=False)
    user_id = Column(Integer, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    status = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
