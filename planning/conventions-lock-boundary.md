# conventions-lock-boundary -- lock the contract, not the folder

**Status:** Adopted (Al, 2026-07-24, in session). Supersedes the open question
left by `conventions-versioning-timestamps.md`: whether a shipped base may be
edited in place. It may not; the answer is to stop locking things that were
never the contract. Companion to that note, which governs *how* the identifier
churns; this one governs *what the identifier covers*.

## Why

The timestamp scheme (0.6.0) froze the contents of `exfu/<timestamp>/` so a
scope pinned to an identifier always sees the same conventions. Correct, and
worth keeping. But the lock was drawn around a *folder of related material*
rather than around the *contract surface*, and the folder holds four things
that nothing resolves against.

Discovered while adding a root `dashboard.html` pointer (0.8.0). Two files
wanted a two-line additive edit -- the ontology's root-layout diagram and the
dashboard-generator librarian's `writes:` list -- and both were frozen. Minting
a whole conventions release for two lines of documentation is absurd; editing
in place is the drift the scheme exists to end. The trap is real and it will
recur on every release, so it gets fixed before clients arrive rather than
after.

Relaxing the rule to "additive-only writes" was considered and rejected:

- The base is read **live**, not copied and forgotten. `agent-registry.json`
  pins agents to definitions by versioned path. An "additive" line in a
  librarian's `writes:` frontmatter is textually additive but **expansive in
  authority** -- it enlarges the set of paths a scheduled agent declares it may
  write.
- The additive-is-safe intuition comes from schemas, where consumers ignore
  unrecognised fields. Agents ignore nothing. An addition that contradicts or
  narrows existing text changes behaviour exactly as an edit would.
- "Byte-identical" is checkable in CI. "Additive enough" is a judgement made by
  the person who wants to make the edit. `v0.3` was patched in place across
  three releases, each presumably locally reasonable. That is the failure mode.
- The identifier stops being a sufficient description of a content set. "I
  follow 20260723-1446" would no longer pin anything without a sync date.

## The test

> A file belongs in the version directory if and only if a `Follows:` line can
> anchor into it. Everything else ships with the plugin.

Mechanically decidable, which is the point -- no per-edit judgement call.

Measured on the current base: **all 16 `Follows:` anchors point into
`ontology.md`.** Nothing anchors into `principles.md`, `readme.md`,
`librarians/`, or `skills/`. They are locked purely by colocation.

## The split

```
exfu/
  20260723-1446/      # THE CONTRACT. One file. Byte-frozen at ship.
    ontology.md       #   normative only: scope model, scope.md format,
                      #   folder-type catalogue, resolution, authoring rules
  latest.txt
  readme.md           # plugin-versioned: orientation + layout depiction
  principles.md       # plugin-versioned: advisory, nothing resolves against it
  librarians/         # plugin-versioned: definitions of plugin-owned scripts
  skills/             # plugin-versioned: wow template
  derived/
  visualisations/
```

Locked becomes *harder* than today -- one hashable file rather than a tree.
Everything else moves at plugin cadence, which is where features, tweaks, and
fixes belong.

### What this also fixes

- **Registry paths stop breaking on every mint.** `agent-registry.json`
  currently pins `exfu/20260723-1446/librarians/nightly-index.md`. Every mint
  silently invalidates those source paths in every installed library -- a
  migration tax on files that have nothing to do with conventions. Unversioned
  `librarians/` makes registry paths stable forever.
- **The recurring conflict disappears.** A librarian's `writes:` list describes
  a *plugin-owned script's* behaviour. Pinning it to a conventions version that
  moves independently guarantees collisions like the one that prompted this.
- **Mints become naturally rare.** The locked surface reduces to the scope
  model, which changes when the conventions genuinely change -- which is what a
  conventions version means. Minting over documentation stops.

## Two mechanisms

1. **Enforce the lock.** A hash manifest plus a pre-commit/CI check that any
   previously-shipped `exfu/<timestamp>/` is byte-identical to its first
   appearance. Doctrine that relies on remembering is what produced three
   in-place `v0.3` patches. The repo already gates commits through APV hooks,
   so this fits existing habits.
2. **Make minting one command.** `build/mint-conventions.sh`: copy the base to
   a fresh UTC timestamp, re-stamp every pin, update `latest.txt`. Then cost is
   never the reason to fudge the rule.

## OKF alignment

Google Cloud published the **Open Knowledge Format** on 2026-06-12 (v0.1):
markdown plus YAML frontmatter, one required field (`type`) and five reserved
(`title`, `description`, `resource`, `tags`, `timestamp`), one concept per file
with the path as identity, ordinary markdown links forming a graph, and two
optional reserved filenames (`index.md`, `log.md`).

**Ruling: align now, adopt natively later, interoperate by projection.**

The surface fit is close -- markdown with YAML frontmatter is already ExFu's
idiom, and path-as-identity is already the planning-corpus convention. But
OKF's one-concept-per-file rule collides head-on with the v7 decision to
flatten the core ontology into ONE file because agents ingest a single read far
more reliably; `Follows:` anchoring depends on that shape. Native conformance
would reverse a considered, evidence-driven decision, and it would do so on a
six-week-old v0.1 spec.

The interop goal does not require it. Consuming public OKF bundles needs an
importer; being read by OKF visualisers needs a generated OKF projection of the
library. Both leave the ingestion property intact.

- **In this upgrade (cheap, forward-compatible):** align frontmatter field
  names with OKF's reserved six wherever ExFu already has the equivalent
  concept; state OKF alignment as a direction in `principles.md`.
- **Own release, later:** native conformance, the projection/exporter, the
  importer for public bundles. The restructure is what makes that mint cheap.

## Enactment

Sequenced so each step is separately revertible.

1. Ship 0.8.0 (root `dashboard.html` pointer) with the base untouched.
2. Mint `20260724-####` containing `ontology.md` only, descriptive content
   stripped out to `readme.md` and the substrate guide, and the two deferred
   0.8.0 edits folded in.
3. Move `principles.md`, `readme.md`, `librarians/`, `skills/` to unversioned
   `exfu/`.
4. Re-point the 2 registry references and the install skills' copy step.
5. Add the hash gate and `build/mint-conventions.sh`.
6. Frontmatter field-name alignment with OKF's reserved six.

Timing: before clients onboard (Al, 2026-07-24 -- "only I break" this week).
