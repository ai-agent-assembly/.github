#!/usr/bin/env bash
#
# validate-ai-workspace.sh — check an installed AI onboarding workspace root
# (and, optionally, one or more org repo checkouts) against the layout
# defined in .claude/WORKSPACE.md (AAASM-3939) and installed by
# bootstrap-ai-workspace.sh (AAASM-3943).
#
# Usage:
#   ./scripts/validate-ai-workspace.sh <workspace-root-path> [repo-path...]
#
# Checks the workspace root for CLAUDE.md, AGENTS.md, .claude/rules/, and
# .claude/skills/, classifying each as: missing, a broken symlink, a local
# override (present but not a symlink back to a recognized .github clone),
# or correctly symlinked (OK). .claude/rules/ and .claude/skills/ are checked
# per file (one classification per file inside them), not as a whole
# directory, so overriding a single file is detected without flagging every
# other file in that directory. Local overrides are reported for visibility
# but do not fail validation — see the override model in .claude/WORKSPACE.md.
#
# Any extra repo-path arguments get a lightweight, informational check for
# their own `.claude/CLAUDE.md` and `AGENTS.md` (repo-level context gaps do
# not affect the exit code — this script validates the workspace scaffold,
# not repo-level completeness).
#
# Exit codes:
#   0 - every expected workspace item is present and either correctly
#       symlinked or a recognized local override. Safe to use as a CI gate.
#   1 - at least one expected item is missing, or a symlink is broken.
#
# This is a plain local script: no network calls, only filesystem checks
# and local (non-network) `git remote -v` reads.

set -euo pipefail

usage() {
  echo "Usage: $(basename "${BASH_SOURCE[0]}") <workspace-root-path> [repo-path...]" >&2
}

if [[ $# -lt 1 ]]; then
  echo "Error: <workspace-root-path> is required." >&2
  usage
  exit 1
fi

case "$1" in
  -h|--help)
    usage
    exit 0
    ;;
  *)
    # Not a flag — fall through to treat as workspace-root-path
    ;;
esac

WORKSPACE_ROOT="$1"
shift
declare -a REPO_PATHS=("$@")

# --- Report buckets ----------------------------------------------------------
# bash 3.2 (macOS default) throws "unbound variable" under `set -u` when
# expanding an array that has zero elements, so every expansion of these is
# guarded with an `${#arr[@]} -gt 0` length check before use.
declare -a MISSING=()
declare -a BROKEN=()
declare -a OVERRIDES=()
declare -a OK=()
declare -a REPO_NOTES=()

# --- Helpers -------------------------------------------------------------

# is_dot_github_clone <dir>
# True if <dir> is inside a git checkout whose configured remotes reference
# the ai-agent-assembly/.github repo. `git remote -v` only reads local repo
# config; it makes no network calls.
is_dot_github_clone() {
  local dir="$1"
  local git_root
  git_root="$(cd "${dir}" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null)" || return 1
  [[ -n "${git_root}" ]] || return 1
  git -C "${git_root}" remote -v 2>/dev/null | grep -qiE 'ai-agent-assembly/\.github(\.git)?'
}

# check_item <target-path> <label>
# Classifies one expected workspace item into MISSING / BROKEN / OVERRIDES / OK.
check_item() {
  local target="$1"
  local label="$2"

  if [[ -L "${target}" ]]; then
    if [[ ! -e "${target}" ]]; then
      BROKEN+=("${label}: ${target} -> $(readlink "${target}") (symlink target does not exist)")
      return
    fi

    local resolved check_dir
    resolved="$(realpath "${target}")"
    if [[ -d "${resolved}" ]]; then
      check_dir="${resolved}"
    else
      check_dir="$(dirname "${resolved}")"
    fi

    if is_dot_github_clone "${check_dir}"; then
      OK+=("${label}: ${target} -> ${resolved}")
    else
      OVERRIDES+=("${label}: ${target} is a symlink to ${resolved}, which is not inside a recognized .github clone (local override — intentional?)")
    fi
    return
  fi

  if [[ -e "${target}" ]]; then
    OVERRIDES+=("${label}: ${target} is a real file/dir, not a symlink back to a .github clone (local override — intentional?)")
    return
  fi

  MISSING+=("${label}: ${target} does not exist")
}

# check_dir_contents <target-dir> <label>
# .claude/rules/ and .claude/skills/ are installed as a real directory
# containing one symlink per file (see bootstrap-ai-workspace.sh's
# ensure_dir_of_symlinks), so each file must be classified individually —
# checking the directory as a single unit would never detect a single
# overridden file inside it. Falls back to check_item's whole-target logic
# if the directory itself turns out to be an old-style whole-directory
# symlink (pre-AAASM-4177 install), for backward compatibility.
check_dir_contents() {
  local target_dir="$1"
  local label="$2"

  if [[ -L "${target_dir}" ]]; then
    check_item "${target_dir}" "${label}"
    return
  fi

  if [[ ! -d "${target_dir}" ]]; then
    MISSING+=("${label}: ${target_dir} does not exist")
    return
  fi

  local found_any=0
  local entry name
  for entry in "${target_dir}"/*; do
    [[ -e "${entry}" || -L "${entry}" ]] || continue
    found_any=1
    name="$(basename "${entry}")"
    check_item "${entry}" "${label}/${name}"
  done

  if [[ "${found_any}" -eq 0 ]]; then
    MISSING+=("${label}: ${target_dir} exists but is empty")
  fi
}

echo "Validating AI onboarding workspace: ${WORKSPACE_ROOT}"
echo

check_item "${WORKSPACE_ROOT}/CLAUDE.md" "CLAUDE.md"
check_item "${WORKSPACE_ROOT}/AGENTS.md" "AGENTS.md"
check_dir_contents "${WORKSPACE_ROOT}/.claude/rules" ".claude/rules"
check_dir_contents "${WORKSPACE_ROOT}/.claude/skills" ".claude/skills"

# --- Generic broken-symlink sweep under the workspace's .claude/ tree -------
# Catches broken symlinks beyond the items already checked above (e.g. a
# contributor's own additions under .claude/commands/). `find` does not
# descend into symlinked directories by default, so a whole-directory
# old-style .claude/rules or .claude/skills symlink is naturally excluded;
# for the new per-file layout (real directories), explicitly skip everything
# under them since check_dir_contents already classified each file.
if [[ -d "${WORKSPACE_ROOT}/.claude" ]]; then
  while IFS= read -r link; do
    [[ -z "${link}" ]] && continue
    case "${link}" in
      "${WORKSPACE_ROOT}/.claude/rules" | "${WORKSPACE_ROOT}/.claude/rules/"* | \
      "${WORKSPACE_ROOT}/.claude/skills" | "${WORKSPACE_ROOT}/.claude/skills/"*)
        continue
        ;;
      *)
        # Other symlinks under .claude/ — check them below
        ;;
    esac
    if [[ ! -e "${link}" ]]; then
      BROKEN+=("extra symlink: ${link} -> $(readlink "${link}") (target does not exist)")
    fi
  done < <(find "${WORKSPACE_ROOT}/.claude" -type l 2>/dev/null)
fi

# --- Optional lightweight repo-level checks ---------------------------------
if [[ ${#REPO_PATHS[@]} -gt 0 ]]; then
  for repo in "${REPO_PATHS[@]}"; do
    if [[ ! -d "${repo}" ]]; then
      REPO_NOTES+=("${repo}: not a directory, skipped")
      continue
    fi
    if [[ -f "${repo}/.claude/CLAUDE.md" ]]; then
      REPO_NOTES+=("${repo}: has .claude/CLAUDE.md")
    else
      REPO_NOTES+=("${repo}: missing .claude/CLAUDE.md (repo-level context gap)")
    fi
    if [[ -f "${repo}/AGENTS.md" ]]; then
      REPO_NOTES+=("${repo}: has AGENTS.md")
    else
      REPO_NOTES+=("${repo}: missing AGENTS.md (repo-level context gap)")
    fi
  done
fi

# --- Report ------------------------------------------------------------------
echo "Missing (${#MISSING[@]}):"
if [[ ${#MISSING[@]} -gt 0 ]]; then
  for item in "${MISSING[@]}"; do
    echo "  - ${item}"
  done
else
  echo "  (none)"
fi
echo

echo "Broken symlink (${#BROKEN[@]}):"
if [[ ${#BROKEN[@]} -gt 0 ]]; then
  for item in "${BROKEN[@]}"; do
    echo "  - ${item}"
  done
else
  echo "  (none)"
fi
echo

echo "Local override (${#OVERRIDES[@]}):"
if [[ ${#OVERRIDES[@]} -gt 0 ]]; then
  for item in "${OVERRIDES[@]}"; do
    echo "  - ${item}"
  done
else
  echo "  (none)"
fi
echo

echo "OK (${#OK[@]}):"
if [[ ${#OK[@]} -gt 0 ]]; then
  for item in "${OK[@]}"; do
    echo "  - ${item}"
  done
else
  echo "  (none)"
fi
echo

if [[ ${#REPO_PATHS[@]} -gt 0 ]]; then
  echo "Repo-level context (informational, does not affect exit code):"
  for item in "${REPO_NOTES[@]}"; do
    echo "  - ${item}"
  done
  echo
fi

echo "Summary: missing=${#MISSING[@]} broken=${#BROKEN[@]} override=${#OVERRIDES[@]} ok=${#OK[@]}"

if [[ ${#MISSING[@]} -gt 0 || ${#BROKEN[@]} -gt 0 ]]; then
  echo "Result: FAIL — workspace scaffold has missing or broken items."
  exit 1
fi

echo "Result: PASS — workspace scaffold is present and correctly linked (local overrides, if any, are allowed)."
exit 0
