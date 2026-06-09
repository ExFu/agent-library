---
name: outcome-framed-elicitation
applies-to: install-agents, scope-creation, ontology-extension
---

# Principle: Outcome-framed elicitation, not concept-framed

## Why

When the agent asks the user about an ontology type the user has never heard of, framing the question around the mechanism ("do you need a todos folder?", "do you want a librarian function?") forces the user to learn the concept before they can give a useful answer. The user is not here to learn ExFu's mental model; they are here to do their work. Concept-framed questions produce shrug answers, false negatives, and users who quietly disengage from parts of the install they actually needed.

Outcome-framed questions ("do you want me to capture todos and tasks for this project?", "if you had someone looking after this data and doing housekeeping at the end of each day, what would you ask them to do, if anything?") let the user respond from their own world. The agent receives a real answer it can act on.

## How

For every user-facing ontology type, the agent reaches for the elicitation prompt at `exfu/ontologies/<type>/elicitation.md`. The prompt is in user vocabulary, frames the question around the outcome the type delivers, and gives a brief illustrative example. The agent does not paraphrase the prompt into insider language; it uses the user-vocabulary phrasing as-is or adapts only to the conversational moment.

Some ontology types are *infrastructure* (librarians, conventions, ontologies, schemas, principles). These are not offered to the user at all. They are materialised silently from `exfu/`.

## What

Always: outcome before mechanism. *"Do you want me to keep track of who you're talking to at Acme, and remember details across sessions?"* is good. *"Do you want a contacts database?"* is not.

Never: ask the user to choose between two ontology-type names. If the user does not know what a "scope" or a "librarian" is, the question fails before the answer. Offer the outcome; name the mechanism only if the user asks how it works.

When the user volunteers a need that matches an ontology type ("I keep forgetting to follow up on things"), reach for the type and offer the outcome ("I can capture those for you and surface them when they're due, want to set that up?"). Do not say the word "reminders" or "ontology" or "type" unless the user does first.
