# Folder type: databases/

Structured data with schemas for this scope. Where records live when they need consistent fields and queryable structure.

**Analogy:** structured records / a spreadsheet.

## Default behaviour

Databases hold data that has a repeating structure: contacts, CRM records, inventory, project logs. Each database is a subfolder or file with a defined schema. Agents reading databases/ know the data is structured and can query, filter, and update it.

## Store-or-point

- **Stored:** Structured files (CSV, JSON, YAML, or markdown tables) with a schema definition.
- **Pointer:** "Contact records live in HubSpot. Use the HubSpot MCP connector. Schema: name, company, role, last-contact-date."

## Boundaries

- Databases hold *structured, repeating records*. One-off documents go in docs/. Unstructured thoughts go in inbox/. Background narratives go in context/.
- The schema matters. If data doesn't have a repeating structure with consistent fields, it's probably context/ or docs/, not databases/.
