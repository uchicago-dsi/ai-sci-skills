# working-with-phi

Lets a coding agent work on protected health information, on a Slurm cluster or
on a single machine, without the data entering its session. The agent writes and submits the code
that reads the data. What comes back is either a numeric summary, released
automatically, or a file you have read and released.

The usual alternative is to develop on synthetic data and have a person run the
real thing. That means building the synthetic data, debugging the code on it,
and then debugging it again on the real data, which may behave differently.
Here there is one round: the agent debugs on the real data, through jobs whose
output it sees only after you have read it and released it, apart from a short
numeric summary of each job.

Claude Code only for now.

## How it works

Three places on disk matter:

| Place | What is there | Can the agent read it? |
| --- | --- | --- |
| Protected folders | your data | no |
| Held area | everything a job prints or saves | no |
| Released area | what you have read and let through, plus each job's numeric summary | yes |

The agent writes jobs, submits them, and reads only the released area.
Before each tool call, Claude Code runs a check (a hook) that refuses any
command reading a protected folder or the held area. An operating-system
sandbox also stops any script the agent runs directly from opening them.

## Before you start

You need, once:

- **The skill and its commands.** Installing ai-sci-skills by asking your agent
  to follow the repository's `INSTALL.md` covers this: it installs the skill
  (in Claude Code, as a plugin, which also turns on its hooks), links the `phi`
  command onto your `PATH` for you to run in your own terminal, and installs
  [labdisk](https://github.com/annawoodard/labdisk), which summarizes data
  folders. The plugin on its own:

  ```
  /plugin install working-with-phi --marketplace uchicago-dsi/ai-sci-skills
  ```

  To install labdisk by hand on RHEL 8, where `python3.11` comes without pip:

  ```
  python3.11 -m venv ~/.local/share/labdisk-env
  ~/.local/share/labdisk-env/bin/pip install git+https://github.com/annawoodard/labdisk
  ln -s ~/.local/share/labdisk-env/bin/labdisk ~/.local/bin/labdisk
  ```

- **On Linux, `bubblewrap` and `socat`.** The sandbox is built on these two
  system packages: `bubblewrap` runs a command inside a restricted view of the
  filesystem, and `socat` carries the command's network traffic across that
  boundary. On a cluster they must be on every node where you run Claude Code;
  if either is missing, ask the administrators to install it. On macOS the
  sandbox is built in and needs nothing. Windows needs WSL2.
- **tmux**, optionally. With it, review files open in a pane beside the agent's.

## Step 1: set up the project

Do this once per project.

1. Start Claude Code in the project and tell it where the data is, naming only
   the top-level data folders:

   ```
   Set up working-with-phi for this project. The protected data is in
   /path/to/data and /path/to/more/data.
   ```

   Never paste file or folder names from inside those folders; they may
   identify people.
2. The agent asks where to keep the held and released areas. Pick a place
   outside the project folder that only you can read, for example your scratch
   space. It then writes `.claude/phi.json`, runs `phi settings --write` to add
   the hooks, the sandbox and the read restrictions to
   `.claude/settings.local.json`, and adds a line to the project's `CLAUDE.md`
   saying the project holds protected data.
3. Quit Claude Code and start it again in the project, so the new settings
   apply. If it refuses to start with "sandbox required but unavailable",
   `bubblewrap` or `socat` is missing; it will not run without the sandbox.
4. Ask the agent to run `phi check`. Every row should say `PASS`.

To protect another data folder later, ask the agent; it runs
`phi protect <folder>`, which can only add folders to the list. Then restart
Claude Code. Loosening protection is yours alone: the agent cannot edit
`.claude/phi.json` or run `phi unprotect <folder>`, which takes a folder off the
list, so a refusal can never be worked around by un-protecting something.

## Step 2: give the agent a task

Ask for what you want, for example `Count the exams in each patient folder.`

The first time, the agent doesn't know how the data is laid out, so it first
runs `labdisk layout` on the data folders, as a Slurm job where there is one. That writes a
summary in which every name is replaced by its shape (`9{8}` means eight
digits, `A{5}` five capital letters) and folders with the same shape are merged
into one line. Only names that recur in many folders, such as `DICOM`, appear
as written. When the job finishes, the agent asks you to review the summary,
which is step 3.

## Step 3: review and release

Every time the agent needs to see something a job printed or saved, it builds
one review file and asks you to read it.

1. **Open it.** In tmux, the file opens in a new pane beside the agent's.
   Without tmux, the agent gives you a path; open it in your own terminal or
   editor. Don't open it through the agent (`!less`, `!cat`): a `!` command's
   output goes to the model.
2. **Read all of it.** The top lists the files it contains and any lines that
   look like identifiers (record numbers, Social Security numbers, birth dates,
   and any patterns the project adds); start there.
3. **Cut what must not reach the agent.** Edit the file and save it. In the
   tmux pane, press `v` to open it in your editor.
4. **Release or reject it.** Run one of these in your own terminal, or in the
   agent's session by typing `!` as the very first character of the prompt (a
   space before the `!` sends the line to the agent as a message instead):

   ```
   !phi release layout-001
   !phi reject layout-001 "line 40 prints a folder name"
   ```

   Release copies the file, as you left it, to the released area, where the
   agent can read it. Reject gives the agent your reason and nothing else.
5. **Tell the agent to carry on**, if you released from your own terminal.

## Day to day

- **While a job runs, you do nothing.** On a Slurm cluster the agent submits
  it as a job with its log in the held area; elsewhere it runs it with
  `phi run`, which sends every line of output there.
- **When a job fails, you usually do nothing either.** Each job leaves a
  numeric summary that is released without review: the exit code, line counts,
  any counts the job recorded, and for a Python error the error's type and the
  file and line in the project where it happened. The error's message, which is
  where values appear, stays held. That is usually enough for the agent to fix
  the code.
- **When it needs more, it asks for a review**, and you repeat step 3.

Things to avoid:

- Pasting data, file names or job output into the prompt. A prompt that looks
  like pasted rows is dropped before the agent sees it, but the text can still
  be saved in the session's local history.
- Viewing held files with `!` commands.
- Asking the agent to work around a refusal. Each refusal says what to do
  instead.

## Reference

| Part | Where | What it does |
| --- | --- | --- |
| The skill | `SKILL.md` | the workflow the agent follows |
| `phi` | `bin/phi` | runs work blind, builds review files, opens them for you, releases them, adds protected folders, checks setup |
| Guard | `hooks/guard_phi.py` | before each tool call, refuses reads of protected or held folders, job logs outside the held area, `srun`/`salloc`/`ssh`, and agent-run releases or `phi unprotect` |
| Output scan | `hooks/phi_output_scan.py` | after a tool call, warns when output looks like it holds an identifier |
| Pasted rows | `hooks/guard_phi_prompt.py` | drops a prompt that looks like pasted data rows |
| Policy | `hooks/phi_policy.py` | reads the project's `.claude/phi.json`; shared by all of the above |
| Plugin hooks | `hooks/hooks.json` | turns the three hooks on when the skill is installed as a Claude Code plugin; they do nothing in a project without `.claude/phi.json` |
| Layout | `labdisk layout` | summarizes data folders with every name replaced by its shape |

`.claude/phi.json` has three required fields, `protected` (a list of folders),
`held` and `released`. Optional fields: `identifier_patterns` (name to regular
expression, for a site's own accession or study numbers), `key_columns` (extra
column names the pasted-rows check looks for) and `max_review_lines` (default
5,000).

Each job gets a folder, `<id>`, in both areas. In the released area, `receipt.json`
records who released the review, when, and its checksum, and `decisions.jsonl`
lists every release and rejection in order. The latest decision stands:
rejecting a review you released earlier removes the released copy, though the
agent may already have read it.

Everything except `labdisk layout` runs on the system Python 3 (3.6 on RHEL 8)
with no packages. `labdisk layout` needs Python 3.11 or newer.

## Limits

- This setup stops accidents by an agent that is trying to follow the rules.
  An agent working against them could, for example, submit a job that copies
  data into the released area.
- Slurm is the only scheduler it checks. Jobs submitted to another scheduler
  (PBS `qsub`, LSF `bsub`) write their logs wherever their own options say.
- The hooks see each command as typed. A script the agent runs directly, which
  opens a protected folder without naming it on the command line, is stopped
  only by the sandbox.
- The automatic summary holds only numbers, each under a name the job chose. A
  count that is really an identifier would pass; the fixed set of fields makes
  that unlikely, not impossible.
- A message a hook shows to you alone is still written to the session
  transcript, which is stored on Anthropic's servers while Remote Control
  (following or continuing the session from claude.ai or a phone) is
  connected. Nothing here routes protected data through such messages.

## Credit

The guard, the output scan and the pasted-rows check are adapted from the CLIF
consortium's clif-icu plugin,
[Common-Longitudinal-ICU-data-Format/skills](https://github.com/Common-Longitudinal-ICU-data-Format/skills)
(`hooks/phi_guard.py`, `hooks/phi_scan.py`), and from the sensitive-data demo
built on it,
[kaveriC/clif-sensitive-data-demo](https://github.com/kaveriC/clif-sensitive-data-demo)
(`no-row-dumps.py`, `no-pasted-rows.py`, `phi-scan.py`).
