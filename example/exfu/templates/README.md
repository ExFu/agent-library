# exfu/templates/

## Purpose

Templates the install agent fills in during the install conversation. Distinct from `exfu/ontologies/<type>/agent.md` templates (which are copied as convention snapshots into typed folders); these are filled-in artifacts the agent generates from user input.

## Contents

- `wow-template.md` — the user's personal `wow` skill template. Filled in during the install with the user's about-me, navigation map, always-on kernel preferences, and pointers to active scopes.

(A real install would carry more: scope-template.md, onboarding-pack-template.md, etc. This example shows one illustrative template.)

## Dependencies

- Read by install entrypoint skills (`exfu-install-solo`, `exfu-install-team`, `exfu-install-team-admin` in current v0.2.x; equivalent in v0.3.0).
- Read by `exfu-create-wow` when generating or regenerating a user's wow.

## Shape of a template

Each template is a markdown file with placeholders (e.g. `{{username}}`, `{{about-me}}`, `{{active-scopes}}`). The install agent reads the template, fills in the placeholders from the install conversation, and produces a personalised artifact.

For wow: the output is packaged as a skill-definition (see `exfu/skills/`) and rendered into the user's target platform.

For scope: the output is written to the scope folder as `scope.md` (the marker + agent reference).

## Why templates are not ontology types

A template is a one-shot input to an install-time generation step. It produces something; it is not itself something the substrate hosts long-term. Ontology types are about persistent folder shapes the substrate carries; templates are about the install agent's generation behaviour.
