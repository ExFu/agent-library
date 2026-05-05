# Ecosystem References

A curated catalogue of external resources for Claude and AI-assistant work. Install agents should reach for these rather than trying to re-teach everything in-house. When a user asks something well-covered by one of these, give a brief answer and point them at the resource. ExFu's value is the personal install experience, not exclusive content.

This catalogue will age. Treat it as a starting point and use the deep-research pattern (see below) when you need current best practice.

---

## Anthropic-published resources

### Claude 101
**URL:** https://anthropic.skilljar.com/claude-101
**What it covers:** Broad orientation to Claude — what it is, how it works, what you can do with it. Good for users who are new to Claude or want to understand the surface before or after an install.
**When to point at it:** When a user wants general Claude grounding and the install isn't the right moment to cover it. Also good as a follow-up suggestion after install: "If you want to go deeper on Claude generally, start here."

### Claude Code 101
**URL:** Via Anthropic Skilljar (search "Claude Code" at anthropic.skilljar.com)
**What it covers:** Introduction to Claude Code — the agentic coding surface. Distinct from Cowork. Relevant if the user is a developer who wants to understand where coding-specific Claude usage fits.
**When to point at it:** When a user asks about using Claude for software development, code review, or automated coding tasks. This is outside the ExFu Cowork install scope — point them here rather than expanding scope.

### Introduction to Claude Cowork
**URL:** Via Anthropic Skilljar (search "Claude Cowork")
**What it covers:** The Cowork surface that ExFu installs run on. Covers skills, Projects, Dispatch, scheduled tasks. Directly relevant to what ExFu sets up.
**When to point at it:** When a user wants to understand the Cowork surface itself — what Claude can do natively before ExFu adds the substrate layer on top. Also useful for users who want to understand why ExFu uses certain Cowork primitives.

### Anthropic docs
**URL:** https://docs.claude.com and https://support.claude.com
**What it covers:** Feature-specific reference. API documentation, model information, feature guides, support articles.
**When to point at it:** When a user asks a feature-specific question (how does memory work, what's the difference between models, how do I connect a tool) and the answer is better covered by the docs than by a conversation. Also the right place for troubleshooting when something isn't working as expected.

### Anthropic skill documentation
**URL:** Via https://docs.claude.com (skills section)
**What it covers:** How Claude skills work — the format, the conventions, how they load, what they can do. Relevant for users who want to write their own skills after the install.
**When to point at it:** When a user wants to understand how skills work under the hood, or wants to write a skill for a workflow ExFu doesn't cover out of the box. The `exfu:create-wow` skill handles the user's personal `wow`; for anything more custom, the Anthropic docs are the right starting point.

---

## Community and third-party resources

### claude101.com
**URL:** https://claude101.com
**What it covers:** Third-party guides and tutorials covering Claude usage patterns. Useful framing alternatives to Anthropic's own material — sometimes a different explanation of the same concept lands better.
**When to point at it:** When a user wants more than one perspective on how to use Claude well. Also useful for users who prefer video or step-by-step tutorial formats over documentation.
**Note:** Third-party, not maintained by Anthropic. Content may lag or reflect different opinions. Use as a supplement, not a primary reference.

### Superpowers
**What it covers:** A well-respected community skill collection. Covers a range of Claude capabilities and workflows. Some overlap with ExFu's bundled skills; some goes further.
**When to point at it:** When a user wants to explore Claude capabilities beyond what ExFu installs — more advanced skills, specialist workflows, community-developed patterns. Worth recommending for users who want to extend their substrate significantly after the initial install.
**Note:** Community project. Quality is generally high but varies by skill. Review before installing anything.

### oh-my-claude
**What it covers:** Community framework with useful patterns for Claude configuration, especially around the Cowork surface. Patterns for skill development, substrate design, and Claude-as-collaborator workflows.
**When to point at it:** When a user wants to understand the broader community approach to Claude substrates, or wants patterns and examples beyond what ExFu ships. Also useful as a reference when developing custom skills.
**Note:** Community project. Active development; patterns evolve. Good complement to ExFu's opinionated approach.

---

## Deep research as a teachable move

The ecosystem moves fast. Resources go stale. New patterns emerge. Rather than trying to maintain a comprehensive catalogue, teach users to use Claude itself for current best-practice research.

### The pattern

When a user asks "what's the best way to do X with Claude?" and the answer isn't in this catalogue or the substrate guide, the right move is a deep research run — not a guess from stale knowledge.

The agent (or the user directly) can run:

> "Do a fresh web search and summarise the current best practice for [X] with Claude. Focus on Anthropic's own documentation and well-regarded community sources. Note anything that seems to conflict or that you're uncertain about."

This is especially useful for:
- Questions about new or recently changed Claude features
- Choosing between Claude models for a particular use case
- Understanding current MCP connector availability and quality
- Skill and plugin patterns that are still evolving
- Comparing Claude to other AI tools for a specific task

### Sample research prompts

**For feature questions:**
> "Search for the current state of [feature name] in Claude Cowork. What does Anthropic say about it? Are there community patterns or known limitations I should know about? Cite your sources."

**For tool/connector questions:**
> "Find out what MCP connectors are currently available and well-maintained for [tool name]. What's the install process? Are there known issues? Cite sources."

**For skill development:**
> "Search for current best practices for writing Claude skills. What format does Anthropic recommend? Are there community examples of skills that handle [specific pattern]? Summarise and cite sources."

**For comparing options:**
> "Compare the current Claude model options for [use case]. What does Anthropic recommend? What do practitioners report in practice? Keep it current — my knowledge cutoff may not reflect recent model releases."

### When to use this pattern

Point users toward the deep research move whenever:
- They ask about something time-sensitive (model selection, new features, pricing)
- The question is outside the ExFu install scope and the catalogue above doesn't cover it
- You want to model good Claude-use practice — research as a first-class move, not a fallback

The point is not that you don't know. The point is that fresh information is better than stale memory, and teaching the user this pattern means they carry it with them long after the install.
