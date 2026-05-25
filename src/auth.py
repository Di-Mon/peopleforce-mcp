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
        if auth_header.startswith("Bearer "):
            token = auth_header[len("Bearer "):]
        else:
            token = request.query_params.get("token", "")

        if not token or not hmac.compare_digest(token.encode(), expected.encode()):
            return JSONResponse({"error": "Invalid token"}, status_code=401)

        return await call_next(request)
