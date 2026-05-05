# The Substrate Primer

*Human-facing pre-install reading. If you want to understand what you're being offered before you install, start here.*

---

## What problem this solves

You've been using Claude. Maybe you're already impressed by it. But there's a version of working with Claude that's categorically different from what most people experience, and it requires a different kind of setup.

In the default mode, every conversation starts from zero. You paste in context. You explain who you are, what you're working on, what matters. You get a useful answer. The conversation ends. Next time, you start over.

That mode is genuinely useful. But it's also limited. You're doing a lot of work just to get to the useful part. And there's a ceiling on what Claude can do for you when it has no memory, no access to your tools, and no sense of what you're trying to achieve over time.

A substrate removes that ceiling.

---

## The four ingredients

A Claude substrate has four things. You can remember them as: where knowledge lives, how Claude behaves, what it can reach, and what it does on its own.

### 1. The knowledge base

This is persistent memory — a set of files that survive between sessions. Context about you: who you are, what you do, what you're working on, how you like to work. Plans. Decision logs. Notes. Anything Claude should know without you having to say it again.

The knowledge base is ordinary files — markdown, mostly — stored in a cloud drive or a git repository. Nothing exotic. You can read them, edit them, add to them, move them. They're yours.

What makes them special is where they live: in a place Claude can access from any surface, any device, any session. The same files that Claude reads in your desktop app are accessible when you're on mobile, in a scheduled task running at 7am, or in a conversation two weeks from now.

The knowledge base stores shareable knowledge: context, conventions, plans, skills. It does not store personal data about other people (customer profiles, identifiable contact details, that kind of thing). That category of information is held separately, behind access control, and Claude reads it at runtime without it ever landing in the shared substrate. This keeps the knowledge base safe to share and version-control.

### 2. Skills

Skills are how you tell Claude to behave. They're short instructions that load into a session and tell Claude what you want it to know and do automatically. A skill might say: "this is how to manage files in this user's knowledge base." Or: "this is how to handle reminders — where they live, how to create one, when to surface it." Or: "this is the user's about-me summary — read this at the start of every conversation."

The most important skill in your substrate is your `wow` skill — your personal way-of-working skill. It's a navigation map for your own setup. It tells Claude how your knowledge base is structured, what each part is for, and where to look when something comes up. As your substrate grows, your `wow` grows with it.

Skills have a property that files don't: they surface themselves. When a skill is installed, Claude knows it exists and loads it when it's relevant. Files, by contrast, are passive — Claude only reads a file if it's pointed there by a skill, a README, or your request. This asymmetry matters. It means the discoverability of your knowledge base depends on the skills that point to it. Skills are the index; files are the library.

### 3. Connectors

Connectors (called MCP connectors, or MCP tools) are how Claude reaches into the tools you already use. Your calendar. Your task manager. Your email. Your cloud storage. Your CRM. Claude can read from and write to these with your permission, as part of a conversation.

Without connectors, Claude knows only what you tell it in the conversation and what's in your knowledge base. With connectors, it can check what's actually on your calendar, pull up the task you mentioned, look at the document you're referring to. It's the difference between an assistant who can help you think and one who can also act.

Connectors don't live in your knowledge base. They're separate integrations you set up once and then mostly forget about. When Claude needs them, it uses them.

### 4. Things on a timer

Scheduled tasks are what Claude does without you asking. A daily briefing delivered at 7am, pulling from your reminders, your calendar, and your inbox. A weekly cleanup of stale files. A regular check on a project status. These run automatically, in the background, while you're doing other things.

Things on a timer are where the "working collaborator" framing becomes most literal. Claude is doing work on your behalf without you initiating it. The briefing is ready when you wake up. The cleanup happened overnight. The reminder surfaced without you having to remember to ask.

---

## The asymmetry worth understanding

Most people, when they first set up a substrate, focus on the knowledge base. They want Claude to know things. They add context, write files, build out their structure.

This is right and necessary. But files alone don't make a substrate work.

Here's why: Claude doesn't browse your knowledge base looking for what might be relevant. It reads what it's pointed at. If you have a great file called `context/work/acme-deal.md` with everything Claude needs to know about a client deal, Claude won't read it unless something points it there — a scope skill that loads when you mention Acme, a README that lists it as a dependency, or your direct request.

Skills are the mechanism that makes files discoverable. A scope skill for the Acme deal says: "when this deal comes up, here's where the context lives." Without that skill, the file is there but effectively invisible.

This is what gets called the discoverability asymmetry, though you don't need that term. The practical implication: when you add something to your knowledge base, think about whether there's a skill or README that will point Claude there. If not, build it.

---

## Why "build by doing"

There's a temptation, when setting up a substrate, to try to design the whole thing first. Figure out every folder, write all the context, install every skill. Then use it.

This doesn't work well in practice. You don't know what you actually need until you start using it. The about-me file you wrote in the first session will look different after three months of working with Claude. The scope you set up for a project will naturally expand as the project evolves. The skill you thought you needed will turn out not to matter; the skill you didn't expect to need will become central.

The right approach is to build as you go. Start with the essentials: a knowledge base location, the bedrock skills that make everything else possible, a basic about-me. Then let the substrate grow through use. Each new thing you want Claude to remember gets a file. Each new pattern of behaviour gets a skill. Each new tool gets a connector.

This is called build by doing, and it's a discipline as much as a technique. It keeps the substrate close to your actual life rather than an imagined ideal version of it.

---

## The chief of staff framing

The felt experience of a well-installed substrate is closest to having a very good chief of staff.

A chief of staff knows your context without being briefed each time. They have access to your calendar, your key relationships, your current priorities. They take initiative — they don't wait to be asked before they notice that two commitments clash, or that a deal you care about has gone quiet. They work in your voice and in line with your values. And they get better at their job over time as they learn how you work.

That's what a substrate makes possible with Claude. Not because Claude is a person, and not because the chief of staff framing is a perfect metaphor — it isn't. But because the combination of persistent memory, tools access, ongoing tasks, and learnable behaviour creates something genuinely closer to a working partner than to a query engine.

The metaphor is useful at the start. Over time, you develop your own sense of how Claude operates. The substrate is the infrastructure that makes that development possible.

---

## What this is not

A few things the substrate is not, worth saying plainly:

**Not a knowledge management tool.** You're not building a wiki or a second brain. Files in the knowledge base are there to give Claude context, not to be a searchable repository you browse. If you find yourself filing things meticulously for your own reference, you may be building a library when you wanted a collaborator.

**Not a chatbot wrapper.** A substrate doesn't change what Claude is or add capabilities it doesn't have. It gives Claude better context, better tools access, and better continuity. The underlying model is the same. The experience is different because the setup is different.

**Not a database product.** The knowledge base can hold simple structured data (Claude can manage a contact list, a pipeline, a set of reminders in files) but it's not designed to replace a real database or a CRM. It fills the gap when you don't have a dedicated tool; it doesn't compete with one.

**Not permanent.** The substrate should evolve. Files that are no longer relevant should be cleaned up or archived. Skills that don't serve you should be removed. A substrate that accumulates indefinitely without pruning becomes noise. Build the cleanup into the routine.

---

## A note on teams, orgs, and multiple memberships

The substrate works for solo users and for people who belong to one or more teams or organisations.

If you're solo, the setup is simple: a personal knowledge base with the standard folders, and you're done.

If you're in a team or org, the substrate adds dedicated folders for org-wide and team-wide context alongside your personal folders. If you're in multiple teams or orgs (a manager spanning departments, a consultant working across clients), that's supported too. Each gets its own folder, and there's no limit on how many you can have.

The knowledge base root also contains a small guard file (`CLAUDE.md`) that tells Claude not to interact with the substrate unless the right skills are loaded. Think of it as a safety catch: it stops Claude from treating your knowledge base as a generic folder if it accidentally gets pointed there without the right context.

---

## A note on this document

The substrate guide in your knowledge base covers the structural conventions, naming rules, folder purposes, and access patterns that Claude uses to navigate your setup. That document is Claude-facing — it's in your knowledge base for Claude to reference. This primer is human-facing — it's here for you to read before you install, so you know what you're getting into.

Both are worth having. They serve different readers.
