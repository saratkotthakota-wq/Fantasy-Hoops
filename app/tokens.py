"""Yahoo OAuth2 token exchange/refresh and encrypted per-user token storage (Redis)."""
import json
import time

import httpx
from cryptography.fernet import Fernet, InvalidToken

from .config import settings
from .redis_client import r

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"

_fernet = Fernet(settings.encryption_key.encode())


class ReauthRequired(Exception):
    """The stored token is missing or can no longer be refreshed; user must log in again."""


# ---------- storage ----------
def _key(guid: str) -> str:
    return f"token:{guid}"


def save_token(guid: str, token: dict) -> None:
    r.set(_key(guid), _fernet.encrypt(json.dumps(token).encode()))


def load_token(guid: str) -> dict | None:
    blob = r.get(_key(guid))
    if blob is None:
        return None
    try:
        return json.loads(_fernet.decrypt(blob))
    except InvalidToken:  # e.g. ENCRYPTION_KEY was rotated
        return None


def delete_token(guid: str) -> None:
    r.delete(_key(guid))


# ---------- Yahoo OAuth ----------
def _token_request(data: dict) -> dict:
    resp = httpx.post(
        TOKEN_URL,
        data=data,
        auth=(settings.yahoo_consumer_key, settings.yahoo_consumer_secret),
        headers={"Accept": "application/json"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _normalize(payload: dict, previous: dict | None = None) -> dict:
    prev = previous or {}
    return {
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token") or prev.get("refresh_token"),
        "token_type": payload.get("token_type", "bearer"),
        "expires_in": int(payload.get("expires_in", 3600)),
        "token_time": time.time(),
        "guid": payload.get("xoauth_yahoo_guid") or prev.get("guid"),
    }


def exchange_code(code: str) -> dict:
    payload = _token_request(
        {"grant_type": "authorization_code", "code": code, "redirect_uri": settings.yahoo_redirect_uri}
    )
    return _normalize(payload)


def _fresh(token: dict) -> bool:
    return time.time() < token["token_time"] + token["expires_in"] - 120


def get_valid_token(guid: str) -> dict:
    """Load the user's token, refreshing it first if it is (nearly) expired.
    A Redis lock makes sure only one worker refreshes at a time."""
    token = load_token(guid)
    if token is None:
        raise ReauthRequired()
    if _fresh(token):
        return token

    with r.lock(f"lock:refresh:{guid}", timeout=20, blocking_timeout=15):
        token = load_token(guid)  # another worker may have refreshed while we waited
        if token is None:
            raise ReauthRequired()
        if _fresh(token):
            return token
        try:
            payload = _token_request(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": token["refresh_token"],
                    "redirect_uri": settings.yahoo_redirect_uri,
                }
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (400, 401):  # revoked / invalid refresh token
                delete_token(guid)
                raise ReauthRequired()
            raise
        token = _normalize(payload, previous=token)
        save_token(guid, token)
        return token
