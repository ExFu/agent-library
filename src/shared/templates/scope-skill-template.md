---
name: scope-{{SCOPE_NAME}}
description: {{ONE_LINE_DESCRIPTION — what this scope is, what kind of work happens in it, key entities or people involved. The description is what Claude matches against to decide whether to load this skill, so make it specific: who/what the scope is about, what triggers should fire it.}}
---

# {{SCOPE_DISPLAY_NAME}}

This is a scope skill. Its job is discoverability: when the user mentions {{SCOPE_NAME}} or the conversation drifts into its territory, this skill triggers and tells Claude where the scope folder is and how the scope is organised.

The substance of the scope lives in the scope folder, not in this skill. This skill is a short anchor.

## Scope folder

- Path: `scopes/{{SCOPE_NAME}}/`
- On load, read the folder's `README.md` to understand what's inside and what dependencies exist.

## What this scope is for

{{Two or three sentences describing what kind of work happens in this scope. Why it exists. What the user is trying to accomplish here. When in doubt, lean specific — this is what helps Claude recognise relevant conversations.}}

## Key entities and relationships

{{List the people, companies, products, teams, or other entities that come up in this scope. If their standing facts live in `context/`, link to the relevant file. For example:

- Main contact at Acme: Jane Doe (see `context/work/acme.md`)
- Internal lead: me
- Related scope: `scope-acme-followup`}}

## Conventions specific to this scope

{{Any per-scope conventions. For example: how meeting notes are named, what format proposals take, which templates to use. Omit this section if there aren't any.}}

## Related skills

{{Any other skills that usually pair with this one — for example, if this is a sales scope, the `call-prep` or `draft-outreach` skills might be relevant. Omit if none.}}
