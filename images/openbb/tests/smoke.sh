#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 IMAGE" >&2
  exit 2
fi

image="$1"
container="platform-images-openbb-smoke-${RANDOM}-${RANDOM}"

cleanup() {
  docker rm --force "$container" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run --detach \
  --name "$container" \
  --publish 127.0.0.1:6900:6900 \
  --security-opt no-new-privileges:true \
  "$image" >/dev/null

for _ in {1..30}; do
  if curl --fail --silent --show-error http://127.0.0.1:6900/docs >/dev/null; then
    break
  fi
  sleep 2
done

curl --fail --silent --show-error http://127.0.0.1:6900/docs | grep -q 'openapi'
[[ "$(docker exec "$container" id -u)" == "10001" ]]
[[ "$(docker inspect --format '{{.Config.User}}' "$container")" == "10001:10001" ]]
[[ "$(docker inspect --format '{{.HostConfig.Privileged}}' "$container")" == "false" ]]

echo "OpenBB smoke test passed for ${image}"

