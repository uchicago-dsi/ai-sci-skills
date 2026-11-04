# Installing ai-sci-skills

These steps are written for a coding agent installing the skills for the person
it works with. Do them in order. Before any step marked **Ask**, say what you
are about to change and wait for a yes. When you finish, report what you
installed, where, and what you skipped.

## 1. Find your skills directory

Work out which agent you are and where you read skills from. If you are not
sure, ask.

| Agent | Every project (default) | One project only |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.codex/skills/` | `.codex/skills/` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |

Install for every project unless the person asks for one.

## 2. Get the repository

If you are not already reading a clone, clone it where the person keeps
software, by default `~/ai-sci-skills`:

```bash
git clone https://github.com/uchicago-dsi/ai-sci-skills.git ~/ai-sci-skills
```

## 3. Link the skills

Symlink each skill folder into the skills directory, so `git pull` in the clone
updates them. Copy instead only if the person wants a fixed snapshot. Install
every skill unless the person names a subset. Do not overwrite an existing entry
of the same name that points elsewhere; report it instead.

```bash
SKILLS_DIR=~/.claude/skills   # from step 1
mkdir -p "$SKILLS_DIR"
for d in ~/ai-sci-skills/skills/*/; do
  name=$(basename "$d")
  [ -e "$SKILLS_DIR/$name" ] || ln -s "${d%/}" "$SKILLS_DIR/$name"
done
```

## 4. Link the commands

Link each file in `bin/` into a directory on the person's `PATH`, by default
`~/.local/bin`. If that directory is not on `PATH`, tell the person the line to
add to their shell profile; do not edit the profile yourself unless they say so.

```bash
mkdir -p ~/.local/bin
for f in ~/ai-sci-skills/bin/*; do
  [ -e ~/.local/bin/"$(basename "$f")" ] || ln -s "$f" ~/.local/bin/
done
```

The commands need only `bash` and the system `python3` (3.6 or newer).

## 5. Finish the setup of skills that need it

Most skills need nothing more. For these, do what is listed, and only for skills
you installed:

| Skill | What it needs |
| --- | --- |
| `run-provenance` | `agent-scratch` needs `AGENT_SCRATCH_BASE`, the person's scratch directory, exported in their shell profile. **Ask** for the directory and before editing the profile. On a Slurm cluster, also **ask** before adding the nightly cleanup to their `scrontab`: `17 3 * * * $HOME/.local/bin/agent-scratch sweep --days 14`, with `#SCRON --time=00:30:00 --mem=1G` above it. |
| `agentcomm` | Install the `agentcomm` command as `skills/agentcomm/SKILL.md` describes under "Where It Lives". **Ask** first; it installs an npm package. |
| `quota-saving-mode` | Nothing for Claude Code. Codex uses `await-notify` from step 4. |
| `claude-code-worker` | Only useful when you are not Claude Code: it lets another agent hand work to Claude Code. Needs the `claude` command installed and logged in; if it is missing, tell the person. |
| `working-with-phi` | Needs `labdisk`; install it as `skills/working-with-phi/README.md` describes. Setting up a project comes later, when the person asks. |
| `slurm` | Nothing now. On first use in a project it writes the cluster's facts to `docs/slurm-site.md`. |

Do not install anything from `hooks/` unless the person asks. Several hooks are
written for one project and need editing first; `hooks/README.md` explains.

## 6. Restart

Tell the person to restart their agent session so it loads the new skills.

## Updating

`git -C ~/ai-sci-skills pull` updates linked skills and commands in place.
Then repeat step 3 and step 4 to link any new skill or command.
