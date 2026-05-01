# Cross-cut: Compliance and data residency

## Why

The team plugin is heading into corporate environments. Many of those will operate under ISO 27001, SOC 2, or sector-specific frameworks (HIPAA, FCA, etc.). Even where formal compliance isn't required, the org's IT and security teams will want to know what data goes where and what can be controlled. If the plugin doesn't have clear answers, it gets blocked at the IT review stage and never reaches the user.

This is also a *trust* consideration in the broader sense. Users are going to put thinking, decisions, and personal context into their substrate. The clearer we are about where it lives, who can see it, and what controls exist, the more confidently they engage.

## How

### Default posture

- **Data lives where the user puts it.** The plugin doesn't phone home or transmit anything to ExFu. Once installed, the plugin is local. Skills and scheduled tasks operate on the user's files, on the user's machine, with the user's API key and Claude's standard data handling.
- **Anthropic's data handling policies apply** wherever Claude is reading or writing. The plugin doesn't change that.
- **Local-first, where viable.** Both plugins are designed to work without sending substrate content to ExFu-controlled infrastructure.

### Solo

Solo users: data lives in their cloud drive (Box for now), on their machine, and is accessed by Claude via Anthropic's standard infrastructure. Standard consumer-grade security applies. Compliance considerations are usually personal: what *they* care about putting in cloud storage.

The substrate-guide already calls out the hygiene rules — no credentials, no government IDs, no raw medical records — and that guidance carries forward into the plugin.

### Team

Team users: data lives on each member's machine, propagated via git. The git remote (GitHub, GitLab, Bitbucket, on-prem) is the central artefact. Compliance posture depends on:

- **Where the git remote lives.** Self-hosted on the org's infrastructure → strongest compliance posture. Hosted by a major provider with appropriate data-residency commitments → next best. Public hosting → least controlled.
- **What's in the substrate.** Team conventions, shared standing context, scope notes, decision logs. Sensitive material (customer PII, financial details, regulated content) should never be there; the team's substrate-champion role includes enforcing this.
- **Local disk encryption.** Recommended (often required) for ISO 27001. The plugin's setup guidance should surface this.

### ISO 27001 specifically

A typical ISO 27001 conversation will want answers to:
- What data is processed and where?
- Who has access?
- How is access controlled?
- How is data deleted when no longer needed?
- What's the audit trail?
- What's the incident response plan?

The plugin doesn't answer these on the org's behalf, but it should give the team-champion enough material that they can answer them with the org's IT/security team. A short "compliance briefing" doc shipped in the plugin's `guides` is probably the right artefact.

### Beyond ISO 27001

Other frameworks may apply (SOC 2, HIPAA, GDPR, sector regulators). v1 doesn't need to address all of them, but the structure should accommodate adding compliance briefings per framework as they come up.

## What (initial)

- Compliance briefing doc shipped in team plugin's `guides` content. Covers data flow, controls, recommended team practices.
- Substrate-hygiene rules (no credentials, no IDs, no raw medical) carried into both plugins via existing substrate guide.
- Disk-encryption recommendation in team-plugin install conversation.
- Research task to confirm specifics of ISO 27001 requirements that affect us.

## Open questions

- What's the standard ISO 27001 SOA (Statement of Applicability) language we should provide for team-plugin deployments? Worth researching once a real client conversation drives it.
- Does the team plugin need to support BYO-encryption-key for the substrate filesystem? Probably out of scope for v1; flag for future.
- GDPR: substrate may contain personal data about the user themselves (about-me, role) and possibly about their colleagues (in shared scopes). Worth a small note about user-controlled retention and deletion.
- Audit trail: git history is one. Is that enough? For most teams yes; for highly regulated ones, no. Flag.
