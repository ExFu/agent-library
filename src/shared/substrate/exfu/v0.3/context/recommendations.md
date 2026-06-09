# Curated recommendations

Suggestions for tools, practices, and integrations that work well with the ExFu substrate. These are opinions, not requirements. Your setup may differ.

## Calendar connector

If your work involves scheduling, connect a calendar MCP server. Agents can check availability, create events, and reference meeting context without you copying dates around. Google Calendar and Outlook both have MCP connectors.

## Task management pointer

Rather than storing tasks as files in todo/, point to a dedicated task tool (ClickUp, Linear, Todoist, Asana). The tool gives you views, filters, and notifications that flat files can't. The todo/agent.md pointer pattern makes this seamless for agents.

## Voice-to-text for context

Dictating context is faster than writing it. Tools like Whisper, Otter, or your phone's built-in transcription can capture thoughts that you then drop into inbox/ for triage. Don't worry about formatting; the inbox librarian sweeps periodically.

## Version control for team substrates

If multiple people share a substrate (team plugin), use git. It gives you history, conflict resolution, and the ability to branch for experiments. The team plugin is designed around git as the storage backend.
