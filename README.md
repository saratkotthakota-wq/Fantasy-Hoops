# Fantasy Hoops

Yahoo fantasy basketball helper. Users log in with their own Yahoo account, then enter a league ID.

- `app/`: FastAPI backend (this folder). yfpy for Yahoo data, Redis for cache + encrypted tokens.
- `frontend/`: Next.js frontend, proxies `/api/*` to the backend so cookies are first-party.

## Yahoo app settings (https://developer.yahoo.com/apps/)
- Client type: **Confidential Client**; API permission: **Fantasy Sports -> Read**
- Redirect URI(s): `https://localhost:3000/api/auth/callback` (dev) and your production
  equivalent. Must match `YAHOO_REDIRECT_URI` exactly.
- See Yahoo's API access form at https://sports.yahoo.com/developer/access/ for the review process.

## Backend setup
1. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. `docker run -p 6379:6379 redis` (or any Redis; see `.env.example`)
3. `cp .env.example .env`; fill in key, secret; run `python -m scripts.gen_keys` for the two secrets
4. `uvicorn app.main:app --reload --port 8000` (plain http is fine locally; the frontend handles https)

Then run the frontend (see `frontend/README.md`) and open https://localhost:3000.

## Deploying the backend
**Render (Blueprint):** push this repo to GitHub, then in Render choose *New -> Blueprint*, select the repo,
and it reads `render.yaml` to create the Key Value store and the API service. Fill in the prompted
secrets (`YAHOO_CONSUMER_KEY`, `YAHOO_CONSUMER_SECRET`, `YAHOO_REDIRECT_URI`, `ENCRYPTION_KEY`).

**Other hosts:** `Dockerfile` is included. Any host that runs a container works (Render, Railway, Fly.io, ...).
Set the same variables as `.env`, with a hosted Redis for `REDIS_URL`.

## API
- `GET /auth/login`, `GET /auth/callback`, `GET /auth/me`, `POST /auth/logout`
- `GET /leagues/{id}`, `/standings`, `/teams`, `/teams/{team_id}/roster`, `/scoreboard/{week}`
