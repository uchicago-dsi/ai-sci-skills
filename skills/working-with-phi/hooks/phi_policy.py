"""What a project protects, and where each path falls: shared by `bin/phi` and the PHI hooks.

A project opts in by writing `.claude/phi.json` at its root:

    {
      "protected": ["/abs/path/to/data", "..."],
      "held": "/abs/path/to/phi/held",
      "released": "/abs/path/to/phi/released",
      "identifier_patterns": {"accession number": "\\bA\\d{8}\\b"},
      "key_columns": ["accession"],
      "max_review_lines": 5000
    }

`protected` lists the data folders. `held` is where every job that touches them
writes its output; the agent may not read it. `released` holds what a person has
read and let through; the agent may read it but not write to it. Without the file
nothing here is active, so the hooks can be installed for every project and stay
silent in the ones that hold no protected data.

Written for Python 3.6, the oldest interpreter a hook may be handed on RHEL 8.
"""

import json
import os
import re

CONFIG_NAME = os.path.join(".claude", "phi.json")
DEFAULT_MAX_REVIEW_LINES = 5000

# Shapes that look like identifiers in free text. Adapted from the CLIF clif-icu
# plugin's hooks/phi_scan.py (https://github.com/Common-Longitudinal-ICU-data-Format/skills).
BUILTIN_PATTERNS = [
    ("record number", r"\bMRN\W{0,3}\d{5,}"),
    ("Social Security number", r"\b\d{3}-\d{2}-\d{4}\b"),
    ("birth date", r"\bDOB\W{0,3}(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})"),
    ("birth date", r"(?:birth\w*|\bdob\b).{0,24}\b(?:19\d{2}|20[0-4]\d)-\d{2}-\d{2}\b"
                   r"|\b(?:19\d{2}|20[0-4]\d)-\d{2}-\d{2}\b.{0,24}(?:birth\w*|\bdob\b)"),
]
BUILTIN_KEY_COLUMNS = ["mrn", "patient_id", "patient_name", "hospitalization_id", "accession",
                       "accession_number", "dob", "birth_date", "ssn"]


class ConfigError(Exception):
    pass


def resolve(path, base=None):
    path = os.path.expanduser(str(path))
    if base and not os.path.isabs(path):
        path = os.path.join(base, path)
    return os.path.realpath(path)


def is_under(path, root):
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def find_config(start=None):
    """The project's config path: $PHI_CONFIG, else the nearest `.claude/phi.json` above `start`."""
    explicit = os.environ.get("PHI_CONFIG")
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    folder = resolve(start or os.getcwd())
    while True:
        candidate = os.path.join(folder, CONFIG_NAME)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


class Policy(object):
    """A loaded `.claude/phi.json`."""

    def __init__(self, path):
        self.path = resolve(path)
        self.project = os.path.dirname(os.path.dirname(self.path))
        with open(self.path, encoding="utf-8") as handle:
            raw = json.load(handle)
        missing = [key for key in ("protected", "held", "released") if not raw.get(key)]
        if missing:
            raise ConfigError("{} is missing {}".format(self.path, ", ".join(missing)))
        for key in ("held", "released"):
            if not os.path.isabs(os.path.expanduser(raw[key])):
                raise ConfigError("{} in {} must be an absolute path".format(key, self.path))
        self.raw_protected = [str(p).rstrip("/") for p in raw["protected"]]
        self.protected = [resolve(p) for p in self.raw_protected]
        self.raw_held = str(raw["held"]).rstrip("/")
        self.held = resolve(raw["held"])
        self.released = resolve(raw["released"])
        if is_under(self.released, self.held) or any(is_under(self.released, p) for p in self.protected):
            raise ConfigError("released must sit outside held and outside every protected folder")
        self.max_review_lines = int(raw.get("max_review_lines", DEFAULT_MAX_REVIEW_LINES))
        self.patterns = [(label, re.compile(rx, re.I)) for label, rx in BUILTIN_PATTERNS]
        for label, rx in sorted((raw.get("identifier_patterns") or {}).items()):
            self.patterns.append((label, re.compile(rx)))
        self.key_columns = BUILTIN_KEY_COLUMNS + [str(c).lower() for c in raw.get("key_columns", [])]

    def hidden_roots(self):
        """(as written, resolved) for every folder the agent may not read."""
        return list(zip(self.raw_protected, self.protected)) + [(self.raw_held, self.held)]

    def classify(self, path, base=None):
        """'hidden', 'released', 'config' or None for an ordinary path."""
        target = resolve(path, base)
        if any(is_under(target, root) for _, root in self.hidden_roots()):
            return "hidden"
        if is_under(target, self.released):
            return "released"
        if target == self.path:
            return "config"
        return None

    def mentioned_roots(self, text):
        """Hidden folders a piece of shell text names, in any spelling it is likely to use."""
        home = os.path.expanduser("~")
        found = []
        for raw, res in self.hidden_roots():
            spellings = {raw, res}
            for spelling in (raw, res):
                if spelling.startswith(home + "/"):
                    spellings.add("~" + spelling[len(home):])
                    spellings.add("$HOME" + spelling[len(home):])
            # A folder is named only when its path ends there or continues with `/`, so that
            # `/data` does not match inside `/data2`.
            if any(s and re.search(re.escape(s) + r"(?![^/\s'\";|&)`])", text) for s in spellings):
                found.append(raw)
        return found

    def flag_lines(self, text):
        """(line number, labels) for each line that looks like it holds an identifier."""
        hits = []
        for number, line in enumerate(text.splitlines(), 1):
            labels = sorted({label for label, rx in self.patterns if rx.search(line)})
            if labels:
                hits.append((number, labels))
        return hits


def load(start=None):
    """The project's Policy, or None when the project has not opted in."""
    path = find_config(start)
    return Policy(path) if path else None
