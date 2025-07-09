from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm


class OAuth2EmailPasswordForm(OAuth2PasswordRequestForm):
    def __init__(
            self,
            grant_type: str = Form(default="password"),
            email: str = Form(...),
            password: str = Form(...),
            scope: str = Form(default=""),
            client_id: str = Form(default=None),
            client_secret: str = Form(default=None),
    ):
        super().__init__(
            grant_type=grant_type,
            username=email,  # treat email as username
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret
        )
