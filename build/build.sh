#!/usr/bin/env bash
# =============================================================================
# ExFu plugin build script
# Composes plugin/src/shared/ + plugin/src/<variant>/ into distributable
# plugin directories under plugin/build/output/<variant>/
#
# Usage:
#   ./plugin/build/build.sh solo
#   ./plugin/build/build.sh team
#   ./plugin/build/build.sh team-admin
#   ./plugin/build/build.sh all
#
# Flags:
#   --dist    Also produce a versioned .zip in public/downloads/ (publishable)
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Colour helpers (sparse — errors red, success green, warnings yellow)
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Colour

err()  { echo -e "${RED}ERROR: $*${NC}" >&2; }
ok()   { echo -e "${GREEN}  ok  ${NC} $*"; }
warn() { echo -e "${YELLOW} warn ${NC} $*"; }
info() { echo "       $*"; }

# ---------------------------------------------------------------------------
# Paths — resolve relative to the script location so the script can be
# invoked from any working directory.
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SRC_ROOT="${REPO_ROOT}/plugin/src"
OUTPUT_ROOT="${SCRIPT_DIR}/output"
DIST_DIR="${REPO_ROOT}/public/downloads"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
WANT_DIST=false
VARIANTS=()

for arg in "$@"; do
  case "$arg" in
    --dist) WANT_DIST=true ;;
    all)    VARIANTS=(solo team team-admin) ;;
    solo|team|team-admin) VARIANTS+=("$arg") ;;
    *)
      err "Unknown argument: $arg"
      echo "Usage: $0 [solo|team|team-admin|all] [--dist]"
      exit 1
      ;;
  esac
done

if [[ ${#VARIANTS[@]} -eq 0 ]]; then
  err "No variant specified."
  echo "Usage: $0 [solo|team|team-admin|all] [--dist]"
  exit 1
fi

# ---------------------------------------------------------------------------
# JSON validation helper
# Prefer jq if available; fall back to python3.
# ---------------------------------------------------------------------------
validate_json() {
  local file="$1"
  if command -v jq &>/dev/null; then
    jq empty "$file" 2>/dev/null
  else
    python3 -c "import json, sys; json.load(open(sys.argv[1]))" "$file" 2>/dev/null
  fi
}

read_json_field() {
  local file="$1"
  local field="$2"
  if command -v jq &>/dev/null; then
    jq -r ".$field // empty" "$file"
  else
    python3 -c "import json, sys; d=json.load(open(sys.argv[1])); print(d.get(sys.argv[2], ''))" "$file" "$field"
  fi
}

# ---------------------------------------------------------------------------
# SKILL.md frontmatter validation
# Checks that there are at least two `---` fence lines (YAML frontmatter).
# ---------------------------------------------------------------------------
validate_skill_frontmatter() {
  local skill_file="$1"
  local count
  count=$(awk '/^---$/{c++} END{print c+0}' "$skill_file")
  if [[ "$count" -lt 2 ]]; then
    return 1
  fi
  # Also require at least a `name:` and `description:` key in the frontmatter
  if ! grep -q '^name:' "$skill_file"; then
    return 1
  fi
  if ! grep -q '^description:' "$skill_file"; then
    return 1
  fi
  return 0
}

# ---------------------------------------------------------------------------
# Safe copy helper — warns if source doesn't exist instead of erroring.
# Creates parent dirs automatically.
# ---------------------------------------------------------------------------
safe_copy_dir() {
  local src="$1"
  local dst="$2"
  local label="${3:-}"
  if [[ ! -d "$src" ]]; then
    warn "Source directory not found${label:+ ($label)}: $src — skipping"
    return 0
  fi
  mkdir -p "$dst"
  # Use cp -r with glob to copy contents; handle empty dir gracefully
  local count
  count=$(find "$src" -maxdepth 1 -mindepth 1 | wc -l | tr -d ' ')
  if [[ "$count" -eq 0 ]]; then
    warn "Source directory is empty${label:+ ($label)}: $src — skipping"
    return 0
  fi
  cp -r "$src"/. "$dst/"
}

# ---------------------------------------------------------------------------
# Count helpers for the summary
# ---------------------------------------------------------------------------
count_skills()         { find "$1" -maxdepth 2 -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' '; }
count_scheduled_tasks(){ find "$1" -maxdepth 2 -name "TASK.md"  2>/dev/null | wc -l | tr -d ' '; }
count_resources()      { find "$1" -type f 2>/dev/null | wc -l | tr -d ' '; }
dir_size()             { du -sh "$1" 2>/dev/null | cut -f1; }

# ---------------------------------------------------------------------------
# Build a single variant
# ---------------------------------------------------------------------------
build_variant() {
  local variant="$1"
  local start_time
  start_time=$(date +%s)

  echo ""
  echo "============================================================"
  echo "  Building: $variant"
  echo "============================================================"

  local src_variant="${SRC_ROOT}/${variant}"
  local src_shared="${SRC_ROOT}/shared"
  local output_dir="${OUTPUT_ROOT}/${variant}"
  local manifest_src="${src_variant}/.claude-plugin/plugin.json"

  # ------------------------------------------------------------------
  # 1. Pre-flight: manifest must exist and be valid JSON
  # ------------------------------------------------------------------
  if [[ ! -f "$manifest_src" ]]; then
    err "Manifest not found: $manifest_src"
    return 1
  fi
  if ! validate_json "$manifest_src"; then
    err "Manifest is not valid JSON: $manifest_src"
    return 1
  fi
  ok "Manifest valid: $manifest_src"

  local plugin_name
  plugin_name=$(read_json_field "$manifest_src" "name")
  local plugin_version
  plugin_version=$(read_json_field "$manifest_src" "version")

  if [[ -z "$plugin_name" ]]; then
    err "Manifest missing 'name' field: $manifest_src"
    return 1
  fi
  if [[ -z "$plugin_version" ]]; then
    err "Manifest missing 'version' field: $manifest_src"
    return 1
  fi

  info "Plugin: $plugin_name  version: $plugin_version"

  # ------------------------------------------------------------------
  # 2. Clean output directory
  # ------------------------------------------------------------------
  if [[ -d "$output_dir" ]]; then
    rm -rf "$output_dir"
    info "Cleaned: $output_dir"
  fi
  mkdir -p "$output_dir"

  # ------------------------------------------------------------------
  # 3. Compose the variant
  # ------------------------------------------------------------------

  # 3a. Shared skills → output/skills/
  #     git-substrate-sync ships only in team and team-admin, NOT solo.
  if [[ -d "${src_shared}/skills" ]]; then
    for skill_dir in "${src_shared}/skills"/*/; do
      [[ -d "$skill_dir" ]] || continue
      local skill_name
      skill_name=$(basename "$skill_dir")

      # Exclusion rule: git-substrate-sync is excluded from solo
      if [[ "$variant" == "solo" && "$skill_name" == "git-substrate-sync" ]]; then
        info "Excluding git-substrate-sync from solo (team/team-admin only)"
        continue
      fi

      mkdir -p "${output_dir}/skills"
      cp -r "$skill_dir" "${output_dir}/skills/${skill_name}"
    done
    ok "Shared skills copied"
  else
    warn "No shared/skills/ directory found"
  fi

  # 3b. Variant-specific skills → output/skills/ (overwrite on conflict)
  if [[ -d "${src_variant}/skills" ]]; then
    mkdir -p "${output_dir}/skills"
    cp -r "${src_variant}/skills"/. "${output_dir}/skills/"
    ok "Variant skills copied ($variant/skills/)"
  else
    warn "No ${variant}/skills/ directory found — skipping"
  fi

  # 3c. Shared scheduled-tasks → output/scheduled-tasks/
  safe_copy_dir \
    "${src_shared}/scheduled-tasks" \
    "${output_dir}/scheduled-tasks" \
    "shared scheduled-tasks"
  if [[ -d "${src_shared}/scheduled-tasks" && \
        $(find "${src_shared}/scheduled-tasks" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ') -gt 0 ]]; then
    ok "Shared scheduled-tasks copied"
  fi

  # 3d. Variant-specific scheduled-tasks → output/scheduled-tasks/ (merge/overwrite)
  if [[ -d "${src_variant}/scheduled-tasks" ]]; then
    mkdir -p "${output_dir}/scheduled-tasks"
    cp -r "${src_variant}/scheduled-tasks"/. "${output_dir}/scheduled-tasks/"
    ok "Variant scheduled-tasks copied ($variant/scheduled-tasks/)"
  fi

  # 3e. Shared templates → output/templates/
  safe_copy_dir \
    "${src_shared}/templates" \
    "${output_dir}/templates" \
    "shared templates"
  if [[ -d "${src_shared}/templates" && \
        $(find "${src_shared}/templates" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ') -gt 0 ]]; then
    ok "Shared templates copied"
  fi

  # 3f. Shared resources → output/resources/ (recursive — includes diagrams/, widgets/)
  safe_copy_dir \
    "${src_shared}/resources" \
    "${output_dir}/resources" \
    "shared resources"
  if [[ -d "${src_shared}/resources" && \
        $(find "${src_shared}/resources" -mindepth 1 -maxdepth 1 | wc -l | tr -d ' ') -gt 0 ]]; then
    ok "Shared resources copied"
  fi

  # 3g. Variant-specific resources → output/resources/ (overwrite on conflict)
  if [[ -d "${src_variant}/resources" ]]; then
    mkdir -p "${output_dir}/resources"
    cp -r "${src_variant}/resources"/. "${output_dir}/resources/"
    ok "Variant resources copied ($variant/resources/)"
  fi

  # 3h. Variant-specific scripts → output/scripts/
  if [[ -d "${src_variant}/scripts" ]]; then
    mkdir -p "${output_dir}/scripts"
    cp -r "${src_variant}/scripts"/. "${output_dir}/scripts/"
    ok "Variant scripts copied ($variant/scripts/)"
  fi

  # 3i. Manifest → output/.claude-plugin/plugin.json
  mkdir -p "${output_dir}/.claude-plugin"
  cp "$manifest_src" "${output_dir}/.claude-plugin/plugin.json"
  ok "Manifest copied"

  # ------------------------------------------------------------------
  # 4. Post-build validation
  # ------------------------------------------------------------------
  echo ""
  info "--- Validating output ---"

  # 4a. Manifest in output is valid JSON
  if ! validate_json "${output_dir}/.claude-plugin/plugin.json"; then
    err "Output manifest is not valid JSON — something went wrong during copy"
    return 1
  fi
  ok "Output manifest valid"

  # 4b. Every skill directory must contain a SKILL.md with valid frontmatter
  local skills_dir="${output_dir}/skills"
  local validation_failed=false
  if [[ -d "$skills_dir" ]]; then
    while IFS= read -r -d '' skill_md; do
      if ! validate_skill_frontmatter "$skill_md"; then
        err "SKILL.md missing or invalid frontmatter: $skill_md"
        validation_failed=true
      fi
    done < <(find "$skills_dir" -name "SKILL.md" -print0)

    # Check for skill subdirectories that have NO SKILL.md at all.
    # These are treated as warnings (not errors) because other agents may still
    # be writing their skill content — the build should succeed with stubs present.
    while IFS= read -r -d '' skill_subdir; do
      if [[ ! -f "${skill_subdir}/SKILL.md" ]]; then
        warn "Skill directory has no SKILL.md (stub/in-progress?): $(basename "$skill_subdir")"
      fi
    done < <(find "$skills_dir" -mindepth 1 -maxdepth 1 -type d -print0)
  fi

  if [[ "$validation_failed" == true ]]; then
    err "Validation failed for $variant"
    return 1
  fi
  ok "All SKILL.md files have valid frontmatter"

  # 4c. No empty directories in output
  local empty_dirs
  empty_dirs=$(find "$output_dir" -type d -empty 2>/dev/null)
  if [[ -n "$empty_dirs" ]]; then
    warn "Empty directories found (these will be included in the build):"
    while IFS= read -r d; do
      warn "  $d"
    done <<< "$empty_dirs"
  fi

  # ------------------------------------------------------------------
  # 5. Optional: produce versioned .zip archive in public/downloads/
  # ------------------------------------------------------------------
  if [[ "$WANT_DIST" == true ]]; then
    mkdir -p "$DIST_DIR"
    local archive_name="${plugin_name}-v${plugin_version}.zip"
    local archive_path="${DIST_DIR}/${archive_name}"
    # Remove any prior archive at the same path so the zip is rebuilt clean
    rm -f "$archive_path"
    (cd "${OUTPUT_ROOT}" && zip -rq "$archive_path" "$variant")
    ok "Archive written: $archive_path  ($(du -sh "$archive_path" | cut -f1))"
  fi

  # ------------------------------------------------------------------
  # 6. Summary
  # ------------------------------------------------------------------
  local end_time
  end_time=$(date +%s)
  local elapsed=$(( end_time - start_time ))

  local n_skills n_tasks n_resources total_size
  n_skills=$(count_skills "${output_dir}/skills")
  n_tasks=$(count_scheduled_tasks "${output_dir}/scheduled-tasks")
  n_resources=$(count_resources "${output_dir}/resources")
  total_size=$(dir_size "$output_dir")

  echo ""
  echo -e "${GREEN}  Built $plugin_name v$plugin_version${NC}"
  info "Skills:          $n_skills"
  info "Scheduled tasks: $n_tasks"
  info "Resources:       $n_resources files"
  info "Total size:      $total_size"
  info "Output:          $output_dir"
  info "Time:            ${elapsed}s"
}

# ---------------------------------------------------------------------------
# Main — iterate over requested variants
# ---------------------------------------------------------------------------
overall_start=$(date +%s)
build_errors=()

for variant in "${VARIANTS[@]}"; do
  if ! build_variant "$variant"; then
    build_errors+=("$variant")
  fi
done

overall_end=$(date +%s)
overall_elapsed=$(( overall_end - overall_start ))

echo ""
echo "============================================================"
if [[ ${#build_errors[@]} -eq 0 ]]; then
  echo -e "${GREEN}  All builds succeeded${NC}  (${overall_elapsed}s total)"
  echo "  Output root: ${OUTPUT_ROOT}"
else
  echo -e "${RED}  Build failed for: ${build_errors[*]}${NC}"
  exit 1
fi
echo "============================================================"
