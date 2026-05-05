# Diagram instructions: substrate-overview

This file is the durable brief for the substrate overview diagram. The diagram itself lives at `plugin/src/shared/resources/diagrams/substrate-diagram.png`. When the diagram needs regenerating, use this file to brief ChatGPT.

---

## 1. What this diagram teaches

A Claude substrate has four ingredients: a knowledge base (persistent files — context, memory, plans), skills (instructions that tell Claude how to behave and what to do), connectors (MCP tools that give Claude access to the user's real-world tools and platforms), and things on a timer (scheduled tasks that run autonomously — maintenance, briefings, monitoring). The diagram teaches what each ingredient does and, more importantly, what they do *together*. A user who only has files gets memory but no behaviour. A user who only has skills gets behaviour but no memory. The combination is what creates the felt experience of a persistent working collaborator rather than a chatbot you query. There is also a structural asymmetry the diagram must carry: skills surface themselves (they load automatically and announce what they do), while files don't — files have to be discovered via README chains, scope skills, or direct navigation. This discoverability asymmetry is not a bug; it's the design. But users need to understand it to work with it.

---

## 2. Key elements to include

- **Knowledge base / files:** labelled clearly as persistent memory. Include visual cues for markdown files, folder structure. Should suggest "context that survives sessions."
- **Skills:** labelled as behaviours or instructions. Should suggest they are active — they load, they do things, they surface themselves. A skill is not a file you read; it's a pattern Claude follows.
- **Connectors (MCP):** labelled as the bridge to the outside world. Tools the user already uses — calendar, task manager, email, cloud storage. Claude reaches into these. They don't live in the substrate; the connector is the handshake.
- **Things on a timer / scheduled tasks:** labelled as the autonomous layer. Runs on a schedule without user initiation. Daily briefing, cleanup, git sync, monitoring. Suggests continuity and background activity.
- **The whole together:** a label or framing device that says what these four produce together — a persistent working collaborator, not a chat window. The "chief of staff" framing is the felt experience, though the diagram doesn't need to use those words explicitly; it should be visually evident.
- **Discoverability asymmetry:** the diagram should show that skills point Claude toward files (not the reverse). Skills are active finders; files are passive stores. This could be shown via directional arrows or a visual layering where skills are "on top" and files are "beneath."

---

## 3. Visual asymmetries that matter

- **Skills vs files:** skills should look more active, more prominent, more foregrounded than files. Files are the substance; skills are the discovery mechanism. If both look the same, the diagram fails to convey the asymmetry.
- **Scheduled tasks vs user-initiated interactions:** the timer/scheduled layer should look separate from the user-facing interaction layer — it operates in the background. This could be shown via spatial separation (e.g. a lower layer or a background band) or a distinct visual treatment (clock icon, darker tone).
- **Connectors as outward-reaching:** connectors point away from the substrate toward external tools. They are the only ingredient that lives partly outside — the substrate reaches *out* through them. Directional arrows pointing outward convey this.
- **Centre of gravity:** the knowledge base is the largest, most central element — it's where the substance lives. Everything else orbits or serves it.

---

## 4. What this diagram is NOT trying to do

- Not a technical architecture diagram. No API endpoints, no data formats, no infrastructure boxes.
- Not a feature comparison with other AI tools or Claude's built-in features.
- Not showing the install *process* — that's a different diagram. This shows the end state: what a substrate *is*, not how you build one.
- Not showing Box specifically, or git, or any particular implementation. The ingredients are abstract — the diagram should work whether the storage is Box, git, or anything else.
- Not trying to show every possible component or option. Four ingredients only. Don't add a fifth just because something doesn't fit cleanly.

---

## 5. Source attribution

ExFu original. The four-ingredient framing is ExFu's own. The concept of Claude substrate as persistent context draws on Anthropic's public Cowork and skills documentation, but this particular framing and the discoverability asymmetry concept are ExFu's.

---

## 6. Phrase to give ChatGPT

> Here is a conceptual brief for a diagram I need. Please render it as a clean infographic, warm earth tones, label everything plainly, no corporate stock-art clichés. The diagram is called "substrate overview" and it teaches what a Claude substrate is made of. There are four ingredients: a knowledge base (persistent memory, markdown files, context that survives sessions), skills (active instructions that tell Claude how to behave — they surface themselves, they load automatically), connectors (MCP tools that bridge Claude to the user's real-world platforms — calendar, email, task tools — pointing outward), and things on a timer (scheduled tasks that run autonomously — briefings, maintenance, monitoring). The four together create a persistent working collaborator, not a chat window. The key visual asymmetry: skills are active and foregrounded; files are the passive substance behind them. Connectors point outward. The timer layer is background / autonomous. The knowledge base is the central, largest element. Please label all four ingredients clearly and show what they produce together.
