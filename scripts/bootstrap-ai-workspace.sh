#!/usr/bin/env bash
#
# bootstrap-ai-workspace.sh — install the ai-agent-assembly org AI baseline
# (CLAUDE.md, AGENTS.md, .claude/rules/, .claude/skills/) into a contributor's
# local multi-repo workspace root, per the layout defined in
# .claude/WORKSPACE.md (AAASM-3939) and tracked as AAASM-3943.
#
# Usage:
#   ./scripts/bootstrap-ai-workspace.sh <workspace-root-path> [--dry-run]
#
# This is a plain local script: no network calls, no eval, nothing piped from
# the network. It only reads from this repo checkout and writes into the
# workspace root you pass in.

set -euo pipefail

# --- Why symlinks instead of copies -----------------------------------------
# Symlinks mean an edit to CLAUDE.md/AGENTS.md/.claude/rules/.claude/skills in
# this repo (after a `git pull`) is picked up immediately by every workspace
# that installed it, with no need to re-run this script. Copies would silently
# drift out of date the moment this repo's source-of-truth files change.
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  echo "Usage: $(basename "${BASH_SOURCE[0]}") <workspace-root-path> [--dry-run]" >&2
}

DRY_RUN=0
WORKSPACE_ROOT=""

for arg in "$@"; do
  case "${arg}" in
    --dry-run)
      DRY_RUN=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown flag: ${arg}" >&2
      usage
      exit 1
      ;;
    *)
      if [[ -n "${WORKSPACE_ROOT}" ]]; then
        echo "Unexpected extra argument: ${arg}" >&2
        usage
        exit 1
      fi
      WORKSPACE_ROOT="${arg}"
      ;;
  esac
done

if [[ -z "${WORKSPACE_ROOT}" ]]; then
  echo "Error: <workspace-root-path> is required." >&2
  usage
  exit 1
fi

# Counters for the final summary.
CREATED=0
UPDATED=0
SKIPPED=0
FAILED=0

# One human-readable line per item, appended as we go, printed at the end.
declare -a REPORT_LINES=()

record() {
  # record <status> <message>
  local status="$1"
  local message="$2"
  case "${status}" in
    created) CREATED=$((CREATED + 1)) ;;
    updated) UPDATED=$((UPDATED + 1)) ;;
    skipped) SKIPPED=$((SKIPPED + 1)) ;;
    failed) FAILED=$((FAILED + 1)) ;;
  esac
  REPORT_LINES+=("[${status}] ${message}")
}

ensure_directory() {
  # ensure_directory <target-dir> <label>
  local target="$1"
  local label="$2"

  if [[ -d "${target}" && ! -L "${target}" ]]; then
    record "skipped" "${label}: already exists (up to date)"
    return 0
  fi

  if [[ -e "${target}" || -L "${target}" ]]; then
    record "skipped" "${label}: exists but is not a plain directory (skipped (local override))"
    return 0
  fi

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    record "created" "${label}: would create directory ${target}"
    return 0
  fi

  if mkdir -p "${target}"; then
    record "created" "${label}: created directory ${target}"
  else
    record "failed" "${label}: failed to create directory ${target}"
  fi
}

ensure_symlink() {
  # ensure_symlink <source-path> <target-path> <label>
  local source="$1"
  local target="$2"
  local label="$3"

  if [[ ! -e "${source}" ]]; then
    record "failed" "${label}: source ${source} does not exist in this repo"
    return 0
  fi

  local resolved_source
  resolved_source="$(realpath "${source}")"

  if [[ -L "${target}" ]]; then
    if [[ -e "${target}" ]]; then
      # Symlink resolves to something that exists — compare real paths so a
      # workspace that was moved/re-cloned still counts as "up to date".
      if [[ "$(realpath "${target}")" == "${resolved_source}" ]]; then
        record "skipped" "${label}: already linked to ${source} (up to date)"
      else
        record "skipped" "${label}: symlink points elsewhere (skipped (local override))"
      fi
      return 0
    fi

    # Broken/dangling symlink — nothing meaningful can be preserved here, so
    # it's safe to treat it as stale (e.g. this repo checkout moved) and
    # relink it rather than treating it as a deliberate local override.
    if [[ "${DRY_RUN}" -eq 1 ]]; then
      record "updated" "${label}: would relink broken symlink ${target} -> ${source}"
      return 0
    fi

    if rm -f "${target}" && ln -s "${source}" "${target}"; then
      record "updated" "${label}: relinked broken symlink ${target} -> ${source}"
    else
      record "failed" "${label}: failed to relink broken symlink ${target}"
    fi
    return 0
  fi

  if [[ -e "${target}" ]]; then
    # Exists and is a real file/directory, not a symlink at all — a
    # contributor's local override. Never clobber it.
    record "skipped" "${label}: exists and is not a symlink (skipped (local override))"
    return 0
  fi

  if [[ "${DRY_RUN}" -eq 1 ]]; then
    record "created" "${label}: would create symlink ${target} -> ${source}"
    return 0
  fi

  if ln -s "${source}" "${target}"; then
    record "created" "${label}: created symlink ${target} -> ${source}"
  else
    record "failed" "${label}: failed to create symlink ${target}"
  fi
}

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "Dry run: no changes will be made."
fi
echo "Bootstrapping AI workspace at: ${WORKSPACE_ROOT}"
echo "Installing from: ${SCRIPT_DIR}"
echo

# --- Workspace root folder structure -----------------------------------------
ensure_directory "${WORKSPACE_ROOT}" "workspace root"
ensure_directory "${WORKSPACE_ROOT}/.claude" "workspace .claude"
ensure_directory "${WORKSPACE_ROOT}/.claude/commands" "workspace .claude/commands (reserved)"

# --- Org baseline artifacts (symlinked, see comment at top of file) ---------
ensure_symlink "${SCRIPT_DIR}/CLAUDE.md" "${WORKSPACE_ROOT}/CLAUDE.md" "CLAUDE.md"
ensure_symlink "${SCRIPT_DIR}/AGENTS.md" "${WORKSPACE_ROOT}/AGENTS.md" "AGENTS.md"
ensure_symlink "${SCRIPT_DIR}/.claude/rules" "${WORKSPACE_ROOT}/.claude/rules" ".claude/rules"
ensure_symlink "${SCRIPT_DIR}/.claude/skills" "${WORKSPACE_ROOT}/.claude/skills" ".claude/skills"

# --- Summary ------------------------------------------------------------------
echo
echo "Summary:"
for line in "${REPORT_LINES[@]}"; do
  echo "  ${line}"
done
echo
echo "created=${CREATED} updated=${UPDATED} skipped=${SKIPPED} failed=${FAILED}"

if [[ "${FAILED}" -gt 0 ]]; then
  exit 1
fi

exit 0
