# Reminders

## Why

People need nudges that aren't tasks. "Check on the proposal Tuesday." "Flag if no client response in 3 days." These are triggers, not items to complete. Reminders/ gives them a home separate from todo/.

## How

Reminders are time-based or condition-based prompts. This folder stores them directly or points to the external system that manages them.

### Store-or-point

- **Stored:** A markdown file with natural-language reminder rules.
- **Pointer:** "Reminders live in Apple Reminders / Google Calendar."

### Boundaries

- Reminders are *nudges*. Things with a completion state go in todo/. Fleeting thoughts go in inbox/. Recurring maintenance goes in librarians/.

## What an agent should do

1. Read reminders/ to know what to surface and when.
2. When creating reminders, use clear natural-language triggers with dates or conditions.
3. A reminder may lead to creating a task, but the reminder itself is the trigger.
