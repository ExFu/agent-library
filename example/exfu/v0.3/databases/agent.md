# Databases

## Why

Some data has repeating structure -- contacts, CRM records, inventory, project logs. This isn't a narrative (context/) or a document (docs/); it's rows and columns. Databases/ is where structured, queryable data lives.

## How

Each database is a subfolder or file with a defined schema. Agents reading this folder know the data is structured and can query, filter, and update it.

### Store-or-point

- **Stored:** Structured files (CSV, JSON, YAML, or markdown tables) with a schema definition.
- **Pointer:** "Contact records live in HubSpot. Use the HubSpot MCP connector. Schema: name, company, role, last-contact-date."

### Boundaries

- Databases hold *structured, repeating records*. One-off documents go in docs/. Unstructured thoughts go in inbox/. Background narratives go in context/.
- The schema matters. If data doesn't have consistent fields, it's probably context/ or docs/.

## What an agent should do

1. Understand the schema before reading or writing records.
2. When the folder is a pointer, use the described connector and respect the stated schema.
3. When creating new databases, define the schema explicitly in a header or companion file.
