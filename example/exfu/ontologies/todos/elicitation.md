# Elicitation: todos

## When the install agent uses this prompt

When the agent is shaping a new scope (user-tier or work-area) and reaches the moment to offer optional ontology types, or when the user volunteers something like "I keep losing track of small things" or "there's stuff I need to follow up on but I forget".

## The prompt (use as-is or lightly adapted)

For a new scope:

> *"Do you want me to keep a running list of things to follow up on or do for this {{scope-name}}? I can capture them as they come up and surface what's due when it's relevant. Nothing fancy unless you want it to be."*

For an existing scope where the user mentions a slip:

> *"That sounds like the kind of thing worth not losing. Want me to start a small follow-ups list for this {{scope-name}}? I'll bring it up when the time matters."*

For the user-tier (cross-scope personal todos):

> *"Do you want me to keep a running list of small things you want to remember to do? Not your full task system, just the little stuff that slips. I can surface what's due when it matters."*

## What to listen for

A clear yes: create the `todos/` folder, copy the `agent.md` snapshot, write the README, create an empty `todos.md`. Confirm briefly and move on.

A clear no: do not create the folder. Note in the scope's `scope.md` that todos were offered and declined, so a future session does not re-ask.

Uncertainty: offer one concrete example ("for instance, you mentioned you wanted to follow up with Acme on Friday — I'd capture that here"). Often the example tips the decision.

## What not to say

Avoid: "do you want a todos folder?", "I can set up a todos ontology type for you", "this is one of the ExFu defaults for this scope", "do you need a task management system?". All of these are concept-framed (or mechanism-framed) and fail.

## Variant selection

If the user wants more than a flat list (assignees, statuses, structured records), offer the `structured-records` variant: *"do you want this to be a simple list, or something more like a small ticket system with status and details per item?"*. Default to flat unless the user clearly wants structured.

## Why this is a separate file from agent.md

`agent.md` is what gets copied into the folder once it exists (the convention snapshot for ongoing behaviour). `elicitation.md` is what the install agent uses to decide whether to create the folder in the first place. Different audiences, different moments, different content.
