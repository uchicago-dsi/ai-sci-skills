---
name: working-with-phi
description: "Work on protected health information (PHI) or other protected data, on a cluster or a single machine, without it ever entering the session: write and submit code that reads the data, get back only a numeric summary or a file a person has read and released. Use in any project with a .claude/phi.json, whenever a task touches patient data, data folders whose names may identify people, or the logs and outputs of jobs that read them, and when setting up a project to do so."
---

# Working with PHI

You write the code that reads protected data and you submit it, but you never see
the data or anything derived from it until a person has read it and let it
through. Two things reach you: where the data is, as a layout summary a person has
released, and what your jobs said, as a numeric summary or a released review file.

The project's `.claude/phi.json` names the protected folders, the held area where
every job's output lands, and the released area you may read. Hooks refuse what
would break this, and say what to do instead; when one refuses, follow its fix
and never reword the command to get past it.

## What you may and may not do

- **Write code that opens protected data.** That is the job. Run it only through
  `phi run`, or on a Slurm cluster as a job with its log in the held area, never
  directly: a script you run yourself prints its
  output, error messages included, straight into this session, and a `KeyError`
  can quote a patient's name.
- **Never read, list or search a protected folder or the held area**, with any tool.
  Do not `ls` a data folder to see what is there; ask for the layout instead.
- **Never use `ssh`, or on a Slurm cluster `srun` or `salloc`,** to run
  anything; they stream output back. Do not submit to other schedulers (PBS
  `qsub`, LSF `bsub`): their logs go where their own options say, which
  nothing here checks.
- **Never name a specific patient, exam or file** in a command, a file name or a
  message. Refer to items by position in a list the job builds ("item 3 of the
  sorted manifest") and let the job resolve the position to a path.
- **Never run `phi release`, `phi reject` or `phi unprotect`.** A person runs
  them. To protect another folder the person names, run `phi protect <folder>`,
  which only adds, and ask them to restart Claude Code.

## Find where the data is

Ask for the layout once per data folder, and again when its layout changes.
`phi new layout` prints a held folder, such as `/…/held/layout-001`. Run the
walk in the background, so a long one does not hold up the session:

```bash
phi run --into /…/held/layout-001 -- labdisk layout --out /…/held/layout-001/layout.txt <data folder>...
```

On a Slurm cluster, submit it as a job instead, because a walk on a shared login
node slows everyone (`labdisk layout` refuses to run there outside a job):

```bash
sbatch --output=/…/held/layout-001/slurm-%j.out <account, partition, time> --cpus-per-task=8 \
  --wrap "phi run --into /…/held/layout-001 -- labdisk layout --out /…/held/layout-001/layout.txt <data folder>..."
```

Write the held path out in full in the `sbatch` line; the hook refuses an
`--output` it cannot resolve, such as `$H/slurm-%j.out`. `labdisk layout`
replaces every name with its shape (`9{8}` is eight digits) and merges siblings,
so a person reviews a few hundred lines. If `labdisk` is not installed, point the
person to the setup steps in this skill's README. Then collect and show the
layout, as below. Once the person releases it, write jobs that find files by the
patterns it shows.

## Run a job

1. `phi new <name>` makes a held folder and prints its path.
2. Run `phi run --into <that folder> -- <command>`, in the background when it
   will take more than a minute or two. On a Slurm cluster, submit it as a job
   instead, with `--output` (and `--error`, if not merged) inside that folder
   and the command wrapped in `phi run --into <that folder> --`.
3. Make the job quiet. It should print counts, shapes, types and timings, never
   values, paths or names. To pass numbers back without review, the job writes a
   flat JSON object of named numbers to the file named by `$PHI_COUNTS`:
   `{"exams_read": 1443, "mean_frames": 6.2}`.

When it finishes, read `<released>/<id>/summary.json` (`summary-<task>.json` for
an array task), which is released without review. It holds the exit code, line and byte counts of standard output and error,
your counts, and for a Python failure the exception type and the file and line in
this project where it was raised, but never the exception's message. That is
usually enough to fix a crash.

## Ask a person to review

When you need what a job printed or saved:

1. `phi collect <id>` gathers the held folder into one review file and prints only
   its path, its length and how many lines look like identifiers. Over the length
   limit it refuses: make the job print less rather than ask a person to read more.
2. `phi show <id>` opens it for the person. In tmux it opens a pane beside yours,
   which shows the file without anything from it coming back to you. Without tmux
   it prints the path for the person to open in their own terminal or editor.
3. Stop and tell the person what you asked for and why. Do not poll.
4. They run `phi release <id>` or `phi reject <id> "reason"`, in their own terminal
   or here as `!phi release <id>` (the `!` must be the first character). Read
   `<released>/<id>/review.txt` or `rejected.json`. They may have cut lines; the
   released file is what you have. The latest decision stands: if a
   review you already read is later rejected, its file disappears, and you stop
   using anything you took from it. `decisions.jsonl` beside it lists every decision.

## Set up a project

When the person asks you to set up a project, they name the top-level data
folders. Until setup is finished nothing guards them, so do not list, search or
open those folders to check them; `phi check` confirms they exist.

1. Ask where the held and released areas should go: outside the project folder,
   readable only by the person, such as their scratch space.
2. Write `.claude/phi.json` with `protected` (the data folders), `held` and
   `released` (see `hooks/phi_policy.py` for the optional fields).
3. Run `phi settings --write`. It adds the hooks, the read-deny rules and the
   sandbox to `.claude/settings.local.json`.
4. Add one line to the project's `CLAUDE.md`: this project holds protected data;
   follow the `working-with-phi` skill.
5. Ask the person to quit and restart Claude Code in the project, then run
   `phi check`. Every row must pass; report any that do not. It reads no data.

## What this does not stop

This setup stops accidents by an agent that follows this skill. An agent working
against it could, for example, submit a job that copies data into the released
area. The sandbox is what stops a script you run directly from reading the data;
until `phi check` shows it enabled, that protection rests on you following the
rules above. The last check is a person reading the file, and a person can miss an identifier.
