# Installing ai-sci-skills

These steps are written for a coding agent installing the skills for the person
it works with; a person installing by hand can follow them the same way. Do them
in order. Before any step marked **Ask**, say what you are about to change and
wait for a yes. When you finish, report what you installed, where, and what you
skipped.

Each skill is one folder under `skills/`. Besides its `SKILL.md`, a folder may
hold commands (`bin/`), helper agents for Claude Code (`agents/`) and hooks
(`hooks/`). Installing a skill means installing those too, and nothing from
skills the person did not choose.

## 1. Choose the skills

Install every skill unless the person names some. If they describe what they
want instead ("the writing ones"), propose a list from the README's groups and
confirm it.

## 2. Get the repository

If you are not already reading a clone, clone it where the person keeps
software, by default `~/ai-sci-skills`:

```bash
git clone https://github.com/uchicago-dsi/ai-sci-skills.git ~/ai-sci-skills
```

## 3. Install the skills

**If you are Claude Code**, install each chosen skill as a plugin. A plugin
brings the skill's helper agents, puts its commands on your `PATH`, and turns
on its hooks where the skill says they should be on.

```
claude plugin marketplace add uchicago-dsi/ai-sci-skills
claude plugin install <skill>@ai-sci-skills --scope user
```

Every skill except `claude-code-worker` is a plugin; that one exists for
agents other than Claude Code. A plugin's helper agents carry its name as a
prefix, as in `humanize:humanize-auditor`. Then do step 4 only for commands
the person runs themselves (see the table in step 5), and skip to step 5.

**Otherwise**, find your skills directory and link each chosen skill's folder
into it, so `git pull` in the clone updates them. Copy instead only if the
person wants a fixed snapshot. Do not replace an existing entry that points
elsewhere; report it.

| Agent | Every project (default) | One project only |
| --- | --- | --- |
| Codex | `~/.codex/skills/` | `.codex/skills/` |
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.gemini/skills/` |
| Claude Code, without plugins | `~/.claude/skills/` | `.claude/skills/` |

```bash
SKILLS_DIR=~/.codex/skills    # from the table
SKILLS="slurm sensemaking"    # the chosen skills
mkdir -p "$SKILLS_DIR"
for s in $SKILLS; do
  [ -e "$SKILLS_DIR/$s" ] || ln -s ~/ai-sci-skills/skills/$s "$SKILLS_DIR/$s"
done
```

For Claude Code without plugins, also link each chosen skill's helper agents:

```bash
mkdir -p ~/.claude/agents
for s in $SKILLS; do
  for f in ~/ai-sci-skills/skills/$s/agents/*.md; do
    [ -e "$f" ] && { [ -e ~/.claude/agents/"$(basename "$f")" ] || ln -s "$f" ~/.claude/agents/; }
  done
done
```

## 4. Link the commands

Link each chosen skill's commands into a directory on the person's `PATH`, by
default `~/.local/bin`. If that directory is not on `PATH`, tell the person the
line to add to their shell profile; do not edit the profile yourself unless
they say so.

```bash
mkdir -p ~/.local/bin
for s in $SKILLS; do
  for f in ~/ai-sci-skills/skills/$s/bin/*; do
    [ -e "$f" ] && { [ -e ~/.local/bin/"$(basename "$f")" ] || ln -s "$f" ~/.local/bin/; }
  done
done
```

The commands need only `bash` and the system `python3` (3.6 or newer).

## 5. Finish the setup of skills that need it

Most skills need nothing more. For these, do what is listed, and only for
skills you installed:

| Skill | What it needs |
| --- | --- |
| `run-provenance` | `agent-scratch` needs `AGENT_SCRATCH_BASE`, the person's scratch directory, exported in their shell profile. **Ask** for the directory and before editing the profile. On a Slurm cluster, also **ask** before adding the nightly cleanup to their `scrontab`: `17 3 * * * $HOME/.local/bin/agent-scratch sweep --days 14`, with `#SCRON --time=00:30:00 --mem=1G` above it. That entry runs outside the agent, so link `agent-scratch` as in step 4 even under plugins. |
| `agentcomm` | Install the `agentcomm` command as `skills/agentcomm/SKILL.md` describes under "Where It Lives". **Ask** first; it installs an npm package. |
| `quota-saving-mode` | Nothing for Claude Code. Codex uses `await-notify` from step 4. |
| `claude-code-worker` | Needs the `claude` command installed and logged in; if it is missing, tell the person. |
| `working-with-phi` | Needs `labdisk`; install it as `skills/working-with-phi/README.md` describes. The person runs `phi release` in their own terminal, so link `phi` as in step 4 even under plugins. Setting up a project comes later, when the person asks. |
| `slurm` | Nothing now. On first use in a project it writes the cluster's facts to `docs/slurm-site.md`. Its login-node guard is optional: **ask** before turning it on, as `hooks/README.md` describes. |
| `humanize` | Its US-spelling commit guard is optional: **ask** before turning it on, as `hooks/README.md` describes. |

## 6. Restart

Tell the person to restart their agent session so it loads the new skills.

## Updating

`git -C ~/ai-sci-skills pull` updates linked skills and commands in place. For
plugins, `claude plugin marketplace update ai-sci-skills` and then
`claude plugin update <skill>@ai-sci-skills` for each one. To add a skill later, repeat steps 3
to 5 for it.
