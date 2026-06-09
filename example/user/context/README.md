# user/context/

## Purpose

Standing personal context for Alastair. Identity-level material; read often, changes slowly.

## Contents

- `me/` — facts about Alastair himself (about-me, role, preferences, tools, writing voice).

Other personal context categories (e.g. `relationships/`, `health/`, `finances/`) can be added as Alastair adopts them. None are required; the substrate grows with the user.

## Dependencies

- Read by every session that loads the user-tier scope.
- The `me/about.md` file is read by setup skills (`setup-reminders`, `setup-inbox`, `setup-writing-styles`) to determine the username for generated per-user skills.

## Why "context" and not "info" or "profile"

Context is the substrate term for read-to-orient material (as distinct from a scope, which is read-to-pick-up-work). The fuzzy-zone test: if Alastair (or his agent) would read it to *orient*, it lives here. If he would read it to *do a piece of work*, it lives in a scope.
