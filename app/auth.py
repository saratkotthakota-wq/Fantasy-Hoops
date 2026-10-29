"""Yahoo login flow: /auth/login -> Yahoo -> /auth/callback -> session cookie."""
import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from . import tokens
from .config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def current_user(request: Request) -> str:
    """Dependency: returns the logged-in user's Yahoo guid or raises 401."""
    guid = request.session.get("user_guid")
    if not guid or tokens.load_token(guid) is None:
        raise HTTPException(401, "Not logged in")
    return guid


@router.get("/login")
def login(request: Request):
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    params = {
        "client_id": settings.yahoo_consumer_key,
        "redirect_uri": settings.yahoo_redirect_uri,
        "response_type": "code",
        "state": state,
        "language": "en-us",
    }
    return RedirectResponse(f"{tokens.AUTH_URL}?{urlencode(params)}")


@router.get("/callback")
def callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    expected = request.session.pop("oauth_state", None)
    if error:
        raise HTTPException(400, f"Yahoo login was not completed ({error})")
    if not code or not state or not expected or not secrets.compare_digest(state, expected):
        raise HTTPException(400, "Invalid login state, please try logging in again")
    try:
        token = tokens.exchange_code(code)
    except httpx.HTTPError:
        raise HTTPException(502, "Could not complete login with Yahoo")
    guid = token.get("guid")
    if not guid:
        raise HTTPException(502, "Yahoo did not return a user id")
    tokens.save_token(guid, token)
    request.session.clear()  # fresh session after login
    request.session["user_guid"] = guid
    return RedirectResponse(settings.frontend_url)


@router.get("/me")
def me(request: Request):
    guid = current_user(request)
    return {"guid": guid}


@router.post("/logout")
def logout(request: Request):
    guid = request.session.get("user_guid")
    if guid:
        tokens.delete_token(guid)
    request.session.clear()
    return {"ok": True}
