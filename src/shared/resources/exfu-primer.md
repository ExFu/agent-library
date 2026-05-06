# ExFu Primer

*For someone considering installing. What this is, who it's for, and how to get started.*

---

## What ExFu is

ExFu is a guided install of a working Claude setup. It ships as a plugin — a bundle of skills, resources, and scheduled tasks that you install into Claude Cowork — and it walks you through the process of setting up a persistent, capable working environment with Claude.

The output is a substrate: a knowledge base that holds your context across sessions, skills that tell Claude how to behave, connectors to your existing tools, and scheduled tasks that run on your behalf. When you're done, Claude knows who you are, what you're working on, how you like to work, and has access to the tools you use every day. It's ready to act as a genuine working collaborator rather than a chat window you open occasionally.

The install itself is a conversation. The ExFu agent (powered by Claude) leads you through it: asking about you and your work, building your context as you talk, installing components as they become relevant. By the end, you have a working setup *and* a clear enough sense of how it's put together to extend it yourself.

That second part matters. ExFu is not implementation-for-hire. The goal is that you can add a new scope, create a skill, or update your context without needing to come back. You leave the install able to grow the setup on your own.

---

## What you get

**A knowledge base.** Your persistent memory with Claude. Context about you — your work, your background, your preferences, your current projects. Structured so Claude can find and use it across every session and device.

**Bedrock skills.** The foundational set that makes everything else work: how Claude manages your files, how it navigates your knowledge base, the `wow` skill (your personal navigation map). These are installed first because everything else depends on them.

**Your personal `wow` skill.** A short, custom-generated skill that lives in Claude's global instructions and loads on every session. It's a map of your setup — tells Claude what you have, how it's structured, and where to look when something comes up. You extend it over time as your setup grows.

**Optional skills, selected to fit you.** The install conversation surfaces what's likely to be useful — reminders, inbox (quick-capture), writing-styles, daily briefing, scope skills for active work areas. You pick what resonates; everything else stays available for a follow-up.

**Scheduled tasks.** At minimum, a daily cleanup task that keeps your knowledge base tidy. If you install the daily briefing, that runs on a schedule too — a summary of what's on your plate waiting for you when you start your day.

**The substrate guide.** A reference document that lives in your knowledge base. Claude reads it to understand the conventions of your setup. You can read it too — it explains the structure, the naming conventions, the access patterns.

**Ecosystem references.** A catalogue of Anthropic's own learning resources and well-regarded community tools, so you know where to go when you want to go deeper on something outside the install scope.

---

## Who it's for

ExFu is built for people who do knowledge work and are ready to invest a couple of hours to change how they work with Claude.

The profile that benefits most: founders, senior operators, professionals who spend their days thinking, writing, deciding, managing relationships, and running projects. People with a lot of context to carry and a lot of tools to connect. People who are already using Claude and can tell there's more available but haven't yet built the infrastructure to get to it.

It's also available in team variants. The team-admin plugin is for the person who wants to set up a shared substrate for their whole team — the substrate champion who builds the shared layer, provisions the git repo, and onboards colleagues. The team plugin is for everyone else on that team — joining the shared substrate and building their personal layer on top.

ExFu is not primarily for people brand new to Claude. If you've never used Claude before, start with Claude 101 (https://anthropic.skilljar.com/claude-101) and spend a few weeks using Claude directly. Come back to ExFu when you've hit the ceiling of what works without a real setup.

---

## What it's not

**Not a SaaS product.** There's no ExFu account, no ExFu cloud, no monthly subscription to a service. You install a plugin. The plugin runs on your Claude. Once installed, everything operates locally and through Anthropic's infrastructure — nothing goes to ExFu servers, because there aren't any.

**Not an Anthropic product or affiliate.** ExFu is an independent service built on Claude's publicly available capabilities. It builds on Anthropic's skills, Cowork, and plugin infrastructure, but it's not made by Anthropic and it doesn't have any special relationship with Anthropic beyond using the same tools anyone can use.

**Not a credential broker.** ExFu doesn't ask for your API keys, your passwords, or your Claude credentials. The install conversation happens within your own Claude session. Any tool connections you set up (calendar, task manager, etc.) are direct connections from Claude to those tools — ExFu is not in the middle.

**Not a set-it-and-forget-it product.** The substrate gets better as you use it. You'll add context when something new becomes relevant. You'll create a scope when a project starts. You'll extend `wow` as your setup evolves. The install is a beginning, not a finished state.

**Not responsible for everything Claude does after you install.** ExFu sets up the structure and installs the skills. Claude's behaviour in that structure is still Claude. If Claude does something unexpected, the answer is to look at the context or skills and adjust them — that's the substrate working as intended, not a support issue.

---

## How to get started

Install the plugin into Claude Cowork. Once it's installed, run `/exfu` to start the install conversation. The ExFu agent will take it from there.

Before you install, it's worth reading the substrate primer (also included in the plugin at `resources/the-substrate-primer.md`) if you want to understand what you're building. The install conversation will explain things as you go, but knowing the four ingredients and why the setup works the way it does makes the conversation faster and the decisions clearer.

The install takes roughly one to two hours. Have your main tools available (calendar, task manager, whatever you use daily) so you can connect them during the session. Clear an uninterrupted block — the conversation works best when it's not interrupted.

If you get stuck, or if something in the install doesn't go as expected, reach Alastair at al@exfu.ai.
