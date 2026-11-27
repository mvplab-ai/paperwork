# Paperwork: a free skill for everyday documents

Design, 2026-11-26. Status: approved 2026-11-26; built. Known issues are in tests/MANUAL.md.

Working name is "paperwork". The public name is undecided (the owner said
names come later). "istack" was floated; "dstack" clashes with an existing
well-known project.

## Intent and why

The owner wants to give away something free that is useful to anyone at
all, in the spirit of public skill packs like gstack, but not for
developers. Almost every skill pack today is written by developers for
developers.

Everyone receives letters, bills, contracts, and forms they do not fully
understand. The stakes are real: missed deadlines, wrong charges paid,
contracts signed unread, scams believed. This skill lets a person hand
over a photo, PDF, or pasted text of a document and get back, in plain
words, what it says, what they must do and by when, what looks wrong, and
a drafted reply.

The user is a non-technical adult: a student, a shop owner, a parent.
Assume they have never opened a terminal and do not know what a skill is.

## Goals

- One install, then it works by plain request ("what is this letter?").
- Works in any agent, not only Claude (owner's requirement): the Claude
  app, coding agents such as Claude Code, Codex, Cursor, and Gemini CLI,
  and, through a paste-in version, any chat assistant at all.
- Easy to install (owner's requirement): each route below is one step.
- No setup, no API keys, no paid services, no accounts.
- Every answer is short, in plain language, in the user's own language.
- Every claim about a document is traceable to the document.
- Honest about what it could not read or does not know.

## Non-goals (v1)

- Sending, filing, or submitting anything on the user's behalf.
- Storing or remembering documents between conversations.
- Preparing tax returns.
- Built-in databases of any country's laws or regulators.
- A website, app, or hosted service.
- A developer pack ("safe to launch" was the runner-up idea and may be a
  later, separate project).

## Anti-goals

The skill has failed, even if it runs, when it:

- States something the document does not say, or guesses an amount, date,
  or name it could not read.
- Tells someone a real deadline can be ignored.
- Buries the answer under disclaimers. One clear line of limits beats a
  paragraph of hedging.
- Lectures, moralises, or talks down.
- Gives confident country-specific legal conclusions it cannot support.

## Constraints

- Must be a standard agent skill in the open format shared across
  agents: a folder with `SKILL.md` (name and description frontmatter)
  plus reference files loaded on demand. Nothing in it may depend on
  one vendor: no Claude-only tool names, no vendor-specific frontmatter
  that other agents reject, no instructions that assume a particular
  app's menus.
- Must run with only what a typical assistant provides: reading images
  and PDFs, and writing text. Web search is used when present and never
  required. Where an agent cannot read images, the skill asks the user
  to paste the text.
- No scripts are required to run it. (Scripts may exist in the repo for
  building and testing only.)
- Documents contain personal data. The skill never sends the user's
  personal details or the document's content to any outside service
  (the one narrow allowance for web search is under shared rules),
  never repeats full ID or account numbers back unless
  needed in a drafted letter, and tells users once that they may cover
  such numbers before sharing.
- All test and example documents are invented. No real people,
  companies, or account details.

## Approaches considered

1. **One skill, six jobs inside (chosen).** A single `SKILL.md` that
   recognises which job is being asked for and loads that job's
   reference file. One install. Trade-off: the description has to cover
   all six triggers, and the main file must stay short so it routes
   well.
2. **Six separate skills.** Each simpler and more precisely triggered,
   each testable alone. Trade-off: six installs for a person who has
   never installed one. Rejected for this audience; right for a
   developer pack.
3. **Website or app.** Rejected: the owner wants a skills pack, and it
   would need hosting, accounts, and handling of personal documents.

The owner handed the how to the designer; choice 1 is the designer's
call, made because install friction is the main thing standing between
this audience and any use at all.

## The six jobs

Each job is one reference file. Names below are working names.

| Job | The person says | They get |
|---|---|---|
| explain | "What is this?" | What it is, who sent it, what they want, by when, what happens if ignored, what to do next, and whether it looks genuine |
| check-bill | "Is this bill right?" | Line by line: what each charge is, anything duplicated, unexplained, or changed from before, and the questions to ask the sender |
| fight | "This charge or decision is wrong" | The strongest honest case, what proof to gather, a drafted letter, who to send it to, and when to follow up or escalate |
| before-i-sign | "Should I sign this?" | What they are agreeing to, what it costs in total, how to get out, the unusual or one-sided terms, and questions to ask first |
| fill-form | "Help me fill this in" | Each field explained in plain words, what to put given what they have told it, and what documents to have ready |
| sort-pile | "I have a stack of these" | Every document in one list, ordered by urgency, with the one action each needs |

"Looks genuine" in explain is scam checking: mismatched sender details,
pressure to act immediately, unusual payment methods, requests for
passwords or codes. It reports signs, never a verdict of "safe".

### What an answer looks like

For explain, roughly:

```
WHAT THIS IS
A final reminder from Northfield Water for an unpaid bill.

WHAT THEY WANT
£84.20, for March to May.

BY WHEN
14 December. The letter says a £15 late fee is added after that.

IF YOU DO NOTHING
They say they will pass it to a collection agency.

WHAT I'D DO
1. Check whether you already paid: the letter is dated 2 days
   after your stated payment date.
2. If you paid, reply with proof. I can draft that.

NOT SURE ABOUT
The account number in the photo is cut off. I could not read it.
```

Other jobs follow the same pattern: short labelled blocks, actions
numbered, a closing block for what was unreadable or uncertain. That
closing block is omitted only when there is truly nothing to put in it.

## Rules shared by every job

These live in the main `SKILL.md` so they apply whichever job loads.

- **Only what the document says.** Quote or point to the line for each
  key fact. Dates and amounts are copied exactly. Unreadable means say
  unreadable.
- **Plain words.** Short sentences. Explain any term the document
  forces on the reader. Reply in the language the user writes in, even
  when the document is in another.
- **Country.** Do not assume one. Work it out from the document
  (currency, addresses, named bodies) and say which was assumed. If it
  cannot be worked out and it matters, ask. Rules that vary by country
  are stated as "this varies; in many places…" unless web search can
  confirm the specific rule, in which case give the source.
- **When to send them to a professional.** For court papers, eviction,
  immigration, criminal matters, debt already in court, and anything
  where the next step is a medical decision: still explain the document
  plainly and state the deadline, then say clearly that this needs a
  qualified person and suggest the kind to look for (for example, free
  legal aid). One or two sentences, placed after the explanation, never
  instead of it.
  What the jobs still do in these categories (designer's call): explain
  explains in full; sort-pile lists and ranks it; fill-form explains
  what each field is asking but does not advise what to answer; fight
  and before-i-sign do not argue the case or draft the substantive
  response. The only letters drafted here are ones that cannot hurt the
  person: asking for more time, asking for a copy of the papers, or
  asking a legal aid body for help.
- **Tax forms** (designer's call). fill-form explains each field and
  what documents are needed. It does not work out figures or advise
  what to claim, and says so in one line.
- **Web search and privacy** (designer's call). When search is present,
  a query may contain only public details of an organisation: its name,
  and a phone number, address, or payment detail printed on the document
  as the organisation's own. It never contains the user's name,
  address, account or ID numbers, or passages from the document. This
  is what makes "is this sender real" checkable without leaking the
  person's data.
- **Deadlines win.** If a document has a deadline, it appears near the
  top of every answer, whatever was asked.
- **Privacy.** As under Constraints.
- **Drafts are drafts.** Letters are written for the user to read,
  correct, and send themselves, with blanks marked where facts are
  missing. Never invent a fact to strengthen a case.

## What ships

- The skill folder: `SKILL.md` plus one reference file per job. This is
  the single source; everything else below is generated from it.
- Three install routes, each one step (designer's call on the routes):
  1. **One command** for coding agents: the cross-agent skills
     installer (`npx skills add <owner>/<repo>`), which places the skill
     in whichever agent the person uses. A Claude Code plugin manifest
     is included as well.
  2. **One file to upload** for app users: a zip of the skill, attached
     to each release.
  3. **One file to paste** for everything else: a single generated
     text file holding the shared rules and all six jobs, pasted as
     the first message (or into a project's instructions) in any chat
     assistant that has no skill support. It is not required to fit
     small custom-instruction fields, so job files carry no size
     budget (designer's call).
- If the docs show the app route needs a paid plan or more than one
  step, the README says so plainly and leads with whichever route is
  free and one step for a non-technical person, most likely the
  paste-in file (designer's call).
- A README written for non-technical people: what it does, the three
  routes with the app route shown in screenshots, five example requests.
- Invented sample documents and the test cases built on them.
- MIT licence.

## Testing

For each job, at least three invented documents (including one poor
photo and one non-English document across the set) with a written list
of facts the answer must contain and facts it must not claim. Cases must
include: a scam letter, a document with a deadline the request did not
ask about, a court-type document that should trigger the professional
referral, and a bill with a planted duplicate charge. A change ships
only when all cases pass.

Because it must work in any agent, testing has two layers (designer's
call):

- **Automated, on every change:** all cases run headless in two coding
  agents from different vendors. Claude Code and the Codex CLI are both
  already on the owner's machine.
- **By hand, once per release:** a short checklist of one case per job,
  run through the app upload route and through the paste-in file in a
  free chat assistant from another vendor. The README screenshots are
  taken during this pass.

## Left to the builder

- Final wording of the skill description and each job file.
- Exact block labels per job, within the pattern above.
- Repo layout, build script for the zip, and test runner.
- Confirming, from official docs, the current way skills are added in
  the Claude app, the current plugin manifest format, the cross-agent
  installer's expected repo layout, and which frontmatter fields are
  safe across agents, before writing the README and manifests.
- Whether web search, when present, is used by default or only on
  request (designer's lean: use it for naming the right regulator or
  complaint body, always with the link).

## Open, for the owner

- Public name. This blocks the release, not the build: it is built as
  "paperwork" and renamed in one step before first publishing.
- Where the repo is published and under whose account.
