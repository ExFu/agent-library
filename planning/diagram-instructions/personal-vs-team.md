# Diagram instructions: personal-vs-team

This file is the brief for the personal vs team skills diagram. The diagram lives at `plugin/src/team/resources/diagrams/personal-vs-team.png` once produced. It ships in both the team and team-admin plugins.

---

## 1. What this diagram teaches

When you install the team plugin, you get two layers of substrate: your own personal substrate (the context, scopes, and skills that belong to you alone) and the team's shared substrate (the conventions, shared context, and skills that the substrate champion has provisioned for everyone). These two layers don't merge — they remain distinct. The user's `wow` skill is the bridge that makes both accessible in a single Claude session. Without this diagram, users often assume the team setup replaces their personal one, or they confuse what they own versus what the team owns. The diagram makes the two-layer structure physically obvious and shows the `wow` skill as the active connector between them.

---

## 2. Key elements to include

- **Two panes or columns:** left side is the user's personal substrate; right side is the team's shared substrate. Clear labels: "Your substrate" (or "Personal") and "Team substrate" (or "Shared").
- **Personal substrate contents:** personal context (about me, work background, preferences), personal scopes (active work areas), personal skills, personal reminders and inbox. Belongs to the individual user, not visible to the team.
- **Team substrate contents:** shared skills (team conventions, shared ways of working, shared context), team context (who the team is, how it operates), potentially shared scopes. Maintained by the substrate champion. Readable by all team members.
- **The `wow` skill:** shown bridging the two panes — it sits in the middle (or spans both), with visual indication that it loads context from both sides into a single session. Label it: "your `wow` skill" or "personal `wow`." This is the key mechanism; it deserves visual prominence.
- **A Claude session:** represented somewhere in the diagram as the place where both layers come together. The user experiences a single conversation that draws on both substrates — the diagram should show this unified experience as the output of the two-layer structure.
- **Directionality:** the personal substrate is the user's to own and grow; the team substrate is provisioned from above (the substrate champion). The diagram can suggest this with a subtle visual cue — e.g. the team substrate has a "maintained by admin" note.

---

## 3. Visual asymmetries that matter

- **Personal substrate should feel individual and owned.** The user's side is theirs — private, flexible, personal. It should look human-scale, not corporate.
- **Team substrate should feel shared and authoritative.** Not intimidating — warm — but it's the structure that the organisation provides. It should look slightly more formal or structured than the personal side.
- **`wow` is the active bridge, not passive.** It's not just an arrow. The `wow` skill is doing something — it's loading, bridging, making both sides available. The visual should suggest activity, not just connection.
- **The two panes are clearly separate.** There's no ambiguity about what belongs to each side. The boundary between them matters.

---

## 4. What this diagram is NOT trying to do

- Not showing the file system structure in detail. No folder trees.
- Not showing the install sequence — this is the end state.
- Not comparing team setup to solo setup (that's a different diagram, or a conversation).
- Not showing IT or security architecture.
- Not trying to show every possible thing in each substrate — representative examples only.

---

## 5. Source attribution

ExFu original. The two-layer personal/team structure and the `wow`-as-bridge concept are ExFu's own design patterns.

---

## 6. Phrase to give ChatGPT

> Here is a conceptual brief for a diagram I need. Please render it as a clean infographic, warm earth tones, label everything plainly, no corporate stock-art clichés. The diagram is called "personal vs team substrate" and it shows the two-layer structure of a team Claude setup. Left pane: the user's personal substrate (personal context, scopes, skills — private, owned by the individual). Right pane: the team's shared substrate (shared skills, team conventions, shared context — maintained by the team's substrate champion). In the middle: the user's `wow` skill, which bridges both sides and makes both layers available in a single Claude session. The personal side should feel individual and owned. The team side should feel shared and lightly authoritative. The `wow` skill should look active — it's the bridge that brings both together. Show a single Claude session as the unified output at the top or bottom. Clear two-pane structure with a distinct boundary between the personal and team sides.
