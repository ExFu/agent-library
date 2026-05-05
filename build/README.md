# ExFu plugin build

Assembles the three distributable ExFu plugins from the shared + variant sources in `plugin/src/`.

## Usage

```bash
# Build one variant
./plugin/build/build.sh solo
./plugin/build/build.sh team
./plugin/build/build.sh team-admin

# Build all three
./plugin/build/build.sh all

# Build and produce versioned tar.gz archives
./plugin/build/build.sh all --dist
```

Output lands in `plugin/build/output/<variant>/` — a ready-to-install plugin directory matching the Claude Code plugin spec (`.claude-plugin/plugin.json` manifest at root, `skills/`, `scheduled-tasks/`, `templates/`, `resources/`, `scripts/` as applicable).

With `--dist`, versioned archives are written to `plugin/build/dist/<plugin-name>-vN.M.P.tar.gz` where the version comes from the variant's `plugin.json`.

## What the build does

For each variant it: cleans the output directory, copies `plugin/src/shared/` content, overlays `plugin/src/<variant>/` content (variant wins on conflicts), validates that every skill has a `SKILL.md` with YAML frontmatter, validates the manifest JSON, then optionally packages a tar.gz. The one variant-specific rule is that `git-substrate-sync` (a shared skill) is excluded from the solo plugin — it ships only in team and team-admin.

The script requires no external tools beyond `bash`, `cp`, `find`, and either `jq` or `python3` for JSON validation (both are standard on macOS and most Linux environments).

## Release workflow

1. Bump `version` in `plugin/src/<variant>/.claude-plugin/plugin.json`
2. Run `./plugin/build/build.sh <variant> --dist`
3. Smoke-test the output in `plugin/build/output/<variant>/`
4. Copy the archive from `plugin/build/dist/` to `public/install/` for distribution
