"""Thin wrapper around yfpy, one instance per (user, league). Keep all Yahoo-specific
quirks here so the rest of the app deals in plain dicts."""
import logging
from datetime import date
from functools import wraps

from yfpy.query import YahooFantasySportsQuery

from . import tokens
from .cache import ttl_cache
from .config import settings

log = logging.getLogger(__name__)
TTL = settings.cache_ttl_seconds


class YahooError(Exception):
    pass


def yahoo_call(fn):
    """Turn any yfpy/Yahoo failure into a YahooError (and log the real cause)."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except tokens.ReauthRequired:
            raise
        except Exception:
            log.exception("Yahoo call failed: %s", fn.__name__)
            raise YahooError(
                "Couldn't load that from Yahoo. Check the league ID and that the "
                "Yahoo account you logged in with is a member of the league."
            )
    return wrapper


def to_plain(obj):
    """yfpy returns model objects, and some string fields come back as bytes.
    Convert everything to JSON-safe primitives."""
    if hasattr(obj, "serialized"):
        obj = obj.serialized()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_plain(v) for v in obj]
    return obj


class YahooLeague:
    def __init__(self, guid: str, league_id: str, token: dict):
        self.guid = guid
        self.league_id = league_id
        kwargs = dict(
            league_id=league_id,
            game_code="nba",
            yahoo_consumer_key=settings.yahoo_consumer_key,
            yahoo_consumer_secret=settings.yahoo_consumer_secret,
            yahoo_access_token_json={
                **token,
                "consumer_key": settings.yahoo_consumer_key,
                "consumer_secret": settings.yahoo_consumer_secret,
            },
            env_var_fallback=False,            # never read a shared token from .env
            save_token_data_to_env_file=False,  # tokens live in our encrypted DB instead
        )
        if settings.yahoo_game_id:
            kwargs["game_id"] = settings.yahoo_game_id
        self.q = YahooFantasySportsQuery(**kwargs)

    @yahoo_call
    @ttl_cache(TTL)
    def metadata(self):
        return to_plain(self.q.get_league_metadata())

    @yahoo_call
    @ttl_cache(TTL)
    def settings(self):
        return to_plain(self.q.get_league_settings())

    @yahoo_call
    @ttl_cache(TTL)
    def standings(self):
        return to_plain(self.q.get_league_standings())

    @yahoo_call
    @ttl_cache(TTL)
    def teams(self):
        return to_plain(self.q.get_league_teams())

    @yahoo_call
    @ttl_cache(TTL)
    def roster(self, team_id: int, on: str | None = None):
        # NBA leagues are usually daily lineups, so roster is by date
        day = on or date.today().isoformat()
        return to_plain(self.q.get_team_roster_player_info_by_date(team_id, day))

    @yahoo_call
    @ttl_cache(TTL)
    def scoreboard(self, week: int):
        return to_plain(self.q.get_league_scoreboard_by_week(week))


_leagues: dict[tuple, YahooLeague] = {}


@yahoo_call
def get_league(guid: str, league_id: str) -> YahooLeague:
    """One YahooLeague per (user, league, token). When the token is refreshed the key
    changes, so a fresh query object (with the new token) replaces the old one."""
    token = tokens.get_valid_token(guid)
    key = (guid, league_id, token["token_time"])
    if key not in _leagues:
        for stale in [k for k in _leagues if k[:2] == (guid, league_id)]:
            del _leagues[stale]
        _leagues[key] = YahooLeague(guid, league_id, token)
    return _leagues[key]
