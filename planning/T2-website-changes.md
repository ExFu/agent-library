# T2 — Website changes

The user-facing changes to `exfu.ai` to support plugin distribution. New install/download page, retiring the existing `/clients/*` URLs, marketing copy adjustments.

Anchors back to: `T1-overview.md`, `T2-build-and-distribution.md`.

---

## Why

The plugin model only works if there's a clean, obvious way for users to find and install it. The website is the front door. It currently serves the fetch-model files at `/clients/*` URLs that the install agent reaches out to during a session. Moving to plugins makes those URLs vestigial — and worse, leaves a partially-broken experience for anyone who hits them.

This T2 covers what the site needs to look like in the plugin world: a download page that works, removal of misleading old paths, and any marketing copy adjustments that flow from the model change.

---

## How

### Download page

Per `T2-build-and-distribution.md`, the page lives at `/install` (or similar). Single page, static HTML/Astro, simple and reliable.

Content shape:

- Lead with what's available: two plugins, solo and team, with one-liners for each ("personal Claude install for individuals" / "personal Claude install for team members"). Brief, not hyped.
- Download buttons for each plugin's latest version.
- Version indicator next to each.
- Quick-start: "Download. Install in Claude (link to Anthropic docs on plugin install). Run `/exfu` to start."
- Link to the substrate primer for users who want to read about it before installing.
- Archive section (collapsed by default) for previous versions.
- Honest note about which plugin to pick if uncertain — probably solo unless they've explicitly come in for a team setup.

### Retiring `/clients/*` URLs

Three options:

1. **Hard delete.** Remove the files entirely. Anyone hitting old URLs gets 404. Cleanest but breaks any external link or bookmark.
2. **Redirect to download page.** Anyone hitting any `/clients/*` URL gets redirected to `/install`. Honest and helpful.
3. **Static page at each old URL** explaining the change and pointing to `/install`. Most graceful but most work.

Recommendation: option 2 (redirect). A blanket redirect from `/clients/*` to `/install` is one line of config (Astro / hosting redirect rules) and gracefully forwards anyone who has a stale link. The user lands somewhere useful even if they don't see the explanation.

Worth keeping the *files* in the repo for source-of-truth and migration purposes — they're the input to `plugin/src/` — but stop *serving* them. The build pipeline pulls from `plugin/src/` (which is itself ported from `public/clients/`); the website just stops exposing the path.

Once the plugin is shipping reliably, hard-delete becomes safe — but no rush.

### Marketing copy adjustments

The website's existing pages probably mention the install model in some places. Need to audit and adjust:

- Anywhere that says "the install agent fetches skills from..." or similar — drop or replace.
- Anywhere that says "we'll set up your Claude in a single afternoon call" — still true, but the mechanism is plugin-installed-then-walked-through. Adjust if specific.
- Anywhere that points at specific `/clients/*` URLs (e.g. "read the substrate guide at...") — repoint to wherever those primers end up published, or to the substrate primer's eventual permanent home.

Probably a one-pass audit covers it. Most of the site is unrelated to the install mechanics.

### Links to public resources

Per `cross-cut-ecosystem-references.md`, the website should also lean into "we're a guide through the ecosystem" framing. Worth a small reference page or a section on the download page linking to:

- Anthropic Claude 101.
- Claude Cowork course.
- Claude help docs.
- claude101.com.
- Notable community skills (superpowers, oh-my-claude).

Doesn't need to be exhaustive. Just demonstrates ExFu's posture and gives users alternatives.

---

## What — components inventory

### `/install` page

New Astro page at `src/pages/install.astro` (or wherever fits the site convention). Content per the shape above.

### Redirects

Configuration change to redirect `/clients/*` to `/install`. Adjust per the site's hosting / Astro config.

### Marketing audit

A pass through existing pages to update or remove references to the old install mechanism.

### Optional: ecosystem references page

Small page at `/ecosystem` or `/learning` (or as a section on `/install`) linking to public resources.

### Sitemap / nav updates

Add `/install` to the site's nav. Update sitemap accordingly.

---

## T3 candidates

- `T3-install-page.md` — design and build the download page.
- `T3-clients-url-retirement.md` — set up redirects, plan the eventual hard-delete.
- `T3-marketing-audit.md` — pass through existing pages, list edits needed.
- `T3-ecosystem-references-page.md` — optional, low priority.

These are mostly small and independent. Install page is the one that has to ship first; others can follow.

---

## Open questions

- **Page URL.** `/install`, `/plugin`, `/download`, `/get-claude-set-up`? `/install` is conventional for software downloads. `/plugin` is most accurate. Either's fine.
- **Marketing changes.** How much of the existing site will need rewriting? Need to look at what's actually there before answering. The audit T3 is the place to figure it out.
- **Ecosystem references page positioning.** Standalone page, section of install page, or sidebar mention? Probably section of install page for v1; promote to standalone if the content grows.
- **Beta vs production cutover.** Do we want a beta period where both the fetch model and the plugin model coexist, or a clean cutover? Probably clean cutover once v1 of each plugin is ready — the fetch model is meant to be deprecated, not maintained alongside.
- **Communicating the change to existing users.** Anyone who has a fetch-model install today should hear about the migration path. Probably a short email or post when v1 ships. Out of strict T2 scope but worth flagging.
