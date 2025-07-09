# BackEnd/Utils/sanitization.py

from fastapi import Request, HTTPException
import html
import re


class SanitizationMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Check for suspicious content in JSON body
            if request.headers.get("content-type") == "application/json":
                body = await request.body()
                try:
                    decoded_body = body.decode()
                    if self.is_malicious(decoded_body):
                        raise HTTPException(
                            status_code=400,
                            detail="Potential malicious content detected"
                        )
                except UnicodeDecodeError:
                    pass

        return await self.app(scope, receive, send)

    def is_malicious(self, content: str) -> bool:
        # Check for common injection patterns
        patterns = [
            r"<script.*?>.*?</script>",
            r"onerror\s*=",
            r"javascript:",
            r"eval\s*\(",
            r"alert\s*\("
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)


def sanitize_input(data: str) -> str:
    """Basic HTML escaping for XSS prevention"""
    return html.escape(data)