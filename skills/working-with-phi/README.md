# working-with-phi

Lets a coding agent work on protected health information on a shared cluster
without the data entering its session. The agent writes and submits the code
that reads the data. What comes back is either a numeric summary, released
automatically, or a file a person has read and released.

The usual alternative is to develop on synthetic data and have a person run the
real thing. Here the agent debugs on the real data, through jobs whose output it
can't see. Building a faithful synthetic copy costs about as much as that
debugging.

Claude Code only for now. Claude Code runs checks before and after each agent
action (its hooks); the checks here go through one helper, `hooks/hookio.py`,
so Codex can be added once its sandbox has been checked.

## Parts

| Part | Where | What it does |
| --- | --- | --- |
| The skill | `SKILL.md` | the workflow the agent follows |
| `phi` | `bin/phi` | runs work blind, builds review files, opens them for a person, releases them, checks setup |
| Guard | `hooks/guard_phi.py` | before each tool call, refuses reads of protected or held folders, job logs outside the held area, `srun`/`salloc`/`ssh`, and agent-run releases |
| Output scan | `hooks/phi_output_scan.py` | after a tool call, warns when output looks like it holds an identifier |
| Pasted rows | `hooks/guard_phi_prompt.py` | drops a prompt that looks like pasted data rows before the model sees it |
| Policy | `hooks/phi_policy.py` | reads the project's `.claude/phi.json`; shared by all of the above |
| Layout | `labdisk layout`, in [labdisk](https://github.com/annawoodard/labdisk) | summarizes data folders with every name replaced by its shape |

Everything except `labdisk layout` runs on the system Python 3 (3.6 on RHEL 8)
with no packages. `labdisk layout` needs Python 3.11 or newer; on RHEL 8 that is
`python3.11`, installed beside the system Python.

## Setting up

1. Link `bin/phi` onto your `PATH`, for example
   `ln -s ~/ai-sci-skills/bin/phi ~/.local/bin/phi`, and install labdisk. On
   RHEL 8 `python3.11` comes without pip, so give labdisk an environment of its
   own:

   ```
   python3.11 -m venv ~/.local/share/labdisk-env
   ~/.local/share/labdisk-env/bin/pip install git+https://github.com/annawoodard/labdisk
   ln -s ~/.local/share/labdisk-env/bin/labdisk ~/.local/bin/labdisk
   ```
2. In the project, write `.claude/phi.json`:

   ```json
   {
     "protected": ["/path/to/data", "/path/to/more/data"],
     "held": "/path/outside/the/project/phi/held",
     "released": "/path/outside/the/project/phi/released"
   }
   ```

   Optional fields: `identifier_patterns` (name to regular expression, for a
   site's own accession or study numbers), `key_columns` (extra column names the
   pasted-rows check looks for) and `max_review_lines` (default 5,000).
3. Run `phi settings --write`. It adds three things to
   `.claude/settings.local.json`: the three hooks; rules that deny Claude's file
   tools any read of the protected and held folders; and the operating-system
   sandbox, which stops a command the agent runs directly from opening those
   folders, even one that doesn't name them. Job submission and `phi` run outside
   the sandbox, since their output goes to the held area. The settings file is
   not committed, because it names this cluster's paths. Restart Claude Code in
   the project.
4. Run `phi check`. Every row must pass. On Linux the sandbox is built on two
   system packages: `bubblewrap`, which runs a command inside a restricted view
   of the filesystem, and `socat`, which carries the command's network traffic
   across that boundary. If either is missing, ask the cluster's administrators
   to install it. Until both are there, Claude Code refuses to start in the
   project, which is deliberate: it never runs without the sandbox.

## How a person reviews output

When the agent needs to see what a job printed or saved, it runs `phi collect`
and `phi show`. There are two ways to read the result:

- **In tmux**: `phi show` opens the review file in a new pane beside the
  agent's. The text goes to your terminal; nothing from it comes back to the
  agent. Press `q` to close the pane.
- **Without tmux**: `phi show` prints the file's path. Open it in your own
  terminal or editor, outside the agent's session.

Either way, delete anything that must not reach the agent, save, and run
`phi release <id>` or `phi reject <id> "reason"`. Run it in your own terminal,
or in the agent's session by typing `!` as the very first character of the
prompt (`!phi release <id>`; a space before the `!` sends the line to the agent
as a message instead). Commands typed with `!` skip the hooks that stop the
agent from releasing, and release prints only the id, the line count and the
released path, so nothing from the file enters the conversation.

Release copies the file as you left it into the released area, with a receipt
saying who released it, when, and its checksum. The latest decision stands:
rejecting a review you released earlier removes the released copy. Every
decision is also appended to `decisions.jsonl` beside it, so a withdrawn release
stays on record.

Don't view held files through the agent's prompt. A `!` command's output goes
to the model, so `!less` or `!cat` on a held file sends it there. A message a
hook shows to you alone is no better: it is still written to the session
transcript, which is stored on Anthropic's servers while Remote Control
(following or continuing the session from claude.ai or a phone) is connected.

## Limits

- This setup stops accidents by an agent that is trying to follow the rules.
  An agent working against them could, for example, submit a job that copies
  data into the released area.
- The hooks see each command as typed. A script the agent runs directly, which
  opens a protected folder without naming it on the command line, is stopped
  only by the sandbox.
- The automatic summary holds only numbers, each under a name the job chose. A
  count that is really an identifier would pass; the fixed set of fields makes
  that unlikely, not impossible.
- A blocked prompt can still be stored in the local transcript and prompt
  history.

## Credit

The guard, the output scan and the pasted-rows check are adapted from the CLIF
consortium's clif-icu plugin,
[Common-Longitudinal-ICU-data-Format/skills](https://github.com/Common-Longitudinal-ICU-data-Format/skills)
(`hooks/phi_guard.py`, `hooks/phi_scan.py`), and from the sensitive-data demo
built on it,
[kaveriC/clif-sensitive-data-demo](https://github.com/kaveriC/clif-sensitive-data-demo)
(`no-row-dumps.py`, `no-pasted-rows.py`, `phi-scan.py`).
