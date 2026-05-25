import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from urllib.parse import parse_qs, urlencode

TOKEN_TTL = 3600               # 1 hour
REFRESH_TOKEN_TTL = 30 * 86400 # 30 days
AUTH_CODE_TTL = 600            # 10 minutes

# access token -> expiry
_tokens: dict[str, float] = {}

# refresh token -> expiry
_refresh_tokens: dict[str, float] = {}

# auth code -> {code_challenge, code_challenge_method, redirect_uri, expires}
_auth_codes: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _cleanup() -> None:
    now = time.time()
    for store in (_tokens, _refresh_tokens):
        expired = [k for k, v in list(store.items()) if v < now]
        for k in expired:
            store.pop(k, None)
    expired_codes = [k for k, v in list(_auth_codes.items()) if v["expires"] < now]
    for k in expired_codes:
        _auth_codes.pop(k, None)


def _issue_tokens() -> tuple[str, str, int]:
    """Issue an access token + refresh token pair."""
    _cleanup()
    access_token = secrets.token_hex(32)
    refresh_token = secrets.token_hex(32)
    _tokens[access_token] = time.time() + TOKEN_TTL
    _refresh_tokens[refresh_token] = time.time() + REFRESH_TOKEN_TTL
    return access_token, refresh_token, TOKEN_TTL


def _issue_auth_code(code_challenge: str, code_challenge_method: str, redirect_uri: str) -> str:
    code = secrets.token_urlsafe(32)
    _auth_codes[code] = {
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
        "redirect_uri": redirect_uri,
        "expires": time.time() + AUTH_CODE_TTL,
    }
    return code


def _verify_pkce(code_verifier: str, code_challenge: str, method: str) -> bool:
    if method == "S256":
        digest = hashlib.sha256(code_verifier.encode()).digest()
        computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return hmac.compare_digest(computed, code_challenge)
    if method == "plain":
        return hmac.compare_digest(code_verifier, code_challenge)
    return False


def _issuer(scope: dict) -> str:
    headers = dict(scope.get("headers", []))
    host = headers.get(b"host", b"localhost").decode()
    return f"https://{host}"


def is_valid_oauth_token(token: str) -> bool:
    exp = _tokens.get(token)
    if exp is None:
        return False
    if time.time() > exp:
        _tokens.pop(token, None)
        return False
    return True


def _token_response(access_token: str, refresh_token: str, ttl: int) -> dict:
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ttl,
        "refresh_token": refresh_token,
    }


# ---------------------------------------------------------------------------
# ASGI endpoint handlers (all called before auth middleware)
# ---------------------------------------------------------------------------

async def handle_authorization_server_metadata(scope: dict, send) -> None:
    """GET /.well-known/oauth-authorization-server — RFC 8414 discovery."""
    base = _issuer(scope)
    await _json(send, 200, {
        "issuer": base,
        "authorization_endpoint": f"{base}/authorize",
        "token_endpoint": f"{base}/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "client_credentials", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
    })


async def handle_protected_resource_metadata(scope: dict, send) -> None:
    """GET /.well-known/oauth-protected-resource[/*] — RFC 9728 discovery."""
    base = _issuer(scope)
    await _json(send, 200, {
        "resource": base,
        "authorization_servers": [base],
    })


async def handle_authorize_request(scope: dict, send) -> None:
    """GET /authorize — issue auth code and redirect back with PKCE."""
    query = parse_qs(scope.get("query_string", b"").decode())

    client_id = query.get("client_id", [""])[0]
    redirect_uri = query.get("redirect_uri", [""])[0]
    state = query.get("state", [""])[0]
    code_challenge = query.get("code_challenge", [""])[0]
    code_challenge_method = query.get("code_challenge_method", ["S256"])[0]

    expected_id = os.environ.get("OAUTH_CLIENT_ID", "")
    if not expected_id or not hmac.compare_digest(client_id.encode(), expected_id.encode()):
        await _json(send, 401, {"error": "invalid_client"})
        return

    if not redirect_uri or not code_challenge:
        await _json(send, 400, {"error": "invalid_request", "error_description": "redirect_uri and code_challenge required"})
        return

    code = _issue_auth_code(code_challenge, code_challenge_method, redirect_uri)

    params: dict = {"code": code}
    if state:
        params["state"] = state
    sep = "&" if "?" in redirect_uri else "?"
    location = redirect_uri + sep + urlencode(params)

    await send({"type": "http.response.start", "status": 302, "headers": [(b"location", location.encode()), (b"content-length", b"0")]})
    await send({"type": "http.response.body", "body": b""})


async def handle_token_request(body: bytes, send) -> None:
    """POST /token — authorization_code, refresh_token, or client_credentials."""
    params = parse_qs(body.decode(errors="replace"))
    grant_type = params.get("grant_type", [""])[0]

    if grant_type == "authorization_code":
        await _authorization_code(params, send)
    elif grant_type == "refresh_token":
        await _refresh_token(params, send)
    elif grant_type == "client_credentials":
        await _client_credentials(params, send)
    else:
        await _json(send, 400, {"error": "unsupported_grant_type"})


async def _authorization_code(params: dict, send) -> None:
    code = params.get("code", [""])[0]
    code_verifier = params.get("code_verifier", [""])[0]
    redirect_uri = params.get("redirect_uri", [""])[0]

    entry = _auth_codes.pop(code, None)
    if not entry:
        await _json(send, 400, {"error": "invalid_grant", "error_description": "Unknown or expired code"})
        return

    if time.time() > entry["expires"]:
        await _json(send, 400, {"error": "invalid_grant", "error_description": "Code expired"})
        return

    if entry["redirect_uri"] != redirect_uri:
        await _json(send, 400, {"error": "invalid_grant", "error_description": "redirect_uri mismatch"})
        return

    if not _verify_pkce(code_verifier, entry["code_challenge"], entry["code_challenge_method"]):
        await _json(send, 400, {"error": "invalid_grant", "error_description": "PKCE verification failed"})
        return

    access_token, refresh_token, ttl = _issue_tokens()
    await _json(send, 200, _token_response(access_token, refresh_token, ttl))


async def _refresh_token(params: dict, send) -> None:
    token = params.get("refresh_token", [""])[0]

    exp = _refresh_tokens.pop(token, None)
    if not exp or time.time() > exp:
        await _json(send, 400, {"error": "invalid_grant", "error_description": "Refresh token expired or invalid"})
        return

    # Rotate: issue a new pair
    access_token, new_refresh_token, ttl = _issue_tokens()
    await _json(send, 200, _token_response(access_token, new_refresh_token, ttl))


async def _client_credentials(params: dict, send) -> None:
    client_id = params.get("client_id", [""])[0]
    client_secret = params.get("client_secret", [""])[0]

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

    access_token, refresh_token, ttl = _issue_tokens()
    await _json(send, 200, _token_response(access_token, refresh_token, ttl))


async def _json(send, status: int, data: dict) -> None:
    body = json.dumps(data).encode()
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
    })
    await send({"type": "http.response.body", "body": body})
