# Cross-cut: Storage architecture

## Why

Where the user's substrate files live determines what works and what breaks. Cloud-drive-mounted-locally has been the canonical answer (Box) but has real failure modes — most painfully, offline-cached files that don't auto-trigger downloads when Claude reads them, leading to silent empty-file failures. Shared cloud drives for teams have additional failure modes: contention, eventual-consistency surprises, multiple clients writing concurrently.

The storage architecture is upstream of nearly everything else. All three plugins depend on it. We need a clear architectural decision, with the trade-offs visible, before T2 work proceeds on any plugin.

## How

### Solo plugin: stay with Box for now, with caveats

Box remains the canonical recommendation for solo users at v1, despite the offline-caching issue. Reason: nothing else is obviously better yet, and migrating to a different mechanism is a project of its own. Document the offline-caching limitation; explain to users that they should not rely on space-saving offlining for files Claude needs to access.

**Add a planning task to keep exploring alternatives.** Candidates worth evaluating:
- Direct local filesystem (no cloud drive at all) — fast, no caching issues, but loses mobile and multi-device access. Pair with a Mac-mini-as-always-on for users who want background scheduled tasks plus mobile access via MCP to that same machine.
- Obsidian vault (local) — same trade-offs as direct local, plus optional Obsidian Sync for multi-device.
- Other cloud-drive options — Google Drive, OneDrive, Dropbox — likely have similar failure modes to Box; worth checking.
- Self-hosted sync (Syncthing, etc.) — control over caching behaviour, more setup overhead.

The right answer probably depends on the user's profile. A solo user with one machine and no need for mobile access can use direct local. A solo user spanning multiple devices needs *something* that reaches them all.

### Team and team-admin plugins: git, not shared cloud drive

Teams use git as the substrate-sync mechanism. Each user has a local clone of the team's substrate repo. Pulling and pushing keeps everyone aligned. The substrate filesystem is local to each machine; git is the propagation layer.

The `git-substrate-sync` skill is shared between the team and team-admin plugins. One source file lives at `plugin/src/team/skills/git-substrate-sync/` and is bundled into both plugins at build time.

Why this works better than shared cloud drives for teams:
- No contention or eventual-consistency surprises. Conflicts surface as merge conflicts, which are explicit and resolvable.
- Versioning and history are first-class. The team can see what changed, when, by whom.
- Permissions are folder-level via git's branch and access controls (or via repo-level for simpler cases).
- Works under most corporate IT policies that allow GitHub/GitLab/Bitbucket.
- ISO 27001 friendly: data lives on controlled endpoints, propagated through controlled channels.

What this requires:
- A git-substrate-sync skill that walks Claude through the safe operations (pull before write, commit with sensible messages, push after, handle merge conflicts gracefully).
- Guidance on what should and shouldn't go in the team substrate (binaries, sensitive data, personal-only files).
- A clear story for how a team member's *personal* substrate (`context/me/`, personal scopes) coexists with the team's substrate. Probably: personal substrate is a separate, non-shared local folder; the team substrate is the shared git repo. The user's `wow` skill points at both.

### Cross-plugin

The substrate skill (`box-filesystem-management` and its successors) needs to abstract the access mechanism enough that Claude doesn't have to care whether it's Box, direct local, or git-synced. The skill teaches Claude *the right operations for this user's setup*, regardless of what's underneath.

Worth considering: a generic `filesystem-management` skill that accommodates all variants, with the specific mechanism noted in the user's `wow` navigation map. Or per-mechanism skills (`box-filesystem`, `git-filesystem`, `local-filesystem`) and the install picks the right one based on the user's setup.

## What (initial)

- Solo v1 stays on Box, with the caveat documented and a research task open to explore alternatives.
- Team and team-admin v1 both use git. They share a single `git-substrate-sync` skill. T2 work for both team variants assumes git from the start.
- The current `box-filesystem-management` skill probably becomes the basis for a generalised filesystem skill, or stays Box-specific while a new git-flavoured skill stands alongside it.

## Open questions

- Solo with multi-device access: what's the recommended path if the user has both a desktop and wants Claude on mobile? Box still wins on that axis despite the offline-cache pain, until something better appears. Worth surfacing as a "this is the trade-off" moment in install conversations.
- Git for teams: does this work over private/internal git servers (GitLab on-prem, etc.) without modification, or are there install steps specific to the user's git setup? Probably the latter — flag for T2 of the team plugin.
- Conflict-resolution UX: when two team members edit the same substrate file and create a merge conflict, how does the team member see and resolve it? Their Claude probably handles this via the git-sync skill, but the UX needs design.
- Backup story: with git-sync, the remote is the backup. With Box, Box is the backup. With direct local, there is no backup unless the user adds one. Each path has different recommendations.
- Encryption-at-rest: does the team plugin need to recommend or require disk encryption on participating machines? Likely yes for ISO 27001 conversations.
