"""Find British spellings in text meant for a reader, and name the American form.

Anna writes American English. British forms come back on their own: from
quoted sources, from earlier drafts, from figure labels copied between
scripts, and from agents whose training leans British. Fixing them by hand
each time has not held, so the commit guard refuses on this list. Chat replies
are not checked: British spelling there costs nothing, and a refused reply
costs a full rewrite.

The list is restricted to forms that are almost never correct in American
English. Words both spellings share ("dialogue", "judgement"), and stems
where the British form is also a common American word, are left out: a
guard that fires on legitimate prose gets routed around.

Identifiers are exempt. A run named `..._centre_g121`, a path, a config key
or a function name is a literal, and renaming it breaks whatever points at
it. A match joined to a word character, `_`, a digit, `/` or a dotted name
on either side is treated as part of an identifier and skipped, and so is
anything inside backticks.
"""

import re

# British form (regex, case-insensitive, whole word) -> American form.
# `\w*` endings cover the inflections of a stem in one entry.
PAIRS = [
    (r"colour\w*", "color"),
    (r"centre[ds]?", "center"),
    (r"tumours?", "tumor"),
    (r"neighbour\w*", "neighbor"),
    (r"behaviour\w*", "behavior"),
    (r"favour\w*", "favor"),
    (r"labour\w*", "labor"),
    (r"honour\w*", "honor"),
    (r"(?:cand|hum|rum|vap|harb|flav|od|vig|rig|sav|endeav|arm|parl|clam|splend)our\w*", "-or (candor, rigor, ...)"),
    (r"grey(?:s|ed|ish)?", "gray"),
    (r"(?:mode|labe|trave|cance|signa|fue|leve|tunne|channe|tota)ll(?:ed|ing)", "single l: modeled, labeled, ..."),
    (r"artefacts?", "artifact"),
    (r"analys(?:e|ed|ing)", "analyze"),
    (r"(?:normal|recogn|organ|real|character|optim|minim|maxim|summar|regular"
     r"|parameter|util|standard|visual|initial|random|emphas|categor|prior"
     r"|stabil|general|special|apolog|critic|digit|harmon|local|neutral"
     r"|polar|synthes|homogen)is(?:e|ed|es|ing|ation|ations|er|ers)",
     "-ize / -ization"),
    (r"whilst", "while"),
    (r"amongst", "among"),
    (r"programmes?", "program"),
    (r"(?:milli|centi)?litres?", "liter"),
    (r"(?:milli|centi|kilo)?metres?", "meter"),
    (r"fibres?", "fiber"),
    (r"oedema\w*", "edema"),
    (r"haem\w+", "hem- (hematocrit, hemoglobin)"),
    (r"oestr\w+", "estr- (estrogen)"),
    (r"anaesth\w+", "anesth-"),
    (r"paediatr\w+", "pediatr-"),
    (r"foetal", "fetal"),
    (r"licence", "license"),
    (r"defence", "defense"),
    (r"offence", "offense"),
    (r"ageing", "aging"),
    (r"catalogu(?:e|ed|es|ing)", "catalog"),
    (r"sulph\w+", "sulf-"),
    (r"aluminium", "aluminum"),
    (r"plough\w*", "plow"),
    (r"travell(?:er|ers)", "traveler"),
    (r"enrol(?:s|ment|ments)?", "enroll"),
    (r"fulfil(?:s|ment)?", "fulfill"),
    (r"skilful", "skillful"),
    (r"judgemental", "judgmental"),
]

# Neighbours that make a match part of an identifier, a path or a filename: a
# word character (which includes `_` and digits), a slash, or a dot joined to
# a word character. A sentence-ending period and a prose hyphen don't count.
_BEFORE = r"(?<![\w/])(?<!\w\.)"
_AFTER = r"(?![\w/])(?!\.\w)"
COMPILED = [
    (re.compile(r"%s(%s)%s" % (_BEFORE, british, _AFTER), re.IGNORECASE), american)
    for british, american in PAIRS
]

# matplotlib's colormap names; there is no American spelling to switch to.
_LIBRARY_NAMES = {"greys"}


def strip_code(text):
    """The text with fenced blocks and inline code blanked out, lines kept."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else re.sub(r"`[^`]*`", " ", line))
    return "\n".join(out)


def find(text):
    """[(british word as written, American form)], one entry per distinct word."""
    seen, hits = set(), []
    for pattern, american in COMPILED:
        for match in pattern.finditer(text):
            word = match.group(1)
            if word.lower() in _LIBRARY_NAMES or word.lower() in seen:
                continue
            seen.add(word.lower())
            hits.append((word, american))
    return hits
