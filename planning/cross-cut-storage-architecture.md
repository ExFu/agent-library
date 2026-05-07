# Cross-cut: Storage architecture

## Why

Where the user's substrate files live determines what works and what breaks. Storage backend affects file access speed, conflict handling, audit trail, access control, backup story, and onboarding complexity. It's upstream of nearly everything else.

The storage backend is a **runtime choice made during install**, not predetermined by which plugin variant the user has. Solo, team, and team-admin installs all offer the same three options. The champion or user picks based on their team's profile and constraints.

---

## Three options

### 1. Git repo

Each user has a local clone of a private git repository. Pulling and pushing keeps everyone aligned. The substrate filesystem is local to each machine; git is the propagation layer.

**Fits when:** the team is comfortable with git, has a git hosting provider (GitHub, GitLab, Bitbucket, on-prem), or has compliance requirements that need a formal audit trail of content changes.

**What you give up:** higher technical bar for joiners; personal substrates need to be managed separately from the shared repo; merge conflicts require resolution.

**Compliance notes:** git history provides a full audit trail — every change records author, timestamp, and diff. This is the strongest posture for ISO 27001 / SOC 2 / regulated environments. Access control is at repo and branch level; consistent across all substrate content.

**Skills:** `git-substrate-sync` (shared between team and team-admin plugins) handles pull-before-write, commit, push, and merge-conflict surfacing. `team-repo-provisioning` handles one-time repo creation for champions.

### 2. Box shared folder(s)

The team's substrate lives in one or more Box shared folders. Each team member accesses their relevant folders via Box Drive mounted locally (or via the Box MCP connector on mobile). No git involved.

**Fits when:** the team prefers familiar cloud-drive UX, has members not comfortable with git, or already has Box as the org's standard file-sharing tool.

**What you give up:** no native file-diff version history (Box retains file versions but not content diffs); no merge-conflict surfacing (two members writing the same file in close succession can overwrite each other); audit trail is access-only (who opened what), not content-change history. More moving parts: team substrates in Box typically need multiple folders (see below).

**Compliance notes:** Box tracks access events but not file-level diffs. Acceptable for many enterprise contexts where Box's existing access controls and logs are already approved. Not the right fit for environments requiring a full content-change audit trail.

**Skills:** `box-filesystem-management` handles reads, writes, and file operations. `team-box-folder-provisioning` handles one-time folder creation and sharing setup for champions.

#### Box and multiple folders

A key difference from git: Box does not work like a single repo with uniform access. Different scopes have different access groups — some shared with the whole team, some with a subset. This means a team substrate in Box is typically **multiple folders**:

- One folder per org (shared with everyone in the org) — holds org-wide context.
- One folder per team — holds team-level conventions, databases, shared skills. Shared with all team members.
- One folder per scope (project, deal, ongoing work area) — holds that scope's context and planning. Shared only with the people working on that scope.
- Personal folders per team member — not shared; each person's `context/me/` and personal scopes.

Each folder has its own sharing configuration. The champion creates and shares them; colleagues accept invitations. There is no single "clone" step like git.

### 3. Local-only / custom

Each team member's Claude works against a local folder on their own machine. No automatic sync. Sharing happens manually or via a mechanism the team manages themselves (their org's existing file infrastructure, manual file exchange, Obsidian Sync, Syncthing, etc.).

**Fits when:** the team has no compliance requirement for a central audit trail, already has its own file-sharing infrastructure, or simply wants substrate that works without any additional tooling.

**What you give up:** no automatic propagation of shared context; substrate champion must manually distribute any shared content; no central audit trail.

**Compliance notes:** no central audit at all from ExFu's side. The team is responsible for whatever logging or backup their own mechanism provides. Not suitable for environments with formal audit requirements unless the team's own infrastructure covers it.

**Skills:** neither `git-substrate-sync` nor `box-filesystem-management` is registered as the storage layer. The `substrate` skill still works, against the local folder directly.

---

## Trade-off summary

| | Git | Box (multi-folder) | Local-only |
|---|---|---|---|
| Onboarding complexity | Medium (git CLI, clone) | Low (accept folder invitations) | Very low (nothing to set up) |
| Access control | Repo/branch-level, consistent | Per-folder, varies by scope | None centrally |
| Audit trail | Full (author, timestamp, diff) | Access logs only | None (unless team adds it) |
| Conflict handling | Explicit merge conflicts | Silent overwrite risk | N/A (no shared writes) |
| Backup | Remote is canonical backup | Box's version retention + org backup policy | Local machine backup only |
| Per-scope sharing granularity | Coarse (whole repo or branch) | Fine (folder-by-folder) | N/A |
| Good fit for regulated environments | Yes | Sometimes | No |

---

## The wrapping principle still applies

Orgs can wrap any of these options with their own custom storage solutions. If an org wants a SharePoint backend, a proprietary sync layer, or a managed secrets vault, they can wrap the ExFu substrate conventions around that infrastructure. The skills describe patterns; the mechanism beneath can be swapped by anyone who wants to invest in the wrapping work.

See `cross-cut-extension-and-wrapping.md` for the wrapping principle in full.

---

## Cross-plugin

The storage skill (`box-filesystem-management` for Box, `git-substrate-sync` for git) abstracts the access mechanism. Skills and resources in the substrate don't need to know which backend is active — they read and write files; the storage skill handles the how.

The install records the chosen backend in the `wow` navigation map (`storage: git`, `storage: box`, or `storage: local-only`) so every future session knows what mechanism is in play.

---

## Open questions

- **Per-scope Box folder sharing:** when a scope changes team membership, the champion needs to update Box sharing manually. Is there a convention for surfacing when sharing configs are stale? (E.g. a `_meta/folder-map.md` that includes expected sharing groups, reviewed quarterly.)
- **Cross-folder skills:** some skills may need to read across multiple Box folders (e.g. a daily briefing pulling from team context and a current-scope folder). What's the convention for substrate-spanning reads in Box? The skill currently needs the relevant folder IDs configured; this may need a more structured approach.
- **Solo multi-device story:** a solo user spanning desktop and mobile still benefits from a cloud-backed option (Box or git). The right answer depends on their comfort with git vs Box. Worth surfacing as an explicit choice moment in the solo install rather than defaulting.
- **Local-only backup:** no built-in backup story. The install should prompt local-only users to confirm they have machine-level backup in place, and include this in the onboarding reminder.
- **Encryption at rest:** for all three backends, disk encryption on participating machines is recommended and required for many ISO 27001 implementations. The compliance briefing covers this; the install should confirm it.
