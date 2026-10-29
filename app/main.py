from fastapi import Depends, FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from .auth import current_user, router as auth_router
from .config import settings
from .tokens import ReauthRequired
from .yahoo_client import YahooError, YahooLeague, get_league

app = FastAPI(title="Fantasy Hoops")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    https_only=settings.cookie_secure,
    same_site="lax",
    max_age=14 * 24 * 3600,
)
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
if origins:  # only needed when the frontend is on a different origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

app.include_router(auth_router)


@app.exception_handler(ReauthRequired)
def _reauth(_, __):
    return JSONResponse({"detail": "Yahoo login expired, please log in again"}, status_code=401)


@app.exception_handler(YahooError)
def _yahoo_error(_, exc):
    return JSONResponse({"detail": str(exc)}, status_code=502)


@app.get("/health")
def health():
    return {"ok": True}


def league_dep(
    league_id: str = Path(..., pattern=r"^\d{1,12}$"),
    guid: str = Depends(current_user),
) -> YahooLeague:
    return get_league(guid, league_id)


# Plain `def` routes on purpose: yfpy is synchronous/blocking,
# and FastAPI runs sync routes in a threadpool.
@app.get("/leagues/{league_id}")
def league(lg: YahooLeague = Depends(league_dep)):
    return {"metadata": lg.metadata(), "settings": lg.settings()}


@app.get("/leagues/{league_id}/standings")
def standings(lg: YahooLeague = Depends(league_dep)):
    return lg.standings()


@app.get("/leagues/{league_id}/teams")
def teams(lg: YahooLeague = Depends(league_dep)):
    return lg.teams()


@app.get("/leagues/{league_id}/teams/{team_id}/roster")
def roster(team_id: int, date: str | None = None, lg: YahooLeague = Depends(league_dep)):
    return lg.roster(team_id, date)


@app.get("/leagues/{league_id}/scoreboard/{week}")
def scoreboard(week: int, lg: YahooLeague = Depends(league_dep)):
    return lg.scoreboard(week)
