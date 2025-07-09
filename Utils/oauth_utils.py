# BackEnd/Utils/oauth_utils.py

import requests
from fastapi import HTTPException, status


def google_oauth_login(google_token: str) -> dict:
    """
    Validates Google ID token and extracts user info.
    Raises HTTPException if token is invalid or email is unverified.
    """
    url = "https://oauth2.googleapis.com/tokeninfo"
    params = {'id_token': google_token}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google OAuth token validation failed"
        )

    user_info = response.json()

    if not user_info.get("email_verified", "false") == "true":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email is not verified by Google"
        )

    return {
        "google_id": user_info["sub"],
        "email": user_info["email"],
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
    }
