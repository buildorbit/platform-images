#!/usr/bin/env bash
set -Eeuo pipefail

: "${GH_TOKEN:?GH_TOKEN is required}"
: "${GITHUB_REPOSITORY_OWNER:?GITHUB_REPOSITORY_OWNER is required}"
: "${PACKAGE_NAME:?PACKAGE_NAME is required}"
: "${KEEP_VERSION_NAME:?KEEP_VERSION_NAME is required}"

encoded_package="$(jq -rn --arg value "$PACKAGE_NAME" '$value | @uri')"
versions_file="$(mktemp)"
trap 'rm -f "$versions_file"' EXIT

gh api \
  --paginate \
  --slurp \
  "/orgs/${GITHUB_REPOSITORY_OWNER}/packages/container/${encoded_package}/versions?per_page=100" \
  > "$versions_file"

if ! jq -e --arg keep "$KEEP_VERSION_NAME" 'any(.[][]; .name == $keep)' "$versions_file" >/dev/null; then
  echo "Current GHCR package version was not found; refusing to delete package versions" >&2
  exit 1
fi

while IFS= read -r version_id; do
  [[ -z "$version_id" ]] && continue
  echo "Deleting old GHCR package version ${PACKAGE_NAME}#${version_id}"
  gh api \
    --method DELETE \
    "/orgs/${GITHUB_REPOSITORY_OWNER}/packages/container/${encoded_package}/versions/${version_id}"
done < <(jq -r --arg keep "$KEEP_VERSION_NAME" '.[][] | select(.name != $keep) | .id' "$versions_file")
