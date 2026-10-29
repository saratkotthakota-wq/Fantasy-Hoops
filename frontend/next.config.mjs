// The browser only ever talks to this app's own origin. Requests to /api/* are proxied to
// the Python backend, so the session cookie is first-party and no CORS setup is needed.
const backend = process.env.BACKEND_URL;

/** @type {import('next').NextConfig} */
export default {
  async rewrites() {
    if (!backend) return [];
    return [{ source: "/api/:path*", destination: `${backend}/:path*` }];
  },
};
