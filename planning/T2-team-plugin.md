# T2 — Team plugin

The plugin for users operating inside a team or organisation. Different storage architecture (git rather than cloud-drive sharing), additional teaching artefacts (admin/user, seniority/trust, personal/team split), and additional resources (compliance briefing, role capture).

Anchors back to: `T1-overview.md`, `T2-shared-skills-and-resources.md`, `cross-cut-storage-architecture.md`, `cross-cut-compliance.md`, `cross-cut-teaching-artefacts.md`.

---

## Why

Team installs are different in kind from solo, not just degree. The user is one of several humans. Their substrate has a personal layer *and* a team-shared layer. Storage has to propagate reliably across machines (git, not Box). IT and security teams will likely review what's being installed. Role-in-org becomes part of identity-level context rather than incidental colour.

Forcing all this into the solo plugin would distort the solo experience and dilute the team experience. Two plugins keeps each clean.

---

## How

### What this plugin contains beyond shared

- **`exfu:install-teams`** — the install conversation skill. Builds on the same shape as `install-solo` but with team-specific concerns surfaced earlier and the storage architecture defaulting to git rather than Box.
- **`git-substrate-sync`** — net-new skill. Wraps git operations safely so the user (and their Claude) don't have to think about git commands during routine substrate work.
- **`role-capture`** support — handled inside `install-teams` as part of the about-me phase. Not a separate skill; a structured beat in the install conversation that produces `context/me/role.md`.
- **Compliance briefing** — `resources/compliance-briefing.md`. Material the team's substrate champion can hand to IT/security to answer ISO 27001 / SOC 2 / similar reviews.
- **Team-specific teaching artefacts** — diagrams covering personal-vs-team skills and instructions, admin plane vs user domain, seniority and trust roles. Live in `resources/diagrams/` per the teaching-artefacts cross-cut convention.
- **Team plugin manifest** — declares contents, version, compatibility.

### Storage decision: git, not shared cloud drives

Per `cross-cut-storage-architecture.md`, the team plugin uses git as the substrate-sync mechanism. Each user has a local clone of the team's substrate repo. Pulling and pushing keeps the team aligned. The substrate filesystem is local; git is the propagation layer.

The `git-substrate-sync` skill is the new design work. It teaches Claude (and by extension the user) the right operations:

- Pull at session start (read-fresh).
- Stage and commit logical units of change with sensible messages.
- Push after substantive changes.
- Detect and surface merge conflicts cleanly — the user resolves; Claude can help walk them through but doesn't force resolution.
- Handle branch hygiene (working on main vs feature branches — most teams will work on main; some may want a per-member branch model).
- Honour the substrate hygiene rules (don't commit credentials, IDs, raw medical data, etc., even by accident).

The skill body should be substantive but not turn the user into a git expert. It does the operations; the user thinks at the substrate level. This is a teach-as-you-go design — the user learns enough git to recover when things go sideways, but doesn't have to learn git to use the substrate.

### Personal vs team layers

Each team member has both:

- **A personal substrate** — local, private, not in the team's git repo. Holds `context/me/`, personal scopes, personal databases, scratch.
- **The team's shared substrate** — git-synced, shared with team members. Holds `context/team-x/`, shared scopes, shared databases, the team's customised skills folder.

Their personal `wow` skill points at both layers via its navigation map. Claude reads from whichever is relevant for the current conversation.

Worth a teaching artefact: a clean diagram showing this split. Probably the highest-leverage team-specific diagram.

### Role capture — first-class beat in the install

Role-in-org isn't optional context for team users; it's identity-level. The install-teams skill should make role-capture a deliberate beat during about-me, not an afterthought.

The capture writes to `context/me/role.md` (or augments `context/me/about.md` with a Role section — probably its own file given how often Claude will want to reach for it independently).

If the user wants their role visible to colleagues' Claude instances, the install can offer to also write a pointer-or-snippet into the team-shared `context/team-x/` layer. That decision should be deliberate, not a default.

### Compliance briefing

Ships as a resource (`resources/compliance-briefing.md`) the substrate champion can adapt and hand to their IT/security team. Covers:

- Data flow: where data goes, where it doesn't.
- Controls: encryption-at-rest recommendations, access controls via git, hygiene rules.
- ISO 27001 control mappings — at the level of "this control: this answer".
- Recommended team practices.
- What this plugin is not (specifically: it's not an Anthropic product, it doesn't grant the team any Anthropic capabilities they don't already have).

The install-teams skill should mention this resource exists and where it lives, so the team champion can find and use it without asking.

### Admin-vs-staff variant — defer the decision

Per T1, the admin-vs-staff split is carried as an option through this T2 and decided once we see the shape of each conversation. Two questions to settle before deciding:

1. **What does an admin install look like differently from a staff install?** Plausible differences: admin captures team conventions and writes them once for everyone; admin sets up the shared git repo; admin writes the team's customised skills; admin briefs IT. Staff just connects to the team's repo and does a personal install on top.
2. **Is the difference enough to warrant separate plugins, or could it be a branch in the install conversation?** A single `install-teams` skill that asks "are you the substrate champion for your team, or coming in as a member?" might handle the variance cleanly without a second plugin.

Recommendation tilts toward "single plugin with conversation branching" unless we discover something during T3 that forces a split. Carry the option open through T3-team-install design.

### Install conversation shape

Same skeleton as install-solo (open with diagram, calibrate, plant priors, about-me, buffet, demonstrate, close), with these team-specific changes:

- **Diagram step.** Show the substrate diagram *and* a team-specific diagram (personal/team split). Two artefacts, one moment.
- **Pre-about-me beat.** "Are you the substrate champion for your team setting things up for the first time, or coming in as a team member to install your personal layer?" — branches the rest of the conversation.
- **About-me beat.** Includes role-capture as a deliberate sub-beat.
- **Storage step.** Set up git remote, clone the team repo (or initialise it if champion). Walk through the `git-substrate-sync` skill.
- **Buffet step.** Same shared-skills options as solo, plus team-specific moves (set up shared scope skills, register pointer to team conventions in `wow`).
- **Compliance step (champion only).** Show the compliance briefing resource. Offer to walk through it with them.
- **Close.** Migration / update notes; champion gets a "here's how to onboard the next team member" pointer.

---

## What — components inventory

### `exfu:install-teams` (new design, content adapted from start.md + team-considerations.md)

Skill body builds on lean `start.md` plus the existing `team-considerations.md`. Champion-vs-member branching at the top. Storage default git. Role-capture as a deliberate beat.

### `git-substrate-sync` (new design, substantial)

Wraps git operations for substrate use:

- Pull-before-write at session start.
- Commit with structured messages (e.g. "scope:acme-deal — meeting notes 2026-05-12" or similar conventions).
- Push after logical units of work.
- Detect uncommitted changes, surface to user.
- Merge-conflict handling — present clearly, let user resolve, help paraphrase.
- Branch awareness — prefer main; respect alternate models if team uses them.
- Hygiene checks — refuse to commit files matching credential patterns, etc.

Body has to be substantive but not pedagogical-overload. The user is expected to understand git is involved; they don't need to become a git practitioner.

### Compliance briefing (new content)

`resources/compliance-briefing.md`. Sections:

- Data flow overview.
- Recommended controls.
- ISO 27001 control mappings (best-effort; teams can adapt).
- Disk encryption recommendation.
- Hygiene rules (no credentials, no PII, no regulated content).
- Audit trail (git history).
- Backup story.
- What this is, what this isn't.

### Team teaching artefacts

Each ships as a static diagram, produced via the ChatGPT instruction-pattern from `cross-cut-teaching-artefacts.md`:

- **Personal vs team skills and instructions** — shows how the user's `wow` points at both their private substrate and the team's shared substrate.
- **Admin plane vs user domain** — what the team admin/champion controls vs what individual members own.
- **Seniority and trust roles** — recommended permissions/setups across organisational seniority levels.

Each gets a planning file with the rich descriptive instructions for ChatGPT.

### Team plugin manifest

TBD pending plugin-format research.

### Migration support

If a team is currently using the fetch model (unlikely but possible), `exfu:migrate-from-fetch-model` (designed in T2-solo) covers them too. Worth confirming during T3.

---

## T3 candidates

- `T3-install-teams-skill.md` — design and write the install-teams skill, including the champion-vs-member branch and role-capture beat.
- `T3-git-substrate-sync-skill.md` — design and write the new git skill. The largest piece of net-new design in the team plugin.
- `T3-compliance-briefing.md` — write the compliance briefing resource.
- `T3-team-teaching-artefacts.md` — write the ChatGPT instructions for the three team-specific diagrams.
- `T3-team-manifest.md` — manifest assembly, post plugin-format research.
- `T3-admin-vs-staff-decision.md` — settle the admin-vs-staff variant question once T3-install-teams design is firm.

Run order: `T3-git-substrate-sync` and `T3-install-teams` are tightly coupled (the install conversation drives users into the git flow); design them in conversation rather than fully parallel. Compliance briefing and teaching artefacts are independent and can run alongside.

---

## Open questions

- **Git provider neutrality.** The skill should work with GitHub, GitLab, Bitbucket, on-prem servers. Anything provider-specific (e.g. issue creation, PR workflows) should be optional. Will the skill detect provider and adapt, or stay provider-agnostic?
- **Branch model.** Default to main-only. But some teams may want per-member branches with periodic merge to main. Should the install offer that as a choice, or pick main-only and let the team override later?
- **Repo provisioning.** When the substrate champion runs the install, do they create the repo manually first (and the install just clones it) or does the install help them create the repo on their git provider? Probably the former for v1; latter is provider-specific work.
- **Two team plugins (admin vs staff).** Carrying as deferred. Settle in `T3-admin-vs-staff-decision.md`.
- **Coexistence with solo plugin.** What if a user already has the solo plugin installed and joins a team that wants them on the team plugin? Need a coexistence story or a clean migration path. Coordination point with T2-solo.
- **Mobile and scheduled tasks under git.** Mobile Claude can't run git directly. Scheduled tasks can. Mobile sessions probably read-only against the local clone via Box-style MCP if the local machine syncs the clone to a cloud drive — but that re-introduces cloud-drive issues. Or mobile sessions just don't get the team substrate's freshest state and live with what was last pulled. Trade-off worth surfacing to the user.
- **Backup story.** Git remote is the canonical backup. What if the remote is lost (provider failure, account deletion)? Recommend per-team backup of the remote? Out of scope for v1, flag for cross-cut-compliance.
