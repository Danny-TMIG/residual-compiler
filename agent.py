"""agent.py — LLM + tool registry + approvals, calling the residual CLI.

Intent in, engineering out. Uses OpenAI tool-calling by default;
swap `llm_call` for Ollama/Anthropic as needed.
"""
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESIDUAL = ROOT / "dist" / "residual"

# ── tool registry: every CLI command is a tool ──
TOOLS = {
    "verify":       "Run control-plane verification. Returns COVERED or REFUTED.",
    "org":          "Org matrix: 16 roles, gaps, independence.",
    "const":        "Validate the 160-class constitutional record.",
    "conform":      "Conformance rings: Ring 1/2/3 summary.",
    "evidence":     "Build the evidence bundle (tarball + manifest).",
    "ship":         "Build, sign, package the release. Asks for approval.",
    "sbom":         "Emit SPDX SBOM.",
    "rats":         "Emit RATS (software-signed) evidence.",
    "sci":          "Compute software carbon intensity.",
}

def run_tool(name: str) -> str:
    if name not in TOOLS:
        return f"unknown tool: {name}"
    r = subprocess.run([str(RESIDUAL), name], capture_output=True, text=True, timeout=300)
    return (r.stdout or r.stderr).strip()

# ── LLM call (OpenAI; swap for Anthropic/Ollama by replacing this) ──
def llm_call(messages: list[dict]) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=os.environ.get("AGENT_MODEL", "gpt-4o-mini"),
        messages=messages,
        tools=[{
            "type": "function",
            "function": {
                "name": name,
                "description": desc,
                "parameters": {"type": "object", "properties": {}},
            },
        } for name, desc in TOOLS.items()],
        tool_choice="auto",
    )
    return resp.choices[0].message.model_dump()

# ── approval gate ──
DANGEROUS = {"ship", "evidence"}
def approve(tool: str, args: dict) -> bool:
    if tool not in DANGEROUS:
        return True
    ans = input(f"\n⚠  agent wants to run `{tool}` {args}. approve? [y/N] ").strip().lower()
    return ans == "y"

# ── the loop ──
def chat_turn(user_text: str, history: list[dict]) -> str:
    history.append({"role": "user", "content": user_text})
    while True:
        msg = llm_call(history)
        history.append(msg)
        if not msg.get("tool_calls"):
            return msg.get("content") or ""
        for call in msg["tool_calls"]:
            name = call["function"]["name"]
            args = json.loads(call["function"]["arguments"] or "{}")
            if not approve(name, args):
                history.append({"role": "tool", "tool_call_id": call["id"],
                                "content": "denied by user"})
                continue
            print(f"\n→ {name}()")
            out = run_tool(name)
            print(out[:500] + ("…" if len(out) > 500 else ""))
            history.append({"role": "tool", "tool_call_id": call["id"], "content": out})

def main():
    print(f"residual agent — tools: {', '.join(TOOLS)}")
    print(f"residual binary: {RESIDUAL} ({'found' if RESIDUAL.exists() else 'MISSING'})")
    history = [{"role": "system", "content":
        "You are an engineering agent. You call tools to inspect and ship this repo. "
        "Always verify before shipping. Ask for approval on anything destructive."}]
    while True:
        try:
            text = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text: continue
        if text in ("exit","quit"): break
        reply = chat_turn(text, history)
        print(f"\n{reply}")

if __name__ == "__main__":
    sys.exit(main())
