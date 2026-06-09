---
recommendation: calendar-connector
category: connector
provider: Anthropic / Google / Apple
status: stable
---

# Recommendation: Calendar connector

## What

A Claude connector that gives Claude read (and optionally write) access to the user's calendar across Google, Apple, and Microsoft sources.

## Why a user would want this

The morning briefing pulls real meetings from the user's actual calendar, not a separate to-do list. Claude can answer "what do I have on this week?" without the user pasting in their schedule. When the user mentions a meeting, Claude knows when it is, who is in it, and can prep accordingly.

## Trigger phrases or contexts to surface this

The install agent surfaces this recommendation when the user mentions any of:

- Their calendar, their week, their schedule.
- Meetings they have to prepare for.
- Conflicts they need to manage.
- "What am I doing today?" / "What's coming up?"
- Setting up a daily briefing.
- Any planning conversation that references time.

Do not surface unsolicited. The point is contextual: the agent recognises the moment when the user would benefit, and offers it then.

## Caveats

- Requires the user to authenticate against their calendar provider via the Claude connector setup flow. Five minutes the first time, zero thereafter.
- Read access is sufficient for most uses; write access is more invasive and should be discussed with the user before enabling.
- Privacy: the connector reads only what the user authorises. If the user has a personal and a work calendar, the agent surfaces both unless the user scopes the connector to one.

## Where to get it

Available in the Claude connector library (Claude Desktop → Settings → Connectors). The install agent can walk the user through enabling it.

## Notes

If the user has already set this up before reaching ExFu, the install agent skips the recommendation and just confirms the connection is active. Wow's navigation map should record that calendar connector is available so future sessions know to reach for it without prompting.
