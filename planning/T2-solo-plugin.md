# T2 — Solo plugin

The plugin for individual users — founders, senior operators, professionals working alone, the AuDHD-flavoured second-brain seekers — installing Claude as a real working collaborator for themselves.

Anchors back to: `T1-overview.md`, `T2-shared-skills-and-resources.md`, `cross-cut-storage-architecture.md`, `cross-cut-brand-voice.md`.

---

## Why

The solo install is the simpler of the two plugins, and the one most ExFu users will reach for first. It has to land cleanly on a single user with no team-context overhead, while still working in environments where outbound fetches to `exfu.ai` are blocked.

The current install model (fetch-and-package from `public/clients/`) works in friendly networks but breaks in restricted ones. The plugin solves distribution. The install conversation itself stays substantively the same as the new lean `start.md` — concrete-first, build-by-doing, chief-of-staff framing, many small wins. The plugin is the delivery vehicle, not a redesign of the install.

---

## How

### What this plugin contains beyond shared

Most of the plugin's content comes from `plugin/src/shared/` (see T2-shared). Solo-specific:

- **`exfu:install-solo`** — the install conversation skill. Body is essentially the lean `start.md` content, adapted to: (a) reference local plugin resources rather than fetching, (b) call `exfu:create-wow` rather than inlining wow generation, (c) hand off to the orchestrator at session start in fresh sessions.
- **`box-filesystem-management`** — the storage skill. Port from `public/clients/box-filesystem/SKILL.md` with light refresh.
- **`box-cleanup`** scheduled task — the daily `_DELETED_` collection and trash purge. Port from `public/clients/box-filesystem/CLEANUP-TASK.md` plus the `cleanup.py` script.
- **The solo manifest** — the plugin-format manifest declaring what the plugin contains, its version, dependencies. Content TBD pending plugin-format research.

### Storage decision: Box for v1, with eyes open

Per `cross-cut-storage-architecture.md`, solo v1 stays on Box despite the offline-caching pain. The install-solo skill should:

- Surface the offline-caching trade-off to the user *during* the install, not as a footnote. "Box has a known issue: if Box Drive is set to space-saver mode, files Claude tries to read may come back empty because Box hasn't downloaded them yet. Recommended: tell Box Drive to keep your knowledge base folder fully downloaded locally."
- Give the user a concrete instruction for how to force the knowledge base folder to stay fully cached locally (TBD: research correct Box Drive setting).
- Note in the user's `wow` navigation map that Box is the storage mechanism, so future-Claude knows the constraints.

### Detect-and-handle for non-Box environments

Some users may want to install the plugin without using Box. The install-solo skill should ask early — *"Where would you like Claude's knowledge base to live? Box is the recommended default; if your team mandates something else (Google Drive, OneDrive, Dropbox, local-only), we can work with that — flag any constraints now."*

For v1, only Box is fully supported. Other answers get a graceful response: "We'll set things up locally, but mobile and scheduled-task access from anywhere other than this machine won't work the same way. Worth coming back to once you have a clearer answer on how your team or setup wants to handle this." The substrate works locally; the cloud-sync layer is the part that requires Box.

### Install conversation shape

The install-solo skill body inherits from the current lean `start.md`. Key adaptations:

- **Step 1 stays as-is** — open with the diagram, calibrate, plant teach-don't-do and why-before-what.
- **Step 2 (about-me)** — same as today. The team-considerations.md check becomes: if user reveals team membership, fetch `{{plugin_root}}/resources/team-considerations.md` and fold in. (Note: in the plugin world, this content is already local. No URL fetch.)
- **Step 3 (buffet)** — same as today.
- **Step 4 (demonstrate)** — same. Each install move now references local skills rather than fetching them.
- **Step 5 (close)** — same, plus a small new beat: tell the user about plugin updates. "When ExFu publishes a new version of the plugin, you'll be able to update via [mechanism]. Your personal substrate (your wow, your context, your scopes) won't be touched — only the bundled templates and skills."

### Migration path for existing ExFu users

Some users are already installed via the fetch model. They need a smooth path to the plugin model. The install-solo skill should detect this case (e.g., `wow` skill already present, substrate folder structure already in place) and offer a one-time migration:

- "Looks like you already have an ExFu setup. The plugin will replace your bundled skills with the plugin-managed versions, but won't touch your personal content. Confirm to proceed."
- Map old fetched-skill installations to plugin-managed ones (delete the old, install the new from the plugin).
- Update the `wow` navigation map to note the plugin-managed source.
- Confirm everything still works.

This logic probably warrants its own small skill: **`exfu:migrate-from-fetch-model`**, callable by `exfu:install-solo` when migration is detected. Same skill pattern works for team plugin if any team users came in through the old route.

---

## What — components inventory

### `exfu:install-solo` (new design, content largely from existing `start.md`)

Skill body adapts the current lean `start.md`:

- **Replace** every URL reference (`https://exfu.ai/clients/...`) with local plugin paths or the `{{plugin_root}}` placeholder.
- **Remove** the `skill-packaging` walkthrough for built-in skills (they're pre-installed). Keep the `skill-packaging` skill itself in the plugin because the user will create new custom skills.
- **Add** the `exfu:create-wow` invocation at the wow moment, replacing the inline "fetch wow template, customise, package, present" flow.
- **Add** the migration-path detection at the start.
- **Add** the storage-mechanism question early in the install (Box default, but ask).
- **Add** a brief beat at the end about plugin updates and how user substrate is preserved across them.
- **Keep** the principles, hard constraints, voice, component catalogue, buffet, opening shape, external resources, and where-to-go-for-help sections roughly as today.

### `box-filesystem-management` (port)

From `public/clients/box-filesystem/SKILL.md`. Refresh:

- Remove URL-fetch references.
- Tighten the offline-caching note: explicit instruction for the user to keep the knowledge base folder fully downloaded locally.
- Carry the `_DELETED_` and `_trash/` conventions exactly as today.

### `box-cleanup` scheduled task (port)

From `public/clients/box-filesystem/CLEANUP-TASK.md` plus `cleanup.py`. Refresh:

- Path resolution: the script reads `{{plugin_root}}/scripts/cleanup.py` rather than expecting it in `_meta/` of the user's substrate. Or alternatively the plugin install copies `cleanup.py` into the user's `_meta/` folder during initial setup, matching today's behaviour. Research file pending on plugin convention.

### Solo plugin manifest

TBD pending plugin-format research. Will declare:

- Plugin name, version, description.
- Components included (skills, scheduled tasks, resources).
- Compatibility (Cowork required, mobile-aware where relevant).
- Dependencies on Anthropic features (MCP, scheduled tasks, etc.).

### `exfu:migrate-from-fetch-model` (new design, modest size)

Skill body:

- Detects existing setup signals (presence of `substrate` skill, `box-filesystem` skill, etc., installed via the old fetch model).
- Confirms with user before proceeding.
- Removes old skill installations.
- Installs plugin-managed equivalents.
- Updates `wow` navigation map.
- Verifies post-migration state.

---

## T3 candidates

- `T3-install-solo-skill.md` — adapt the lean `start.md` content into the install-solo skill body. Key call-out: ensure the migration check is the first move in the conversation, not buried.
- `T3-port-box-filesystem.md` — the port-and-refresh of the Box storage skill and cleanup task.
- `T3-migration-skill.md` — design and write `exfu:migrate-from-fetch-model`.
- `T3-solo-manifest.md` — the manifest assembly, post plugin-format research.

These can run in parallel except `T3-solo-manifest.md`, which needs the plugin-format research closed.

---

## Open questions

- **Storage alternatives evaluation.** The cross-cut lists candidates (direct local, Mac-mini + Obsidian Sync, etc.). Which is the v2 recommendation for solo? Track in `research/box-alternatives-for-solo.md` as solo users surface the offline-caching pain.
- **Box Drive caching configuration.** What's the exact setting for "keep this folder always available offline" in Box Drive on macOS / Windows? Needs a concrete instruction in the install-solo skill.
- **Migration detection precision.** False-positive migration prompts would be irritating. What's the most reliable signal that the user has an existing fetch-model setup? Probably presence of specific bundled skills installed via packaging rather than via plugin. Worth a check in T3.
- **Both-plugins-installed edge case.** A user who installs solo first, then later joins a team and installs team — what happens? The `wow` navigation map can carry both, but the install-solo and install-teams skills should detect the other and not overwrite anything. Coordination point with T2-team-plugin.
