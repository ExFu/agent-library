# Skills + Resources Audit (May 2026)

## Summary

Of 18 skills audited, 2 descriptions are CRITICAL, 11 are NEEDS-WORK, and 5 are GOOD. On body quality, 1 is CRITICAL, 5 are NEEDS-WORK, and 12 are GOOD. On trigger realism — the new dimension — 5 are CRITICAL, 9 are NEEDS-WORK, and 4 are GOOD. The headline problem is not depth of content (most bodies are solid) but description framing: the majority trigger on insider vocabulary (ExFu, install, substrate) rather than on the natural language real users bring into conversations. Of 12 resources and templates audited, 0 are CRITICAL, 3 are NEEDS-WORK, and 9 are GOOD.

---

## Common patterns

- **Insider-vocabulary triggers.** Most descriptions list ExFu-specific trigger phrases ("user says install", "user mentions exfu", "user says 'load my substrate'"). Real users don't talk this way. They ask "where do you keep stuff", "remind me about this", "do you have notes on the Acme deal". The trigger gap means skills will miss their moment far more often than the descriptions imply.

- **Missing Why in descriptions.** Descriptions explain *when* to load a skill but not *what ExFu is* or *who the user is*. A Claude encountering these descriptions cold has no idea whether ExFu is a company, a product, a framework, or internal jargon — so context-free trigger matching is all it can do.

- **Bodies lead with constraints, not rationale.** Almost every skill opens with "Hard constraints" — the list of what not to do. The Why (why this skill exists, what it's actually for, what good outcome it's driving toward) is either buried mid-body or absent entirely. The install skills (solo, team, team-admin) are the exception: they have genuine Why sections that explain the transformation being delivered.

- **Trigger realism weakest in utility skills.** `skill-packaging`, `writing-styles`, `reminders`, `inbox`, and `git-substrate-sync` have descriptions that only fire if Claude already knows ExFu vocabulary. But these are precisely the skills most likely to be needed mid-conversation when a user says something natural — "save this", "write this email for me", "remind me Friday". The descriptions don't catch those.

- **Good bodies let down by weak descriptions.** Several skills have genuinely strong bodies — `substrate`, `git-substrate-sync`, `exfu-install-solo`, `writing-styles` — but the description and trigger framing means Claude is unlikely to load them at the right moment. The body quality doesn't compensate for a description that only fires on insider words.

---

## Skill-by-skill (18 items)

---

### `exfu-start`
- **Description score:** NEEDS-WORK
- **Description issue:** Says what it does (first-run detection, triage) but doesn't tell Claude what ExFu is, who the user is, or why this skill matters — cold-reading Claude has no grounding context.
- **Trigger realism:** NEEDS-WORK — triggers on "exfu", "install", "set up my Claude": all insider vocabulary. Misses a returning user who opens a session and immediately says "where was I?" or "I need to update my setup."
- **Body score:** GOOD
- **Body issue:** Strong first-run detection logic and clear routing; the example conversation lines are well-calibrated. Minor: Why is implicit (orientation + routing) but could be stated in one line at top.
- **Recommended fix:** Add one sentence to description naming what ExFu is and who uses it. Add natural-language triggers: "I want to update my Claude setup", "where does all my stuff live", "I just installed something".

---

### `exfu-guides`
- **Description score:** NEEDS-WORK
- **Description issue:** Lists question types well but doesn't say what ExFu is or who the user is — Claude reading cold only knows this is a reference surface for something called ExFu.
- **Trigger realism:** NEEDS-WORK — triggers on "what is X", "explain the substrate", "what are scopes for" — plausible, but misses implicit questions like "how do you remember things between sessions?" or "can you explain how this all works?" which are more likely phrasings from real users.
- **Body score:** GOOD
- **Body issue:** Solid coverage of question types, reference index is clear, deep-research teaching move is a good inclusion. Why is implicit but present ("answer architecture-level questions well"). No structural issues.
- **Recommended fix:** Description should name ExFu as a Claude setup tool and characterise the user (someone who just installed or is curious about their setup). Add more natural phrasings to triggers.

---

### `exfu-create-wow`
- **Description score:** NEEDS-WORK
- **Description issue:** Describes when to invoke (install flow, explicit user request) but no context about what a "wow" is or what ExFu is — a Claude reading this cold doesn't know what it's creating or why.
- **Trigger realism:** NEEDS-WORK — triggers on "rebuild my wow", "regenerate my way of working": insider vocabulary. Real user is more likely to say "I've changed a lot of my setup, can you update your map?" or "things have moved around, you're pointing at old folders."
- **Body score:** GOOD
- **Body issue:** Read-set, customisation rules, and generation process are clear and well-disciplined. Why is genuinely present: "generates the user's personal wow skill". Minor: the "substantial regeneration" distinction is useful but could be one line earlier.
- **Recommended fix:** Description should define what wow is in plain language ("the user's personal navigation map for their Claude setup"). Add triggers for substrate-evolution language ("my folders have changed", "things are different now").

---

### `exfu-migrate-from-fetch-model`
- **Description score:** NEEDS-WORK
- **Description issue:** Detection criteria are technically precise but entirely insider ("fetch model", "exfu.ai/clients/ URLs", "packaged .skill file") — a cold Claude won't know what these mean without prior context.
- **Trigger realism:** CRITICAL — trigger phrases assume knowledge of ExFu install history ("old fetch model", "exfu.ai/clients/"). Real user is unlikely to say any of these; they'll say "I already had this set up" or "I used the old version". The skill is mostly invoked by other skills rather than users directly, which limits the real-world exposure — but the description still fails for the edge case where a user triggers it conversationally.
- **Body score:** GOOD
- **Body issue:** Detection logic, confirmation step, migration steps, and verify sequence are all solid. Constraint "Do not proceed without explicit user confirmation" is well-placed. Why is implicit: preserving personal content while upgrading the delivery mechanism. Could be one explicit sentence.
- **Recommended fix:** This skill is mostly agent-invoked, but the description should still work in isolation. Add plain-language framing: "user who already has an ExFu setup installed via an older method and is upgrading to the plugin version." Triggers should include "I already set this up before" / "I used the old version."

---

### `substrate`
- **Description score:** NEEDS-WORK
- **Description issue:** Description is long and attempts to cover everything the skill does, but is framed in insider vocabulary ("substrate", "substrate-aware conversation", "wow skill delegates to it") — a Claude with no ExFu context won't know what a "substrate" is, undermining the usefulness of an otherwise detailed description.
- **Trigger realism:** CRITICAL — triggers listed include "substrate", "load my substrate", "check my setup", "save", "share for review", "check for updates". Of these, only "save" and "check for updates" are natural user language. The others are insider terms. Real user is far more likely to say "do you know who I am?", "can you pull up the Acme deal?", "where is my stuff?", "what have we got on X?" None of these appear.
- **Body score:** GOOD
- **Body issue:** One of the strongest bodies in the codebase. Steps are clear, the Why is embedded throughout (giving Claude persistent memory and context), two-layer model is well-explained, and ongoing-behaviour rules are disciplined. Hard constraints are genuinely hard and placed prominently. No significant issues.
- **Recommended fix:** Description needs a plain-English lead sentence explaining what the substrate is for a cold reader. Trigger vocabulary should be expanded with natural user-domain phrasings: "do you know about X?", "can you find my notes on Y?", "what's in my inbox?", "what do I have on for today?".

---

### `skill-packaging`
- **Description score:** NEEDS-WORK
- **Description issue:** Describes itself as "an addendum to skill-creator" which assumes Claude knows what skill-creator is. No context for why this override exists or what ExFu is.
- **Trigger realism:** CRITICAL — triggers include "install a skill", "create a skill", "package a skill". These are plausible technical phrasings, but miss the natural user expression: "I want to make a new skill", "can you turn this into something reusable?", "how do I save this behaviour?" The "addendum" framing also means Claude might not load it alongside skill-creator if it only looks for "package a skill" as a literal phrase.
- **Body score:** NEEDS-WORK
- **Body issue:** Very brief — the constraint and the rule are clear, but there is no Why. Why does this override exist? What's the consequence of the wrong method? One sentence of rationale would dramatically improve Claude's ability to apply good judgement if the situation deviates. The Drafts section is good.
- **Recommended fix:** Add Why: this override exists because writing to `.claude/` bypasses the user-facing install flow and creates skills the user hasn't consciously approved. Expand triggers to natural user phrasings. Description should stand alone without requiring knowledge of "skill-creator."

---

### `reminders`
- **Description score:** GOOD
- **Description issue:** None — description covers the use cases clearly: set a reminder, check the list, complete, snooze, session-start surface. Natural-language triggers are present ("remind me to X", "don't let me forget").
- **Trigger realism:** NEEDS-WORK — trigger phrases are reasonable but slightly formal ("flag this for [date]", "when they ask what's on their reminder list"). Misses very natural phrasings: "don't let that slip", "I'll forget this", "ping me about this next week", "what did I say I'd follow up on?"
- **Body score:** GOOD
- **Body issue:** Clear, practical, well-structured. File format is shown, all four actions are covered, conventions are sensible. Why is implicitly present (the distinction between reminders and task managers is well drawn). No significant gaps.
- **Recommended fix:** Add a few more natural trigger phrasings to the description. Consider whether the "called by substrate on session load" path needs any clarification in the body for when reminders is invoked programmatically vs conversationally.

---

### `inbox`
- **Description score:** GOOD
- **Description issue:** None significant — triggers cover the common cases ("save this", "add to inbox", "capture that", "don't lose this thought"). The distinction from reminders is drawn.
- **Trigger realism:** NEEDS-WORK — "save this" and "capture that" are good. Misses natural variations: "hold onto this", "I want to come back to this", "jot this down for me", "this is important but I don't know where it goes yet."
- **Body score:** GOOD
- **Body issue:** Clean, practical, well-disciplined. The distinction from reminders is sharp ("place-agnostic quick capture"). Review/process logic is useful. The one omission: Why is not explicitly stated — "because the user's head is full and they need frictionless dump" is the rationale and it's worth one line.
- **Recommended fix:** Add slightly more natural capture phrasings to the description trigger list. One-line Why in the body would complete the picture.

---

### `writing-styles`
- **Description score:** GOOD
- **Description issue:** Description covers the scope clearly ("whenever producing written output for or on behalf of the user") and the two-part mechanism (voice profile + anti-slop). Who the user is and what they're trying to do is reasonably clear.
- **Trigger realism:** NEEDS-WORK — "drafting emails, posts, docs, messages, replies, or editing their text" is solid scope coverage but as trigger language it's generic. Misses real user-initiated phrasings: "write this for me", "draft an email to X", "can you sound more like me?", "this doesn't sound right, fix it", "edit this in my style."
- **Body score:** GOOD
- **Body issue:** Strong. Intake process, anti-slop layer, profile template, drafting vs editing distinction are all well-specified. Why is genuinely present: "Write in the user's voice, not Claude's." Iteration section is good practice.
- **Recommended fix:** Add natural trigger phrasings to the description. Consider whether "first use: run the intake" should note that the intake is a one-time investment worth explaining to the user ("this takes 5 minutes once and then applies forever").

---

### `git-substrate-sync`
- **Description score:** NEEDS-WORK
- **Description issue:** Description names the technical scope well (team git substrate, pull/commit/push/merge) but is entirely insider — "team-plugin or team-admin-plugin is active", "substrate read or write is happening" — assumes Claude knows ExFu's plugin architecture.
- **Trigger realism:** CRITICAL — triggers on "loads automatically when team-plugin or team-admin-plugin is active" — this is purely system-level. There are no user-language triggers. Real team member is unlikely to say "git-substrate-sync" — they'll say "save my changes", "pull down the latest", "I think there's a conflict", "did my colleague update this?", "how do I share this with the team?" None of these appear.
- **Body score:** GOOD
- **Body issue:** Excellent. One of the best bodies in the codebase. Session-start pull, commit timing, push cadence, merge conflict handling, hygiene checks, recovery patterns, and skill interplay are all well-specified. Why is genuinely present ("make git invisible when things go well, and clear when they don't"). Hard constraints are well-placed and non-negotiable in tone.
- **Recommended fix:** Description needs natural user-language triggers: "save to the team", "check if anything changed", "pull the latest", "I think there's a conflict", "share my notes with the team". The auto-load trigger should also survive in case a user explicitly mentions git.

---

### `exfu-install-solo`
- **Description score:** NEEDS-WORK
- **Description issue:** Trigger phrases ("install me", "set up my substrate", "let's start the install") are partially natural but still insider ("substrate" in particular). No framing of what ExFu is or who this user is for a cold reader.
- **Trigger realism:** NEEDS-WORK — "install me", "set up my substrate", "let's start the install" are half-insider. Real user is more likely to say "I just installed something, what do I do?", "I want to get set up", "I'm new to this, where do I start?" after installing the plugin. The trigger should also note that this is almost always agent-invoked by `exfu-start`, not user-triggered directly.
- **Body score:** GOOD
- **Body issue:** One of the best bodies. Why is explicitly stated ("coaching as much as technical setup", the transformation section is strong). The opening sequence is well-structured. Hard constraints are clear. The Box caveat is appropriately surfaced. The checklist at the end is useful. Minor: the inline TODO about Box Drive UI labels should either be resolved or marked as a known open item rather than left as a TODO comment in production content.
- **Recommended fix:** Resolve the Box Drive TODO or move it to a known-issues doc. Description should note that this skill is typically invoked by exfu-start, not directly by users. Add natural first-session triggers.

---

### `box-filesystem-management`
- **Description score:** NEEDS-WORK
- **Description issue:** Describes the technical scope well but is entirely Claude-facing and insider ("Box store", "knowledge base", "CRUD workarounds"). No framing of why this exists or what problem it solves for the user.
- **Trigger realism:** NEEDS-WORK — triggers on "Box store, knowledge base, file management, or instructions to save, update, move, or delete files" — the last part ("save, update, move, delete files") is natural language but mixed with insider terms. Real user says "save that", "move this to the Acme folder", "get rid of that note", "where did that file go?" Those phrasings are implied but not stated.
- **Body score:** GOOD
- **Body issue:** Technically solid. Access mode selection, connector workarounds, trash workflow, naming conventions, and behaviour rules are all well-specified. Why is implicit (Box has limitations that need workarounds; Claude manages files on the user's behalf). One sentence stating this explicitly would help a cold reader.
- **Recommended fix:** Add a Why sentence to the body intro. Description trigger should lead with natural user phrasings ("save this", "organise my files", "where did that go") before or instead of "Box store" terminology.

---

### `exfu-install-team`
- **Description score:** NEEDS-WORK
- **Description issue:** Describes the user well ("team member joining an existing team setup, not the champion") which is the most context-rich description in the set — but still relies on insider terms ("personal substrate", "team substrate", "orchestrator routes").
- **Trigger realism:** NEEDS-WORK — triggers on "install me", "join my team's setup", "team plugin install" — the first is generic, the others are insider. Real new team member says "I was told to set this up", "my colleague said I need to install something", "I have a link to a plugin, what do I do?" None of these appear.
- **Body score:** GOOD
- **Body issue:** Strong. The "two layers, one experience" principle is the best articulation of the joiner's mental model across any of the install skills. Why is explicitly stated. The onboarding pack beat is a good structural decision. Hard constraints are appropriately differentiated from solo install. Checklist at end is useful.
- **Recommended fix:** Description should replace "orchestrator routes" with plain language. Add triggers for what a real new joiner actually says when they arrive.

---

### `exfu-install-team-admin`
- **Description score:** NEEDS-WORK
- **Description issue:** Reasonably descriptive of who this is for (substrate champion, team admin plugin) but "champion install" and "orchestrator routes" are insider terms. No plain-language framing of what ExFu is.
- **Trigger realism:** NEEDS-WORK — "set up team admin", "champion install" are insider. Real substrate champion may have just been handed the plugin by Alastair and says "I'm supposed to set up the team's shared AI setup" or "I'm the one responsible for our team's Claude configuration". These are more realistic than "champion install."
- **Body score:** GOOD
- **Body issue:** Strong. The champion-as-designer framing is excellent. Why is explicitly stated ("not just setting up for themselves; setting up the infrastructure every future team member lands on"). The 14-step sequence is comprehensive. "What this plugin does NOT do" section is a good guardrail for scope.
- **Recommended fix:** Replace insider trigger vocabulary with role-description language. Description should name what a substrate champion is in plain terms.

---

### `team-repo-provisioning`
- **Description score:** NEEDS-WORK
- **Description issue:** Describes the technical task well but assumes the reader knows what "team substrate", "substrate champion", and "substrate repo" mean. No context about why this step exists.
- **Trigger realism:** NEEDS-WORK — triggers on "set up team repo", "create team substrate repo", "provision team git repo". These are plausible but technical. Real champion may say "how do I create the repo for the team?", "where should the team's shared stuff live?", "I need to set up a git repo for our Claude setup." The last is close but more natural variations are missing.
- **Body score:** GOOD
- **Body issue:** Provider-by-provider steps are useful and clear. Hard constraints are well-placed (private always, no credential commits). Why is implicit but underarticulated — one sentence on why the repo exists (it's the shared substrate's home; every team member clones it) would help a cold reader. The "Start small" note at the end is well-placed.
- **Recommended fix:** Add one Why sentence at the top of the body. Description should include natural trigger phrasings from a champion who's been told to "set up the team's shared AI knowledge base."

---

### `team-shared-skills-authoring`
- **Description score:** NEEDS-WORK
- **Description issue:** Trigger phrases ("write a shared skill", "add to team skills", "promote this skill") are reasonable but assume the champion knows the ExFu skill vocabulary. No context on why shared skills are different from personal ones.
- **Trigger realism:** NEEDS-WORK — "refactor skill for the team", "team skill conventions" are insider. Real champion says "I've got a skill that would be useful for the whole team, how do I share it?", "how do I make a skill everyone on the team can use?", "I want all my colleagues' Claude to know about X." More natural phrasings need to appear.
- **Body score:** GOOD
- **Body issue:** Strong. The "what makes a skill shared" framework is exactly right. The personal-vs-shared distinction is well-drawn. Pre-commit hygiene checks are useful and well-placed. The worked example (poor vs good shared skill) is the best teaching element in the codebase. Why is implicit throughout but could be one line: "because a skill that works for one person often fails everyone else if personal assumptions are embedded."
- **Recommended fix:** Add Why sentence to body intro. Description triggers should include champion-natural phrasings about sharing a skill with the team.

---

### `team-onboard-member`
- **Description score:** NEEDS-WORK
- **Description issue:** Describes the output clearly (onboarding pack, markdown, champion sends to joiner) but assumes "substrate champion" is a known term. No context on why onboarding packs exist or what problem they solve.
- **Trigger realism:** NEEDS-WORK — "onboard a new member", "create onboarding pack", "add someone to the team" are reasonable. Missing: "someone new is joining the team", "I need to get [person] set up", "how do I tell a new person to install this?", "my colleague just joined and needs to set up Claude." These are the more natural phrasings.
- **Body score:** GOOD
- **Body issue:** Step-by-step is clear, pack template is well-structured, hard constraints are appropriate (no credentials, plain markdown). Why is implicit: "so the joiner can paste it into their install conversation and get a personalised flow." Worth stating explicitly, as it explains why the pack format is what it is.
- **Recommended fix:** Add Why to body intro explaining why packs are structured the way they are. Description should include natural champion-phrasings for "I have a new team member to set up."

---

### `exfu-upgrade-from-team-to-admin`
- **Description score:** CRITICAL
- **Description issue:** "This skill fires once, only when a team-plugin install is detected during the team-admin install flow. Do not invoke it manually outside that context." — this is purely internal routing guidance. There is no description of what ExFu is, who the user is, or what this skill is for. It reads as a developer comment, not a skill description.
- **Trigger realism:** CRITICAL — "Do not invoke it manually outside that context" explicitly removes user-language triggers. This is correct since the skill is agent-invoked, but then the description needs to say so clearly and explain what it does for a cold-reading Claude. Currently it only says what it is NOT (a manual trigger), not what it IS.
- **Body score:** NEEDS-WORK
- **Body issue:** Steps are reasonable but Why is largely absent. Why would someone upgrade from team to admin? (They're becoming the team's substrate champion.) What is preserved and why does that matter? The Step 2 explanation is the closest to a Why, but it's buried in a user-facing message rather than stated as rationale for Claude. Step 4 lists skill names without explaining what each does, which is unhelpful for a Claude encountering this cold.
- **Recommended fix:** Rewrite description to explain this is an agent-invoked upgrade skill (not user-triggered) and what it accomplishes. Body should add a brief Why: a team member who becomes their team's substrate champion needs admin capabilities without losing what they've built.

---

## Resource-by-resource (12 items)

---

### `substrate-guide.md` (v5)
- **Independence:** GOOD — reads well in isolation; the opening "What is a substrate?" section provides sufficient context for a cold reader. The Why section ("Why a substrate, rather than Claude's built-in features") is particularly strong and self-contained.
- **Richness:** GOOD — comprehensive coverage of the two-layer model, data tiers, directory structure, CLAUDE.md guard, naming conventions. V5 additions (multi-org/team, wrapping plugin) are well-integrated.
- **Structural quality:** GOOD — de facto golden-circle structure: opens with what/why, then how (conventions, directory layout), then what (specific rules). Not labelled as such but follows the pattern naturally.
- **Score:** GOOD
- **Issue:** None critical. The "Why a substrate" section could signal more explicitly that it's optional reading for users who already bought in — it's aimed at a sceptic, which is a different reader from the Claude doing substrate work.

---

### `the-substrate-primer.md`
- **Independence:** GOOD — explicitly flagged as "human-facing pre-install reading." Self-contained and digestible by a non-technical reader with no prior ExFu knowledge. Best onboarding read in the plugin.
- **Richness:** GOOD — four ingredients, discoverability asymmetry, build-by-doing, chief-of-staff framing, what-it-is-not, teams/orgs note. Covers the full picture without being exhaustive.
- **Structural quality:** GOOD — implicitly golden-circle: starts with the problem (Why), covers the mechanism (How via four ingredients), then what you get and what it isn't. Flows naturally without feeling like a framework exercise.
- **Score:** GOOD
- **Issue:** None. This is the strongest resource document in the set.

---

### `exfu-primer.md`
- **Independence:** GOOD — self-contained. Clear framing of what ExFu is, what you get, who it's for, what it's not, how to start. Would work as a standalone product page.
- **Richness:** GOOD — covers all the key claims and distinguishes ExFu from other products clearly. The "what it's not" section is one of the clearest trust-building moves in the set.
- **Structural quality:** GOOD — golden-circle pattern: Why (problem with default Claude), How (the install conversation, the transformation), What (the deliverables). Well sequenced.
- **Score:** GOOD
- **Issue:** The "unlock" in "People who are already using Claude and can tell there's more to unlock" technically violates the brand-voice banlist. Minor, but worth noting.

---

### `ecosystem-references.md`
- **Independence:** GOOD — clearly framed as a catalogue and reads well in isolation. Explains why it exists (ExFu doesn't re-teach everything in-house) and what to do when it ages.
- **Richness:** GOOD — covers Anthropic resources, third-party community tools, and the deep-research-as-a-move pattern. The sample research prompts are genuinely useful.
- **Structural quality:** NEEDS-WORK — the document leads with the catalogue items and ends with the deep-research pattern, but doesn't open with a clear framing of why this resource exists or how to use it. The first paragraph covers intent but could be stronger. The deep-research section (arguably the most durable content since the catalogue will age) is buried at the bottom.
- **Score:** NEEDS-WORK
- **Issue:** Consider moving the deep-research pattern section earlier — it's more durable than the specific URLs — and adding a one-line framing at the top of each section ("these are the resources we trust most right now; treat them as a starting point, not gospel").

---

### `teaching-artefacts.md`
- **Independence:** GOOD — reads clearly in isolation. The intro explains what the catalogue is and how to use it (one diagram per moment of need).
- **Richness:** GOOD — all five artefacts are described with path, variant, what-it-teaches, and when-to-show-it. The format is consistent. The extensibility note is important.
- **Structural quality:** GOOD — each entry is well-structured. The catalogue is immediately usable by any install skill that reads it.
- **Score:** GOOD
- **Issue:** None significant. The `admin-vs-user-domain` entry references `admin-plane-vs-user-domain.png` in one install skill but the path listed here is `admin-vs-user.png` — potential filename mismatch worth verifying.

---

### `pii-layer-guidance.md`
- **Independence:** GOOD — strong opening section ("Why the PII layer exists") that any reader can follow without ExFu context. The what-counts-as-PII and what-doesn't sections remove ambiguity. The skill-author checklist makes it actionable.
- **Richness:** GOOD — covers the rationale, the contract shape, good and bad patterns, ExFu vs wrapper responsibilities, solo user guidance. One of the most substantive resources in the set.
- **Structural quality:** GOOD — golden-circle naturally: Why (the threat model), How (the contract shape and access patterns), What (the checklist and examples). Could make the golden-circle structure explicit in headings for faster navigation.
- **Score:** GOOD
- **Issue:** None critical. The document references `cross-cut-extension-and-wrapping.md` which is a planning file, not a plugin resource — the reference will not resolve in a deployed plugin. Worth checking whether this reference should be updated or removed.

---

### `claude-desktop-general-instructions.md`
- **Independence:** NEEDS-WORK — the document gives no context for why these instructions exist or what they're for. A cold reader (or a Claude reading it) gets only the paste-ready block with no framing about why each directive is included.
- **Richness:** NEEDS-WORK — the block is thin: three directives. No rationale for any of them. Why no sycophantic openers? Why can't Claude make unilateral plan changes? Why load wow? None of this is explained.
- **Structural quality:** NEEDS-WORK — there is no structure. It's a paste block with a brief intro. For a resource that installs in every user's Claude Desktop, the absence of any reasoning is a missed teaching moment.
- **Score:** NEEDS-WORK
- **Issue:** The resource is purely operational. Adding a brief comments layer (not in the paste block itself) explaining the rationale for each directive would help install agents understand why they're installing this and answer user questions about it.

---

### `claude-desktop-cowork-global-instructions.md`
- **Independence:** NEEDS-WORK — even thinner than the general instructions. Two directives with no rationale. The note about wow and this block complementing each other is helpful but brief.
- **Richness:** NEEDS-WORK — minimal content. The golden-circle directive ("plans must be rich and complete") is a good inclusion but its rationale ("no conversational context survives the bridge to Claude Code") is explained in the wrapper text, not in the paste block itself, which means it's invisible to users who read their global instructions.
- **Structural quality:** NEEDS-WORK — same issue as above: purely a paste block, no structural reasoning.
- **Score:** NEEDS-WORK
- **Issue:** Same recommendation as the general instructions: add rationale in comments outside the paste block so install agents can explain each directive if asked.

---

### `compliance-briefing.md`
- **Independence:** GOOD — excellent. Explicitly framed as "written for the substrate champion to share with their IT or security team." Defines what it covers and explicitly excludes Anthropic's own terms (directing readers elsewhere). A cold reader who has never heard of ExFu can follow it.
- **Richness:** GOOD — data flow, recommended controls, ISO 27001 mapping, hygiene rules, audit trail, backup, and what-this-is-and-isn't. Comprehensive for its audience.
- **Structural quality:** GOOD — appropriate for its context (IT review audience). Numbered sections, table format for ISO controls. The framing is compliance-report-shaped rather than golden-circle-shaped, which is correct for the audience.
- **Score:** GOOD
- **Issue:** None critical. The "Questions" section visible in the file appears to be a heading with no content following it — worth checking whether this is a truncation artifact.

---

### `wow-template.md`
- **Independence:** GOOD — the template is self-describing. The intro explains what wow does, what it holds, and what it doesn't hold. The "discipline: keep wow lean" principle is clear.
- **Richness:** GOOD — navigation map, always-on kernel with all four subsections, bootstrap sequence, and iteration guidance. The stubs are honest ("note any deviations here as they emerge") rather than pre-populated with false content.
- **Structural quality:** GOOD — the two jobs of wow (navigation map + thin kernel) frame the whole template. Bootstrap before content, content in two clear sections, iteration at the end. Well-organised.
- **Score:** GOOD
- **Issue:** The description frontmatter ("Triggers on 'wow', 'way of working'...") is in the same position as a skill description, but this is a template that generates real wow skills — Claude should read it as a template, not as a loadable skill. The `name: wow` frontmatter might cause confusion if Claude treats it as a real skill rather than a template. Worth a note at the top of the file clarifying it's a template.

---

### `scope-skill-template.md`
- **Independence:** GOOD — the template explains its own purpose clearly in the body ("its job is discoverability"). The placeholder guidance is specific enough to be actionable.
- **Richness:** NEEDS-WORK — the template is minimal by design, which is appropriate, but the description frontmatter placeholder is arguably the most important part and gets only one line of guidance. "What this skill is, what kind of work happens in it, key entities or people involved" is correct but doesn't explain the trigger-realism principle — that the description should catch real user-domain phrasings, not just the scope name.
- **Structural quality:** GOOD — short, structured, and well-targeted. The "key entities and relationships" section is a good prompt for content that helps triggering.
- **Score:** NEEDS-WORK
- **Issue:** The description placeholder guidance should teach the trigger-realism principle: real users will say "what's happening with Acme?" not "load the Acme scope." The description should trigger on those user-natural phrasings. This is the most transferable lesson from the skill audit and it's missing from the template that will govern all future scope skills.

---

## Recommended rework order

**1. `substrate` — description + triggers (CRITICAL)**
This is the core session-bootstrap skill. It loads in almost every substantive conversation. Its trigger description is the most consequential in the codebase — if it only fires on "substrate" and "load my substrate", real users' sessions never get properly bootstrapped. Fix first. The body needs nothing; only the description/triggers need work. High impact, low effort.

**2. `exfu-upgrade-from-team-to-admin` — description + body (CRITICAL)**
This is the only skill with a CRITICAL description and NEEDS-WORK body. The description is currently a developer note, not a skill description. Since it's agent-invoked, the risk is lower than substrate, but it's the most broken description in the set. Fix second.

**3. `git-substrate-sync` — triggers (CRITICAL trigger realism, GOOD body)**
The skill body is one of the best in the codebase, but the trigger description means team users will never benefit from it conversationally. Adding natural user-language triggers ("save to the team", "check if my colleague updated this", "I think there's a conflict") directly enables team substrate use. Third because team install is the more complex use case and good trigger coverage matters.

**4. `skill-packaging` — description + body Why (CRITICAL trigger realism, NEEDS-WORK body)**
This skill governs how all future user-authored skills are created. If it doesn't trigger correctly, users create skills the wrong way. The body needs a one-sentence Why. Description needs natural triggers. Fourth because skill authoring is a post-install behaviour that matters for retention.

**5. `scope-skill-template.md` — description placeholder guidance (NEEDS-WORK)**
Every scope skill the user ever creates will be modelled on this template. Teaching trigger realism here multiplies forward into every scope skill in every substrate. The fix is small (add guidance about natural user phrasings in the description placeholder) but the leverage is high.

**The rest (13 skills + remaining resources):** Can be batched as a single sweep. The pattern is the same across all of them: add a Why sentence to descriptions, add natural-user-language trigger phrasings, and where bodies lack an explicit Why statement, add one at the top. This is an editing pass, not a rewrite. Estimated two to three hours for a thorough human editor working through them in order.

---

*Audit completed May 2026. Covers 18 skills and 12 resources across solo, team, and team-admin plugin variants. Three scoring dimensions applied to skills: description quality, body quality, trigger realism.*
