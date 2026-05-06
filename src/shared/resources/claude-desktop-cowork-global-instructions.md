# Claude Desktop — Cowork Global Instructions

Universal Cowork-specific text, intended to be pasted into Cowork's Global Instructions field. Applies at the start of every Cowork session.

The text is paste-ready as a single block. The user's personalised `wow` skill content is installed alongside this (per the install skill's wow step) — the two complement each other: the `wow` skill is the user's personal navigation map; this block is the universal directive that ensures it gets loaded.

---

## About these directives

Install agents can use this section to understand what each directive does and why it's here, so they can explain it to users who ask.

**"At the start of every session, load the `wow` skill."**
The wow skill is the user's personal navigation map — it tells Claude how their substrate is laid out and carries a thin kernel of always-on instructions. Without this directive, a fresh Cowork session has no awareness of the user's setup unless the user explicitly invokes a skill. This line makes substrate awareness automatic, not opt-in.

**"When planning things, always create plans in a way that addresses the golden circle (Why, How, What)..."**
Plans created in Cowork are often implemented by Claude Code or another agent in a separate session. No conversational context survives that handoff — the implementing agent starts cold. A plan that only says what to do (without why it matters and how to approach it) gives the downstream agent nothing to reason from when something unexpected comes up. The golden circle structure ensures plans carry enough context to be executed well even without the originating conversation.

---

```text
At the start of every session, load the `wow` skill.

When planning things, always create plans in a way that addresses the golden circle (Why, How, What). Plans might be created in Cowork but implemented by Claude Code. No conversational context survives the bridge. Plans must be rich and complete. The golden circle at least ensures the implementing agent has an anchor for what they're building.
```
