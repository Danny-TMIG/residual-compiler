import { useState } from "react";
import { AutomationService } from "../bindings/residual-control/internal/services";

export default function App() {
  const [out, setOut] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function call(fn: () => Promise<string>) {
    setLoading(true);
    try { setOut(await fn()); } catch (e: any) { setOut(String(e)); }
    setLoading(false);
  }

  return (
    <div style={{ padding: 20, fontFamily: "monospace" }}>
      <h1>Residual Control</h1>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={() => call(() => AutomationService.Verify())} disabled={loading}>Verify</button>
        <button onClick={() => call(() => AutomationService.Org())} disabled={loading}>Org</button>
        <button onClick={() => call(() => AutomationService.Const())} disabled={loading}>Constitution</button>
        <button onClick={() => call(() => AutomationService.Conform())} disabled={loading}>Conformance</button>
      </div>
      {loading && <div>running…</div>}
      <pre style={{ background: "#111", color: "#0f0", padding: 16, overflow: "auto", maxHeight: "70vh" }}>
        {out}
      </pre>
    </div>
  );
}
