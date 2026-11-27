#!/usr/bin/env python3
"""Build the two files people download, from the skill folder (the only source).

    dist/paperwork.zip          upload this in an app that takes skill files
    dist/paperwork-paste-in.txt  paste this into any chat assistant with no skill support

Run from anywhere: python3 scripts/build.py
"""
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_structure  # noqa: E402

ROOT = check_structure.ROOT
SKILL_DIR = check_structure.SKILL_DIR
JOBS = check_structure.JOBS
DIST = ROOT / "dist"

PASTE_HEADER = """\
Follow the guide below for the rest of this conversation. When I share a document (a letter,
bill, notice, contract or form) or ask about one, use it to answer. If this message has a
request or a document after the guide, answer that now. If it has nothing after the guide,
reply with only: "Ready. Share a document, or paste its text, and tell me what you need."

"""


def build_zip():
    target = DIST / "paperwork.zip"
    files = [SKILL_DIR / "SKILL.md"] + [SKILL_DIR / "jobs" / f"{j}.md" for j in JOBS]
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, f"paperwork/{f.relative_to(SKILL_DIR).as_posix()}")
    return target, len(files)


def build_paste():
    """One file: the shared rules, then every job as a section of the same text."""
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    _, body = check_structure.parse_frontmatter(text)
    # In the skill, each job is a file to open. Here it is a section further down.
    body = body.replace(
        "then read that job's file before you\nanswer.",
        "then follow that job's section, further down, when you\nanswer.")
    body = body.replace("| Job | Read |", "| Job | Section |")
    body = re.sub(r"`jobs/([a-z-]+)\.md`", r'"Job: \1" below', body)
    body = body.replace("Each job file gives", "Each job section gives")
    body = body.replace("each job file gives", "each job section gives")
    body = body.replace("this guide, its files, its jobs or its rules",
                        "this guide, its sections or its rules")

    parts = [PASTE_HEADER, body.strip(), ""]
    for job in JOBS:
        section = (SKILL_DIR / "jobs" / f"{job}.md").read_text(encoding="utf-8").strip()
        if not section.startswith(f"# Job: {job}"):
            sys.exit(f"jobs/{job}.md must start with '# Job: {job}'")
        parts += ["\n---\n", section, ""]
    whole = "\n".join(parts).rstrip() + "\n"
    # Nothing in the standalone file may still talk about files to open.
    leftovers = re.findall(r"jobs/[a-z-]+\.md|job'?s? file|its files|read that job", whole)
    if leftovers:
        sys.exit(f"paste-in build: file references left over: {sorted(set(leftovers))}")
    target = DIST / "paperwork-paste-in.txt"
    target.write_text(whole, encoding="utf-8")
    return target


def main():
    problems = check_structure.check()
    if problems:
        for p in problems:
            print("FAIL:", p)
        sys.exit("build stopped: fix the skill first")
    DIST.mkdir(exist_ok=True)
    zip_path, count = build_zip()
    paste_path = build_paste()
    print(f"wrote {zip_path.relative_to(ROOT)} ({count} files)")
    words = len(paste_path.read_text(encoding="utf-8").split())
    print(f"wrote {paste_path.relative_to(ROOT)} ({words} words)")


if __name__ == "__main__":
    main()
