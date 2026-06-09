# T3 -- Substrate, WoW, and guides skill rewrite

Rewrite the session bootstrap chain (substrate skill, exfu-create-wow, exfu-guides) for the v0.3 scope-based model.

**Parents:** `T2-shared-skills-and-resources.md` (domain), `M2-substrate-redesign.md` (milestone, phase 2)
**Prerequisites:** T3-convention-base (phase 1, complete). Can run in parallel with other phase 2 T3s.
**Status:** not started.

---

## Why

The substrate skill loads at the start of every session. It finds the substrate, reads the user's ways-of-working, orients to the structure, and pulls in scope context. Currently it does this by looking for orgs/, teams/, and README.md files. None of that exists in v0.3.

The wow generator creates a personal skill that maps the substrate layout. It currently references v0.2 directories. The guides skill explains the architecture to curious users. It currently explains the wrong architecture.

All three skills touch every session. Getting them wrong means every session starts confused.

---

## What to build

### 1. Substrate skill rewrite

The substrate skill is the most-loaded skill in the plugin. Its job doesn't change, but its implementation does:

**Current (v0.2):**
- Find substrate root (look for exfu/ or _meta/)
- Read wow skill for orientation
- Detect orgs and teams via directory structure
- Read scope context from scope.md (old format) and README.md files
- Surface git verbs for team substrates

**New (v0.3):**
- Find substrate root (look for exfu/ directory)
- Read wow skill for orientation
- Read the global index (`exfu/derived/index.json`) for whole-substrate picture
- Resolve user's exfu version from latest pointer
- Read user/ scope for personal context and preferences
- Navigate scopes via the index (not by walking the filesystem)
- For a specific scope: read scope.md (new format), load relevant agent.md files via Follows: references, apply local deviations
- Surface git verbs for team substrates (unchanged)
- Surface librarian health if the registry exists

**Key change:** the index is the primary navigation tool. Instead of walking directories, the substrate skill reads one JSON file and knows the whole map. It only reads individual scope files when it needs depth.

### 2. WoW generator rewrite

`exfu-create-wow` generates a personal skill installed as the user's always-loaded skill. It needs to:

- Map the substrate layout using v0.3 structure (exfu/, user/, scopes/)
- Reference the convention base version
- Point to the substrate skill for runtime orientation
- Include personal preferences from user/context/ and user/ontology/
- Be lean: the wow skill is loaded every session, so it must be concise

**Current wow template references to update:**
- `orgs/` -> `scopes/`
- `teams/` -> removed (scopes handle all nesting)
- `_meta/` -> `exfu/derived/`
- Scope detection by README.md -> scope detection by scope.md
- Storage backend references (unchanged, still Box or git)

### 3. Guides skill rewrite

`exfu-guides` answers "how does this work?" questions. It needs to explain:

- What a scope is (bounded working context, not an org chart)
- How nesting works (scopes/ subdirectory, parent declaration)
- What the convention base is (exfu/v0.3/, the defaults your scopes reference)
- What folder-types are (the 10 standard types, what each is for)
- What store-or-point means (data here or pointer to a tool)
- What librarians are (autonomous maintenance, nightly index as the example)
- How versioning works (side-by-side versions, pinning, migration)
- What the dashboard shows (when M2.1 ships)

The guides skill is reference material, not a tutorial. It answers questions; it doesn't walk users through a process.

### 4. Cross-references

The three skills reference each other:
- Substrate skill delegates to wow detection, loads the wow skill at session start
- Wow skill points to the substrate skill for runtime orientation
- Guides skill explains what the other two do

All three must be updated together to avoid inconsistency.

---

## Acceptance criteria

1. Substrate skill correctly orients in a v0.3 substrate (reads index, resolves versions, navigates scopes)
2. Substrate skill falls back gracefully if the index doesn't exist (walks filesystem like before)
3. Wow generator produces a skill that correctly maps v0.3 substrate layout
4. Guides skill explains v0.3 concepts accurately and in plain language
5. All three skills are internally consistent (no references to v0.2 concepts)
6. A user starting a new session with a v0.3 substrate gets correct orientation without errors
7. A user asking "how does this work?" gets accurate, helpful explanations

---

## Files to modify

- `plugin/src/shared/skills/substrate/SKILL.md` + content
- `plugin/src/shared/skills/exfu-create-wow/SKILL.md` + content
- `plugin/src/shared/skills/exfu-guides/SKILL.md` + content
- `plugin/src/shared/resources/` -- any resource files these skills reference

---

## Where this plan lives

- This file: `plugin/planning/T3-substrate-skill-rewrite.md`
- Domain: `plugin/planning/T2-shared-skills-and-resources.md`
- Milestone: `plugin/planning/M2-substrate-redesign.md`
