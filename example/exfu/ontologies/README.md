# exfu/ontologies/

## Purpose

Definitions of the folder *types* the substrate recognises. Each type defines a folder shape, a convention for its contents, and (for user-facing types) the prompt the install agent uses to offer it.

## Contents

- `todos/` — capture and surface todos. User-facing; offered during install with an elicitation prompt.

(A real install would carry more: contacts, sops, instructions, databases, librarians, conventions, ontologies itself (meta-recursive), principles, recommendations, skills, templates. This example shows one illustrative type.)

## Shape of an ontology type definition

Each `<type>/` subfolder contains:

- `agent.md` — the **template** convention for folders of this type. Copied into new folders of this type at creation time as the per-folder snapshot.
- `schema.yaml` — the structural shape (what files/subfolders a folder of this type must or may contain).
- `elicitation.md` — (user-facing types only) the outcome-framed question the install agent reaches for when offering this type.

## Dependencies

- Read by the install agent at install time (for elicitation) and at folder-creation time (for the agent.md template).
- Read by librarians at runtime (to check folder conformance).
- Self-references: the `ontologies/` type is itself an ontology type (meta-recursive). Users and scopes can extend the ontology via their own `ontologies/<type>/` folders.

## User-facing vs infrastructure types

Some types are offered to the user during install (todos, contacts, sops, databases). Some are materialised silently and not offered (librarians, conventions, ontologies, schemas, principles). The split is recorded in each type's schema. The install agent only surfaces user-facing types in conversation.

## Why types are ontology-shaped, not just named folders

Naming convention alone (any folder called `todos/` is a todos folder) is the discoverability mechanism. The ontology adds *what makes a folder valid as that type*: a schema, a convention snapshot, an outcome the install agent can offer. This lets the substrate be both flexible (users can create folders of any type wherever they want) and disciplined (the agent knows what to expect).
