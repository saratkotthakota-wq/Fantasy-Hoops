"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useApi } from "@/lib/useApi";

export default function Home() {
  const router = useRouter();
  const { data: me, error, loading } = useApi<{ guid: string }>("/auth/me");
  const [leagueId, setLeagueId] = useState("");

  useEffect(() => {
    setLeagueId(localStorage.getItem("leagueId") ?? "");
  }, []);

  const loggedOut = error?.status === 401;

  function submit(e: React.FormEvent) {
    e.preventDefault();
    const id = leagueId.trim();
    if (!/^\d{1,12}$/.test(id)) return;
    localStorage.setItem("leagueId", id);
    router.push(`/league/${id}`);
  }

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.reload();
  }

  return (
    <>
      <h1>Fantasy Hoops</h1>
      <p className="muted">Look at your Yahoo fantasy basketball league.</p>

      {loading && <p className="muted">Checking your login…</p>}

      {error && !loggedOut && (
        <div className="card error">
          <p>Couldn&apos;t reach the server: {error.message}</p>
        </div>
      )}

      {loggedOut && (
        <div className="card">
          <p>Connect your Yahoo account so we can read your leagues (read-only).</p>
          <a className="button" href="/api/auth/login">
            Connect Yahoo
          </a>
        </div>
      )}

      {me && (
        <div className="card">
          <form className="row" onSubmit={submit}>
            <input
              inputMode="numeric"
              placeholder="Your league ID, e.g. 12345"
              value={leagueId}
              onChange={(e) => setLeagueId(e.target.value)}
              aria-label="League ID"
            />
            <button type="submit">Load league</button>
          </form>
          <p className="muted">
            The league ID is the number in your league&apos;s Yahoo URL, e.g. the 12345 in
            …/nba/12345.
          </p>
          <button className="link" onClick={logout}>
            Log out
          </button>
        </div>
      )}
    </>
  );
}
