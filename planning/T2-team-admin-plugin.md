# T2 — Team-admin plugin

The plugin for substrate champions: the people who set up a team's shared substrate from scratch, design its shared conventions, brief IT/security on what's being installed, and onboard their colleagues. Strict superset of the team plugin's capability surface, with admin-only skills and resources layered on top.

Anchors back to: `T1-overview.md`, `T2-team-plugin.md`, `T2-shared-skills-and-resources.md`, `cross-cut-storage-architecture.md`, `cross-cut-compliance.md`, `cross-cut-teaching-artefacts.md`.

---

## Why

Substrate champions do work that other team members never do. They:

- Decide where the team's shared substrate lives (which git provider, which repo).
- Provision the repo and seed it with the initial structure.
- Author the team's shared skills, scopes, and conventions — the things every team member's Claude reads.
- Brief IT and security on what the plugin does and doesn't do.
- Onboard new team members — give them the team plugin download URL, walk them through their first install, hand off the team's git-remote details.
- Maintain the shared substrate over time as the team's working patterns evolve.

This is meaningful, distinct work. It needs its own install conversation, its own teaching artefacts, and its own skills. Folding it into the team plugin would distort the team-plugin experience for the 90% of team members who are joiners, and would put admin capabilities into hands that shouldn't have them. Splitting at the plugin boundary makes the access control explicit.

The team-admin plugin is also where compliance documentation lives. The substrate champion is the person who'll talk to IT/security; the briefing material should be in their plugin, not in every team member's plugin.

---

## How

### What this plugin contains beyond shared

- **`exfu:install-team-admin`** — the install conversation skill. Builds on the install-team conversation but adds the champion-specific beats: provisioning, shared-skills authoring, IT briefing, onboarding-handoff prep.
- **`git-substrate-sync`** — net-new skill for both team variants. Wraps git operations safely. Same source file shared with the team plugin; bundled into both at build time.
- **`team-repo-provisioning`** — admin-only. Walks the champion through creating the team's shared substrate repo on their git provider of choice, seeding it with the recommended initial structure, configuring access controls.
- **`team-shared-skills-authoring`** — admin-only. The champion's tooling for writing skills that go in the team's shared `skills/` folder (as opposed to their personal one). Different conventions: shared skills must be more conservative about assumptions, must declare their dependencies clearly, must not embed personal context.
- **`team-onboard-member`** — admin-only. Generates an onboarding pack for a new team member: the team's git-remote URL, the team plugin download link, a short customised "what you're joining" doc the champion can hand to the joiner.
- **`role-capture`** support — handled inside `install-team-admin` as part of the about-me phase. Same beat as in the team plugin (and yes, the admin captures their own role too).
- **Compliance briefing** — `resources/compliance-briefing.md`. Material the champion can hand to IT/security to answer ISO 27001 / SOC 2 / similar reviews. Lives only in the team-admin plugin.
- **Admin teaching artefacts** — diagrams covering admin plane vs user domain, seniority and trust roles, plus the personal-vs-team split. Some of these are shared with the team plugin (personal-vs-team) and some are admin-only (admin-plane-vs-user-domain).
- **Team-admin manifest** — declares contents, version, compatibility, capability declarations.

### Storage architecture

Same as the team plugin: git, with the substrate filesystem local on each machine and git as the propagation layer. The team-admin plugin adds the provisioning step that the team plugin doesn't need (the team plugin assumes the repo already exists).

### First-run politeness check

The install-team-admin skill should open with a brief calibration question: *"This is the team-admin plugin — designed for the substrate champion of your team. You'll be setting up the team's shared substrate, choosing where it lives, designing conventions, and onboarding your colleagues. If that's not you, the team plugin is what you want — install that instead and reach out to your champion for the team's repo URL."*

Not aggressive, not gate-keeping — just honest about who the plugin is for. If the user confirms they're the right person, proceed. If they say they're not, point them at the team plugin and stop.

### Detection of existing team-plugin install

If the user has the team plugin installed already (i.e. they joined the team first, then became its champion later), the team-admin install should detect this and offer a clean upgrade path:

- "Looks like you have the team plugin installed. Team-admin is a strict superset — it includes everything the team plugin does plus admin-only skills and resources. The recommended path is to uninstall the team plugin and install team-admin in its place; your personal substrate, your wow, and your connection to the team's git remote will all be preserved. Confirm to proceed."

The detection logic and the upgrade flow probably live in a small `exfu:upgrade-from-team-to-admin` skill, callable from `exfu:install-team-admin` when the upgrade is detected.

### Repo provisioning step

Once the user is confirmed as the champion and the about-me phase is done, the install reaches the repo-provisioning beat. Options the champion picks between:

- **They already created the repo** — the install just collects the remote URL, clones, and proceeds.
- **They want help creating it** — the `team-repo-provisioning` skill walks them through provider-specific instructions (GitHub, GitLab, Bitbucket, on-prem), recommends initial visibility/access settings, seeds the repo with the recommended substrate structure, makes the first commit.

The skill should stay provider-aware but not provider-coupled. It can paste in the right CLI commands for each major provider, or walk through the web UI flow, depending on what the champion prefers.

### Shared-skills authoring

Different conventions apply to skills that live in the team's shared `skills/` folder versus skills that live in any one user's personal substrate. Specifically:

- Shared skills must not embed any single team member's personal context (about-me, role-specific assumptions, personal preferences).
- Shared skills must declare dependencies clearly, because they'll be loaded by Claude across many sessions and many team members.
- Shared skills should reach for team-level resources (e.g. `context/team-x/ways-of-working.md`) rather than personal ones.
- Shared skills evolve through git history, with commit messages explaining the change.

The `team-shared-skills-authoring` skill teaches the champion these conventions and helps them author or refactor skills against them. It can also detect when a personal skill is being inappropriately promoted to shared (e.g. it references `context/me/`) and warn before the commit.

### Onboarding-handoff helper

When the champion is ready to onboard a new team member, they invoke `team-onboard-member`. The skill collects:

- Who the new joiner is (name, role, anything specific they should know).
- Whether they need a tailored intro to the team's substrate (most do).

The skill produces an onboarding pack: a short markdown doc with the team plugin download URL, the git remote URL, an introduction to the team's conventions, and a one-paragraph "here's what your install conversation will cover" preview. The champion sends this to the joiner; the joiner installs the team plugin; the install-team conversation reads this onboarding pack if available and uses it to personalise their flow.

### Compliance briefing as conversational beat

The compliance briefing is a resource (`resources/compliance-briefing.md`), but the install-team-admin skill should mention its existence and offer to walk the champion through it. Some champions will already have a strong compliance posture; others will be on their first IT review and need help. The skill should accommodate both without forcing the conversation.

### Install conversation shape

Skeleton mirrors install-team but with admin-specific layers:

- **Politeness check.** "Is this you?"
- **Diagram step.** Show the substrate diagram, the personal-vs-team split, *and* the admin-plane-vs-user-domain diagram. Three artefacts, calibration moment.
- **Pre-about-me beat.** Confirm role: "You're the substrate champion for [team name]?"
- **About-me beat.** Includes role-capture (admin's own role).
- **Storage step.** Repo provisioning if needed; otherwise just clone an existing repo. Walk through `git-substrate-sync`.
- **Shared-substrate seeding.** Set up the recommended initial structure in the team's repo. Establish team-conventions doc, optional initial team scopes, the team's `context/team-x/` skeleton.
- **Buffet step.** Same shared-skills options as solo and team, plus admin-specific moves (set up team-shared scopes, register pointers to team conventions in `wow`, prepare onboarding pack template).
- **IT briefing step.** Surface the compliance briefing resource. Walk through it if helpful.
- **Onboarding-prep step.** Generate a first onboarding pack the champion can use immediately.
- **Close.** Migration / update notes; pointer to the maintenance rhythm (when to add new shared skills, how to evolve team conventions over time).

### What the team-admin plugin is NOT

Worth being explicit:

- It's not an org-wide IT-administration tool. It doesn't manage Anthropic accounts, doesn't provision Claude licences, doesn't monitor team usage.
- It doesn't enforce org policy. The plugin is what it is; what the user does with it is their responsibility (and the org's).
- It doesn't grant Anthropic capabilities to the team. Whatever Claude features the team has access to via their org's Anthropic relationship are unchanged by the plugin.

---

## What — components inventory

### `exfu:install-team-admin` (new design, content adapted from start.md + team-considerations.md + admin-specific additions)

Skill body builds on lean `start.md`. Champion-specific politeness check up front. Storage default git, repo-provisioning option. Role-capture as a deliberate beat. IT-briefing and onboarding-prep beats added.

### `git-substrate-sync` (new design, substantial — shared with team plugin)

Wraps git operations for substrate use:

- Pull-before-write at session start.
- Commit with structured messages (e.g. "scope:acme-deal — meeting notes 2026-05-12" or similar conventions).
- Push after logical units of work.
- Detect uncommitted changes, surface to user.
- Merge-conflict handling — present clearly, let user resolve, help paraphrase.
- Branch awareness — prefer main; respect alternate models if team uses them.
- Hygiene checks — refuse to commit files matching credential patterns, etc.

Same source file used by both team plugin builds. The behaviour is identical; what differs across the two plugins is the *capability surface* of the user invoking it. Admin can write shared skills, member can't. The git skill itself is policy-agnostic.

### `team-repo-provisioning` (new design, admin-only)

Walks the champion through creating the team's shared substrate repo on their git provider of choice. Provider-aware:

- GitHub (web + `gh` CLI).
- GitLab (web + `glab` CLI).
- Bitbucket.
- On-prem GitLab / Gitea / Forgejo.

Recommends initial visibility (private), access settings (team-level read/write), and seeds the repo with:

- `context/team-x/ways-of-working.md` skeleton.
- `scopes/` folder.
- `skills/` folder for shared skills.
- `databases/` folder for shared databases.
- `_meta/README.md` describing the substrate's structure.
- Initial commit.

### `team-shared-skills-authoring` (new design, admin-only)

Teaches the champion the conventions for shared skills:

- No personal context embedded.
- Dependencies declared clearly.
- Reaches for team-level resources, not personal ones.
- Tracked via git history with descriptive commits.

Includes pre-commit hygiene checks: warns when a skill references `context/me/`, when a skill name collides with a known personal skill, when a skill body assumes facts that are personal (e.g. "the user's calendar timezone is...").

Can also help the champion *refactor* a personal skill into a shared one.

### `team-onboard-member` (new design, admin-only)

Generates an onboarding pack for a new team member. Inputs:

- Joiner's name, role, anything specific.
- Whether they need a tailored intro (most do).

Output: markdown doc the champion sends to the joiner. Contents:

- Welcome paragraph.
- Team plugin download URL.
- Git remote URL.
- A one-paragraph intro to the team's conventions (auto-generated from the team's `context/team-x/ways-of-working.md`).
- A preview of what the joiner's install conversation will cover.
- Champion's contact details for help.

### Compliance briefing (new content, admin-only)

`resources/compliance-briefing.md`. Sections:

- Data flow overview.
- Recommended controls.
- ISO 27001 control mappings (best-effort; teams can adapt).
- Disk encryption recommendation.
- Hygiene rules (no credentials, no PII, no regulated content).
- Audit trail (git history).
- Backup story.
- What this is, what this isn't.

### Team-admin teaching artefacts

Each ships as a static diagram, produced via the ChatGPT instruction-pattern from `cross-cut-teaching-artefacts.md`:

- **Personal vs team skills and instructions** — also shipped in the team plugin. Shared diagram.
- **Admin plane vs user domain** — admin-only. Shows what the team admin/champion controls vs what individual members own.
- **Seniority and trust roles** — admin-only. Recommended permissions/setups across organisational seniority levels.

Each gets a planning file with the rich descriptive instructions for ChatGPT.

### `exfu:upgrade-from-team-to-admin` (new design, modest size)

Skill body:

- Detects existing team-plugin install.
- Confirms with user before proceeding.
- Removes team-plugin's bundled skills (preserves user's personal substrate).
- Installs team-admin's bundled skills.
- Updates `wow` navigation map to reflect new capability surface.
- Verifies post-upgrade state.

### Migration support

If a team is currently using the fetch model (unlikely but possible), `exfu:migrate-from-fetch-model` (designed in T2-solo) covers them too. Worth confirming during T3.

### Team-admin plugin manifest

Declares contents, version, compatibility, capability declarations. Per `T2-build-and-distribution.md`.

---

## T3 candidates

- `T3-install-team-admin-skill.md` — design and write the install-team-admin skill, including the politeness check, role-capture, and admin-specific beats.
- `T3-git-substrate-sync-skill.md` — design and write the git skill (shared with team plugin; coordinated in T3 with that variant).
- `T3-team-repo-provisioning-skill.md` — design the provisioning flows per git provider.
- `T3-team-shared-skills-authoring-skill.md` — design the shared-skills conventions and the authoring/refactoring helpers.
- `T3-team-onboard-member-skill.md` — design the onboarding-pack generator.
- `T3-upgrade-from-team-to-admin-skill.md` — design and write the upgrade detection and flow.
- `T3-compliance-briefing.md` — write the compliance briefing resource.
- `T3-team-admin-teaching-artefacts.md` — write the ChatGPT instructions for the admin-only diagrams.
- `T3-team-admin-manifest.md` — manifest assembly per plugin format.

Run order: `git-substrate-sync` is a shared dependency for both team variants — design it once, in coordination with T2-team-plugin. The other admin-only skills can run in parallel after that.

---

## Open questions

- **Git provider neutrality.** Same as the team-plugin question — the skill should work with GitHub, GitLab, Bitbucket, on-prem servers. The provisioning skill is provider-aware by necessity; the sync skill stays provider-agnostic.
- **Branch model.** Default to main-only. But some teams may want per-member branches with periodic merge to main. Should the install offer that as a choice, or pick main-only and let the team override later? Probably pick main-only for v1 with a brief note about alternatives.
- **Repo provisioning depth.** Should the skill actually run `gh repo create` for the user, or just walk them through doing it themselves? Probably the latter for v1 — fewer permissions, less brittle. Champion runs the command, skill verifies success.
- **Initial repo seeding.** What's the canonical starting structure for a fresh team substrate? Probably the same as solo's substrate-guide-recommended layout, minus personal-only folders, plus a `context/team-x/` placeholder. Worth a small canonical template.
- **Shared-skill collision detection.** When the team has many shared skills authored over time, what stops two skills from claiming the same name? Git surface conflicts on merge, but ideally the authoring skill flags the collision pre-commit. Easy to add.
- **Onboarding pack format.** Markdown is the natural choice but worth checking — would a small bundled HTML version be more useful for non-technical joiners? Defer; markdown for v1.
- **Mobile and scheduled tasks under git.** Same trade-off as the team plugin. The admin's mobile sessions probably read the local clone via Box-style MCP if they sync the clone, but that re-introduces cloud-drive issues. Surface as trade-off; don't pretend it's solved.
- **Compliance briefing localisation.** The default briefing is ISO 27001-flavoured. Some teams will need SOC 2, HIPAA, GDPR-specific framing. v1 ships ISO 27001; flag the others as future work. The compliance cross-cut tracks this.
- **What if the champion changes?** Substrate champions move on. The new champion needs the admin plugin, the old one's admin plugin is now extraneous. Worth a "transfer of championship" flow eventually, but probably v2.
