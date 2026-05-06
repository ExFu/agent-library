# PII Layer Guidance

version: 1

This document explains when to use the PII layer, what the connector contract looks like, and what wrapping plugins need to provide. It is written for substrate champions, skill authors, and wrapping-plugin implementers. An installing Claude helping a user think through PII handling can also use it.

---

## Why the PII layer exists

The substrate is designed to be shared: versioned in git, replicated across team members' machines, auditable over time. That's a good design for skills, templates, and context docs. It is the wrong design for anything containing identifiable PII.

PII in a versioned shared substrate is durable. It appears in git history long after a file is deleted. It gets replicated to every team member who pulls the repo. It can escape through a misconfigured remote or a careless export. The threat model is wrong.

PII at runtime is unavoidable. Claude has to read emails to help draft replies. Claude has to see a customer's name and history to write a follow-up. That's fine. The constraint is on what gets *stored*, not what Claude *sees*. The substrate's job is persistence; the boundary is at the point of writing to disk.

The PII layer is where PII lives when it needs to be persisted. It is an access-controlled store, separate from the substrate proper, accessed through a guarded connector. Skills in Layer 1 talk to Layer 2 through that connector at runtime. Nothing PII-bearing is written into the substrate itself.

---

## What counts as PII for this purpose

Treat these as PII that belongs in the layer rather than the substrate:

- Customer and contact identifiers: names, email addresses, phone numbers, postal addresses.
- Financial details: account numbers, transaction records, credit details.
- Health and medical information.
- Personal communications: emails, messages, call notes containing third-party content.
- Any category an org's privacy policy treats as personal data.

These are not PII for this purpose:

- The user's own self-disclosed information (their name, role, preferences, working style). This belongs in the substrate's `context/` folder.
- Anonymised or aggregated records where the individual cannot be identified.
- Sanitised test fixtures (real PII removed or replaced with synthetic values).

The practical test: would it matter to the individual if this appeared in a data breach or a git repository leak? If yes, it belongs in the PII layer.

---

## The two-layer contract

**Layer 1 (substrate proper)** holds shareable knowledge: skills, templates, context docs, structured non-PII data, configuration. Versioned, auditable, synced across the team. See `substrate-guide.md` for the full directory structure and conventions.

**Layer 2 (PII layer)** holds anything that includes identifiable PII. Skills in Layer 1 reach Layer 2 only through a connector. The connector is the single point of access, and it enforces the access model.

### Connector contract shape

ExFu does not prescribe the connector's implementation. The wrapping plugin (or the installing Claude, where no wrapper exists) owns the schema, the database, and the access-control logic. What ExFu does prescribe is the shape of the interface:

**Every query is parameterised by identity.** The connector must accept at minimum a `user_id` (the rep making the request) and a `subject_id` (the individual whose data is being accessed). No query operates without both.

**No general SELECT.** The connector does not expose a way to retrieve all records or enumerate subjects. Every query is scoped to a specific subject.

**No admin verbs from the rep-side connector.** Create, update, and delete operations are restricted. The connector exposed to reps is read-heavy. Write operations go through a separate admin path, not through the same endpoint skills use.

**Connector defines its own schema.** The substrate does not need to know the shape of the PII store. Skills pass named parameters; the connector maps those to whatever fields and tables exist. The substrate is decoupled from the data model.

**Every read and write is logged.** The connector appends an audit entry for every operation: who requested, whose data, what operation, when. This log is the connector's responsibility, not the skill's.

**Graceful failure is required.** If the connector is unavailable, the skill must refuse cleanly with a plain explanation. It must not fall back to writing PII into the substrate as a workaround. The failure mode is: tell the user the operation cannot be completed right now, and stop.

---

## Good patterns for wrapping plugin connectors

These are access-control patterns the connector should implement. They are not required by ExFu, but they represent sensible defaults for most org contexts.

**Per-user rate limits.** Limit how many subjects a given user can query in a time window. This prevents bulk exfiltration even by authenticated users. A rep querying 200 customer records in an hour is worth noticing.

**Logged justification for sensitive reads.** For categories of data the org treats as particularly sensitive, require the user to supply a brief reason before the connector returns the data. Log the reason alongside the read. This creates a human-readable audit trail.

**Field-level redaction.** Where full values are not needed, return partial values. Return the last four digits of an account number rather than the full number. Apply this by default for high-sensitivity fields and let the org's admin configure exceptions.

**Per-subject access scoping.** A rep should only be able to query subjects assigned to them. The connector checks the assignment, not just the authentication.

**Read/write asymmetry.** Writing PII is rarer than reading it, and higher-risk. Treat writes as a separate operation class: require confirmation before committing, log with additional detail, apply a stricter rate limit.

---

## Bad patterns to avoid

**Caching PII reads in substrate files.** A skill that reads from the connector and writes the result to a file in the substrate defeats the entire boundary. The data is now in git history. This is not a minor implementation detail; it is the primary failure mode the PII layer exists to prevent.

**Persisting PII in `scratch/` or equivalent areas.** Scratch is ephemeral but it is still inside the substrate. It gets synced. It appears in git history. PII does not go there regardless of how temporary the intent is.

**Connectors that return whole records when only one field was needed.** A skill that needs a customer's email address should not receive the customer's full profile including financial history. The connector should return what was asked for and nothing else.

**Admin endpoints reachable from rep contexts.** The connector used by rep-facing skills and the connector (or path) used for admin operations should be separated. A rep's authenticated session must not grant access to admin functions.

**Direct database connections from skills.** Skills must go through the connector. No direct connection strings, no raw queries from skill logic. The connector is the only path.

---

## What is ExFu's job and what is the wrapper's job

**ExFu ships:**

- This guidance document.
- The principle: PII is never persisted in the shareable substrate.
- The contract shape described above.
- The substrate skill's PII boundary enforcement: the skill will refuse to write PII into substrate files and will tell the user why.
- General framing in the substrate guide and the substrate primer.

**The wrapping plugin (or the installing Claude) ships:**

- The actual MCP connector and its implementation.
- The database schema and choice of store.
- The access-control logic: authentication, per-subject scoping, rate limits.
- The audit log destination and retention policy.
- Any vertical-specific compliance additions (HIPAA field handling, FCA data-residency requirements, etc.).
- The justification prompts and UI for sensitive reads, if implemented.

This distinction is part of ExFu's broader extension pattern: ExFu defines the contract and enforces the boundary; the wrapping plugin (or installing Claude) resolves the implementation details for the specific org context.

---

## For solo users

Solo installs typically have no PII layer. The substrate is a personal Box or local filesystem, not a shared git repository. The threat model is different, and the operational overhead of running a connector and access-controlled database is disproportionate for a single user.

If a solo user starts working with material that includes third-party PII (a freelance consultant with client data, for example), they are moving into territory where a PII layer may be appropriate. At that point the right question is: is there a small connector worth setting up for this situation?

The substrate skill will still refuse to persist PII regardless of whether a connector is present. If the user is solo and has no connector, the skill will explain that it cannot store this material in the substrate and suggest they consider whether a connector is the right next step.

---

## Skill author checklist

When writing a skill that might touch PII, work through these before finishing:

- Does this skill need to read PII? If yes: does it route through the connector? Does it pass `user_id` and `subject_id` correctly? Does it handle connector-unavailable gracefully?
- Does this skill need to write PII? If yes: it should almost certainly not be writing PII directly. Route through the connector with full audit trail. If there is no connector, the skill must refuse and explain.
- Does this skill cache or log anything to substrate files? If yes: confirm that no PII from connector responses ends up in those files. Strip or exclude PII fields before any write to Layer 1.
- Does this skill have a graceful failure path? If the connector is unavailable or returns an error, the skill must not silently proceed with degraded behaviour. It must tell the user it cannot complete the operation and why.

---

## Changelog

- 2026-05-02 v1: Initial version. Covers the two-layer model, what counts as PII, the connector contract shape, good and bad patterns, ExFu vs wrapper responsibilities, solo user guidance, and skill author checklist.
