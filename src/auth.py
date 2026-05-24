import hmac
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Validates Authorization: Bearer <token> on every request except /health."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        expected = os.environ.get("MCP_SECRET_TOKEN", "")
        if not expected:
            return JSONResponse({"error": "MCP_SECRET_TOKEN not configured"}, status_code=500)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Missing or invalid Authorization header"}, status_code=401)

        token = auth_header[len("Bearer "):]
        if not hmac.compare_digest(token.encode(), expected.encode()):
            return JSONResponse({"error": "Invalid token"}, status_code=401)

        return await call_next(request)
