"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import ErrorBox from "@/components/ErrorBox";
import RawJson from "@/components/RawJson";
import { show, unwrap } from "@/lib/api";
import { useApi } from "@/lib/useApi";

export default function LeaguePage() {
  const { leagueId } = useParams<{ leagueId: string }>();
  const league = useApi(`/leagues/${leagueId}`);
  const standings = useApi(`/leagues/${leagueId}/standings`);

  const meta = league.data?.metadata;
  const rows: any[] = Array.isArray(standings.data) ? standings.data : standings.data?.teams ?? [];

  return (
    <>
      <div className="topbar">
        <Link href="/">← Change league</Link>
      </div>

      {league.error ? (
        <ErrorBox error={league.error} />
      ) : (
        <>
          <h1>{league.loading ? "Loading…" : show(meta?.name)}</h1>
          <p className="muted">
            Season {show(meta?.season)} · {show(meta?.num_teams)} teams · Week {show(meta?.current_week)}
          </p>
        </>
      )}

      <h2>Standings</h2>
      {standings.error && !league.error && <ErrorBox error={standings.error} />}
      {standings.loading && <p className="muted">Loading standings…</p>}
      {rows.length > 0 && (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Team</th>
                <th>W-L-T</th>
                <th>Win %</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => {
                const t = unwrap(row, "team");
                const s = t?.team_standings;
                const o = s?.outcome_totals;
                return (
                  <tr key={t?.team_id ?? i}>
                    <td>{show(s?.rank ?? i + 1)}</td>
                    <td>
                      <Link href={`/league/${leagueId}/team/${t?.team_id}`}>{show(t?.name)}</Link>
                    </td>
                    <td>
                      {show(o?.wins)}-{show(o?.losses)}-{show(o?.ties)}
                    </td>
                    <td>{show(o?.percentage)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {standings.data && <RawJson data={standings.data} label="Raw standings (for debugging)" />}
      {league.data && <RawJson data={league.data} label="Raw league info (for debugging)" />}
    </>
  );
}
