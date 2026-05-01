# T2 — Build and distribution

The pipeline from source to installed plugin: build process, packaging, distribution channel(s), versioning, update notification, archives.

Anchors back to: `T1-overview.md`, `cross-cut-plugin-distribution.md`.

---

## Why

The whole point of moving to plugins is reliable distribution into restricted environments. If the build pipeline is fragile, or distribution is awkward, the plugin model fails on its core promise. This T2 designs how source becomes a downloadable file the user (or their org's IT team) can install with confidence.

It's also the substrate maintenance story for ExFu. As the plugins evolve, releasing new versions has to be smooth enough that updates happen often. Friction here means stale plugins in the wild.

---

## How

### Build pipeline shape

Source layout (per `T2-shared-skills-and-resources.md`):

```
plugin/src/
  shared/
    skills/
    scheduled-tasks/
    templates/
    resources/
  solo/
    skills/
    scheduled-tasks/
    manifest.json
  team/
    skills/
    resources/
    manifest.json
```

Build script reads `plugin/src/shared/` and `plugin/src/<variant>/`, merges them per the variant's overlay rules, packages into the Anthropic plugin format. Output:

```
plugin/build/
  exfu-solo-vN.M.P.plugin
  exfu-team-vN.M.P.plugin
```

The build is reproducible — same source produces the same output. Worth keeping deterministic so users can verify their installation if needed.

### Build automation: minimal for v1

V1 is a documented manual build: a script (Bash or Python — pick whichever is simpler given Anthropic's plugin tooling) that:

1. Validates source — checks every skill has a `SKILL.md`, every scheduled task has a `TASK.md`, the manifest is valid, no missing references.
2. Assembles the plugin file from `shared/` + `<variant>/`.
3. Versions the output filename per the manifest.
4. Writes a brief build log.

Author runs it locally before releasing. If it grows in complexity, automate via GitHub Actions later.

### Distribution channels

Primary (v1): direct download from `exfu.ai`. A page (URL TBD — `/install`, `/plugin`, `/download`) hosts the latest build of each plugin with versioned archives behind. Pure static-file serving — no auth, no API, works in any network that allows outbound HTTPS to `exfu.ai`.

Secondary (research-pending): Anthropic plugin marketplace if they operate one and accept third-party submissions. If yes, list there too — better discoverability, potentially better update mechanism. The download page stays as the canonical fallback for restricted networks.

Tertiary (defer): direct git source for technical teams who want to build the plugin themselves from a tagged release. Useful for very locked-down corp environments where even downloading binary files is restricted, and for teams who want to verify what's in the build. Out of scope for v1, flag as natural extension.

### Versioning

Semantic versioning per plugin, independently:

- **Major.** Breaking changes. Skill names changing, file paths moving, manifest format incompatible. Requires a migration path documented in release notes.
- **Minor.** Feature additions. New skills, new scheduled tasks, new resources, expanded capabilities. Backward-compatible.
- **Patch.** Bug fixes. Tightening a skill body, fixing a typo, updating an external link.

Solo and team plugins version independently. Solo can be on v1.3.0 while team is on v0.4.2 if their release cadences differ.

### Manifest content

Pending plugin-format research, but expected to declare:

- Plugin name (`exfu-solo`, `exfu-team`).
- Version (semver).
- Description (one-liner).
- Author (Alastair Whaley / WhaleyBear Ltd / ExFu).
- License (TBD — probably permissive but not necessarily open-source; needs decision).
- Components: skills, scheduled tasks, resources, with paths.
- Compatibility: minimum Claude version, required surfaces (Cowork required), optional ones (mobile, scheduled tasks).
- Dependencies on Anthropic features (MCP for connectors, etc.).

### Update mechanism

For v1, manual updates via download:

- The user (or their Claude) checks the version on `exfu.ai` against their installed version.
- If outdated, they download the new plugin file and install over the old.
- The plugin install replaces bundled skills, scheduled tasks, and resources. User's personal substrate is untouched.

A small scheduled task or skill behaviour can surface the version check automatically — e.g. once a week, the orchestrator skill checks the published version and nudges the user if they're behind.

If Anthropic's plugin system supports auto-update notifications natively, hook into that. Otherwise the scheduled-task-based check is fine.

### License decision

Defer, but flag. The plugin contains:

- Skills authored by ExFu.
- Reference content (substrate guide, primer) authored by ExFu.
- Diagrams (some by ExFu, some borrowed-with-credit).
- Possibly bundled third-party content (the `cleanup.py` script, attribution to anything else).

A permissive license that lets users install and run, but doesn't grant commercial redistribution rights, is the likely shape. Worth a research pass when v1 is closer.

### Release process

Tactical, for each release:

1. Bump version in the relevant plugin's manifest.
2. Add changelog entry to the plugin's `CHANGELOG.md`.
3. Run the build script.
4. Validate the output (install locally, run a quick smoke test).
5. Copy the built plugin to `public/install/` (or wherever the download page reads from).
6. Update the download page's "current version" indicator.
7. Commit and push.

Once this process feels routine, automate via a make target or release script.

### Migration mechanics

Major-version bumps require migration logic. Per `T2-solo-plugin.md` and `T2-team-plugin.md`, an `exfu:migrate-from-fetch-model` skill handles the v1 case (legacy fetch-model installs). Future major bumps need their own migration skills, named per the from-version (e.g. `exfu:migrate-v1-to-v2`).

---

## What — components inventory

### Build script

Location: `plugin/build/build.sh` (or `.py`). Inputs: source folder, target variant (solo or team). Output: built plugin file.

Validates, assembles, writes to `plugin/build/output/`. Idempotent.

### Distribution page

Location: `public/install/index.astro` (or wherever the existing site convention puts it). Content:

- Brief explanation: what the plugins are, who each is for.
- Download buttons: solo and team, latest versions.
- Version indicators visible.
- Archive links to previous versions.
- Quick-start instructions: download, install in Claude, run `/exfu`.
- Link to the substrate primer for users who want to read first.

Static HTML, simple and reliable.

### Versioned archive

Location: `public/install/archive/`. Holds previous versions of each plugin so users can pin or roll back. Naming: `exfu-solo-vN.M.P.plugin`.

### Release process documentation

Location: `plugin/RELEASING.md`. Documents the manual release process so it's repeatable. Update as automation grows.

### Update-check mechanism

Either built into the orchestrator skill (light-touch version check at session start, throttled to once a week) or a dedicated scheduled task. Probably the orchestrator-level approach is cleaner — fewer moving parts.

---

## T3 candidates

- `T3-build-script.md` — design and write the build script.
- `T3-distribution-page.md` — design and build the download page on `exfu.ai`.
- `T3-versioning-and-changelog-conventions.md` — formalise the versioning rules and changelog structure.
- `T3-update-check.md` — design the update-check behaviour (in orchestrator vs scheduled task).
- `T3-release-process.md` — write `RELEASING.md`.
- `T3-license-decision.md` — research and decide on the plugin license.

Most can run in parallel. License decision is independent. Update-check depends on the orchestrator skill design landing first (T3 of T2-shared).

---

## Open questions

- **Anthropic plugin marketplace.** Does it exist for third-party plugins? What does listing require? Pending research file.
- **Plugin file size limits.** Affects whether we can liberally include PNGs and reference docs. Pending research.
- **Auto-update support.** Native to Anthropic's plugin system, or do we roll our own? Pending research.
- **License.** Permissive but not commercial-redistribute? Plain MIT? Custom? Worth a small research / decision pass.
- **Validation rigour.** How thoroughly should the build script validate before producing output? V1 minimum: every skill has a SKILL.md, every scheduled task has a TASK.md, manifest parses, all referenced paths exist. More sophisticated checks can land later (e.g. cross-skill reference validation, lint for banlist words in shipping content, etc.).
- **CI/CD on plugin builds.** Worth setting up GitHub Actions to build on every commit? Useful for catching breaks early, but may be overkill for v1. Defer.
- **Plugin signing.** Is there a mechanism for signing plugin files so users can verify authenticity? Probably out of scope until Anthropic supports it natively.
