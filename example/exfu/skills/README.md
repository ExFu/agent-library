# exfu/skills/

## Purpose

Skill-definitions ExFu ships. Provider-agnostic at the definition layer; rendered into a target platform (Claude Code skill, Cowork skill, Gemini gem, etc.) at use time.

## Contents

(Empty in this example.)

In a real install this would carry the ExFu-shipped skill definitions: `exfu-start`, `exfu-guides`, `exfu-create-wow`, `setup-reminders`, `setup-inbox`, `setup-writing-styles`, `box-filesystem-management`, `git-substrate-sync`, etc. Each as a folder with a `definition.md` (the provider-agnostic shape) and per-target rendered outputs as they are produced.

## Shape of a skill definition (sketch)

Each `<skill-name>/` subfolder would contain:

- `README.md` — what this skill does.
- `agent.md` — the skill convention snapshot.
- `definition.md` — the provider-agnostic skill content (description, trigger guidance, body in plain markdown without platform-specific syntax).
- `rendered/` — generated outputs for specific targets (e.g. `rendered/claude.skill`, `rendered/gemini-gem.json`).

The renderer is a separate concern (T2-E in the v0.3.0 plan). The definition is portable; the rendered output is per-platform.

## Why this is empty in the example

The example is about substrate *shape*, not the v0.2.x → v0.3.0 skill migration. T2-E is where the actual skill-definition shape and the renderer pattern get worked out. Until that lands, this folder shows the placeholder.

## Dependencies

- T2-E (portable skill-definitions) in the v0.3.0 plan.
- The current v0.2.x skills in `plugin/src/shared/skills/` and `plugin/src/{solo,team,team-admin}/skills/` are the input material; T2-E migrates them.
