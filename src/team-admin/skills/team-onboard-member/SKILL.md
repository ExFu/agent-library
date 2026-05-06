---
name: team-onboard-member
description: Generates a personalised onboarding pack — a markdown document the substrate champion sends to a new team member before or alongside the team plugin download link. The joiner pastes the pack into their install conversation, and the install skill reads it to pre-populate the git repo URL, team conventions, and contact details. Use when the champion is bringing someone new onto the team. Also invoked by exfu-install-team-admin at the onboarding-prep step. Triggers on "someone new is joining the team", "I need to get [person] set up", "how do I tell a new person to install this?", "my colleague just joined and needs to set up Claude", "create onboarding pack", or any champion intent to onboard a new team member.
---

# Team onboard member

The pack format exists for a specific reason: the joiner pastes it into their install conversation and the install skill reads it directly, using it to pre-populate the git remote URL, surface the team's conventions at the right moment, and personalise the flow without requiring the joiner to look anything up. A plain email introduction achieves none of that. The structured pack is what makes the joiner's install smooth rather than generic.

You are helping the substrate champion generate an onboarding pack for a new team member. The pack is a markdown document the champion sends to the joiner before or alongside the team plugin download link. The joiner pastes it into their install conversation, and install-team reads it to personalise their flow.

**Hard constraints:**
- The pack must include the git remote URL. Without it, the joiner cannot connect to the team substrate.
- The pack must be plain markdown. No HTML, no attachments. The joiner needs to be able to read it raw or paste it directly into a Claude conversation.
- Do NOT include any sensitive information in the pack: no credentials, no API keys, no internal financial data, no personal details beyond the joiner's name and role.

---

## Step 1: Gather inputs

Ask the champion for the following. All are required unless marked optional.

1. **Joiner's name** — how they should be addressed in the welcome.
2. **Joiner's role** — their job title or function (e.g. "account director", "senior engineer", "operations lead").
3. **Anything specific they should know up front** — optional. Could be: which scope they'll be working in first, a specific convention they need to follow early, or a person to contact for something. If the champion has nothing to add, skip this section.
4. **Champion's contact details** — how the joiner can reach the champion for help. An email address, Slack handle, or similar.

You also need:
- The git remote URL for the team substrate. Read this from the champion's local git config for the substrate repo:
  ```bash
  git -C [substrate-path] remote get-url origin
  ```
  If you cannot determine the path automatically, ask the champion to confirm it.

- A summary of the team's conventions. Read `context/team-x/ways-of-working.md` from the team substrate. You will use it to generate the one-paragraph conventions intro in the pack. If the file does not exist yet, note this to the champion and use a placeholder.

---

## Step 2: Generate the pack

Produce a markdown document with this structure. Fill in each section from the inputs above.

---

```markdown
# Welcome to [team name] — your setup pack

Hi [joiner name],

[Champion writes a brief welcome in their own voice. 2-4 sentences. Introduce the team setup and what the joiner is getting access to. Keep it warm and practical, not ceremonial.]

---

## What you need

### Team plugin

Download the ExFu team plugin here:
**[TEAM PLUGIN DOWNLOAD URL — champion to insert before sending]**

This is the Claude plugin that connects your Claude to the team's shared substrate.

### Team substrate repo

Your Claude will connect to the team's shared substrate via git. The remote URL is:

```
[git remote URL]
```

You will need read access to this repo. If you get a permissions error when cloning,
contact [champion name or IT contact].

---

## How the team works

[One paragraph, auto-generated from context/team-x/ways-of-working.md. Keep it concise — 80 to 120 words. Cover: what the shared substrate is for, the key naming or filing conventions, and how personal vs shared content is divided. Do not include anything sensitive.]

---

## Your install conversation

When you open the team plugin for the first time, you will have an install conversation with Claude. Here is what to expect:

- You will be asked to paste or share this document early in the conversation. Do that — it will personalise the install for you.
- Claude will walk you through connecting to the team repo and setting up your personal layer on top of it.
- You will set up your own context (your role, background, working style). This stays on your machine and is never shared with the team.
- By the end, your Claude will know who you are, what team you are on, and how to find the shared context and skills.

The whole install usually takes 30 to 60 minutes. No prior technical setup required beyond having Claude and git installed.

[If anything specific for this joiner — insert here, or omit this section entirely.]

---

## Questions?

Reach out to [champion name] at [champion contact details].

```

---

## Step 3: Review with the champion

Present the draft pack. Ask: "Does this look right? A few things to check before you send it:
- The welcome paragraph sounds like you, not like a template.
- The team plugin download URL is filled in (I've left a placeholder — you'll need to insert the real link before sending).
- The conventions paragraph covers what a new person actually needs to know."

Make any edits the champion requests.

---

## Step 4: Save the pack

Save the final pack to the team substrate at:

```
_meta/onboarding-packs/[joiner-name].md
```

For example: `_meta/onboarding-packs/sarah-chen.md`

Saving it here means:
- It is git-tracked. The champion can find it later and see what was sent.
- The champion can edit it before sending if anything changes.
- Future champions can see who was onboarded and what they were told.

Commit the file via `git-substrate-sync` with the message:
```
meta: onboarding pack for [joiner name]
```

---

## Step 5: Send it

The pack is plain markdown. The champion can send it any way that works:
- Email it as a `.md` file attachment, or paste the text body directly.
- Share it in Slack, Teams, or wherever the team communicates.
- Paste it into a direct message with the joiner.

The joiner does not need any special viewer. They paste it into their install conversation and the install-team skill reads it from there.

---

## Note on the download URL

The team plugin download URL is managed by the ExFu install page. The champion should retrieve the current URL from `exfu.ai/install` at the time of onboarding, and insert it into the pack before sending. The URL in the template is a deliberate placeholder — it is not filled automatically because download links may change between plugin versions.
