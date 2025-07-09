# BackEnd/Routes/settings.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from BackEnd.Models.settings import UserSettings
from sqlalchemy.orm import Session
from BackEnd.Models.user import User
from BackEnd.Utils.auth_utils import get_current_user
from BackEnd.Utils.database import get_db
import json
from datetime import datetime
router = APIRouter(tags=["Settings"])


@router.get("/")
async def get_settings():
    return {"message": "Settings endpoint"}


@router.post("/reset-theme")
def reset_scoped_theme(
        page: str = Query("default"),  # Scope by page name
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    default_themes = {
        "default": {"primary": "#3b82f6", "secondary": "#8b5cf6", "version": 1},
        "dashboard": {"primary": "#10b981", "secondary": "#f97316", "version": 1}
    }

    # Update theme with scoped reset
    theme = json.loads(settings.theme)
    theme[page] = default_themes.get(page, default_themes["default"])
    theme["version"] = theme.get("version", 1) + 1

    # Save to history
    history = json.loads(settings.theme_history)
    history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "theme": theme,
        "scope": page,
        "action": "reset"
    })

    settings.theme = json.dumps(theme)
    settings.theme_history = json.dumps(history)
    db.commit()

    return {"status": "success", "version": theme["version"]}