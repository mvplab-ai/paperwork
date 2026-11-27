#!/usr/bin/env python3
"""Static checks on the skill folder. Exit 0 when clean, 1 with one line per failure."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "paperwork"
JOBS = ["explain", "check-bill", "fight", "before-i-sign", "fill-form", "sort-pile"]
BANNED = [
    "claude", "anthropic", "codex", "openai", "gemini", "cursor", "chatgpt",
    "WebSearch", "AskUserQuestion",
]
ALLOWED_KEYS = {"name", "description"}
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 200
MIN_JOB_CHARS = 200


def parse_frontmatter(text):
    """Return (dict, body) or (None, text) when there is no frontmatter."""
    m = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.S)
    if not m:
        return None, text
    fields = {}
    key = None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            key = km.group(1)
            fields[key] = km.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] = (fields[key] + " " + line.strip()).strip()
    for k, v in fields.items():
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            fields[k] = v[1:-1]
    return fields, m.group(2)


def check():
    errors = []
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.is_file():
        return [f"missing {skill_md.relative_to(ROOT)}"]

    text = skill_md.read_text(encoding="utf-8")
    fields, _ = parse_frontmatter(text)
    if fields is None:
        errors.append("SKILL.md has no frontmatter")
    else:
        extra = set(fields) - ALLOWED_KEYS
        if extra:
            errors.append(f"frontmatter has extra keys: {sorted(extra)}")
        if fields.get("name") != "paperwork":
            errors.append(f"frontmatter name is {fields.get('name')!r}, expected 'paperwork'")
        desc = fields.get("description", "")
        if not desc:
            errors.append("frontmatter description is empty")
        if len(desc) > MAX_DESCRIPTION:
            errors.append(f"description is {len(desc)} characters, limit {MAX_DESCRIPTION}")

    lines = text.count("\n") + 1
    if lines > MAX_SKILL_LINES:
        errors.append(f"SKILL.md is {lines} lines, limit {MAX_SKILL_LINES}")

    for job in JOBS:
        rel = f"jobs/{job}.md"
        path = SKILL_DIR / rel
        if not path.is_file():
            errors.append(f"missing job file {rel}")
            continue
        if len(path.read_text(encoding="utf-8").strip()) < MIN_JOB_CHARS:
            errors.append(f"job file {rel} is under {MIN_JOB_CHARS} characters")
        if rel not in text:
            errors.append(f"SKILL.md does not mention {rel}")

    for path in sorted(SKILL_DIR.rglob("*")):
        if not path.is_file():
            continue
        body = path.read_text(encoding="utf-8", errors="replace")
        for term in BANNED:
            if re.search(rf"\b{re.escape(term)}\b", body, re.I):
                errors.append(f"{path.relative_to(SKILL_DIR)} contains vendor term {term!r}")
    return errors


if __name__ == "__main__":
    problems = check()
    for p in problems:
        print("FAIL:", p)
    if problems:
        sys.exit(1)
    print("OK: skill structure is clean")
