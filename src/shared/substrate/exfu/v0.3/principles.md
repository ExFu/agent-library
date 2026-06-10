# ExFu principles and recommendations

The design principles behind the ExFu substrate, plus curated recommendations for tools and practices that work well with it. Principles guide how conventions are written and how agents approach their work; recommendations are opinions, not requirements.

## Principles

### Golden Circle

Start with Why, then How, then What. This applies to everything: agent.md files, planning docs, scope descriptions, skill definitions. If you can't articulate why something exists, it probably shouldn't.

### Concrete-first

Show a working example before explaining the abstract pattern. People (and agents) learn faster from concrete instances than from theory. The example prototype exists for this reason.

### File economy

Fewer, more complete files. Agents ingest one complete read far more reliably than a folder of fragments; every extra file is a read a future agent might skip. Prefer extending an existing file over creating a sibling, one complete file over a sharded concept, and flat layouts over nested ones. Create structure only when volume genuinely demands it. (The authoring rules in `ontology.md` make this concrete.)

### Outcome-framed elicitation

When asking users for information, frame questions around outcomes they care about, not structural details. "What are you trying to accomplish with this project?" beats "What folder-types do you need?"

### Build by doing

The substrate grows through use, not through upfront planning. A new scope starts minimal (scope.md, maybe context/ and todo/) and gains structure as work demands it. Don't scaffold more than you need -- folder-types materialise when there's content for them, never "for completeness".

### Accept chaos, annotate intent

Real knowledge doesn't fit neatly into categories. Rather than forcing everything into the "right" place, accept that things will be messy and focus on annotating intent. An agent that knows WHY something was put somewhere can work with imperfect placement. An agent that only knows WHERE something is can't.

## Recommendations

### Calendar connector

If your work involves scheduling, connect a calendar MCP server. Agents can check availability, create events, and reference meeting context without you copying dates around. Google Calendar and Outlook both have MCP connectors.

### Task management pointer

Rather than storing tasks as files in todo/, point to a dedicated task tool (ClickUp, Linear, Todoist, Asana). The tool gives you views, filters, and notifications that flat files can't. The todo/agent.md pointer pattern makes this seamless for agents.

### Voice-to-text for context

Dictating context is faster than writing it. Tools like Whisper, Otter, or your phone's built-in transcription can capture thoughts that you then drop into inbox/ for triage. Don't worry about formatting; the inbox-triage librarian sweeps periodically.

### Version control for team substrates

If multiple people share a substrate (team plugin), use git. It gives you history, conflict resolution, and the ability to branch for experiments. The team plugin is designed around git as the storage backend.
