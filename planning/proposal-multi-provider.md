# Proposal -- Multi-provider ExFu

**Status:** Proposal. Not yet adopted into the plan. Adoption, sequencing, and version
numbering are Alastair's decisions. On adoption this would spawn a
`cross-cut-provider-model.md`, updates to several existing T2s (substrate-architecture,
librarian-framework, build-and-distribution, website-changes, solo-plugin), and a new
milestone.

**Date:** 22 July 2026. Based on a same-day research pass across OpenAI, Google, and
cross-platform standards; sources and confidence flags in the appendix. The OpenAI
surface described here is two weeks old and churning -- re-verify before implementation.

---

## Why

ExFu's promise is that your substrate is *yours*: plain files in a folder you control,
outliving any vendor decision. Today the implementation contradicts the promise -- only
Claude can drive it. That was the right v0.3 scoping call, but three things have changed:

1. **The skills layer became an open standard and everyone adopted it.** Anthropic
   published Agent Skills (SKILL.md) as an open standard in December 2025. OpenAI's
   Codex reads it natively; the merged ChatGPT desktop app (9 July 2026) inherits it;
   Gemini's tooling implements it; so do Copilot, Cursor, and a long tail. The format
   ExFu is built on is no longer Claude-specific.

2. **The platforms are productising ExFu's category.** ChatGPT Work and Gemini Spark
   both bundle tasks + skills + schedules for knowledge workers. Competing on "we have
   skills and schedules" is a losing game against the vendors themselves. Competing on
   **vendor-neutrality** is not: their memory portability is one-time snapshot imports;
   ExFu's substrate is genuinely user-owned files. "Your brain in your folder, whichever
   agent you point at it" becomes the defensible position -- but only if it's true.

3. **Users mix providers.** Individuals hold two subscriptions; teams are heterogeneous
   by procurement accident if nothing else. A team substrate that only Claude users can
   work in is a real adoption blocker for the team variants.

**Why OpenAI first:** the 9 July merge made the ChatGPT desktop app a near-1:1 port
target -- same SKILL.md standard, a plugin + GitHub-marketplace model copied from Claude
Code's, a global `~/.codex/AGENTS.md` read every session, sandboxed local filesystem
access, and RRULE scheduled tasks. Available on every plan including Free. Gemini is
deferred: Antigravity CLI is technically viable but terminal-shaped (wrong audience),
and Spark -- the strategically interesting one -- is Ultra-only, US-only, and
Drive-object-gravity rather than plain files. Watchlist, not workstream.

---

## How

### Layer analysis

| Layer | Portability | Notes |
|---|---|---|
| Substrate (md/JSON files) | Already agnostic | The original bet holds. Access route varies (local FS vs connector). |
| Skills (SKILL.md) | Open standard | Port near-verbatim after a Claude-ism audit. |
| Connectors (MCP) | Open standard | Linux Foundation governed; per-surface gating varies. |
| Packaging | Per-vendor wrappers | Same anatomy, incompatible manifests. Mechanical, not architectural. |
| Session bootstrap | Per-vendor files | `~/.claude/CLAUDE.md` vs `~/.codex/AGENTS.md` vs `~/.gemini/GEMINI.md`. No cross-tool global standard exists. |
| Scheduled runners | Fully proprietary | Definitions port as markdown; registration and execution need per-provider adaptors. |

### Provider-agnostic core

Rewrite the convention base so nothing in the ontology, principles, folder-type
definitions, or librarian definitions mentions provider mechanics. The core speaks of
"your agent" and defines *what* must happen (a nightly index run, a registered schedule,
a bootstrap that loads wow). Anywhere the core needs a provider mechanism, it delegates.

**Provider adaptors** are a new convention-base area:

```
exfu/vNEXT/providers/
  claude.md
  openai.md
```

Each adaptor is agent instructions (consistent with the definitions-read-cold
philosophy) answering a fixed contract of HOW questions:

- Where the global bootstrap file lives and how wow gets wired into it.
- Where skills install; how the plugin is packaged and distributed.
- How to create/update/delete a scheduled task, and how ExFu cadences (nightly, weekly,
  hourly, on-demand) map onto the provider's scheduling primitives.
- How to run headlessly (for runners and CI-style execution).
- How the substrate is reached (local filesystem, synced-drive folder, or MCP
  connector) and any storage quirks.
- Sandbox/approval-mode posture and known platform quirks.

The claude adaptor absorbs what is currently baked in implicitly (Cowork scheduled
tasks, `~/.claude/CLAUDE.md`, plugin marketplace, Box MCP workarounds). The openai
adaptor documents the Codex-runtime equivalents (see OpenAI mapping below).

### Main and augmentor

A substrate declares its providers: exactly one **main**, zero or more **augmentors**.
Proposed home: a small installer-written config in `exfu/` (precedent: `latest.txt`),
e.g. `exfu/providers.json` -- placement and format are open decisions.

**Instruction files: pointer, not copy.** The main provider's file carries the real
instructions; each augmentor's file is a thin stub pointing at it.

- main = claude → `CLAUDE.md` contains the instructions; `AGENTS.md` is a stub:
  "Instructions for this project live in CLAUDE.md. Read that file now."
- main = openai → `AGENTS.md` contains the instructions; `CLAUDE.md` is the stub.

This is store-or-point applied to instruction files: one source of truth, no drift,
and every agent finds its expected entry file. Stubs are plain files, not symlinks
(symlinks do not survive cloud-drive sync reliably). The same pattern applies at every
level the pair exists -- substrate root, project directories, scope-level instruction
files if/when those exist.

**Scheduling default follows main.** When a user or agent registers a scheduled agent,
the main provider's mechanism is used by default. Explicit per-agent override to an
augmentor is always allowed ("run the nightly index under Claude, but this listings
scanner under ChatGPT"). Consequences:

- `exfu/derived/agent-registry.json` gains a `provider` field per registered agent.
- The runner model becomes one runner per cadence *per provider that has registered
  agents* -- and the nightly-index-style dedup rule must ensure a given agent is
  registered under exactly one provider at a time unless deliberately duplicated.
- Health checks (`agent-registry.json` status, the dashboard's librarian view) span
  providers.

**Sane defaults, maximum flexibility.** A single-provider user never sees any of this:
main defaults to whichever provider ran the install, no augmentor exists, no stub files
are written, behaviour is identical to today. An `add-provider` skill retrofits an
augmentor later: writes the stub, installs the counterpart plugin, extends the wow
wiring, and offers (never forces) migration of scheduled agents.

### Skills portability pass

Audit the ~25 shipped skills for Claude-isms: "Claude" as the agent's name where "your
agent" is meant, Cowork/claude.ai UI references, Claude-specific tool names, hardcoded
paths, and the experimental `allowed-tools` frontmatter. Provider-specific steps move
behind adaptor references ("register the schedule per your provider adaptor") rather
than inline instructions. Skills that are inherently provider-specific (e.g. Claude
plugin packaging mechanics) get marked as such and included only in the relevant
plugin build.

### Packaging and build

One source tree (already the build model), composed per provider at build time --
exactly the pattern T1 established for solo/team-admin/team, now with a second axis:

- **Claude plugin** -- existing format and marketplace.
- **OpenAI plugin** -- `.codex-plugin/plugin.json` bundling the same skills plus MCP
  config and (optionally) a SessionStart hook; distributed via a GitHub
  `marketplace.json` (no review gate), with the official Plugin Directory as a later
  channel.

`T2-build-and-distribution.md` grows a provider dimension; the website's download page
grows an "install for ChatGPT" path.

### OpenAI mapping (what the openai adaptor will say, in short)

- **Bootstrap:** wow content is generated into / referenced from `~/.codex/AGENTS.md`
  (read at every session start); a plugin-bundled SessionStart hook can make loading
  deterministic rather than instruction-dependent.
- **Skills:** user-level `~/.agents/skills` (and repo-level `.agents/skills`);
  invocation via `@`/`$` or implicit triggering.
- **Storage:** prefer the Box Drive synced folder as plain local filesystem under the
  app's sandbox (workspace-write). The Box *MCP* route and its workarounds are largely
  a Claude-surface concern and stay in the claude adaptor.
- **Scheduled agents:** desktop Scheduled Tasks (RRULE) running in the substrate
  directory, with the honest caveat that they only fire while the machine is awake and
  the app running; `codex exec` + cron/launchd as the headless fallback for users who
  want reliability.
- **Guided install:** Work/Codex modes support long agentic sessions that write files
  and create scheduled tasks from conversation -- the install-solo shape translates.

### What stays honest in positioning

- **Mobile:** ChatGPT mobile and web Chat mode get no skills, plugins, or filesystem.
  Claude currently remains the stronger mobile companion for a substrate. A
  main=openai user may still want Claude as augmentor for exactly this.
- **Scheduling reliability:** Claude's cloud-run scheduled tasks against the substrate
  are currently a genuine advantage; OpenAI desktop schedules die with the lid closed.
  Say so plainly in install conversations rather than papering over it.

---

## What -- indicative phasing

Phases, not commitments; sequencing is Alastair's.

**Phase 0 -- spike.** Hand-port wow + the substrate skill to a ChatGPT desktop test
install against a copy of the real substrate. Success criteria: skills load and
trigger; substrate reads/writes work through the Box Drive folder under sandbox; one
scheduled task runs a librarian definition unattended and logs to the registry; the
AGENTS.md bootstrap self-orients a cold session. Output: a research note in
`plugin/planning/research/` with findings and any spec corrections to this proposal.

**Phase 1 -- provider-agnostic core.** New convention-base version: scrub ontology,
principles, and librarian definitions of provider mechanics; author `providers/claude.md`
and `providers/openai.md`; extend the registry schema with `provider`; define the
per-provider runner and dedup rules; migration notes for v0.3-pinned scopes.

**Phase 2 -- skills pass and OpenAI packaging.** Portability audit across shipped
skills; OpenAI plugin wrapper; build pipeline emits both plugin artefacts; distribution
via GitHub marketplace.

**Phase 3 -- install flows.** Provider-aware `install-solo` (main = installing
provider); `add-provider` skill implementing main/augmentor wiring, stub files, and
optional schedule migration; first-run migration story for existing v0.3 installs.

**Phase 4 -- website and positioning.** Download/install paths per provider;
messaging shift to "your substrate, whichever agent you use"; the vendor-neutrality
story as the headline differentiator.

---

## Open decisions

1. **Version number** for the agnostic core (v0.4?). Alastair's call.
2. **Providers config**: placement (`exfu/providers.json`?), format, and whether
   per-scope main override is allowed or main is substrate-global. Recommend
   substrate-global first; per-scope override only if a real need appears.
3. **wow shape**: one generated wow emitted into each provider's bootstrap location,
   or a single wow file both bootstraps point at. The pointer pattern suggests the
   latter; the deterministic-hook option on OpenAI may favour the former.
4. **Cadence dedup**: exact rule preventing double-runs (e.g. nightly index registered
   under both providers by accident).
5. **Terminology**: "provider" vs "platform"; "main/augmentor" naming as user-facing
   language or internal-only (T1 principle: internal vocabulary stays internal).
6. **Team variants**: does main/augmentor extend to team substrates (per-member
   provider choice against a shared substrate)? Likely yes and likely potent for
   adoption -- but defer detailed design until solo lands.
7. **Sandbox posture**: an ExFu-recommended approval-mode configuration for OpenAI
   installs (safety vs friction).
8. **Gemini trigger conditions**: what would promote Spark or Antigravity from
   watchlist to workstream (e.g. Spark leaves Ultra/US-only; agy ships a consumer
   shell).

## Risks

- **Surface churn.** The merged ChatGPT app is weeks old; APIs, paths, and gating may
  shift under us. Mitigation: Phase 0 spike before any core rewrite lands; re-verify
  the appendix at implementation time.
- **Gating uncertainty.** Consumer (Plus/Pro) access to hosted ChatGPT Skills is
  unconfirmed; the desktop app path is confirmed on all plans and is the one we build
  on.
- **Double-run hazards** from two schedulers touching one substrate. The registry
  provider field and dedup rule are the mitigation; design them early.
- **Adaptor drift.** Two adaptors describing fast-moving platforms will rot.
  Mitigation: adaptors carry an "as-of" date and the deep-research-as-a-move pattern
  applies to them.
- **Support matrix growth.** Every install conversation branch doubles. Mitigation:
  sane-defaults principle -- single-provider installs remain identical to today.
- **Box divergence.** Box-via-MCP (Claude) and Box-via-Drive-folder (OpenAI) have
  different failure modes against the same substrate. The storage cross-cut should
  absorb this.

---

## Appendix -- platform capability snapshot (as of 22 July 2026)

**OpenAI / ChatGPT desktop (post 9 July merge).** One desktop app (macOS/Windows, all
plans incl. Free) with Chat, Work, and Codex modes sharing the Codex agent runtime:
Agent Skills (SKILL.md; `~/.agents/skills`), plugins (`.codex-plugin/plugin.json`) with
GitHub-based marketplaces and a reviewed Plugin Directory, global `~/.codex/AGENTS.md`
plus SessionStart hooks, sandboxed local filesystem (read-only / workspace-write /
full), RRULE Scheduled Tasks (desktop tasks can run in a local project directory but
need the machine awake; web tasks are cloud-run, connector-only, auto-pause without
engagement), `codex exec` for headless runs. Web Chat mode and mobile get none of
this. Workspace Agents (cloud-persistent) are Business/Enterprise-only. Custom GPTs
being phased out; Apps SDK folded into the Plugin Directory.

**Google.** Consumer Gemini CLI reportedly retired June 2026 in favour of Antigravity
CLI (`agy`), which keeps Agent Skills, GEMINI.md/AGENTS.md, MCP, and
extensions-as-plugins -- developer-shaped, quota-constrained on non-Ultra plans
(transition partially contested; geminicli.com docs remained live at time of
writing). Gemini app: native desktop app since April 2026; skills/schedules/custom
MCP exist only inside **Spark** (24/7 cloud-resident personal agent; accepts
Anthropic-format SKILL.md uploads; Ultra-only ~$250/mo, US-only, 18+; custom-MCP
writes require manual confirmation; gravity is Drive/Docs objects, not plain files).
Spark is both the best future host and a direct category competitor -- watchlist.

**Standards.** MCP governed by the Agentic AI Foundation (Linux Foundation; Anthropic,
OpenAI, Block founding; Google/Microsoft/AWS supporting). Agent Skills open standard at
agentskills.io with ~45 listed adopters incl. OpenAI Codex, Gemini CLI, GitHub
Copilot, Cursor. AGENTS.md is the de facto *project*-level standard (28+ tools, incl.
Claude Code reading it); **no user-level/global cross-tool standard exists** --
proposals only. Packaging remains per-vendor. Vendor memory portability is one-time
snapshot import/export, not user-owned sync -- ExFu's positioning wedge.

**Sources:** [ChatGPT Work announcement](https://openai.com/index/chatgpt-for-your-most-ambitious-work/) ·
[ChatGPT Learn: what's new](https://learn.chatgpt.com/docs/whats-new) ·
[Skills in ChatGPT](https://help.openai.com/en/articles/20001066) ·
[Agent Skills standard](https://agentskills.io) ·
[Gemini CLI skills docs](https://geminicli.com/docs/cli/skills/) ·
[Gemini Spark](https://gemini.google/overview/agent/spark/) ·
[MCP donation to AAIF](https://www.anthropic.com/news/donating-the-model-context-protocol)
