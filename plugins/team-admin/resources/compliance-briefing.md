# Compliance Briefing: ExFu Team Substrate

*Written for the substrate champion to share with their IT or security team. Covers data flow, controls, and how this deployment maps to common compliance requirements.*

---

## What this document is

This briefing describes the data handling, security controls, and compliance posture of a team Claude substrate deployed using the ExFu team-admin plugin. It is intended to give an IT or security reviewer enough information to assess the deployment and identify any additional controls their organisation needs.

This document covers what ExFu configures and controls. It does not cover Anthropic's data handling for Claude itself — that is governed by Anthropic's own terms of service and privacy documentation, available at https://docs.anthropic.com and https://support.claude.com. Reviewers should read both.

---

## 1. Data flow overview

**What data the substrate holds.** The team substrate is a collection of plain-text files (primarily markdown). Contents typically include: team conventions and ways of working, shared context about the team and its work, shared skills (instructions for Claude), and personal substrates for each team member (context about them, their active work areas, their preferences). The substrate does not hold production data, customer records, or system credentials. See the hygiene rules section below for what must not be in the substrate.

**Where it lives.** The substrate lives wherever the substrate champion chose during install. Three options:

- **Git repository.** The repo lives wherever the organisation chooses to host it: self-hosted on internal infrastructure, or a hosted git provider (GitHub, GitLab, Bitbucket, or a private instance). The choice of git remote is entirely within the organisation's control. ExFu does not operate or have access to the repository.
- **Dropbox shared folder(s).** The substrate lives in one or more Dropbox folders the champion created and shared with team members. Dropbox is the org's own Dropbox account; ExFu does not operate or have access to it. Team substrates in Dropbox typically span multiple folders (one per org, one per team, one per scope) because different scopes have different sharing groups.
- **Local-only / custom.** Each team member's substrate lives on their own machine. There is no shared central store via ExFu. Any propagation mechanism the team uses is outside ExFu's scope and control.

**How it reaches team members.** Delivery depends on the chosen backend:

- Git: each team member's Claude instance pulls from the git repository via the `git-substrate-sync` skill. Sync happens on demand and writes to the local filesystem.
- Dropbox: each team member accesses their shared folders via the Dropbox client synced locally, or via the Dropbox MCP connector. Files live in Dropbox and are read by Claude on demand.
- Local-only: no automatic propagation. Each member's Claude reads from their own local folder.

In all cases, there is no ExFu-controlled relay or intermediary.

**What ExFu receives.** Nothing. Once the plugin is installed, all operations happen locally and between the user's Claude instance and their chosen storage backend. ExFu does not receive telemetry, substrate contents, or any other data from installed plugins. The plugin is a bundle of files, not a connected service.

**What Anthropic receives.** Anthropic processes the contents of Claude conversations in accordance with their standard terms. When Claude reads substrate files as part of a conversation, those file contents are part of the conversation context that Anthropic processes. Teams with strict data handling requirements should review Anthropic's enterprise data handling terms and consider whether a Claude enterprise agreement with appropriate data processing commitments is appropriate.

---

## 2. Recommended controls

**Storage access control.** Access controls depend on the chosen backend:

- *Git:* use your standard git access management. At minimum: the substrate champion has write access; team members have read access; the repository is private. Use your organisation's existing git hosting access policies (SSH keys, SSO, short-lived tokens). Review access when team members leave.
- *Dropbox:* access is managed via Dropbox folder sharing. Each folder can have different sharing groups. The champion controls who is invited to each folder and at what permission level (can view, can edit; the champion owns the folder). Remove team members from all shared folders when they leave. Because sharing is per-folder, access reviews require checking each folder independently.
- *Local-only:* no central access control. Each member's substrate is on their own machine. Machine-level controls (login, disk encryption) are the relevant layer.

**Encryption at rest.** The substrate files live on each team member's local disk, regardless of storage backend. Disk encryption (FileVault on macOS, BitLocker on Windows) is strongly recommended and is required by many ISO 27001 implementations. This is the team member's machine configuration, not the substrate's — but the substrate champion should confirm it is in place for everyone who handles sensitive substrate content.

**Encryption in transit.**

- *Git:* uses HTTPS or SSH — both encrypted in transit.
- *Dropbox:* uses HTTPS for all file operations — encrypted in transit.
- *Local-only:* no transit (files stay on the local machine). If the team uses a custom sync mechanism (e.g. Syncthing), ensure that mechanism is configured for encrypted transit.

**Access review cadence.** When someone leaves the team:

- *Git:* remove their access to the substrate repository and remove their personal substrate folder from the shared layer. Git history will retain a record; the live repository should not retain access for former members.
- *Dropbox:* remove them from all shared folders. Check each folder in the team's access map.
- *Local-only:* no central access to revoke. Confirm the former member no longer uses a copy of any shared content the team has distributed manually.

**Claude enterprise agreement.** For teams with formal compliance requirements (ISO 27001, SOC 2, sector regulators), consider whether Anthropic's enterprise agreement with data processing addendum is appropriate. The ExFu substrate is local-first, but Claude conversations still flow through Anthropic's infrastructure.

---

## 3. ISO 27001 control mappings

The following is a best-effort mapping of this deployment to relevant ISO 27001:2022 controls. It is not a formal Statement of Applicability and should not be used as one without review by a qualified assessor.

Some rows note where the applicable control differs by storage backend.

| Control | ISO 27001 clause | How this deployment addresses it |
|---|---|---|
| Access control | A.5.15 | *Git:* repository access managed via org's standard git hosting policies. *Dropbox:* per-folder sharing managed by the champion; each folder's sharing group should match its intended audience. *Local-only:* machine-level access controls only. Personal substrates are not accessible to other team members in any backend. |
| Information classification | A.5.12 | Hygiene rules (below) define what must not enter the substrate. No formal classification scheme is built in; organisations with classification requirements should document this separately. |
| Cryptography | A.8.24 | *Git:* transport encrypted via HTTPS/SSH. *Dropbox:* transport encrypted via HTTPS. *Local-only:* no transport; custom sync mechanisms should use encrypted transit. At-rest encryption depends on local disk encryption (recommended) across all backends. |
| Physical and environmental security | A.7.8 | Out of scope for this deployment — substrate files live on team members' existing workstations. |
| Supplier relationships | A.5.19–A.5.22 | Anthropic is the primary supplier. Review Anthropic's security documentation and DPA. *Git:* git hosting provider (if external) is a secondary supplier. *Dropbox:* Dropbox is a secondary supplier; your organisation's Dropbox relationship and DPA applies. |
| Information security in project management | A.5.8 | Substrate champion role provides a defined owner for the shared substrate. Role should be documented in the organisation's security roles register. |
| Secure development | A.8.25–A.8.31 | Skills are plain-text instruction files. No compiled code or executed binaries in the standard substrate. Custom skills should be reviewed before deployment to the shared layer. |
| Logging and monitoring | A.8.15–A.8.16 | *Git:* git history provides an audit trail for all changes to shared substrate content (author, timestamp, content diff). *Dropbox:* Dropbox's activity log records who added, edited, moved, or deleted files, but does not retain content diffs. *Local-only:* no central audit log. See audit trail section below. |
| Backup | A.8.13 | *Git:* git hosting provider's backup policies apply to the remote. *Dropbox:* Dropbox's version retention and your org's Dropbox backup policy. *Local-only:* relies on individual machines being backed up. See backup section below. |
| Vulnerability management | A.8.8 | Claude model updates are managed by Anthropic. Plugin updates are versioned and distributed by ExFu. No network-facing services are deployed by this installation. |

---

## 4. Disk encryption recommendation

All team members accessing the substrate should have disk encryption enabled on their workstations. Substrate files are stored locally and may contain sensitive standing context. Disk encryption is the primary control protecting this data at rest.

macOS: Enable FileVault via System Settings > Privacy and Security > FileVault.
Windows: Enable BitLocker via Control Panel > System and Security > BitLocker Drive Encryption.

This should be a prerequisite confirmed before onboarding a team member to the substrate, not an afterthought.

---

## 5. Hygiene rules

These are standing rules for what must not be placed in the substrate — personal or shared, regardless of storage backend. The substrate is routinely accessed storage and a frequently-read AI context. These categories do not belong there:

**No credentials.** API keys, passwords, access tokens, SSH private keys, OAuth secrets. Use a password manager or secrets vault. If an operation requires a credential, pass it in at the moment of use — do not store it in the substrate.

**No personally identifiable information about third parties without consent.** Names and general context about colleagues and clients that appear in normal work notes are fine. Full personal data records (home addresses, phone numbers, national ID numbers, financial details) are not.

**No regulated content.** This includes: government identifiers (SSNs, passport numbers, national insurance numbers), full payment card numbers, bank account numbers, raw health and medical records, and any data subject to sector-specific regulation (HIPAA, FCA-regulated data, etc.).

**No confidential data beyond team scope.** If a piece of information is marked confidential and its audience is smaller than the team, it should not be in the shared substrate. The shared substrate is visible to all team members with access.

The test: would it matter if this file appeared in a data breach or an accidental exposure? If yes, it should not be in the substrate.

---

## 6. Audit trail

The audit trail available to the team depends on which storage backend they chose.

**Git.** Git history provides a full audit trail for all changes to shared substrate content. Every commit records who made a change, when, and what changed (content diff). This log is append-only (without force-push access, which should be restricted). The substrate champion should retain git history in accordance with the organisation's data retention policy. Git is the recommended backend for environments where a content-change audit trail is a compliance requirement.

**Dropbox.** Dropbox tracks activity events: who added, edited, moved, or deleted a file, and it keeps per-file version history (retention depends on the plan). It does not retain a native content diff history over time (versions, but not a structured record of what changed between them). This means the audit trail is activity-level, not content-change-level. If IT or security ask about audit trail specifics, make this distinction clear. Dropbox is acceptable for environments where activity logging is sufficient and a content-diff trail is not required.

**Local-only.** There is no central audit log. Each team member's substrate changes are local to their machine. Teams that choose local-only are responsible for any logging or audit requirements their own mechanism provides. If audit trail is a compliance requirement, local-only is not an appropriate backend.

**Personal substrate content (all backends).** Personal substrate changes are local to each team member's machine regardless of backend. There is no centralised audit log for personal substrate content. Teams that require audit logging of all AI-context changes should note this gap and decide whether their requirements extend to personal substrates.

---

## 7. Backup

**Shared substrate — by backend:**

- *Git remote:* backed up according to the git hosting provider's policies. For self-hosted git, ensure the repository is included in the organisation's standard infrastructure backup. Verify recovery procedures.
- *Dropbox shared folders:* backed up according to Dropbox's version retention and your organisation's Dropbox backup policy. Confirm with your IT team what version retention is configured for your org's Dropbox account.
- *Local-only:* each team member's substrate files should be covered by the organisation's standard endpoint backup. The substrate champion should confirm this during onboarding and periodically. There is no central backup; each member is responsible for their own machine.

**Personal substrates (local, all backends).** Each team member's local personal substrate files should be covered by the organisation's standard endpoint backup. The substrate champion should confirm this during onboarding.

**Plugin files.** The ExFu plugin itself is re-downloadable from exfu.ai. It does not need to be separately backed up, though retaining the installed version is good practice for rollback purposes.

---

## 8. What this is, what it isn't

**This is** a set of plain-text files, skills (instruction documents), and scheduled tasks deployed within Claude Cowork. It uses Claude's standard plugin mechanism and a team-chosen storage backend (git, Dropbox, or local-only) for shared distribution. It is local-first and does not connect to any ExFu-controlled infrastructure after install.

**This is not** an Anthropic product. ExFu is an independent service that builds on Anthropic's publicly available infrastructure. Anthropic does not endorse, certify, or support ExFu specifically.

**This does not** grant the team any Claude capabilities they don't already have through their Anthropic account. The substrate improves how Claude is configured and what context it has; it does not change what the underlying model can do or bypass any Anthropic policies.

**This does not** include any data processing services operated by ExFu. There is no ExFu server, no ExFu telemetry, no ExFu-controlled data store. The substrate champion's responsibility is to manage the team's chosen storage backend and the shared content in it. ExFu's responsibility ends at delivering the plugin.

---

## Questions

For questions about this deployment or its compliance posture, contact the substrate champion first — they are the operational owner of the team's substrate. For questions about Claude's data handling and Anthropic's compliance certifications, contact Anthropic directly via https://support.anthropic.com. For questions about ExFu specifically, contact al@exfu.ai.
