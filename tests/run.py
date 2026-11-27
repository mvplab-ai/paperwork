#!/usr/bin/env python3
"""Run the paperwork test cases through a headless agent and grade the replies.

    python3 tests/run.py --agent claude            # skill installed as a project skill
    python3 tests/run.py --agent codex             # same, in a second vendor's agent
    python3 tests/run.py --agent paste             # no skill; the paste-in file is the prompt
    python3 tests/run.py --agent claude --case E1 --case B2
    python3 tests/run.py --agent claude --no-skill # baseline: what the agent does unaided

Working invocations (recorded so the next person does not have to rediscover them):

  claude: prompt on stdin, cwd = temp project holding .claude/skills/paperwork
      claude -p --setting-sources project --strict-mcp-config --no-chrome
             --no-session-persistence --allowedTools Read Glob Skill
      --setting-sources project keeps the owner's personal settings, hooks and plugins
      out of the run.

  codex: prompt on stdin, cwd = temp project holding .agents/skills/paperwork
      codex exec -s read-only --skip-git-repo-check -C <dir> -o <reply file> -

  paste: claude with every tool and skill switched off, in an empty directory;
      the paste-in file and the document text are the whole prompt. This stands in
      for a plain chat assistant with no skill support.

Replies are saved to tests/out/<agent>/<case id>.txt. Exit status 1 if any case fails.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "paperwork"
DOCS = ROOT / "tests" / "docs"
PASTE_FILE = ROOT / "dist" / "paperwork-paste-in.txt"
TODAY = "Today is 26 November 2026."
TIMEOUT = 300
# "Every answer is short": word ceilings per job. These sit about 40% above the limits the
# job files state, on purpose: agents overshoot a stated limit by roughly that much, so the
# job files carry the number that steers and this table carries the number that fails. fight and fill-form carry a drafted
# letter or a field-by-field walk, so they get more room.
MAX_WORDS = {"explain": 300, "check-bill": 300, "sort-pile": 260,
             "before-i-sign": 450, "fill-form": 450, "fight": 480}
# The person never asked about the skill. No reply may point at its files or quote its rules.
ALWAYS_NONE = [r"/var/folders/|/private/|\.agents/|\.txt\)", r"^\|.+\|\s*$", r"my instructions|the guide (says|tells|requires)", r"paperwork skill", r"SKILL\.md", r"jobs/[a-z-]+\.md", r"the skill (says|tells|requires|instructs)"]
EARLY_WINDOW = 90  # "Deadlines win": the deadline must appear within this many words
MONTHS = ("January February March April May June July August September "
          "October November December").split()


def date_regex(text):
    """'14 December' -> a regex matching 14 December, 14th of Dec, December 14th, Dec 14."""
    day, month = text.split()
    assert month in MONTHS, month
    mon = f"{month[:3]}(?:{month[3:]})?" if len(month) > 3 else month
    suffix = "(?:st|nd|rd|th)?"
    return (rf"(?<!\d){day}{suffix}(?: of)? {mon}\b"
            rf"|\b{mon}\.? {day}{suffix}(?!\d)")


def grade(case, reply):
    """Return a list of failure strings; empty means pass."""
    fails = []
    flags = re.I | re.M
    # Agents differ in typography; grade the words, not the quote style.
    reply = reply.translate(str.maketrans("\u2018\u2019\u201c\u201d", "''\"\""))
    for pattern in ALWAYS_NONE:
        m = re.search(pattern, reply, flags)
        if m:
            fails.append(f"forbidden everywhere: {pattern!r} matched {m.group(0)!r}")
    if not reply.strip():
        return ["empty reply"]
    for pattern in case.get("all", []):
        if not re.search(pattern, reply, flags):
            fails.append(f"missing: {pattern}")
    for pattern in case.get("none", []):
        m = re.search(pattern, reply, flags)
        if m:
            fails.append(f"forbidden: {pattern!r} matched {m.group(0)!r}")
    # Stating a country's law is allowed only when it was looked up and the page is given.
    if not re.search(r"https?://", reply):
        for pattern in case.get("none_unless_sourced", []):
            m = re.search(pattern, reply, flags)
            if m:
                fails.append(f"unsourced: {pattern!r} matched {m.group(0)!r}")
    for d in case.get("dates", []):
        if not re.search(date_regex(d), reply, flags):
            fails.append(f"missing date: {d}")
    words = len(reply.split())
    limit = case.get("max_words", MAX_WORDS[case["job"]])
    if words > limit:
        fails.append(f"too long: {words} words, limit {limit}")
    opening = " ".join(reply.split()[:EARLY_WINDOW])
    for d in case.get("early_dates", []):
        if not re.search(date_regex(d), opening, flags):
            fails.append(f"deadline {d} not in the first {EARLY_WINDOW} words")
    last, last_name = -1, None
    for d in case.get("date_order", []):
        m = re.search(date_regex(d), reply, flags)
        if not m:
            fails.append(f"missing date: {d}")
            continue
        if m.start() < last:
            fails.append(f"out of order: {d} appears before {last_name}")
        last, last_name = m.start(), d
    return fails


# Criteria checked on every reply, whatever the case.
ALWAYS_MUST_NOT = [
    "States a specific amount, date, time, name or reference number as a fact about this "
    "document or its sender that is not in the documents and is not simple arithmetic on "
    "figures in them.",
    "Mentions the assistant's own instructions, guide, skill or rules, or shows a file path "
    "or a link to a local file.",
]

JUDGE_PROMPT = """You are checking an assistant's reply to a member of the public who shared \
a document. Judge only what the reply says. Be strict and literal.

=== DOCUMENTS THE PERSON SHARED ===
{docs}

=== WHAT THE PERSON ASKED ===
{request}

=== THE ASSISTANT'S REPLY ===
{reply}

=== STATEMENTS ===
{statements}

For each numbered statement, decide whether it is TRUE of the reply. Answer with one JSON \
object and nothing else, mapping each number to true or false, for example {{"1": true, "2": false}}."""


def judge(case, reply):
    """Ask a model whether each plain-English criterion holds. Returns failure strings."""
    criteria = ([("must", s) for s in case.get("must", [])]
                + [("must_not", s) for s in case.get("must_not", [])]
                + [("must_not", s) for s in ALWAYS_MUST_NOT])
    docs = "\n\n".join(f"[{n}]\n{(DOCS / n).read_text(encoding='utf-8')}" for n in case["docs"])
    statements = "\n".join(f"{i}. {s}" for i, (_, s) in enumerate(criteria, 1))
    prompt = JUDGE_PROMPT.format(docs=docs, request=f"{TODAY} {case['request']}",
                                 reply=reply, statements=statements)
    work = Path(tempfile.mkdtemp(prefix="paperwork-judge-"))
    try:
        cmd = ["claude", "-p", "--setting-sources", "project", "--strict-mcp-config",
               "--no-chrome", "--no-session-persistence", "--disable-slash-commands",
               "--tools", ""]
        try:
            proc = subprocess.run(cmd, input=prompt, text=True, capture_output=True,
                                  cwd=work, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return ["judge timed out"]
    finally:
        shutil.rmtree(work, ignore_errors=True)
    m = re.search(r"\{.*\}", proc.stdout, re.S)
    try:
        verdict = json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        verdict = None
    if not isinstance(verdict, dict):
        return [f"judge gave no verdict: {proc.stdout.strip()[:200] or proc.stderr.strip()[:200]}"]
    fails = []
    for i, (kind, statement) in enumerate(criteria, 1):
        value = verdict.get(str(i))
        if value is None:
            fails.append(f"judge skipped: {statement}")
        elif kind == "must" and value is not True:
            fails.append(f"judge, should be true: {statement}")
        elif kind == "must_not" and value is not False:
            fails.append(f"judge, should be false: {statement}")
    return fails


def grade_full(case, reply, use_judge=True):
    """Pattern checks for hard facts, then the judge for what patterns cannot tell."""
    fails = grade(case, reply)
    if use_judge and reply.strip():
        fails += judge(case, reply)
    return fails


def build_prompt(case, inline):
    if inline:
        # What a real person does: types the question and pastes the text underneath.
        docs = "\n\n\n".join((DOCS / name).read_text(encoding="utf-8") for name in case["docs"])
        return f"{TODAY} {case['request']}\n\n{docs}\n"
    listing = "\n".join(f"- documents/{name}" for name in case["docs"])
    noun = "document is" if len(case["docs"]) == 1 else "documents are"
    return (f"{TODAY}\n\n{case['request']}\n\n"
            f"The {noun} in this folder:\n{listing}\n")


def run_case(case, agent, use_skill, use_judge=True):
    work = Path(tempfile.mkdtemp(prefix=f"paperwork-{agent}-{case['id']}-"))
    try:
        if agent in ("claude", "codex"):
            (work / "documents").mkdir()
            for name in case["docs"]:
                shutil.copy(DOCS / name, work / "documents" / name)
        if agent == "claude":
            if use_skill:
                shutil.copytree(SKILL, work / ".claude" / "skills" / "paperwork")
            cmd = ["claude", "-p", "--setting-sources", "project", "--strict-mcp-config",
                   "--no-chrome", "--no-session-persistence",
                   "--allowedTools", "Read", "Glob", "Skill"]
            prompt = build_prompt(case, inline=False)
        elif agent == "codex":
            if use_skill:
                shutil.copytree(SKILL, work / ".agents" / "skills" / "paperwork")
            reply_file = work / "reply.txt"
            cmd = ["codex", "exec", "-s", "read-only", "--skip-git-repo-check",
                   "-C", str(work), "-o", str(reply_file), "-"]
            prompt = build_prompt(case, inline=False)
        else:  # paste
            cmd = ["claude", "-p", "--setting-sources", "project", "--strict-mcp-config",
                   "--no-chrome", "--no-session-persistence",
                   "--disable-slash-commands", "--tools", ""]
            head = PASTE_FILE.read_text(encoding="utf-8") if use_skill else ""
            prompt = head + "\n\n" + build_prompt(case, inline=True)
        try:
            proc = subprocess.run(cmd, input=prompt, text=True, capture_output=True,
                                  cwd=work, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return case, "", [f"timed out after {TIMEOUT}s"]
        if agent == "codex":
            reply = reply_file.read_text(encoding="utf-8") if reply_file.exists() else ""
        else:
            reply = proc.stdout
        if proc.returncode != 0 and not reply.strip():
            tail = (proc.stderr or proc.stdout).strip()[-400:]
            return case, reply, [f"agent exited {proc.returncode}: {tail}"]
        return case, reply, grade_full(case, reply, use_judge)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--agent", choices=["claude", "codex", "paste"])
    ap.add_argument("--no-judge", action="store_true",
                    help="pattern checks only; skips the model that reads each reply")
    ap.add_argument("--selfcheck", action="store_true",
                    help="test the grader itself: every known-wrong reply must fail")
    ap.add_argument("--case", action="append", help="case id; repeat for several")
    ap.add_argument("--jobs", type=int, default=4, help="cases to run at once")
    ap.add_argument("--no-skill", action="store_true",
                    help="run without the skill, to see the unaided baseline")
    args = ap.parse_args()

    cases = json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))
    if args.selfcheck:
        by_id = {c["id"]: c for c in cases}
        wrong = json.loads((ROOT / "tests" / "selfcheck.json").read_text(encoding="utf-8"))
        with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            results = list(pool.map(lambda w: grade_full(by_id[w["case"]], w["reply"]), wrong))
        missed = 0
        for w, fails in zip(wrong, results):
            missed += not fails
            print(f"{'caught' if fails else 'MISSED'} {w['case']}: {w['why']}")
        print(f"\ngrader catches {len(wrong) - missed}/{len(wrong)} known-wrong replies")
        sys.exit(1 if missed else 0)
    if not args.agent:
        ap.error("--agent is required unless --selfcheck is given")
    if args.case:
        wanted = {c.upper() for c in args.case}
        unknown = wanted - {c["id"] for c in cases}
        if unknown:
            sys.exit(f"unknown case id: {sorted(unknown)}")
        cases = [c for c in cases if c["id"] in wanted]
    if args.agent == "paste" and not args.no_skill and not PASTE_FILE.exists():
        sys.exit(f"{PASTE_FILE.relative_to(ROOT)} not found; run scripts/build.py first")
    if shutil.which("codex" if args.agent == "codex" else "claude") is None:
        sys.exit(f"the {args.agent} command is not installed")

    label = args.agent + ("-baseline" if args.no_skill else "")
    out_dir = ROOT / "tests" / "out" / label
    out_dir.mkdir(parents=True, exist_ok=True)

    failed = 0
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        results = pool.map(lambda c: run_case(c, args.agent, not args.no_skill, not args.no_judge), cases)
        for case, reply, fails in results:
            (out_dir / f"{case['id']}.txt").write_text(reply, encoding="utf-8")
            if fails:
                failed += 1
                print(f"FAIL {case['id']} ({case['job']})")
                for f in fails:
                    print(f"       {f}")
            else:
                print(f"PASS {case['id']} ({case['job']})")
    print(f"\n{label}: {len(cases) - failed}/{len(cases)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
