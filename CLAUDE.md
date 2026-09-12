# MCP course — Claude instructions

> Filming / lecture-plan work? Behind-the-scenes material (filming plan, Skillmea descriptions,
> archived 2025 slides and intent tests) lives in `training-ops/filming/mcp/`, never in this
> public student repo.

A short Python course on the Model Context Protocol. **One notebook is the course**:
`MCP_course.ipynb`, scrolled top to bottom in class (Colab; Robert speaks Slovak over English
material). Its H1 sections are the in-class flow and, later, the video units. The README is the
take-home textbook version of the same material; keep the two in step.

Rebuilt 2026-09-12 on `mcp==2.2.0` (spec 2026-07-28) and `openai==3.13.0` / `gpt-5.6-luna`.
The 2025 version (three notebooks, low-level `Server` API, `gpt-5-nano`, Chat Completions,
Gemma 2 notebook) is in git history before that date.

## Layout

```
MCP_course.ipynb        the lecture notebook, committed EXECUTED with outputs, Colab badge first
README.md               textbook; EXERCISE.md the capstone
servers/                common.py + ticket/customer/billing/kb/asset servers + hr_server (resources/prompts)
client/                 agent_loop.py (Toolbox + run_with_tools, Responses API), interactive_client.py
.mcp.json               Claude Code project-scope registration of the six servers
requirements.txt        mcp==2.2.0, openai==3.13.0 (pins must match the notebook's %pip line)
```

## Conventions that matter

- **Servers: four parts in order** (data, private helpers `_x`, plain tool functions, MCP layer).
  Tools are registered at the bottom with `mcp.tool(annotations=READ_ONLY|WRITES)(fn)`; the
  notebook prints the file from the `# 4. MCP LAYER` marker, so keep that marker line.
  Every parameter typed; docstring first line = tool description; expected failures return
  `make_error(...)` (never raise); **never `print()` in a server** (stdio is the wire); all
  mock dates via `days_ago()/days_from_now()`.
- **Notebook markdown is classroom voice**: the recipe in `ADK-tutorial/CLAUDE.md`
  ("Notebooks → classroom voice"). Short cells, want-first, bolded term + plain gloss, key-line
  decode next to each new API line, "### 🔍 What just happened?" after every demo, "### 🎯
  Mini-task" interleaved, `\$` for amounts, no relative repo links (break in Colab), no
  em-dashes, no LLMish vocabulary.
- **No `nest_asyncio` anywhere.** The 2.x `Client` runs with plain top-level `await` in Jupyter
  and Colab; with nest_asyncio it hangs. Colab needs the `sys.stderr.fileno()` swap before the
  first subprocess (in the "Be the Client" cell).
- **Logging**: set `httpx`, `httpx2` (the SDK's vendored copy) and `openai` loggers to WARNING
  in the key cell, or every HTTP request lands in cell outputs.
- **ADK bridge is shown, not run**: ADK pins `mcp<2`; a 2.x server works with its 1.x client
  (verified 2026-09-12), but the two cannot share one environment.
- The notebook is built by a builder script kept in the session scratchpad (nbformat); when
  editing by hand, keep cell order = section order and re-execute.

## Running and verifying

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt jupyter nbconvert ipykernel
export OPENAI_API_KEY=...            # Robert's key: testing-tutorial/.env
jupyter nbconvert --to notebook --execute --inplace MCP_course.ipynb --ExecutePreprocessor.timeout=300
pgrep -fl "servers/.*_server.py"     # must be empty afterwards (no stray servers)
printf 'Which customers have both open tickets and overdue invoices?\nexit\n' | python client/interactive_client.py
```

After a run, read the outputs against the prose (dump code cells to text); the TKT-9999
recovery demo should show three rounds (details → error → search → details). Colab check by
Robert: badge, Run all, terminal for the interactive client.

## Drive sync

`training-ops/drive-push` course key `mcp`: the WHOLE repo root maps to the Courses drive
folder `6. MCP (SYNCED)/course_materials (shared)` (excluding `recordings/**`; push.py skips
`.venv`, `.git`, `CLAUDE.md`). Run `python3 training-ops/drive-push/push.py --status --course mcp`
before and after touching files. Restructures go through server-side `rclone moveto` (keeps
file IDs), never delete-and-reupload.

## Git

Commit directly to `main` and push. No force-pushes, no `--no-verify`.
