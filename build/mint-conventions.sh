#!/usr/bin/env bash
#
# Mint a new convention version.
#
# Changing the conventions means minting a fresh identifier, never editing a
# version that already shipped (build/check-conventions-lock.sh enforces that).
# This script makes minting a single command, so cost is never the reason to
# fudge the rule.
#
# What it does:
#   1. Copies the current version directory to a fresh UTC timestamp
#   2. Re-points every pin in src/ to the new identifier
#   3. Removes the superseded directory (the plugin ships exactly one)
#
# What it does NOT do: decide whether a change belongs in the contract at all.
# A file belongs in a version directory if and only if a `Follows:` line can
# anchor into it. Documentation, principles, shipped librarian definitions and
# templates live unversioned at src/shared/substrate/exfu/ and need no mint.
#
# Usage: build/mint-conventions.sh [--dry-run]

set -euo pipefail

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"
BASE_DIR="src/shared/substrate/exfu"

current="$(find "$BASE_DIR" -maxdepth 1 -type d -name '[0-9]*-[0-9]*' -exec basename {} \; | sort | tail -1)"
if [ -z "$current" ]; then
  echo "error: no current version directory found under $BASE_DIR" >&2
  exit 1
fi

new="$(date -u +%Y%m%d-%H%M)"
if [ "$new" = "$current" ]; then
  echo "error: current version $current was minted this minute; wait 60s" >&2
  exit 1
fi

echo "Minting $current -> $new"

# Files that record history and must keep their historical identifiers.
# Note the path is normalised first: `grep -r src/` emits `src//shared/...`
# with a doubled slash, which silently defeated a literal match here and let a
# mint rewrite the changelog's historical entries. Normalise, then compare.
is_historical() {
  case "$(printf '%s' "$1" | tr -s '/')" in
    src/shared/resources/CHANGELOG.md) return 0 ;;
    *) return 1 ;;
  esac
}

if [ "$DRY_RUN" -eq 1 ]; then
  echo "(dry run -- no changes written)"
  echo "would copy   $BASE_DIR/$current -> $BASE_DIR/$new"
  echo "would repoint pins in:"
  grep -rl "$current" src/ --include='*.md' --include='*.json' --include='*.txt' 2>/dev/null |
    while IFS= read -r f; do is_historical "$f" || echo "  $f"; done
  exit 0
fi

cp -R "$BASE_DIR/$current" "$BASE_DIR/$new"

# Re-point pins everywhere except the historical record.
grep -rl "$current" src/ --include='*.md' --include='*.json' --include='*.txt' 2>/dev/null |
  while IFS= read -r f; do
    is_historical "$f" && continue
    # substrate-guide keeps its own changelog: leave everything below it alone
    if [ "$(basename "$f")" = "substrate-guide.md" ] && grep -q '^## Changelog' "$f"; then
      python3 - "$f" "$current" "$new" <<'PY'
import sys, pathlib
p, old, new = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
text = p.read_text(encoding="utf-8")
head, sep, tail = text.partition("\n## Changelog")
p.write_text(head.replace(old, new) + sep + tail, encoding="utf-8")
PY
    else
      python3 - "$f" "$current" "$new" <<'PY'
import sys, pathlib
p, old, new = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
PY
    fi
    echo "  repointed $f"
  done

rm -rf "${BASE_DIR:?}/$current"
echo "  removed   $BASE_DIR/$current (superseded)"

cat <<MSG

Minted $new. Next:
  1. Make the conventions change in $BASE_DIR/$new/ontology.md
  2. Record it in src/shared/resources/CHANGELOG.md and the substrate guide
  3. ./build/build.sh all
MSG
