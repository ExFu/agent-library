# Actors

Who this library acts as, and every other name each actor goes by. The dispatcher fires only the triggers whose `owner` resolves to this library's actor (or is `any`), and it honours an automatic dm only when the channel's target resolves to that same actor. Anything written here is a name that resolves; the first record is the library's own actor. Written at install or on first use of the docket; corrected only by appending, never by rewriting.

```markdown
## <handle>
- display: <full name as it appears in conversation>
- aliases: <first name, nickname, initials; comma-separated>
- slack: <Slack member id, e.g. U0123456789>
- email: <address>
- recorded: <ISO date> by <actor> (<surface>), plugin <version>
- notes: <anything a later reader should know>
```

- The heading is the **canonical handle**: short, lower-case, the value `owner` fields should carry. Every `- key: value` line beneath it except `recorded` and `notes` is a name that resolves to the handle. `aliases` is a comma list; every other key (`display`, `slack`, `email`, or any medium you add) is one name taken whole.
- An agent that writes `owner` should write the handle. When one writes a display name or an alias instead, the tools resolve it here, so nothing goes silent; the `explain` command shows the resolution.
- A name that resolves to no record is flagged by the due view as unfireable. Add the alias here rather than editing the trigger.
- To add an alias later, append a new record under the same handle heading with the new lines and a fresh `recorded:`; readers union every record with that handle.
