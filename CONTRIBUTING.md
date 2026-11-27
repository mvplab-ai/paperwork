# Contributing

Thank you for helping. The most useful contributions are reports of bad answers and tests
in assistants we have not tried.

## Reporting a bad answer

[Open an issue](https://github.com/mvplab-ai/paperwork/issues) with:

- which assistant you used and how you installed the skill
- what you asked
- what it answered, and what was wrong

Remove names, addresses and account numbers first. If you can, rewrite the document as an
invented one that shows the same problem.

## Layout of the repository

```
skills/paperwork/SKILL.md      shared rules and the table that picks a job
skills/paperwork/jobs/*.md     one file per job
scripts/check_structure.py     static checks (frontmatter, size, no vendor-specific terms)
scripts/build.py               writes dist/paperwork.zip and dist/paperwork-paste-in.txt
tests/docs/                    invented documents; no real people or companies
tests/cases.json               what each reply must and must not contain
tests/selfcheck.json           known-wrong replies the grader must reject
tests/run.py                   runs the cases through a headless agent and grades them
tests/MANUAL.md                the hand check before each release, and known issues
demo/                          source of the README demo (a HyperFrames project)
site/                          the landing page, deployed to GitHub Pages on every push
docs/superpowers/              the original design and build plan
```

The skill folder is the only source. `dist/` is generated; never edit it.

## Rules for the skill text

- Nothing vendor-specific: no product names, tool names or app menus. `check_structure.py`
  enforces a list.
- Frontmatter has `name` and `description` only.
- Write for the reader of the answer: a busy, possibly worried person who is not an expert.
- Every test document is invented.

## Changing the skill

Work test-first. A change to behaviour starts with a case that fails.

1. Add or change a case in `tests/cases.json`. If you are fixing a bad answer, also add that
   answer to `tests/selfcheck.json` so the grader is proven to reject it.
2. Run it and watch it fail.
3. Change the skill.
4. Run everything:

```
python3 scripts/build.py
python3 tests/run.py --selfcheck         # the grader must reject every known-wrong reply
python3 tests/run.py --agent claude      # skill installed in Claude Code
python3 tests/run.py --agent codex       # skill installed in Codex
python3 tests/run.py --agent paste       # no skill; the paste-in file only
```

Useful extras:

```
python3 tests/run.py --agent claude --case E2 --case F3   # some cases only
python3 tests/run.py --agent claude --no-skill            # what the agent does unaided
python3 tests/run.py --agent claude --no-judge            # pattern checks only, faster
```

Everything is Python 3 standard library. The runner needs the `claude` and `codex` command
line tools installed and signed in, and each run uses your own accounts. Replies are saved
to `tests/out/`.

When a case fails, read the saved reply before changing anything. Decide whether the skill
is wrong or the check is too narrow for a correct reply. Never loosen a check to pass a
reply that is wrong.

## How replies are graded

Twice: pattern checks for hard facts (amounts, dates, length), then a model that reads the
reply against the plain-English `must` and `must_not` lists in the case. Agents overshoot a
stated word limit by about 40%, so the limits in the job files are the numbers that steer
and the table in `run.py` holds the numbers that fail.

## Releasing

1. All three agents green, or every failure listed under known issues in `tests/MANUAL.md`.
2. Run the hand checklist in `tests/MANUAL.md`.
3. `python3 scripts/build.py`, then attach both files in `dist/` to the release.
4. Update the results table in `docs/how-it-works.md` and the limits in `README.md`.

## The demo

`demo/` is a HyperFrames project. After editing `demo/compositions/demo.html`:

```
cd demo
npx hyperframes check
npx hyperframes render
ffmpeg -i renders/<file>.mp4 -vf "fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse" ../assets/demo.gif
```

Keep the demo truthful: the answer shown must be one the skill really gave.
