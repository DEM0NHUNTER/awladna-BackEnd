# BackEnd/Utils/audit_logger.py

import logging
from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from BackEnd.Models.audit_log import AuditLog
import json
from contextlib import contextmanager


class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def log_security_event(
            self,
            db: Session,
            event_type: str,
            user_id: Optional[int],
            request: Request,
            status: str = "success",
            details: Optional[dict] = None
    ):
        """Log security-related events with detailed context"""
        try:
            log = AuditLog(
                action=f"security_{event_type}",
                user_id=user_id,
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "")[:255],
                status=status,
                details=json.dumps({
                    "event": event_type,
                    "path": request.url.path,
                    "method": request.method,
                    "metadata": details or {}
                })[:500]
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            logging.info(f"Security event logged: {event_type} for user {user_id}")
        except Exception as e:
            db.rollback()
            logging.error(f"Failed to log security event: {str(e)}", exc_info=True)

    @contextmanager
    def log_action(
            self,
            action: str,
            user_id: Optional[int],
            request: Request,
            db: Session
    ):
        try:
            yield
            # Log success after successful execution
            self.log_security_event(db, action, user_id, request, "success")
        except Exception as e:
            # Log failure
            self.log_security_event(db, action, user_id, request, "failed", {"error": str(e)})
            db.rollback()
            raise


# Configure logging when module is imported
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Singleton instance
audit_logger = AuditLogger()

