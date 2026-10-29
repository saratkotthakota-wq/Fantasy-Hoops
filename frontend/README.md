# Fantasy Hoops: frontend (Next.js)

Pages: `/` (login + league ID form), `/league/[id]` (info + standings), `/league/[id]/team/[teamId]` (roster).
All data comes from the Python backend through the `/api/*` proxy in `next.config.mjs`.

## Local dev
1. Start Redis and the backend (see the root README); backend on http://localhost:8000.
2. `cp .env.example .env.local`
3. `npm install && npm run dev`  ->  https://localhost:3000
   (`--experimental-https` makes Next generate a local TLS cert; Yahoo requires https redirects.)
4. On your Yahoo app, add the redirect URI `https://localhost:3000/api/auth/callback`
   and set the same value as `YAHOO_REDIRECT_URI` in the backend `.env`.

## Deploy to Vercel
1. Import the repo, set **Root Directory** to `frontend`.
2. Add env var `BACKEND_URL` = your deployed backend's public URL.
3. Add `https://<your-vercel-domain>/api/auth/callback` to the Yahoo app's redirect URIs
   and use it as the backend's `YAHOO_REDIRECT_URI`.
