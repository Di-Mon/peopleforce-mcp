import hmac
import json
import os
import secrets
import time
from urllib.parse import parse_qs

TOKEN_TTL = 3600  # seconds

# token -> expiry timestamp
_store: dict[str, float] = {}


def _cleanup() -> None:
    now = time.time()
    expired = [t for t, exp in list(_store.items()) if exp < now]
    for t in expired:
        _store.pop(t, None)


def _issue_token() -> tuple[str, int]:
    _cleanup()
    token = secrets.token_hex(32)
    _store[token] = time.time() + TOKEN_TTL
    return token, TOKEN_TTL


def is_valid_oauth_token(token: str) -> bool:
    exp = _store.get(token)
    if exp is None:
        return False
    if time.time() > exp:
        _store.pop(token, None)
        return False
    return True


async def handle_token_request(body: bytes, send) -> None:
    """POST /oauth/token — client credentials flow."""
    params = parse_qs(body.decode(errors="replace"))

    grant_type = params.get("grant_type", [""])[0]
    client_id = params.get("client_id", [""])[0]
    client_secret = params.get("client_secret", [""])[0]

    if grant_type != "client_credentials":
        await _json(send, 400, {"error": "unsupported_grant_type"})
        return

    expected_id = os.environ.get("OAUTH_CLIENT_ID", "")
    expected_secret = os.environ.get("OAUTH_CLIENT_SECRET", "")

    if not expected_id or not expected_secret:
        await _json(send, 500, {"error": "server_error", "error_description": "OAuth not configured"})
        return

    id_ok = hmac.compare_digest(client_id.encode(), expected_id.encode())
    secret_ok = hmac.compare_digest(client_secret.encode(), expected_secret.encode())

    if not (id_ok and secret_ok):
        await _json(send, 401, {"error": "invalid_client"})
        return

    token, ttl = _issue_token()
    await _json(send, 200, {"access_token": token, "token_type": "Bearer", "expires_in": ttl})


async def _json(send, status: int, data: dict) -> None:
    body = json.dumps(data).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
        ],
    })
    await send({"type": "http.response.body", "body": body})
