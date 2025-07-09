# BackEnd/Routes/admin.py
from fastapi import APIRouter, Depends
from BackEnd.Utils.auth_utils import require_role
from BackEnd.Models.user import UserRole

router = APIRouter(tags=["Admin"], dependencies=[Depends(require_role(UserRole.ADMIN))])

@router.get("/dashboard")
async def admin_dashboard():
    return {"message": "Admin dashboard"}