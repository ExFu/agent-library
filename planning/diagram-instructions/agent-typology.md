# Diagram instructions: agent-typology

This file is the brief for the agent typology diagram. The diagram lives at `plugin/src/shared/resources/diagrams/agent-typology.png` once produced.

---

## 1. What this diagram teaches

There are four broad modes of working with AI agents, and they're genuinely different in what they offer and what they require. **Chat** is the familiar query-response loop — you ask, it answers, the conversation ends, nothing persists. **Cowork** (knowledge-worker assistant) is what ExFu installs — an AI with persistent context, access to your tools, ongoing tasks, and a way of working that accumulates over time. **Coding** (Claude Code and equivalents) is agentic work inside a codebase — reading and writing files, running tests, making structured changes. **Custom-hosted** agents are purpose-built pipelines deployed for a specific task — a customer support bot, a data processor, a document reviewer — not general-purpose working partners. Users arriving at an ExFu install often have a vague sense that "AI is changing" but not a map of the landscape. This diagram gives them that map in one glance and immediately answers: "where does ExFu fit?" (Cowork), "what's not in scope?" (Coding and Custom-hosted), and "what am I moving away from?" (Chat-only usage).

---

## 2. Key elements to include

- **Four clearly labelled zones or segments:** Chat, Cowork, Coding, Custom-hosted.
- **Chat zone:** conversational, ephemeral, no persistence, no tools. The baseline most users are familiar with. Could suggest a chat bubble or a simple Q&A exchange. No memory carries over.
- **Cowork zone:** persistent context, tool access, ongoing routines, the knowledge-worker setup. This is where ExFu operates. Should feel richer, more layered than Chat — there's memory, there are connections, there's continuity. Label ExFu's scope within or adjacent to this zone.
- **Coding zone:** agentic, codebase-oriented, file-reading and writing, test-running. Distinct from Cowork — it's a different surface and a different use case. Claude Code is the canonical example. Not in scope for ExFu.
- **Custom-hosted zone:** purpose-built, deployed for a specific task, not a general-purpose assistant. Usually invisible to the end user (they interact with a product, not "Claude"). Not in scope for ExFu.
- **ExFu's scope marker:** a clear visual call-out, bracket, or highlight showing ExFu sits in the Cowork zone. Not as a logo, just as a label: "ExFu installs here" or "this install."
- **Relationship between zones:** they are not a hierarchy (one isn't better than another) — they are genuinely different modes for different purposes. The visual should suggest parallel tracks, not a ladder.

---

## 3. Visual asymmetries that matter

- **Cowork should look substantively richer than Chat.** Chat is simple (one arrow back and forth). Cowork has layers — memory, tools, routines, continuity. The visual complexity of the Cowork zone should be visibly greater, not because it's "better" but because it's structurally more.
- **Coding and Custom-hosted should look distinct from Cowork,** not vague — each is its own clear thing. Coding has a code/terminal feel. Custom-hosted has a deployed/pipeline feel. Neither should bleed into the Cowork zone.
- **ExFu's placement marker should be calm, not triumphalist.** It's saying "here's where this fits" not "this is the best one." A simple label or bracket is enough.
- **No implied hierarchy** — don't use a pyramid, a staircase, or anything that suggests one mode is more advanced than another. They are parallel.

---

## 4. What this diagram is NOT trying to do

- Not a competitive comparison between AI providers (OpenAI vs Anthropic vs Google). This is about usage modes, not vendors.
- Not a feature matrix. No bullet lists of capabilities inside each zone.
- Not positioning ExFu as the only way to access Cowork — Anthropic's own tools and other approaches do this too. ExFu is a guided install, not the Cowork category itself.
- Not trying to be comprehensive about every possible AI agent pattern. Four zones only. Real-world variations that don't fit cleanly get rounded to the nearest zone.
- Not showing the install process, the substrate ingredients, or anything about how these modes work internally. It's a landscape map, not a mechanism diagram.

---

## 5. Source attribution

The four-mode framing is ExFu's own categorisation. The underlying concepts (chat, agentic coding, deployed pipelines) draw on Anthropic's public discussion of Claude usage patterns, but this particular four-zone map is ExFu's.

---

## 6. Phrase to give ChatGPT

> Here is a conceptual brief for a diagram I need. Please render it as a clean infographic, warm earth tones, label everything plainly, no corporate stock-art clichés. The diagram is called "agent typology" and it maps four modes of working with AI: Chat (ephemeral, query-response, no persistence), Cowork (knowledge-worker assistant — persistent context, tool access, ongoing routines, this is where ExFu operates), Coding (agentic, codebase-oriented, Claude Code style), and Custom-hosted (purpose-built deployed pipelines for a specific task). The four zones are parallel — not a hierarchy, not a ladder. Cowork should look visibly richer/more layered than Chat, reflecting its structural depth. Include a calm label showing ExFu's scope sits in the Cowork zone. Please show these as four distinct parallel zones or segments with clear labels and brief descriptors for each.
