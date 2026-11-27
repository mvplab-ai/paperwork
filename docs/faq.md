# Questions people ask

## Is it really free?

Yes. The skill is free and open source under the MIT licence. You still need an AI
assistant to run it in, and that assistant may be free or paid.

## Which assistants does it work with?

It is plain text written to work in any assistant that can read your document. It has been
tested in Claude (as an installed skill and as pasted text) and in Codex. Others should work
through the paste-in file but have not been tested yet. If you try one, please
[tell us how it went](https://github.com/mvplab-ai/paperwork/issues).

## Do I have to install anything?

No. Copy the [paste-in file](https://github.com/mvplab-ai/paperwork/releases/latest/download/paperwork-paste-in.txt)
into a new chat and start. Installing is only a convenience so you don't paste it each time.

## How do I share a document?

Take a clear photo, attach a PDF, or paste the text. If your assistant can't read images,
paste the text. Cover account and ID numbers first if you can.

## Can I trust the answer?

Treat it as a careful friend's reading, not as professional advice. The skill is built to
copy facts exactly, to say when it can't read something, and never to guess. Even so, check
every date and amount against the paper in your hand before you act.

## Why won't it write my court defence?

Because a wrong word in court papers can cost you the case, and free qualified help exists
for exactly this. It will explain the paper, give you the deadline, and tell you what kind
of adviser to look for. It can write a letter asking for more time or for help, and it will
tell you that such a letter does not move the deadline.

One known gap: in Codex this limit does not hold. See the
[known limits](../README.md#known-limits-read-before-you-rely-on-it).

## Why won't it tell me what to put on my tax form or visa form?

It explains what each box or question is asking. Working out a tax figure, or choosing your
answer on an immigration form, is advice with real consequences if it is wrong. It points
you to an accountant, the tax office, or a registered immigration adviser.

## It said a letter looks like a scam. Is it sure?

No, and it can't be: it has only seen a picture of the letter. It reports warning signs,
such as payment by gift card or a request for a password. Check with the real organisation
using a phone number or website you find yourself, never one printed on the letter.

It also can't confirm a letter is genuine. If it finds no warning signs, that is all it
can say.

## Does it work in my language?

It replies in the language you write in, even when the document is in another language.
The tests cover a Spanish bill with questions in English. Other pairs are untested.

## Does it work for my country?

It does not assume a country. It works one out from the document and tells you which it
assumed. It does not state your country's law unless it looked it up and can show you the
page. For anything that depends on local rules, it tells you who can say.

## What does it do with my documents?

Nothing of its own. The skill has no server and stores nothing. Your assistant's provider
sees what you share, as with anything else you send it.

## I found a bad answer. What should I do?

Please [open an issue](https://github.com/mvplab-ai/paperwork/issues) with the request you
made and what was wrong. Remove personal details first. Bad answers become test cases, so
each report makes the skill safer.
