# Cross-cut: Plugin distribution and updates

## Why

Both plugins ship as installable packages. How they're packaged, where they're hosted, how users discover them, and how they update once installed are decisions that shape the user experience and the maintenance burden on Alastair. Get this wrong and we're hand-delivering zips to clients forever; get it right and the plugins update themselves cleanly as ExFu evolves.

This is also a corporate-friendliness consideration. Corp networks that block fetches from arbitrary URLs are the original reason we're going to plugins. The distribution mechanism has to work even when the only allowed move is "download a file once, install it locally".

## How

### Format: Anthropic plugin format

Use the format Anthropic ships for Claude Code / Cowork plugins. Single packaged file containing skills, scheduled tasks, slash commands, MCP definitions, and resources. Versioned via the manifest.

Specifics to confirm during the dedicated research pass (see `research/`):
- Exact format and manifest schema
- Where plugins are normally installed from (Anthropic's marketplace, custom URLs, local files)
- Update mechanism — does the user's Claude check for updates automatically, or is updating manual
- Permissions and capability declarations
- Compatibility across Cowork / Code / mobile / web

### Distribution channels (in order of preference)

1. **Anthropic plugin marketplace** if it exists and accepts third-party submissions. Best UX for the user; centralised update mechanism. Worth checking what's possible.
2. **Direct download from a website page** — the canonical fallback. User downloads the `.plugin` file, opens or imports it in Claude. Works in restricted networks. Requires the user to manually update (download new version, install over old). A page on `exfu.ai` (e.g. `exfu.ai/install`) hosts the latest build of each plugin, with versioned archives behind for rollback or pinning.
3. **Package manager / git source** — a more developer-flavoured option. Worth exploring for the team plugin where a team champion may want to pull from a specific tag in a git repo. Less relevant for solo users.

### Update model

For v1, manual updates from a download page is fine. The plugin manifest carries the version; the user (or their Claude) can check the current version on the website and decide whether to upgrade.

If Anthropic's plugin system supports automatic update notifications, we use that. Otherwise we add a small scheduled task (or a check baked into the `exfu` orchestrator skill) that compares the installed plugin version against the published version once per week or month and surfaces a nudge.

Important: plugin updates ship templates, skills, and stock content. The user's *personal* substrate — their `wow`, their `context/me/`, their scopes, their databases — are not touched by a plugin update. This separation is worth making explicit so users don't fear updating.

### Versioning

Semantic versioning: major.minor.patch. Breaking changes (file paths moving, skill names changing, conventions diverging) require a major bump and a migration path. Minor bumps add features. Patches fix bugs.

Each plugin is versioned independently. Solo plugin and team plugin can be on different versions without coupling.

### Build and source

Source lives in `plugin/src/` (canonical, human-editable markdown and assets). A build step packages it into the Anthropic plugin format. The build output goes into the website's `public/` so it's served as a download. Both source and built plugin live in the `exfu_website` repo.

Build automation can come later. For v1, a documented manual build step is enough.

## What (initial)

- Plugin format and conventions: research file pending in `research/plugin-format.md`.
- Distribution: dedicated download page on `exfu.ai`. URL TBD (`/install`, `/plugin`, `/download`?).
- Versioning policy: semver, per-plugin.
- Build: source → built plugin → published. Manual for v1, automatable later.

## Open questions

- Does Anthropic operate a plugin marketplace that accepts third-party submissions? If so, what are the requirements?
- What's the size limit on a plugin file? Affects whether we can bundle PNG diagrams and reference docs liberally.
- Is there an update-notification mechanism we can hook into, or do we need to roll our own?
- Should the team plugin's distribution be different — e.g. a team champion downloads once and serves it internally to team members from their own intranet? Probably useful for very locked-down corps.
- When breaking changes happen, what's the migration path? Probably a "what changed in this version" page on `exfu.ai` plus a one-time migration skill bundled in the plugin.
