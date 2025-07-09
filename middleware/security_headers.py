# BackEnd/middleware/security_headers.py

from fastapi import Request, Response
from fastapi.middleware import Middleware


async def security_headers(request: Request, call_next):
    """
    Middleware function to add security headers to all HTTP responses.
    Enhances security by setting headers that control content policies,
    prevent MIME sniffing, enforce HTTPS, disable framing, and restrict permissions.
    """
    # Process the request and get the response from the next middleware or route handler
    response = await call_next(request)

    # Define common security headers to add
    security_headers = {
        "Content-Security-Policy": "default-src 'self'; script-src 'self'",  # Limit resource loading to same origin
        "X-Content-Type-Options": "nosniff",  # Prevent MIME type sniffing
        "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",  # Enforce HTTPS for 2 years
        "X-Frame-Options": "DENY",  # Prevent clickjacking by disallowing framing
        "Permissions-Policy": "geolocation=(), microphone=()"  # Disable geolocation and microphone features
    }

    # Add each security header to the response
    for header, value in security_headers.items():
        response.headers[header] = value

    return response


# To use this middleware, add it to your FastAPI app like so:
from fastapi import FastAPI
app = FastAPI(middleware=[Middleware(security_headers)])
