#!/usr/bin/env bash
set -Eeuo pipefail

: "${GH_TOKEN:?GH_TOKEN is required}"
: "${GITHUB_REPOSITORY_OWNER:?GITHUB_REPOSITORY_OWNER is required}"
: "${PACKAGE_NAME:?PACKAGE_NAME is required}"
: "${KEEP_VERSION_NAME:?KEEP_VERSION_NAME is required}"

encoded_package="$(jq -rn --arg value "$PACKAGE_NAME" '$value | @uri')"
versions_file="$(mktemp)"
trap 'rm -f "$versions_file"' EXIT

# OCI indexes reference untagged child manifests and attestations. Delete only
# old tagged non-semantic versions so those referenced manifests remain intact.

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
done < <(
  jq -r --arg keep "$KEEP_VERSION_NAME" '
    .[][]
    | select(.name != $keep)
    | (.metadata.container.tags // []) as $tags
    | select(($tags | length) > 0)
    | select(any(
        $tags[];
        test("^(0|[1-9][0-9]*)(\\.(0|[1-9][0-9]*)){0,2}(-[0-9A-Za-z-]+(\\.[0-9A-Za-z-]+)*)?(\\+[0-9A-Za-z-]+(\\.[0-9A-Za-z-]+)*)?$")
      ) | not)
    | .id
  ' "$versions_file"
)
