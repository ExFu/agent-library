# Compliance Briefing: ExFu Team Substrate

*Written for the substrate champion to share with their IT or security team. Covers data flow, controls, and how this deployment maps to common compliance requirements.*

---

## What this document is

This briefing describes the data handling, security controls, and compliance posture of a team Claude substrate deployed using the ExFu team-admin plugin. It is intended to give an IT or security reviewer enough information to assess the deployment and identify any additional controls their organisation needs.

This document covers what ExFu configures and controls. It does not cover Anthropic's data handling for Claude itself — that is governed by Anthropic's own terms of service and privacy documentation, available at https://docs.anthropic.com and https://support.claude.com. Reviewers should read both.

---

## 1. Data flow overview

**What data the substrate holds.** The team substrate is a collection of plain-text files (primarily markdown) stored in a git repository. Contents typically include: team conventions and ways of working, shared context about the team and its work, shared skills (instructions for Claude), and personal substrates for each team member (context about them, their active work areas, their preferences). The substrate does not hold production data, customer records, or system credentials. See the hygiene rules section below for what must not be in the substrate.

**Where it lives.** The git repository lives wherever the organisation chooses to host it: self-hosted on internal infrastructure, on a hosted git provider (GitHub, GitLab, Bitbucket), or a private instance. The choice of git remote is entirely within the organisation's control. ExFu does not operate or have access to the repository.

**How it reaches team members.** Each team member's Claude instance pulls from the git repository via the `git-substrate-sync` skill. Sync happens on demand (at session start or when the user triggers it) and writes to the local filesystem. The substrate files live on each team member's local machine, inside their Claude substrate directory. There is no ExFu-controlled relay or intermediary.

**What ExFu receives.** Nothing. Once the plugin is installed, all operations happen locally and between the user's Claude instance and the git remote. ExFu does not receive telemetry, substrate contents, or any other data from installed plugins. The plugin is a bundle of files, not a connected service.

**What Anthropic receives.** Anthropic processes the contents of Claude conversations in accordance with their standard terms. When Claude reads substrate files as part of a conversation, those file contents are part of the conversation context that Anthropic processes. Teams with strict data handling requirements should review Anthropic's enterprise data handling terms and consider whether a Claude enterprise agreement with appropriate data processing commitments is appropriate.

---

## 2. Recommended controls

**Git repository access control.** The substrate repository should use your standard git access management. At minimum: the substrate champion has write access; team members have read access; the repository is private. Use your organisation's existing git hosting access policies (SSH keys, SSO, short-lived tokens). Review access when team members leave.

**Encryption at rest.** The substrate files live on each team member's local disk. Disk encryption (FileVault on macOS, BitLocker on Windows) is strongly recommended and is required by many ISO 27001 implementations. This is the team member's machine configuration, not the substrate's — but the substrate champion should confirm it is in place for everyone who handles sensitive substrate content.

**Encryption in transit.** Git operations use HTTPS or SSH — both encrypted in transit. No plaintext transport.

**Access review cadence.** When someone leaves the team, remove their access to the substrate repository and remove their personal substrate folder from the shared layer. Git history will retain a record; the live repository should not retain access for former members.

**Claude enterprise agreement.** For teams with formal compliance requirements (ISO 27001, SOC 2, sector regulators), consider whether Anthropic's enterprise agreement with data processing addendum is appropriate. The ExFu substrate is local-first, but Claude conversations still flow through Anthropic's infrastructure.

---

## 3. ISO 27001 control mappings

The following is a best-effort mapping of this deployment to relevant ISO 27001:2022 controls. It is not a formal Statement of Applicability and should not be used as one without review by a qualified assessor.

| Control | ISO 27001 clause | How this deployment addresses it |
|---|---|---|
| Access control | A.5.15 | Git repository access managed via org's standard git hosting policies. Personal substrates are not accessible to other team members. |
| Information classification | A.5.12 | Hygiene rules (below) define what must not enter the substrate. No formal classification scheme is built in; organisations with classification requirements should document this separately. |
| Cryptography | A.8.24 | Git transport is encrypted (HTTPS/SSH). At-rest encryption depends on local disk encryption (recommended). |
| Physical and environmental security | A.7.8 | Out of scope for this deployment — substrate files live on team members' existing workstations. |
| Supplier relationships | A.5.19–A.5.22 | Anthropic is the primary supplier. Review Anthropic's security documentation and DPA. Git hosting provider (if external) is a secondary supplier. |
| Information security in project management | A.5.8 | Substrate champion role provides a defined owner for the shared substrate. Role should be documented in the organisation's security roles register. |
| Secure development | A.8.25–A.8.31 | Skills are plain-text instruction files. No compiled code or executed binaries in the standard substrate. Custom skills should be reviewed before deployment to the shared layer. |
| Logging and monitoring | A.8.15–A.8.16 | Git history provides an audit trail for all changes to shared substrate content. |
| Backup | A.8.13 | Git hosting provider's backup policies apply to the remote. Local substrate files should be covered by the organisation's standard endpoint backup. |
| Vulnerability management | A.8.8 | Claude model updates are managed by Anthropic. Plugin updates are versioned and distributed by ExFu. No network-facing services are deployed by this installation. |

---

## 4. Disk encryption recommendation

All team members accessing the substrate should have disk encryption enabled on their workstations. Substrate files are stored locally and may contain sensitive standing context. Disk encryption is the primary control protecting this data at rest.

macOS: Enable FileVault via System Settings > Privacy and Security > FileVault.
Windows: Enable BitLocker via Control Panel > System and Security > BitLocker Drive Encryption.

This should be a prerequisite confirmed before onboarding a team member to the substrate, not an afterthought.

---

## 5. Hygiene rules

These are standing rules for what must not be placed in the substrate — personal or shared. The substrate is routinely accessed cloud storage and a frequently-read AI context. These categories do not belong there:

**No credentials.** API keys, passwords, access tokens, SSH private keys, OAuth secrets. Use a password manager or secrets vault. If an operation requires a credential, pass it in at the moment of use — do not store it in the substrate.

**No personally identifiable information about third parties without consent.** Names and general context about colleagues and clients that appear in normal work notes are fine. Full personal data records (home addresses, phone numbers, national ID numbers, financial details) are not.

**No regulated content.** This includes: government identifiers (SSNs, passport numbers, national insurance numbers), full payment card numbers, bank account numbers, raw health and medical records, and any data subject to sector-specific regulation (HIPAA, FCA-regulated data, etc.).

**No confidential data beyond team scope.** If a piece of information is marked confidential and its audience is smaller than the team, it should not be in the shared substrate. The shared substrate is visible to all team members with repository access.

The test: would it matter if this file appeared in a data breach or an accidental git push to a public repository? If yes, it should not be in the substrate.

---

## 6. Audit trail

Git history provides a full audit trail for all changes to shared substrate content. Every commit records who made a change, when, and what changed. This log is append-only (without force-push access, which should be restricted). The substrate champion should retain git history in accordance with the organisation's data retention policy.

For personal substrate content, changes are local to each team member's machine. There is no centralised audit log for personal substrate changes. Teams that require audit logging of all AI-context changes should note this gap and decide whether their requirements extend to personal substrates.

---

## 7. Backup

**Shared substrate (git remote).** Backed up according to the git hosting provider's policies. For self-hosted git, ensure the repository is included in the organisation's standard infrastructure backup. Verify recovery procedures.

**Personal substrates (local).** Each team member's local substrate files should be covered by the organisation's standard endpoint backup. The substrate champion should confirm this during onboarding. Personal substrate files are also effectively backed up in the git remote for the shared layer components; personal-only files are not.

**Plugin files.** The ExFu plugin itself is re-downloadable from exfu.ai. It does not need to be separately backed up, though retaining the installed version is good practice for rollback purposes.

---

## 8. What this is, what it isn't

**This is** a set of plain-text files, skills (instruction documents), and scheduled tasks deployed within Claude Cowork. It uses Claude's standard plugin mechanism and git for distribution. It is local-first and does not connect to any ExFu-controlled infrastructure after install.

**This is not** an Anthropic product. ExFu is an independent service that builds on Anthropic's publicly available infrastructure. Anthropic does not endorse, certify, or support ExFu specifically.

**This does not** grant the team any Claude capabilities they don't already have through their Anthropic account. The substrate improves how Claude is configured and what context it has; it does not change what the underlying model can do or bypass any Anthropic policies.

**This does not** include any data processing services operated by ExFu. There is no ExFu server, no ExFu telemetry, no ExFu-controlled data store. The substrate champion's responsibility is to manage the git repository and the shared content in it. ExFu's responsibility ends at delivering the plugin.

---

## Questions

For questions about this deployment or its compliance posture, contact the substrate champion first — they are the operational owner of the team's substrate. For questions about Claude's data handling and Anthropic's compliance certifications, contact Anthropic directly via https://support.anthropic.com. For questions about ExFu specifically, contact al@exfu.ai.
