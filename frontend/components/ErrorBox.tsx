import Link from "next/link";
import { ApiError } from "@/lib/api";

export default function ErrorBox({ error }: { error: ApiError }) {
  const expired = error.status === 401;
  return (
    <div className="card error">
      <p>{expired ? "You're not logged in with Yahoo (or your session expired)." : error.message}</p>
      {expired ? <a href="/api/auth/login">Log in with Yahoo</a> : <Link href="/">Back to start</Link>}
    </div>
  );
}
