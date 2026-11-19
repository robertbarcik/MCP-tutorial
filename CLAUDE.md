# MCP course — Claude instructions

> Filming / lecture-plan work? Behind-the-scenes material (filming plan, Skillmea descriptions,
> archived 2025 slides and intent tests) lives in `training-ops/filming/mcp/`, never in this
> public student repo.

A short Python course on the Model Context Protocol. **One notebook is the course**:
`MCP_course.ipynb`, scrolled top to bottom (Colab; Robert speaks Slovak over English
material). The README is the take-home textbook version of the same material; keep the two in
step.

**Heading contract (since 2026-11-18): the notebook follows the videos.** `# K. Title` = chapter
(0 to 4), `## K.V Title` = exactly one video, and `K.V` is the lecture code `K_V` in the Skillmea
overview tab "MCP". `###` = rituals and sub-parts inside a video. Sections without a video are
unnumbered `## Optional: …` (Inspector, Beyond your laptop). Developer corners are unnumbered
`## 🛠️ Developer corner: …` and are not filmed. Renaming, adding or moving a numbered section
means updating the Skillmea tab and the chapter table at the top of the README in the same go.
Cross-references in the text use section numbers ("section 2.2"), never "the previous chapter".

**Two paths in one notebook (since 2026-09-13).** The audience is mixed (IT/PO colleagues with
basic Python next to developers). Everything visible by default is the *everyone path*: README
voice, short cells, copyable four-line client shape, no plumbing. Each chapter may end with one
`## 🛠️ Developer corner: …` H2 (previous technical notebook voice, "optional detail" lines,
`**🛠️ Stretch.**` tasks). Corners are listed in notebook metadata `colab.collapsed_sections`
(the `metadata.id` of the corner heading cells, verified against real Colab notebooks) so they
open collapsed in Colab. Two invariants, both tested by executing a copy with every corner
stripped: a corner never defines anything the everyone path uses, and every corner is
self-contained (Run all still works). Mini-task levels: `### 🎯 Mini-task` for everyone,
`**🛠️ Stretch.**` inside corners. When a concept moves, it moves to a corner, never out of
the notebook.

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
  first subprocess (it lives in the third setup cell, section 0.2).
- **GUI tools stay optional.** Robert does not film Inspector; checks in mini-tasks and the
  exercise go through a client cell, with Inspector mentioned as an alternative at most.
- **One cell needs the internet**: the DeepWiki cell in 3.2 (`Client("https://mcp.deepwiki.com/mcp")`),
  wrapped in try/except so Run all survives an outage. After a re-execute, check that its
  output shows the three tools and an answer, not the fallback line.
- **Logging**: set `httpx`, `httpx2` (the SDK's vendored copy) and `openai` loggers to WARNING
  in the key cell, or every HTTP request lands in cell outputs.
- **ADK bridge is shown, not run**: ADK pins `mcp<2`; a 2.x server works with its 1.x client
  (verified 2026-09-12), but the two cannot share one environment.
- **How the notebook is edited.** The notebook file is the source. Larger restructures go
  through a one-off nbformat script that addresses cells by id, validates every anchor before
  writing and refuses to run twice (latest, both 2026-11-19: `training-ops/filming/mcp/merge_1_4_1_5_2026_11_19.py`
  merged videos 1_4 and 1_5 into section 1.4 and added the context-window picture, then
  `highlevel_1_4_2026_11_19.py` put the who-is-who picture on top; before them `restructure_2026_11.py`).
  Vocabulary in 1.4: "the application" = the model + "ordinary software" that contains the client.
  The client is never "software plus model"; "host" is introduced only in 3.1, "harness" is not used.
  Word map (bridged in the text by `terms_bridge_2026_11_19.py`): application (1.4) = host (3.1);
  ordinary software (1.4) = orchestrator / the loop (2.1) + the client; agent (3.2) = a model with a
  loop around it; "Claude Code is a client" in 0.1 and 0.3 is the everyday shortcut, named as such in 1.4.
  The 2026-09-13 builder `training-ops/filming/mcp/build_mcp_course.py` is STALE (it predates the
  2026-09-27 and 2026-11-18 restructures); running it would undo both. After any edit: keep
  cell order = section order, keep corner headings in `colab.collapsed_sections`, re-execute.

## Running and verifying

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt jupyter nbconvert ipykernel
export OPENAI_API_KEY=...            # your own key
jupyter nbconvert --to notebook --execute --inplace MCP_course.ipynb --ExecutePreprocessor.timeout=300
pgrep -fl "servers/.*_server.py"     # must be empty afterwards (no stray servers)
# skip-safety: strip every corner (cells from a collapsed_sections heading to the next H1/H2), execute
# the copy with nbclient and cwd = this folder, expect zero errors (16 code cells on the everyone path,
# 22 in total). Keep the copy OUTSIDE the repo: drive-push uploads everything in this folder.
printf 'Which customers have both open tickets and overdue invoices?\nexit\n' | python client/interactive_client.py
```

After a run, read the outputs against the prose (dump code cells to text); the TKT-9999
recovery demo should show three rounds (details → error → search → details), and the
"escalated" demo in 2.2 should show the invalid-status error followed by an answer that names
the three allowed statuses.

**Colab check** (do it after any change to the setup cells; a local run cannot see these):
Claude can run it through Chrome when Robert is signed in to Google there and has the Colab
secret `OPENAI_API_KEY` (ask him; never type a key). Open the notebook by commit hash
(`.../blob/<sha>/MCP_course.ipynb`; `main` is cached for a few minutes), Run all, and test the
FIRST-RUN path: secret access switched off for the notebook, then wait ~15 s before clicking
"Grant access". On 2026-11-18 that path failed twice (`userdata.get` raises `TimeoutException`
after a few seconds; the fallback `getpass()` then swallowed the dialog's late reply, a dict)
before the key cell got its retry loop. Robert still checks the terminal chat himself.
Since 2026-11-19 the key cell asks for the secret 12 times (`userdata.get` waits 10 s per dialog,
so about two minutes; every attempt stacks one more dialog), re-reads the secret when a late
"Grant access" click lands in the typed-key prompt, and ends with one tiny test request, so a key
that OpenAI rejects fails there with a readable `RuntimeError`. Without that, the failure only
showed in 2.1 as `ExceptionGroup: unhandled errors in a TaskGroup` (the client block wraps
whatever the OpenAI call raises). Verified in Colab: happy path. NOT yet verified in Colab: a
click later than two minutes (the re-read path), and the opened notebook stays granted per
Google account, so switch access off in the Secrets panel to see the dialog at all.
A Colab "Save to Drive" by Robert shows up in drive-push as `CONFLICT drive-newer`; compare
sources cell by cell before deciding (on 2026-11-19 only outputs differed).

## Drive sync

`training-ops/drive-push` course key `mcp`: the WHOLE repo root maps to the Courses drive
folder `6. MCP (SYNCED)/course_materials (shared)` (excluding `recordings/**`; push.py skips
`.venv`, `.git`, `CLAUDE.md`). Run `python3 training-ops/drive-push/push.py --status --course mcp`
before and after touching files. Restructures go through server-side `rclone moveto` (keeps
file IDs), never delete-and-reupload.

## Git

Commit directly to `main` and push. No force-pushes, no `--no-verify`.
