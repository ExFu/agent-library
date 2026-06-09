# Todo

## Why

Every scope has tasks. Without a conventional location, agents don't know where to look for them or where to put new ones. Todo/ is the answer to "how does this scope handle tasks?"

## How

This folder either stores tasks directly or points to the external system where they live. The convention guarantees the location is discoverable -- the agent always knows where to ask about tasks.

### Store-or-point

- **Stored:** Task files in markdown. Each task has a description and completion state.
- **Pointer:** "Tasks are in ClickUp / Jira / Linear. Use the [connector] to read/write. Tag tasks with the scope name."

The pointer pattern is common -- most users already have a task system.

### Boundaries

- Todos have a *completion state*. Time-based nudges go in reminders/. Fleeting thoughts go in inbox/.

## What an agent should do

1. Check todo/ to understand how tasks work for this scope.
2. If it's a pointer, use the described connector.
3. If storing locally, maintain a clear completion state per task.
