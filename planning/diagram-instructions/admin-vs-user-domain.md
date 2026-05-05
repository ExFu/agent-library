# Diagram instructions: admin-vs-user-domain

This file is the brief for the admin plane vs user domain diagram. The diagram lives at `plugin/src/team-admin/resources/diagrams/admin-vs-user.png` once produced. It ships in the team-admin plugin only.

---

## 1. What this diagram teaches

The team-admin plugin draws a hard boundary between two distinct planes of operation. The **admin plane** is what the substrate champion controls: shared skills that apply to every team member, team-wide conventions and ways of working, the git repository structure and its policies, onboarding materials, and the compliance briefing. The **user domain** is what individual team members own: their personal substrate (context, scopes, inbox, reminders), their own `wow` customisations, their personal skills, and how they choose to use the shared layer. These planes are not a hierarchy of trust — a team member's personal substrate is fully theirs and the admin has no business in it. They are a division of responsibility. The substrate champion manages the shared layer so it stays coherent and usable; team members manage their personal layer so it stays relevant to them. The diagram makes this division obvious and prevents two failure modes: substrate champions who over-reach into personal domains, and team members who accidentally try to edit shared infrastructure they shouldn't touch.

---

## 2. Key elements to include

- **Two clearly separated planes or zones:** upper or left zone is the admin plane; lower or right zone is the user domain. Clear labels: "Admin plane" (or "Substrate champion") and "User domain" (or "Team member").
- **Admin plane contents:** shared skills (team conventions, shared ways of working), team context (who the team is, how it operates, standing context about the organisation), git repository (the mechanism for distributing the shared layer), repo policies (what goes in, what doesn't), onboarding materials, compliance briefing. These are the substrate champion's responsibility to create and maintain.
- **User domain contents:** personal substrate (context/me, personal scopes), personal `wow` skill (their navigation map of their combined personal + shared setup), personal skills (inbox, reminders, writing-styles, scope skills), personal customisation of how shared skills apply to them. These are fully owned by the team member.
- **The shared layer as the interface:** there should be a clear visual representation of the shared layer — the thing the admin plane produces and the user domain consumes. It is read by all team members but written only by the substrate champion. This is the boundary between the two planes.
- **Git as the distribution mechanism:** a small label or icon indicating that the shared layer flows to team members via git sync. This doesn't need to be technically detailed — just enough to show the shared layer isn't pushed into personal substrates directly; it's pulled by each member.
- **No overlap:** the personal substrate is not visible to the admin. The admin plane produces shared infrastructure; it does not govern personal use.

---

## 3. Visual asymmetries that matter

- **Admin plane is the structural layer.** It looks like infrastructure — shared, maintained, institutional (but not cold). The substrate champion is building something everyone uses.
- **User domain is the personal layer.** It looks individual, flexible, human-scale. The team member's personal substrate belongs to them.
- **The shared layer flows downward or outward** from the admin plane to multiple user domains. The visual should suggest one-to-many — one admin plane feeding multiple user domains.
- **The boundary between planes is clear and respected.** The diagram should not show any arrow going from the user domain *up* into the admin plane (team members don't push to shared skills directly) and no arrow going from the admin plane *into* the personal substrate (the admin doesn't touch personal context).
- **Multiple user domains:** show more than one user domain receiving the shared layer. This emphasises that the admin plane is genuinely shared — it's not a personal setup for one person.

---

## 4. What this diagram is NOT trying to do

- Not showing the technical details of git operations.
- Not a permission matrix or access control table.
- Not suggesting the substrate champion has surveillance capability over team members' personal use — the opposite is true.
- Not showing the install process. This is the operational state after install.
- Not implying the user domain is lesser or restricted — it's the member's own space, fully theirs.

---

## 5. Source attribution

ExFu original. The admin-plane/user-domain distinction and the one-to-many shared-layer distribution pattern are ExFu's own design.

---

## 6. Phrase to give ChatGPT

> Here is a conceptual brief for a diagram I need. Please render it as a clean infographic, warm earth tones, label everything plainly, no corporate stock-art clichés. The diagram is called "admin plane vs user domain" and it shows the operational structure of a team Claude substrate. Top zone (admin plane): the substrate champion manages shared skills, team context, conventions, the git repo, and onboarding materials — this is team-wide infrastructure. Bottom or right zone (user domain): each team member owns their personal substrate — personal context, personal `wow` skill, personal scopes, personal skills. In the middle: the shared layer, which is produced by the admin plane and consumed by user domains via git sync. Key visual requirement: one admin plane flowing to multiple user domains (one-to-many). The boundary between planes is clear — no arrows go from user domain into admin plane, and no arrows go from admin plane into personal substrates. The admin plane looks like shared infrastructure; the user domains look individual and human-scale.
