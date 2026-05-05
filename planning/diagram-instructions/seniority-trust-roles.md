# Diagram instructions: seniority-trust-roles

This file is the brief for the seniority and trust roles diagram. The diagram lives at `plugin/src/team-admin/resources/diagrams/seniority-trust.png` once produced. It ships in the team-admin plugin only.

---

## 1. What this diagram teaches

Different people on a team have different relationships with shared context, different levels of comfort exposing their work to others, and different risks if substrate data leaks or is misused. A substrate champion designing the team's setup needs a mental model for matching substrate configuration to seniority and trust level — not applying one setup to everyone. This diagram proposes three rough profiles: **exec / senior leader** (broad context-sharing appropriate, full automation useful, personal context likely spans strategy and people), **senior IC or team lead** (substantial context, active scopes, some sharing appropriate, automation high-value), and **new joiner or contractor** (narrower shared context, more constrained access, less personal context needed from day one, trust builds over time). The point is not to be prescriptive — real organisations vary — but to give the substrate champion a starting framework they can adapt. The diagram shows that configuration is not one-size-fits-all and provides a usable set of defaults to start from.

---

## 2. Key elements to include

- **Three profile rows or bands:** labelled by seniority/trust archetype. Suggested labels: Exec / Senior Leader; Senior IC / Team Lead; New Joiner / Contractor. These are archetypes, not rigid categories.
- **For each profile, show three or four configuration dimensions:**
  - *Shared context depth* — how much of the team's shared context this profile gets access to (exec: full; senior IC: substantial; new joiner: curated essentials).
  - *Personal context scope* — how much personal context is useful to build early (exec: extensive, spans people/strategy; senior IC: active scopes and work context; new joiner: role and immediate team context only).
  - *Automation level* — how much autonomous scheduled-task activity makes sense (exec: daily briefing, calendar integration, cross-team monitoring; senior IC: daily briefing, project reminders, tool integrations; new joiner: lighter, mainly onboarding prompts).
  - *Sharing / visibility* — what the person's substrate output is visible to (exec: potentially visible to EA or admin; senior IC: personal by default; new joiner: personal, limited visibility).
- **A clear indication that these are starting points, not rules.** A label like "adapt to your organisation" or a visual footnote.
- **The substrate champion as the designer:** a small visual cue that the substrate champion configures the shared layer, and these profiles guide what they provision per role.

---

## 3. Visual asymmetries that matter

- **Exec profile should look fuller and more connected** — more dimensions active, more tools integrated, richer shared context. Not because execs are more important, but because their setup genuinely spans more of the organisation.
- **New joiner profile should look lighter and simpler** — fewer active dimensions, not because they're less valued but because trust is built over time and context accumulates gradually. It shouldn't look impoverished — it should look like a clean starting point.
- **Progression from new joiner to senior IC to exec is about depth and breadth, not about unlocking features.** The visual should avoid suggesting you "earn" more features. The progression is about context and trust accumulating, not access being granted.
- **The three profiles are roughly equal in visual weight** — they're all valid configurations. No profile should look like the "real" one that the others are lesser versions of.

---

## 4. What this diagram is NOT trying to do

- Not a permissions matrix for IT security (that's a separate conversation and highly org-specific).
- Not prescribing org hierarchy — "seniority" here means context depth and trust level, not reporting structure.
- Not suggesting junior employees should have a worse Claude experience — a lighter substrate is appropriate, not inferior.
- Not showing technical access controls (who can read which git branches, etc.). That's implementation detail.
- Not covering every possible role type. Three archetypes only.

---

## 5. Source attribution

ExFu original. The seniority/trust-profile framing for substrate configuration is ExFu's own approach. It draws on general thinking about role-based access design but is not derived from any specific framework.

---

## 6. Phrase to give ChatGPT

> Here is a conceptual brief for a diagram I need. Please render it as a clean infographic, warm earth tones, label everything plainly, no corporate stock-art clichés. The diagram is called "seniority and trust roles" and it shows recommended substrate configurations for three organisational archetypes: Exec / Senior Leader, Senior IC / Team Lead, and New Joiner / Contractor. For each archetype, show four configuration dimensions: (1) shared context depth — how much shared team context they get, (2) personal context scope — how much personal context is useful to build early, (3) automation level — how much scheduled-task activity is appropriate, (4) sharing / visibility — what their substrate output is visible to. The exec profile should look fuller and more connected. The new joiner profile should look clean and simple — a starting point, not a lesser version. Include a visual note that these are starting points to adapt. The three profiles should have roughly equal visual weight — they're all valid configurations, not a hierarchy of privilege.
