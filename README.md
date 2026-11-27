# Paperwork

A free skill that helps your AI assistant deal with everyday documents: letters, bills,
fines, contracts and forms.

You show it the document. It tells you, in plain words, what the document says, what you
have to do, and by when. It can also check a bill, draft a reply, and sort a pile of post by
what is most urgent.

The skill itself needs no account, no key and no payment. It is written to work with any
assistant that can read your document. It has been tested in Claude Code, in Codex, and as
pasted text in Claude; other assistants should work but have not been tested yet.

## What you can ask

| Say this | You get |
|---|---|
| "What is this?" | What it is, who sent it, what they want, by when, and whether it shows signs of being a scam |
| "Is this bill right?" | Each charge explained, anything charged twice or that doesn't add up, and questions to ask |
| "This is wrong, help me fight it" | Your strongest honest case, what proof to gather, and a letter ready to send |
| "Should I sign this?" | What it really costs, how you get out, and the terms to push back on |
| "Help me fill this in" | Each box explained, and what to put based on what you've told it |
| "I have a pile of these" | One list, most urgent first, with the one thing each needs |

## Install it

Pick the one that matches how you use your assistant. Each is one step.

### 1. I use a chat app and I'm not technical

Download **`paperwork-paste-in.txt`** from the Releases page of this project. Open it, copy
everything, and paste it as your first message in a new chat. Then share your document, or
paste its text.

This needs nothing but a chat box, so it is the route to try in any assistant, free or
paid. You paste it once per conversation. If your
assistant has projects or custom instructions with enough room, you can put it there and
never paste it again.

### 2. My app lets me add skills

Download **`paperwork.zip`** from the Releases page of this project and upload it.

In the Claude app this is under **Customize > Skills > Add > Upload a skill**. Skills there
need code execution switched on in your settings, and whether you have the option can depend
on your plan. If you don't see it, use route 1.

### 3. I use a coding agent

```
npx skills add mvplab-ai/paperwork
```

This installs it into whichever agent you use (Claude Code, Codex, Cursor, Gemini CLI and
others). Add `-g` to install it for all your projects.

In Claude Code you can also add it as a plugin:

```
/plugin marketplace add mvplab-ai/paperwork
/plugin install paperwork@paperwork
```

Or copy the `skills/paperwork` folder into your agent's skills folder by hand.

## Your privacy

- The skill runs inside your assistant. It has no server and collects nothing.
- Your assistant's own provider still sees what you share with it, as with anything else you
  send. Cover account and ID numbers before you share a document if you can.
- If your assistant can search the web, the skill tells it to search only for an
  organisation's public details, such as its name or phone number, and never for your name,
  your numbers, or the text of your document. This is an instruction to the assistant, not a
  technical lock.

## What it won't do

- **It is not a lawyer, an accountant or a doctor.** For court papers, eviction, immigration
  and criminal matters it explains the document and the deadline, then points you to the
  right kind of qualified person. It will not write your legal response.
- **It will not work out your tax figures** or tell you what to claim. It explains the boxes.
- **It will not send anything.** Letters it writes are drafts for you to read, correct and
  send yourself.
- **It can be wrong.** Always check dates and amounts against the document in your hand
  before you act on them.

## For people changing the skill

```
skills/paperwork/SKILL.md      shared rules and the table that picks a job
skills/paperwork/jobs/*.md     one file per job
scripts/check_structure.py     static checks (frontmatter, size, no vendor-specific terms)
scripts/build.py               writes dist/paperwork.zip and dist/paperwork-paste-in.txt
tests/docs/                    invented documents; no real people or companies
tests/cases.json               what each reply must and must not contain
tests/selfcheck.json           known-wrong replies the grader must reject
tests/run.py                   runs the cases through a headless agent and grades them
tests/MANUAL.md                the short hand check to do before each release
```

```
python3 scripts/build.py
python3 tests/run.py --agent claude      # skill installed in Claude Code
python3 tests/run.py --agent codex       # skill installed in Codex
python3 tests/run.py --agent paste       # no skill; the paste-in file only
python3 tests/run.py --agent claude --no-skill   # what the agent does without it
python3 tests/run.py --selfcheck         # checks the grader: wrong replies must fail
```

Each reply is graded twice: patterns for hard facts (amounts, dates, length), then a model
that reads the reply against plain-English safety criteria, such as "contains any part of a
court defence". The second grader exists because patterns alone passed replies that were
clearly wrong. When you find a bad reply, add it to `tests/selfcheck.json` first.

Everything is Python 3 standard library. The runner needs the `claude` and `codex` command
line tools installed and signed in. A change ships only when every case passes in all three.

**Known issues.** See the notes at the end of `tests/MANUAL.md`.

**Before the first public release:** confirm the `npx skills add` route installs the skill from the public
repository (it could not be tried before publishing), run `tests/MANUAL.md`, and add
screenshots of the upload route.

The skill folder is the only source. Never edit the files in `dist/`; rebuild them.

## Licence

MIT. See [LICENSE](LICENSE).
