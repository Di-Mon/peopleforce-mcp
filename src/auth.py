import hmac
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from oauth import is_valid_oauth_token


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Accepts: static MCP_SECRET_TOKEN (header or ?token=) or OAuth-issued tokens."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]
        else:
            token = request.query_params.get("token", "")

        if not token:
            return JSONResponse({"error": "Missing Authorization"}, status_code=401)

        static = os.environ.get("MCP_SECRET_TOKEN", "")
        if static and hmac.compare_digest(token.encode(), static.encode()):
            return await call_next(request)

        if is_valid_oauth_token(token):
            return await call_next(request)

        return JSONResponse({"error": "Invalid token"}, status_code=401)
