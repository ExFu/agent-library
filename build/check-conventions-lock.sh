#!/usr/bin/env bash
#
# Conventions lock gate.
#
# A convention version directory is frozen the moment it ships: its contents
# must never change under a stable name. Changing conventions means minting a
# fresh timestamp identifier (build/mint-conventions.sh), never editing a
# version that already exists.
#
# This gate exists because the rule was broken three times under the previous
# scheme -- the shipped v0.3/ was patched in place across plugin 0.4.0, 0.5.0,
# and 0.5.1. Doctrine that relies on remembering does not hold; a check does.
#
# Passes when: every version directory present in both HEAD and the working
# tree is byte-identical. Adding a new version directory is fine. Deleting one
# is fine (that is how a mint supersedes its predecessor in src/).
#
# Usage: build/check-conventions-lock.sh [ref]     (ref defaults to HEAD)

set -euo pipefail

REF="${1:-HEAD}"
BASE_DIR="src/shared/substrate/exfu"
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

fail=0

# Version directories as they exist in the reference commit.
tracked_versions="$(
  git ls-tree -r --name-only "$REF" -- "$BASE_DIR" 2>/dev/null |
    sed -n "s#^$BASE_DIR/\([0-9]\{8\}-[0-9]\{4\}\)/.*#\1#p;s#^$BASE_DIR/\(v[0-9][^/]*\)/.*#\1#p" |
    sort -u || true
)"

if [ -z "$tracked_versions" ]; then
  echo "conventions-lock: no shipped version directories in $REF, nothing to check"
  exit 0
fi

while IFS= read -r version; do
  [ -n "$version" ] || continue

  # Gone from the working tree: superseded by a mint. Allowed.
  if [ ! -d "$BASE_DIR/$version" ]; then
    echo "  ok    $version (removed -- superseded by a mint)"
    continue
  fi

  if diff_out="$(git diff --stat "$REF" -- "$BASE_DIR/$version" 2>/dev/null)" &&
     [ -z "$diff_out" ]; then
    echo "  ok    $version (unchanged)"
  else
    echo "  FAIL  $version has been modified in place" >&2
    git diff --stat "$REF" -- "$BASE_DIR/$version" >&2
    fail=1
  fi
done <<EOF
$tracked_versions
EOF

if [ "$fail" -ne 0 ]; then
  cat >&2 <<'MSG'

A shipped convention version was edited in place. This is the drift the
timestamp scheme exists to prevent: scopes pinned to that identifier would
silently receive different conventions.

Mint a new version instead:

    build/mint-conventions.sh

Then re-point pins and rebuild. If the edit is genuinely not part of the
contract -- documentation, principles, shipped librarian definitions,
templates -- it belongs in the unversioned files at src/shared/substrate/exfu/,
not inside a version directory. The test: a file belongs in a version
directory if and only if a `Follows:` line can anchor into it.
MSG
  exit 1
fi

echo "conventions-lock: all shipped versions intact"
