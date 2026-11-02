# IYMC Pre-Final coach

My training setup for the IYMC Pre-Final Round, in three tiers:

| Tier | What | Runs on |
|---|---|---|
| 1 | Arithmetic/algebra speed runs | Python only (made + graded locally) |
| 2 | Multi-step geometry & number theory | Ollama cloud model + local SymPy checks |
| 3 | Research-style problem structures | Ollama cloud model + local SymPy checks |

The coach only gives Socratic hints, never the final proof. Before it states any math fact it has to
run a local check (`iymc_tutor/verify.py`). Every miss goes into `iymc_tutor/progress.json`, and the
next session starts on my weakest topics.

## Setup

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
3. Turn on cloud models (needs credits or a paid plan). Pick one:
   - Run `ollama signin`. Then the coach talks to the local Ollama app at `localhost:11434`.
   - Or create a key at https://ollama.com/settings/keys and set it as `OLLAMA_API_KEY`.
     Then the coach calls `https://ollama.com` directly.
4. Optional: pick a different model with `OLLAMA_MODEL` (default `gemma4:cloud`).

## Use

Run a Tier 1 speed run (15 questions, 20 s each):
```bash
python -m iymc_tutor.drills 15 20
```

Start a Tier 2 session:
```bash
python -m iymc_tutor.tutor 2
```

Start a Tier 3 session:
```bash
python -m iymc_tutor.tutor 3
```
