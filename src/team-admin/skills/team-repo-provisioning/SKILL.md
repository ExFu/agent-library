---
name: team-repo-provisioning
description: Walks the substrate champion through creating the team's shared git repo -- the home for the shared substrate that every team member's Claude will read. Use when the champion is setting up a new team from scratch and needs to create the remote repo, configure access, clone it, and verify connectivity. Seeding the substrate itself (convention base, team scope, guard file) happens back in the install conversation. Also invoked by exfu-install-team-admin at the storage step when no repo exists yet. Triggers on "how do I create the repo for the team?", "where should the team's shared stuff live?", "I need to set up a git repo for our Claude setup", "set up team repo", or when the champion reaches the storage step of their install.
---

# Team repo provisioning

The team's shared substrate needs a home: a private git repo that every team member clones and that the champion maintains. Without it, shared context, conventions, and skills have nowhere to live and cannot propagate to colleagues. This skill handles the one-time setup -- creating the repo, configuring access, cloning it, and verifying connectivity -- so the install conversation can seed the substrate into it.

You are helping the substrate champion create the team's shared substrate repo. This is a one-time setup step. By the end of this skill, the repo will exist on their chosen provider, have the right access settings, be cloned locally, and be reachable from the champion's machine. What goes INSIDE it is not this skill's job: the install conversation (exfu-install-team-admin, shared-substrate seeding step) deploys the convention base, creates the team's scope via scope-setup, writes the guard file, and makes the first commit against the clone this skill produces.

**Hard constraints:**
- NEVER suggest a public repository for a team substrate. Default to private, always.
- NEVER skip the access-settings step. A substrate that anyone in the organisation can push to unreviewed is a liability.
- NEVER commit credentials, API keys, personal information, or customer data into the repo.
- NEVER invent folder structure inside the repo. Seeding is the install conversation's job, against the current conventions.

---

## Step 1: Determine where the repo will live

Ask the champion: "Where will the team substrate live? Pick the option that matches your setup."

Options:
- GitHub (cloud)
- GitLab (cloud)
- Bitbucket (cloud)
- On-prem GitLab, Gitea, or Forgejo
- Something else (ask them to describe it; adapt accordingly)

Also ask: "Do you have a CLI tool installed for this provider? (`gh` for GitHub, `glab` for GitLab.) If yes, we can use it. If not, the web UI works fine."

Note their answer and proceed with the matching provider section below.

---

## Step 2: Create the repo

### GitHub

**Web UI:**
1. Go to github.com/new.
2. Repository name: suggest `team-substrate` or `[team-name]-substrate`. The champion picks.
3. Visibility: Private. (If they ask about internal visibility for GitHub Enterprise, that is also acceptable -- but not public.)
4. Do NOT initialise with a README. The install conversation seeds the repo after cloning.
5. Click "Create repository". Copy the remote URL shown.

**CLI (`gh`):**
```bash
gh repo create [org-or-username]/[repo-name] --private --description "Team shared substrate" --confirm
```
Copy the HTTPS or SSH remote URL shown after creation.

---

### GitLab

**Web UI:**
1. Go to gitlab.com/projects/new (or your instance URL + `/projects/new`).
2. Project name: `team-substrate` or `[team-name]-substrate`.
3. Visibility: Private.
4. Do NOT initialise with a README.
5. Click "Create project". Copy the remote URL.

**CLI (`glab`):**
```bash
glab repo create [namespace]/[repo-name] --private --description "Team shared substrate"
```

---

### Bitbucket

**Web UI:**
1. Go to bitbucket.org/repo/create (or your workspace URL).
2. Repository name: `team-substrate` or `[team-name]-substrate`.
3. Access level: Private.
4. Advanced settings: uncheck "Include a README?" for now.
5. Click "Create repository". Copy the SSH or HTTPS clone URL.

---

### On-prem GitLab / Gitea / Forgejo

The web UI flow is the same pattern as GitLab cloud. Navigate to your instance's new-project page. Set visibility to Private (or the most restrictive option available on your instance). Confirm with your IT contact which namespace to use. Copy the clone URL once created.

---

## Step 3: Configure access settings

Before seeding content, set up who can access the repo.

Ask: "Who on your team needs access -- the full team, a smaller group, or just you for now?"

Recommended settings:
- **Team members** (joiners using the team plugin): read and write access, or read-only if your team uses a PR-based contribution model.
- **Champion**: maintainer or owner -- needs to be able to manage the repo settings.
- No-one outside the team should have access by default.

On GitHub: go to Settings > Collaborators and teams (or your org's team settings) to grant access at the team level rather than individually. Individual invites are fine for small teams.

On GitLab: Settings > Members. Assign Developer role to team members, Maintainer to the champion.

On Bitbucket: Repository settings > User and group access.

On on-prem: follow your instance's group/project member settings; ask IT if you are unsure which group to add.

---

## Step 4: Clone the empty repo

```bash
git clone [remote-url] [local-path]
cd [local-path]
```

A clone of an empty repo warns that you appear to have cloned an empty repository; that is expected.

Create nothing here. Hand the champion (and this clone's path) back to the install conversation -- its shared-substrate seeding step deploys the folder structure and ground rules, creates the team's scope, writes the guard file, and makes the first commit. If this skill was invoked outside an install conversation, route to `exfu-install-team-admin` rather than improvising structure.

---

## Step 5: Verify connectivity

Ask the champion to run:

```bash
git ls-remote [remote-url]
```

If it returns refs (including `HEAD`), the remote is reachable. If it fails, troubleshoot:
- SSH remote: confirm the champion's public key is registered with the provider.
- HTTPS remote: confirm credentials are cached or a credential helper is configured.
- On-prem: confirm VPN or network access if required.

Once the remote is verified, note the remote URL -- the `git-substrate-sync` skill will need it for ongoing pull/push operations.

---

## Step 6: Hand off to git-substrate-sync

The repo is now created, cloned, and reachable. Ongoing operations -- pull-before-write, commit, push, merge-conflict handling -- are handled by the `git-substrate-sync` skill.

If you are inside the `install-team-admin` flow, return to it now. The storage step is complete.

---

## A note on scope

This skill ends where content begins. Repo exists, access is right, clone works: done. Everything inside the repo follows the current conventions and is seeded by the install conversation, then grows as the team's working patterns make the need clear -- adding structure too early creates maintenance work without value.
