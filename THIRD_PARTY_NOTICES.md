# Third-party notices

Parts of this repository adapt work from other projects. See each project for
its license.

- **`skills/humanize`** and **`agents/humanize-auditor.md`** are adapted from
  Pedro H. C. Sant'Anna's `humanize` skill in
  [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow),
  at commit `9d371f0bf8a8bc99569feca3210ef5133af28d33`.
- **`skills/working-with-phi`**, **`hooks/guard_phi.py`**,
  **`hooks/phi_output_scan.py`** and **`hooks/guard_phi_prompt.py`** adapt the
  PHI guard and output scan from the CLIF consortium's clif-icu plugin,
  [Common-Longitudinal-ICU-data-Format/skills](https://github.com/Common-Longitudinal-ICU-data-Format/skills)
  (`hooks/phi_guard.py`, `hooks/phi_scan.py`), and the guards in the
  sensitive-data demo built on it,
  [kaveriC/clif-sensitive-data-demo](https://github.com/kaveriC/clif-sensitive-data-demo)
  (`no-row-dumps.py`, `no-pasted-rows.py`, `phi-scan.py`).
