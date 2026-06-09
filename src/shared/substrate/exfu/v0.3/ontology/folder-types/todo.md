# Folder type: todo/

How this scope handles tasks. Things with a completion state that need doing.

**Analogy:** a task list.

## Default behaviour

Agents check todo/ to understand how tasks work for this scope. If tasks are stored locally, agents read and update them here. If tasks live in an external system, agents use the connector described in agent.md.

## Store-or-point

- **Stored:** Task files in markdown (one per task, or a task list file). Each task has at minimum a description and a completion state.
- **Pointer:** "Tasks are in ClickUp. Use the ClickUp MCP connector. Tag all tasks with the scope name."

The pointer pattern is common for todo/ -- most users already have a task management system. The value of the folder is that an agent always knows *where to ask* about tasks for this scope.

## Boundaries

- Todos have a *completion state* (done or not done). Lightweight time-based nudges go in reminders/. Fleeting thoughts go in inbox/.
- Todo/ describes how this scope handles tasks, not every task ever. If it's a pointer, the folder is just the routing instructions.
