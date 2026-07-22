# The Agent Library Primer

*Human-facing pre-install reading. If you want to understand what you're being offered before you install, start here.*

---

## What problem this solves

You've been using Claude. Maybe you're already impressed by it. But there's a version of working with Claude that's categorically different from what most people experience, and it requires a different kind of setup.

In the default mode, every conversation starts from zero. You paste in context. You explain who you are, what you're working on, what matters. You get a useful answer. The conversation ends. Next time, you start over.

That mode is genuinely useful. But it's also limited. You're doing a lot of work just to get to the useful part. And there's a ceiling on what Claude can do for you when it has no memory, no access to your tools, and no sense of what you're trying to achieve over time.

An Agent Library removes that ceiling.

The name is literal. ExFu installs a library: a place where everything Claude should know about you and your work lives, kept in order not by you but by Agent Librarians, scheduled agents whose whole job is making sure your stuff is filed, indexed, and findable. You don't need to care how the shelves are managed. You need to be able to find your stuff when you need it, and to trust that someone is keeping the place in order overnight. That's what the librarians are for.

---

## The four ingredients

An Agent Library has four things. You can remember them as: where knowledge lives, how Claude behaves, what it can reach, and who keeps it all in order.

### 1. The knowledge base

This is persistent memory: a set of files that survive between sessions. Context about you: who you are, what you do, what you're working on, how you like to work. Plans. Decision logs. Notes. Anything Claude should know without you having to say it again.

The knowledge base is ordinary files, markdown mostly, stored in a cloud drive or a git repository. Nothing exotic. You can read them, edit them, add to them, move them. They're yours.

What makes them special is where they live: in a place Claude can access from any surface, any device, any session. The same files that Claude reads in your desktop app are accessible when you're on mobile, in a scheduled task running at 7am, or in a conversation two weeks from now.

One rule about what goes in: only true secrets are banned. API keys, passwords, credential files never enter the library; they belong in a password manager. Everything else, names, contacts, notes, records, lives wherever it naturally belongs.

### 2. Skills

Skills are how you tell Claude to behave. They're short instructions that load into a session and tell Claude what you want it to know and do automatically. A skill might say: "this is how to manage files in this user's library." Or: "this is how to handle reminders, where they live, how to create one, when to surface it."

The most important skill in your library is your `wow` skill, your personal way-of-working skill. It's a navigation map for your own setup. It tells Claude how your library is structured, what each part is for, and where to look when something comes up. As your library grows, your `wow` grows with it.

Skills have a property that files don't: they surface themselves. When a skill is installed, Claude knows it exists and loads it when it's relevant. Files, by contrast, are passive. Claude only reads a file if it's pointed there by a skill, a README, or your request. This asymmetry matters, and the library metaphor makes it intuitive: skills are the catalogue; files are the books. A book that isn't in the catalogue is effectively invisible, no matter how good it is.

### 3. Connectors

Connectors (called MCP connectors, or MCP tools) are how Claude reaches into the tools you already use. Your calendar. Your task manager. Your email. Your cloud storage. Your CRM. Claude can read from and write to these with your permission, as part of a conversation.

Without connectors, Claude knows only what you tell it in the conversation and what's in your library. With connectors, it can check what's actually on your calendar, pull up the task you mentioned, look at the document you're referring to. It's the difference between an assistant who can help you think and one who can also act.

Connectors don't live in your library. They're separate integrations you set up once and then mostly forget about. When Claude needs them, it uses them.

### 4. The librarians

Agent Librarians are what runs without you asking. Overnight, on a schedule, they do the maintenance a library needs: one walks the whole library and rebuilds the index so everything stays findable. One sweeps your inbox of quick captures and suggests where each item belongs. One redraws the visual dashboard so you can see your whole setup at a glance.

There are deliberately several of them, not one. Your library isn't run by a single all-knowing agent; it's an ecosystem, each librarian with a narrow job it does well. When you want something, you (or Claude, on your behalf) appeal to the right one. That's also why the library stays trustworthy: each job is small, inspectable, and runs on a cadence you can see.

The same machinery can also work *for your domain*, not just for the library. A business agent is a standing brief: watch the market for a car matching this spec, draft a weekly digest of this project, file invoices as they arrive. Librarians keep the library; business agents do your recurring work. Same mechanics, different remit.

This is where the "working collaborator" framing becomes most literal. The index is fresh when you wake up. The inbox is triaged. The reminder surfaced without you having to remember to ask.

---

## The asymmetry worth understanding

Most people, when they first set up their library, focus on the files. They want Claude to know things. They add context, write notes, build out structure.

This is right and necessary. But files alone don't make a library work.

Here's why: Claude doesn't browse your library looking for what might be relevant. It reads what it's pointed at. If you have a great file with everything Claude needs to know about a client deal, Claude won't read it unless something points it there: a skill that loads when you mention the client, an index entry, or your direct request.

This is the catalogue problem every real library has, and it's why the librarians matter more than the shelves. The nightly index is the catalogue; your `wow` skill is the map at the entrance; skills are the signs on the stacks. When you add something to your library, the question to ask is: will the catalogue find it, or does it need a sign? If neither, build one.

---

## Why "build by doing"

There's a temptation, when setting up a library, to try to design the whole thing first. Figure out every section, write all the context, install every skill. Then use it.

This doesn't work well in practice. You don't know what you actually need until you start using it. The about-me file you wrote in the first session will look different after three months of working with Claude. The work area you set up for a project will naturally expand as the project evolves. The skill you thought you needed will turn out not to matter; the skill you didn't expect to need will become central.

The right approach is to build as you go. Start with the essentials: a location, the bedrock skills, a basic about-me. Then let the library grow through use. Each new thing you want Claude to remember gets a file. Each new pattern of behaviour gets a skill. Each new tool gets a connector. Each recurring chore gets a librarian or a standing brief.

This is called build by doing, and it's a discipline as much as a technique. It keeps the library close to your actual life rather than an imagined ideal version of it.

---

## The chief of staff framing

The felt experience of a well-installed Agent Library is closest to having a very good chief of staff.

A chief of staff knows your context without being briefed each time. They have access to your calendar, your key relationships, your current priorities. They take initiative; they don't wait to be asked before they notice that two commitments clash, or that a deal you care about has gone quiet. They work in your voice and in line with your values. And they get better at their job over time as they learn how you work.

That's what the library makes possible with Claude: a chief of staff with a well-kept library behind them. Not because Claude is a person, and not because the metaphor is perfect. But because the combination of persistent memory, tools access, ongoing librarians, and learnable behaviour creates something genuinely closer to a working partner than to a query engine.

The metaphor is useful at the start. Over time, you develop your own sense of how Claude operates. The library is the infrastructure that makes that development possible.

---

## What this is not

A few things the Agent Library is not, worth saying plainly:

**Not a filing hobby.** The library is for your AI to work from, not a wiki for you to browse. If you find yourself meticulously filing things for your own reference, you're curating for the wrong reader. Let the librarians do the filing; your job is to hand things in.

**Not a chatbot wrapper.** The library doesn't change what Claude is or add capabilities it doesn't have. It gives Claude better context, better tools access, and better continuity. The underlying model is the same. The experience is different because the setup is different.

**Not a database product.** The library can hold simple structured data (Claude can manage a contact list, a pipeline, a set of reminders in files) but it's not designed to replace a real database or a CRM. It fills the gap when you don't have a dedicated tool; it doesn't compete with one.

**Not permanent.** The library should evolve. Files that are no longer relevant should be cleaned up or archived. Skills that don't serve you should be removed. A library that accumulates indefinitely without pruning becomes noise. Pruning is a librarian's job too; the routine has it built in.

---

## A note on teams, orgs, and multiple memberships

The library works for solo users and for people who belong to one or more teams or organisations.

If you're solo, the setup is simple: a personal library with your own working areas, and you're done.

If you're in a team, there's a shared library that the whole team reads and writes, and your personal layer sits alongside it. If you're in multiple teams or orgs (a manager spanning departments, a consultant working across clients), that's supported too: each is just another area of the library, and there's no limit on how many you can have.

The library root also contains a small guard file (`CLAUDE.md`) that tells Claude not to interact with it unless the right skills are loaded. Think of it as a safety catch: it stops Claude from treating your library as a generic folder if it accidentally gets pointed there without the right context.

---

## A note on words

Under the hood, ExFu's internal name for the library's machinery is the *substrate*: the conventions, the folder model, the index. You'll see the word in a few file names and in Claude's own reference material. You never need it. "Your library" and "your librarians" are the words that matter; if you ever ask Claude how it all works underneath, it'll happily switch registers and show you.

The library guide in your knowledge base covers the structural conventions, naming rules, and access patterns that Claude uses to navigate your setup. That document is Claude-facing. This primer is human-facing: it's here for you to read before you install, so you know what you're getting into.

Both are worth having. They serve different readers.
