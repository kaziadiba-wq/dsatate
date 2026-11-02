"""Tiers 2 + 3: Socratic tutor on an Ollama model, with local SymPy checks as tools.

Run: python -m iymc_tutor.tutor [2|3]

Connection (pick one):
  - Local Ollama app, signed in with `ollama signin`: nothing to set. Uses http://localhost:11434.
  - Direct to Ollama cloud: set OLLAMA_API_KEY (from https://ollama.com/settings/keys).
Model: set OLLAMA_MODEL (default gemma4:cloud).
"""
import json
import os
import sys
import urllib.request

from . import progress, verify

KEY = os.environ.get("OLLAMA_API_KEY")
HOST = os.environ.get("OLLAMA_HOST", "https://ollama.com" if KEY else "http://localhost:11434")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:cloud")

SYSTEM = """You are my coach for the IYMC (International Youth Math Challenge) Pre-Final Round.
Tier {tier}: {tier_desc}

Rules, no exceptions:
1. Socratic only. Ask one guiding question or give one small hint per turn. NEVER reveal the final
   answer or a full proof, even if I ask. If I'm stuck 3 turns in a row, give a slightly bigger hint.
2. Before you state ANY identity, value, solution, factorization or number-theory pattern, call a
   verify tool and use its result. If a tool says something does not hold, say so plainly.
   Never claim something is true that you did not check.
3. When I make a mistake or show a gap, call log_weak_point with a short topic name
   (e.g. "modular inverses", "angle chasing", "AM-GM") and one-line note. Also log correct solves.
4. Start by giving me one problem that targets my weak points: {weak}
5. Keep messages short. I'm working under timed exam conditions.
"""
TIERS = {
    2: "advanced multi-step competition geometry and number theory.",
    3: "research-style problem structures: open-ended investigations, generalisations, "
       "conjecture-then-prove, constructing and checking examples.",
}


def _tool(name, desc, props, req):
    return {"type": "function", "function": {"name": name, "description": desc, "parameters": {
        "type": "object", "properties": props, "required": req}}}


S = {"type": "string"}
I = {"type": "integer"}
TOOLS = [
    _tool("check_identity", "Exactly check whether lhs == rhs for all values (SymPy).",
          {"lhs": S, "rhs": S}, ["lhs", "rhs"]),
    _tool("solve", "Solve an equation like 'x^2 - 5x + 6 = 0' for a variable.",
          {"equation": S, "variable": S}, ["equation"]),
    _tool("evaluate", "Exact + 30-digit value of an expression.", {"expression": S}, ["expression"]),
    _tool("integer_scan", "Brute-force an integer expression over n=start..end; primality and "
          "optional divisibility.", {"expression": S, "variable": S, "start": I, "end": I,
                                     "divisor": I}, ["expression"]),
    _tool("factor", "Factor an integer or polynomial.", {"expression": S}, ["expression"]),
    _tool("log_weak_point", "Save an attempt to my weak-points log.",
          {"topic": S, "correct": {"type": "boolean"}, "note": S}, ["topic", "correct"]),
]


def chat(messages):
    req = urllib.request.Request(
        f"{HOST.rstrip('/')}/api/chat",
        data=json.dumps({"model": MODEL, "messages": messages, "tools": TOOLS, "stream": False}).encode(),
        headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {KEY}"} if KEY else {})},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["message"]


def call_tool(tier, name, args):
    if isinstance(args, str):
        args = json.loads(args or "{}")
    try:
        if name == "log_weak_point":
            return progress.record(tier, args["topic"], bool(args["correct"]), args.get("note", ""))
        return verify.TOOLS[name](**args)
    except Exception as e:  # report errors back so the model can fix its input
        return {"error": f"{type(e).__name__}: {e}"}


def main(tier: int = 2):
    weak = progress.weak_points(tier=tier) or "none logged yet, so start mid-difficulty"
    messages = [{"role": "system", "content": SYSTEM.format(tier=tier, tier_desc=TIERS[tier], weak=weak)},
                {"role": "user", "content": "Start."}]
    print(f"Tier {tier} coach on {MODEL} via {HOST}. Ctrl+C to stop.\n")
    while True:
        msg = chat(messages)
        messages.append(msg)
        calls = msg.get("tool_calls") or []
        for c in calls:
            fn = c["function"]
            out = call_tool(tier, fn["name"], fn.get("arguments", {}))
            print(f"  [checked: {fn['name']}]")
            messages.append({"role": "tool", "tool_name": fn["name"], "content": json.dumps(out)})
        if calls:
            continue
        print(f"\nCoach: {msg.get('content', '').strip()}\n")
        messages.append({"role": "user", "content": input("You: ")})


if __name__ == "__main__":
    try:
        main(int(sys.argv[1]) if len(sys.argv) > 1 else 2)
    except KeyboardInterrupt:
        print("\nWeak points now:", progress.weak_points())
