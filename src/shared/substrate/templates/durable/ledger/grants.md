# Grants

Consent you gave for a channel to send on your behalf without asking first. Written once per decision; corrected only by appending a later entry, never by rewriting.

```markdown
## <channel id> (<channel name>, <scope>)
- granted: <ISO date>
- by: <actor> (<surface>), plugin <version>
- send: auto
- notes: <what the user said, in their words>

## <channel id> (<channel name>, <scope>)
- revoked: <ISO date>
- by: <actor> (<surface>), plugin <version>
- notes: <why>
```

A channel is `auto` only while its latest entry here is a grant. The dispatcher checks this file before every automatic send; the `send:` flag on the channel itself grants nothing.
