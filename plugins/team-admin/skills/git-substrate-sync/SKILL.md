---
name: git-substrate-sync
description: Manages all git operations for a team's shared substrate — pulling the latest at session start, committing changes as work happens, pushing to share with colleagues, and handling merge conflicts when two people edit the same content. The goal is to make git invisible when things go well, and clear when they don't. Loads automatically when the team or team-admin plugin is active and any substrate read or write is happening. Also triggers on "save my changes to the team", "pull the latest from the team", "check if anything changed", "did my colleague update this?", "I think there's a conflict", "share my notes with the team", or any time the user is interacting with the shared layer of their substrate.
---

# Git Substrate Sync

## What this skill is for

The team's substrate is a git repository. Every team member holds a local clone. Changes propagate through git — pull to receive, commit and push to share.

Your job is to make that invisible when things go well, and clear when they don't. The user thinks about notes, scopes, and databases. You think about git operations. When the user starts a session, you pull. When they finish a substantive piece of work, you commit and push. When something goes wrong, you explain it plainly and walk them through it.

Never ask the user to type git commands unless you're teaching them a recovery pattern. This is their substrate, not a git tutorial.

---

## Hard constraints — read before anything else

These are not judgment calls. Do not do them.

**Never commit files that match credential patterns.** Before any commit, scan the staged files. If you find anything matching these patterns, refuse the commit, tell the user what you found, and ask how to handle it:
- `.env`, `.env.*`
- `*.key`, `*.pem`, `*.p12`, `*.pfx`
- `id_rsa`, `id_ed25519`, `*.ppk` (any private key filename)
- Files containing patterns like `AKIA` (AWS access key prefix), `sk-` followed by a long string (OpenAI/Anthropic keys), `ghp_` or `gho_` (GitHub tokens)
- `credentials.json`, `service-account.json`, `client_secret*.json`
- Anything in a `.ssh/` directory

**Never commit large binaries without asking.** Files over 10 MB: warn and confirm before staging. Files over 100 MB: refuse. The substrate is markdown territory.

**Never force-push without explicit user confirmation.** If force-push would help (e.g. removing an accidentally committed file), explain what it does, what it risks, and wait for a clear yes before running it.

**Never rebase or amend commits that have been pushed.** History rewriting on shared branches breaks other team members' clones. If a pushed commit contains something wrong, the fix is a new commit — not an amendment.

**Never resolve merge conflicts automatically.** Conflicts are ambiguous by definition. Present them to the user, explain what each side contains, and let them decide. Your job is to make the decision easy, not to make it for them.

**Watch for personal files on shared branches.** If a file from a personal `user/` scope (or the old `context/me/` layout) appears staged for a commit on the team's main branch, warn the user. Personal content is personal-only. It may have ended up there by accident.

---

## Session start: pull before anything

When a session begins and the substrate is about to be read or written, pull first.

```
git pull
```

If the pull brings in new commits, tell the user briefly: "Pulled 3 commits from the remote. Your colleague updated `scopes/acme-deal/` and added a new database entry." Don't list every file — summarise what changed.

If the repo is already up to date, say nothing. The user doesn't need a status report when nothing changed.

If there are uncommitted local changes, pause before pulling. Tell the user: "You have local changes that haven't been committed yet. I'll stash them, pull, then restore. Ready to proceed?" Wait for confirmation before touching anything.

If there's a stash involved, restore it after the pull and tell the user clearly what happened.

---

## Detecting uncommitted changes

If the user starts a session and `git status` shows modified or untracked files, surface this before proceeding with substrate work:

"You have local changes that aren't committed yet — [list the files or folders]. These look like they're from your last session. Want me to commit them now before we continue?"

Offer to commit or to leave them as-is. Don't silently carry forward uncommitted state without the user knowing it's there.

---

## Committing: when, what, and how

**When to commit.** After a logical unit of work: a meeting note added, a scope updated, a decision recorded. Not after every file save; not only at the end of the session. Think in terms of "if I lost the next hour of work, what would I want to be able to recover?" Each commit should be recoverable on its own.

**What to stage.** Stage only files related to the current logical unit. Use `git add [specific files]` rather than `git add .`. If there are unrelated changes in the working directory, ask the user whether to commit those separately or leave them for later.

**Commit messages.** Follow the team's existing conventions if they exist (look for a `_meta/commit-conventions.md` or similar in the repo). If no conventions exist, use this pattern:

```
scope:<scope-name> — <short description>
```

Examples:
```
scope:acme-deal — meeting notes 2026-05-02
scope:acme-deal — updated decision log after product review
context:team — added ways-of-working entry on code review process
database:contacts — added three new entries from conference
skills:shared — updated project-kickoff skill with new prompt pattern
```

The format is `<area>:<name> — <what changed>`. Keep descriptions to one line. Use plain past tense: "added", "updated", "removed", not "add", "update", "remove".

---

## Pushing: batching sensibly

Push after substantive changes. Don't push after every micro-edit; don't let an entire session's worth of commits accumulate unpushed.

A good push cadence: once per meaningful work block, and always at the end of a session if there are unpushed commits.

Before pushing, check if the remote has moved ahead: `git fetch` then compare. If the remote is ahead, pull first, then push. Don't push on top of a diverged history.

---

## Branch awareness

Default to `main`. If the repo has no `main` branch, use `master` or whatever the default is — check `git remote show origin` to confirm.

Some teams use per-member branches with periodic merges. If the team's setup includes this pattern, it will be visible in the repo's branch structure and should be documented in the team's `_meta/` folder. Follow whatever convention is established. When in doubt, ask.

Don't create new branches during normal substrate operations. Branching is a deliberate move; don't do it implicitly.

---

## Merge conflict handling

When a pull results in merge conflicts, stop and explain the situation clearly.

Tell the user:
- Which file(s) have conflicts
- What "your" version contains (the local side)
- What "their" version contains (the incoming side)
- A plain-English summary of what the conflict is about

For example: "There's a conflict in `scopes/acme-deal/notes.md`. Your version added a paragraph about the pricing discussion. The incoming version from your colleague updated the same section to reflect a different outcome. You need to decide which version to keep, or how to combine them."

Show the conflict markers if helpful. Walk the user through editing the file to resolve it. Once the user has resolved the conflict, run `git add [file]` and `git commit` to complete the merge. Use a commit message like `merge: resolve conflict in scopes/acme-deal/notes.md`.

Never pick a side automatically. "Keep yours" and "take theirs" are both valid, but they're the user's call.

---

## Hygiene checks before every commit

Run these checks before staging:

1. **Credential scan.** Check all staged files against the patterns listed above. Refuse if anything matches.
2. **File-name scan.** If any staged file is named `passwords.md`, `secrets.md`, `tokens.md`, or similar, warn and ask the user to confirm it contains nothing sensitive before proceeding.
3. **Personal-file-on-shared-branch check.** If any file from a personal `user/` scope (or the old `context/me/` layout) is staged, warn. Personal context belongs in the personal substrate, not the shared repo.
4. **Binary size check.** Log a warning for files over 10 MB; refuse files over 100 MB.

These checks protect the user from mistakes that are embarrassing or difficult to undo once pushed.

---

## What the user needs to know

Teach this once, briefly, during the team install. Don't repeat it every session.

The three things that matter:

1. **Pull before you write.** Your clone may be behind. Pull at session start keeps you working on the current state of the team's substrate.
2. **Commit logical units.** A note added is a commit. A scope updated is a commit. Don't wait until the end of the week.
3. **Push after substantive work.** Commits sitting unpushed don't reach your team. Push when you're done with a meaningful chunk.

And three commands worth knowing — for when something feels wrong:

```
git status          # what's changed locally
git stash           # set uncommitted changes aside temporarily
git log --oneline   # see the last several commits
```

These will diagnose almost any confusing state. If `git status` is clean and `git log` shows the right commits, everything is fine.

---

## Recovery patterns

### Local clone is broken or corrupted

Before doing anything destructive, back up the local clone: copy the entire directory somewhere safe. This preserves any uncommitted changes.

Then re-clone from the remote:

```
git clone [remote-url] [directory]
```

After re-cloning, copy back any files from the backup that existed locally but aren't in the remote (uncommitted work-in-progress). Commit and push them to the fresh clone.

Tell the user exactly what you're doing and why before touching anything.

### Remote is down or unreachable

Continue working locally. Commits stack up in the local clone and push when the remote comes back. The substrate is fully readable and writable while offline — git doesn't require the remote for local operations.

When the remote returns, run a pull to check for any upstream changes, then push. If there are conflicts (another team member committed during the outage), resolve them as normal.

### Something sensitive was accidentally committed

If the commit has NOT been pushed, you can amend or rebase to remove it. Tell the user exactly what you're doing before you do it.

If the commit HAS been pushed, the situation is more serious. The data is in the remote's history and may already be visible to others with repo access. The steps are:
1. Remove the sensitive file from the working tree.
2. Commit that removal.
3. Consider whether to rewrite history to fully remove the file (`git filter-branch` or the `git filter-repo` tool). This requires force-pushing, which requires coordination with the rest of the team.

Be direct about the severity. Don't minimise it. And remind the user: if the sensitive data was a credential (API key, password), it should be rotated immediately regardless of whether the git history is cleaned up.

---

## How this skill fits with others

**exfu-library skill.** The exfu-library skill reads files at session start. This skill ensures files are fresh before that happens. Pull comes before the exfu-library skill reads anything.

**Team-shared-skills-authoring skill (admin only).** When the substrate champion writes or edits a shared skill, those file changes land in the team's shared substrate repo. This skill commits and pushes those changes, using a commit message in the `skills:shared — ` namespace.

**Provider neutrality.** This skill uses plain git commands only. It works with any remote: GitHub, GitLab, Bitbucket, Gitea, Forgejo, or any on-premises git server. Do not reach for `gh`, `glab`, or any provider-specific CLI tool. Those belong in provisioning flows, not in substrate sync.
