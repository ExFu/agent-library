# Cross-cut: Extension and wrapping

## Why

ExFu is a universal substrate plugin. It cannot make implementation decisions that vary org-by-org, install-by-install, or provider-by-provider. Many real-world specifics — which git provider, what PII storage looks like, which connectors exist, what permission model the org uses, what regulated data needs special handling — sit outside ExFu's scope by design.

Without an explicit pattern for who decides what, every new requirement looks like a candidate for a cross-cut spec or a new T2 plan. That would slowly turn the plugin into either a) prescriptive about things it can't responsibly prescribe (and brittle when orgs deviate), or b) bloated with optionality that no single user needs.

The pattern: **ExFu provides the shape; the wrapping plugin or the installing Claude resolves the specifics.** This document captures that principle so future planning, T2/T3 work, and v-bumps stay honest about what's ExFu's job and what isn't.

## How

### Three layers of decision

There are three places a decision can land:

1. **Inside ExFu** — universal, ships in every install, reasonable across all orgs and contexts.
2. **In a wrapping plugin** — an org-specific (or vertical-specific, or client-specific) plugin that depends on ExFu and adds the org's own conventions, integrations, and constraints. This is the most likely shape for any org that runs ExFu at scale.
3. **In the installing Claude (i.e. the install conversation itself)** — captured during install via questions to the user, written into their personal `wow`, scopes, or context. Right when no wrapping plugin exists yet, or for one-off variance.

A decision belongs in ExFu only if all three of these are true:
- It applies broadly across orgs and use cases (not provider-specific, not vertical-specific).
- The right answer is well-established and unlikely to vary.
- ExFu would be wrong without it (i.e. it's a defining feature of the substrate model, not a flavour).

Anything else lives in the wrapping plugin or the install conversation.

### What ExFu owns

ExFu is responsible for:

- The substrate model and its conventions (folder layout, naming, the four ingredients, the discoverability principle).
- The install conversation shape (how we calibrate, demonstrate, and hand off to working substrate).
- The bedrock skills and templates (substrate, wow template, scope-skill template, skill-packaging, etc.).
- The teaching artefacts and guidance content.
- The contract shape that wrappers and install conversations resolve against (e.g. "the substrate skill expects a permission lookup function to surface admin verbs; here's the function signature, here's the fallback if it returns null").
- The brand-voice rules and the principles that govern how skills should behave.

### What the wrapping plugin provides

A wrapping plugin (e.g. `acme-exfu`) typically provides:

- Org-specific git provider integration (which provider, which API, which auth pattern).
- Org-specific PII layer connector (which database, which schema, which access-control model).
- Org-specific scopes, databases, conventions, and shared skills.
- Org-specific compliance briefing additions on top of ExFu's generic one.
- Org-specific brand voice overrides (where they exist) layered on top of ExFu's voice rules.
- Org-specific onboarding-pack templates.

The wrapping plugin lists ExFu as a dependency and adds its layer on top. The install conversation runs ExFu's install entrypoint, then the wrapper's install entrypoint adds the org-specific beats.

### What the installing Claude resolves

When no wrapping plugin exists, the install conversation captures the same kinds of org-specific decisions inline, into the user's personal substrate:

- Asks the user which git provider their team uses; writes the answer into the user's `wow` navigation map and the team substrate's `_meta/`.
- Asks whether PII handling is needed for this user's work; if yes, walks them through configuring a connector or skipping if there's no infrastructure for it yet.
- Captures any org-level conventions the user mentions; promotes them into the team's shared substrate when there is one.

The installing Claude's job here is to ask the right questions and write the answers into durable places. It doesn't invent the org's policies.

### Surfaces this pattern applies to

Currently identified surfaces where ExFu provides shape and the wrapper or installing Claude resolves specifics:

- **Git provider integration.** ExFu's `git-substrate-sync` is provider-neutral; provider-specific provisioning and permission lookups are wrapper or install-time decisions.
- **PII layer.** ExFu defines the principle (PII never persisted in shareable substrate, accessed via a guarded connector at runtime). The connector's schema, access-control model, audit logging, and reference implementation belong to the wrapping plugin.
- **Permission-aware skill behaviours.** ExFu's substrate skill (v0.2.0+) expects a permission lookup; what that lookup returns and how it integrates with the org's identity system is the wrapper's job.
- **Storage backends beyond the defaults.** ExFu ships Box for solo and git for team. Anything else (Mac-mini-as-server, Obsidian Sync, S3, on-prem NFS) is wrapper or install-time territory.
- **Compliance briefings.** ExFu ships a generic ISO 27001 briefing in the team-admin plugin. Vertical-specific briefings (HIPAA, FCA, SOC 2, GDPR specifics, on-prem regulator briefings) belong to the wrapper.
- **Org-specific verb vocabulary.** ExFu's non-techie verbs (save / share for review / check for updates) are universal defaults. An org can override them in their wrapping plugin if their culture wants different language.
- **Specific scope patterns.** ExFu provides the scope-skill template; the org's actual scopes (what scopes typically look like, naming conventions, default contents) are wrapper territory.

This list is not exhaustive. New surfaces will appear; the test is the same: does it vary org-by-org? If yes, it's not ExFu's call.

### Guardrails

What ExFu does NOT delegate to wrappers or install conversations:

- The principle of universal vocabulary in ExFu's own docs and skills (no client-specific names, no specific git provider in stock content).
- The hygiene rules around PII, credentials, and regulated content (these are non-negotiable defaults; wrappers can tighten them but not relax them).
- The brand voice banlist (wrappers can add to it but should not relax it).
- The substrate model's structural conventions (the folder layout, the four ingredients, the discoverability principle). Wrappers can add their own subfolders, but the top-level shape is ExFu's.
- The plugin format itself (manifest shape, build pipeline conventions). Wrappers consume the format, they don't redefine it.

### How wrapping plugins should be built (sketch)

Out of strict scope for this cross-cut, but worth flagging: a wrapping plugin is itself a Claude Code plugin that lists `exfu-solo` (or `exfu-team`, or `exfu-team-admin`) as an upstream dependency. It adds its own skills, resources, and install-conversation extensions. It does not fork ExFu; it composes with it.

When the wrapping pattern matures into something concrete (likely during the first paid engagement that produces a real org-specific wrapper), it warrants its own how-to doc as a separate ecosystem reference. For now, this cross-cut just establishes the principle.

## What

This cross-cut is the durable anchor for the principle. It does not describe a workstream of its own — it constrains other workstreams.

Concrete uses:

- The v0.2.0 plan (`v0.2.0-substrate-revision.md`) references this when explaining why the PII layer ships as a principle rather than a reference implementation, and why the permission-aware substrate skill ships as a contract rather than a per-provider integration.
- Future T2 and T3 plans should check against this cross-cut when scoping: if a deliverable looks like it requires per-org specifics, the deliverable as written probably belongs to the wrapping plugin, not to ExFu.
- New cross-cuts that propose org-specific specs are red flags; this cross-cut is the pre-emptive answer.

## Open questions

- **How does the wrapping plugin compose with ExFu's install entrypoints at runtime?** The Claude Code plugin spec's behaviour around dependent plugins and skill-namespace overlap needs verification (research file pending). The principle is "wrapper layers on top of ExFu"; the mechanics are TBD.
- **How does the installing Claude know whether a wrapping plugin is present?** The substrate skill probably needs a small lookup that surfaces "this install has a wrapper named X with conventions Y" so downstream skills behave consistently. Worth a small T3 in the v0.2.0 implementation pass.
- **What's the upgrade path when a wrapper publishes a new version?** Same considerations as ExFu's own version updates, but with the additional dimension that the wrapper's substrate skill behaviour may change. Probably handled per-wrapper rather than centrally.
