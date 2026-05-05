# T2 — Team plugin

The plugin for ordinary team members: people joining a team that already has its shared substrate set up, installing their own personal layer on top, and reading/writing the shared layer through it. Strict subset of the team-admin plugin's capability surface — no admin tooling, no repo provisioning, no IT briefing.

Anchors back to: `T1-overview.md`, `T2-team-admin-plugin.md`, `T2-shared-skills-and-resources.md`, `cross-cut-storage-architecture.md`, `cross-cut-teaching-artefacts.md`.

---

## Why

Most team members are joiners, not champions. They're given a git remote URL, a download link, and a quick "this is what we use, get yourself set up" message from whoever is maintaining the team's substrate. They don't need to know how the repo got provisioned, what the IT briefing said, or how to author shared skills. They need their personal substrate set up, their connection to the team's shared substrate working, and a clear sense of what's theirs vs what's the team's.

The team plugin gives them exactly that. Nothing more.

The split from team-admin matters because:

- **Capability boundary.** A joiner cannot accidentally write to the team's shared `skills/` folder if the authoring skill isn't installed. The plugin enforces the boundary by what's *not* present.
- **Conversation cleanliness.** The install-team conversation doesn't have to navigate champion-vs-joiner branching. It's just the joiner flow.
- **Lean install.** No compliance briefing the joiner doesn't need. No provisioning step they can't use. No diagrams about admin domains that don't apply to them.

If a joiner later becomes the team's champion, they upgrade to team-admin (handled by `exfu:upgrade-from-team-to-admin` in T2-team-admin-plugin).

---

## How

### What this plugin contains beyond shared

- **`exfu:install-team`** — the install conversation skill. Builds on the lean `start.md` shape, adapted for: joining an existing team substrate, layering personal-only content on top, defaulting to git as the storage mechanism.
- **`git-substrate-sync`** — net-new skill for both team variants. Wraps git operations safely. Same source file shared with team-admin; bundled into both at build time.
- **`role-capture`** support — handled inside `install-team` as part of the about-me phase. The joiner captures their own role; this is identity-level context.
- **Team-related teaching artefact** — the personal-vs-team-skills diagram. Shared with team-admin.
- **Team plugin manifest** — declares contents, version, compatibility.

### Storage architecture

Git, identical to team-admin. The joiner clones the team's substrate repo (URL provided by their champion, possibly via the onboarding pack the champion's `team-onboard-member` skill produced). After cloning, `git-substrate-sync` handles all subsequent operations.

The joiner does not provision a repo. The repo already exists; their job is to connect to it.

### Personal vs team layers

Each team member has both:

- **A personal substrate** — local, private, not in the team's git repo. Holds `context/me/`, personal scopes, personal databases, scratch.
- **The team's shared substrate** — git-synced, shared with team members. Holds `context/team-x/`, shared scopes, shared databases, the team's customised skills folder.

Their personal `wow` skill points at both layers via its navigation map. Claude reads from whichever is relevant for the current conversation.

The personal-vs-team-skills diagram is the calibration moment for this concept; the install conversation reaches for it during the diagram step.

### Reading the onboarding pack

If the joiner's champion used `team-onboard-member`, the joiner will have an onboarding pack — typically a markdown doc with the team plugin download URL, the git remote URL, an intro to the team's conventions, and a preview of the install flow.

The install-team skill should ask early: "Do you have an onboarding pack from your team's substrate champion? If yes, paste it in or point me at it; I'll use it to personalise this install."

If the joiner has the pack, the install reads it and adjusts:
- Pre-populates the git remote URL.
- Surfaces the team's conventions during the relevant calibration moments.
- Shapes the buffet step around what the team uses.
- Mentions the champion by name when relevant.

If the joiner does not have a pack, the install proceeds with default flow but flags that the joiner should confirm details with their champion when uncertainty arises (e.g. naming conventions, where personal vs shared content lives).

### Install conversation shape

Skeleton mirrors install-solo with team-specific adjustments:

- **Diagram step.** Show the substrate diagram and the personal-vs-team split. Two artefacts.
- **Onboarding-pack step.** "Do you have a pack from your champion?"
- **About-me beat.** Includes role-capture (joiner's own role). If the team's `context/team-x/role-conventions.md` exists in the cloned substrate, surface its conventions to the joiner.
- **Storage step.** Clone the team repo using the URL from the onboarding pack (or ask if no pack). Walk through `git-substrate-sync` so the joiner understands pull-before-write and commit hygiene.
- **Personal-layer step.** Set up the joiner's personal substrate (local folder structure for `context/me/`, personal scopes, etc.) parallel to the team's shared one.
- **Buffet step.** Same shared-skills options as solo. Plus connection points to team-shared scopes (read-only or contribute-via-PR depending on the team's git access model).
- **Wow generation.** `exfu:create-wow` with navigation map pointing at both personal and team layers.
- **Close.** Update notes; pointer to the team-admin contact for help; pointer to the team's conventions doc for ongoing reference.

### What the team plugin does NOT do

Worth being explicit:

- It does not provision the team's git repo. The champion did that.
- It does not let the joiner write to the team's shared `skills/` folder. (They can write to it via raw git commands, but the team plugin gives them no skill for doing so. The team's git access model — branch protection, PR review — is the real enforcement layer.)
- It does not ship the compliance briefing. The champion has that.
- It does not include admin-only diagrams.

If the joiner finds themselves wanting any of the above, they're probably on their way to becoming the team's champion. That's the path that triggers the upgrade to team-admin.

### Migration path

Joiners coming from the fetch model (rare for team installs but possible) use `exfu:migrate-from-fetch-model` (designed in T2-solo). Same skill works for any plugin variant.

---

## What — components inventory

### `exfu:install-team` (new design, content adapted from start.md + team-considerations.md)

Skill body builds on lean `start.md`. Joiner-flavoured opening: "this is the team plugin, you're joining a team that already has its substrate set up." Onboarding-pack reading early. Storage default git, clone existing repo (no provisioning). Role-capture as a deliberate beat.

### `git-substrate-sync` (new design, substantial — shared with team-admin)

Wraps git operations for substrate use. See T2-team-admin-plugin for full description. Same source file; bundled into both team plugin variants at build time.

For the team plugin, the relevant subset of behaviour:

- Pull at session start.
- Stage and commit personal changes (the joiner's own personal substrate is local and not in the team repo, so most personal work doesn't trigger git).
- Stage and commit changes to shared substrate when the joiner makes them (e.g. updating a shared scope's database).
- Push after substantive shared changes.
- Detect and surface merge conflicts for shared substrate edits.

### Team plugin manifest

Declares contents, version, compatibility. Per `T2-build-and-distribution.md`.

### Personal-vs-team-skills teaching artefact

Shared with team-admin. Ships in both.

### Migration support

`exfu:migrate-from-fetch-model` from T2-solo applies.

---

## T3 candidates

- `T3-install-team-skill.md` — design and write the install-team skill, including the onboarding-pack reading and the joiner-flavoured beats.
- `T3-git-substrate-sync-skill.md` — shared with T3 of team-admin; design once, bundle into both.
- `T3-team-plugin-manifest.md` — manifest assembly per plugin format.

Run order: `git-substrate-sync` is the shared dependency. Once it's designed, the install-team skill can wrap around it. Manifest follows the plugin-format research.

---

## Open questions

- **Git access model.** Most teams will give all members read-write access to the substrate repo. Some will use branch protection requiring PR review for shared changes. Should the install-team skill detect or ask, and adapt the git-sync flow accordingly? Probably yes — surface as a "is your team's repo direct-push or PR-required?" question early.
- **Onboarding pack format.** Markdown is the assumption. Worth confirming once team-admin's `team-onboard-member` skill is firm.
- **No-pack flow.** When the joiner has no onboarding pack, what's the minimum information needed to proceed? Git remote URL is essential. Team conventions doc is highly desirable but can be read from the cloned repo. Champion's contact is helpful but not blocking. Worth a clear "minimum to start" definition.
- **Read-only mode.** Some joiners (e.g. interns, contractors) may have read-only access to the team substrate. Should the team plugin support this gracefully? Probably yes — the git skill should detect read-only and adjust (no commit attempts, all changes are local-only). Flag for T3.
- **Multi-team membership.** A user on two teams (e.g. a manager spanning departments) needs two team substrates. Out of scope for v1; the team plugin assumes one team. Flag for future.
- **Mobile and scheduled tasks under git.** Same trade-off as team-admin. Mobile sessions probably read the local clone via Box-style MCP if the joiner syncs the clone; surface the trade-off, don't pretend it's solved.
- **Coexistence with solo plugin.** What if the joiner already has the solo plugin installed (their personal Claude setup) and is now joining a team? Probably the team plugin coexists fine — the personal substrate is already there, the team layer is added on top. The `wow` navigation map points at both. Worth verifying no skill name collisions in T3.
