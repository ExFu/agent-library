# Folder type: reminders/

How this scope handles lightweight nudges. Time-based or condition-based prompts that don't have a completion state.

**Analogy:** a notification list.

## Default behaviour

Reminders are triggers, not tasks. "Remind me to check on the proposal next Tuesday." "Flag if no response from client within 3 days." Agents read reminders/ to know what to surface and when.

## Store-or-point

- **Stored:** A markdown file with natural-language reminder rules. One file works for most scopes.
- **Pointer:** "Reminders live in Apple Reminders / Google Calendar / Todoist. This folder describes the conventions for how reminders are phrased."

## Boundaries

- Reminders are *nudges*. Things with a completion state go in todo/. Fleeting thoughts go in inbox/. Recurring maintenance goes in librarians/.
- A reminder may trigger a todo ("remind me to follow up" might create a task), but the reminder itself is the trigger, not the task.
