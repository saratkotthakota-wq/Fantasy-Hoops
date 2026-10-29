// Handy while you're building: shows exactly what the API returned so you can see
// which fields exist. Delete once your UI is settled.
export default function RawJson({ data, label = "Raw data" }: { data: unknown; label?: string }) {
  return (
    <details className="raw">
      <summary>{label}</summary>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </details>
  );
}
