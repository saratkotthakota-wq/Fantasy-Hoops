"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import ErrorBox from "@/components/ErrorBox";
import RawJson from "@/components/RawJson";
import { show, unwrap } from "@/lib/api";
import { useApi } from "@/lib/useApi";

export default function TeamPage() {
  const { leagueId, teamId } = useParams<{ leagueId: string; teamId: string }>();
  const [date, setDate] = useState(""); // empty = today
  const { data, error, loading } = useApi(
    `/leagues/${leagueId}/teams/${teamId}/roster${date ? `?date=${date}` : ""}`
  );

  const players: any[] = Array.isArray(data) ? data : data?.players ?? [];

  return (
    <>
      <div className="topbar">
        <Link href={`/league/${leagueId}`}>← Back to league</Link>
      </div>
      <h1>Roster</h1>
      <p className="muted">
        Team {teamId} ·{" "}
        <label>
          Date:{" "}
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            style={{ flex: "none", padding: "0.2rem 0.4rem" }}
          />
        </label>
      </p>

      {error && <ErrorBox error={error} />}
      {loading && <p className="muted">Loading roster…</p>}

      {players.length > 0 && (
        <div className="card">
          <table>
            <thead>
              <tr>
                <th>Slot</th>
                <th>Player</th>
                <th>Pos</th>
                <th>Team</th>
              </tr>
            </thead>
            <tbody>
              {players.map((p, i) => {
                const pl = unwrap(p, "player");
                return (
                  <tr key={pl?.player_id ?? i}>
                    <td>{show(pl?.selected_position?.position)}</td>
                    <td>{show(pl?.name?.full)}</td>
                    <td>{show(pl?.display_position)}</td>
                    <td>{show(pl?.editorial_team_abbr)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {data && <RawJson data={data} label="Raw roster (for debugging)" />}
    </>
  );
}
