#!/usr/bin/env bash
set -euo pipefail

image_ref="${1:?image reference is required}"

# Execute inside the image without mounting the host Docker socket. The
# GitHub-hosted worker itself has Docker, so checking `docker info` here would
# test the worker rather than the image.
docker run --rm --entrypoint /bin/bash "${image_ref}" -ceu '
  docker --version
  if docker buildx version >/dev/null 2>&1; then
    echo "Buildx must be installed by the calling workflow, not bundled in the runner image" >&2
    exit 1
  fi
  if docker info >/dev/null 2>&1; then
    echo "unexpected Docker daemon is available inside the runner image" >&2
    exit 1
  fi
'

echo "BuildKit runner toolchain smoke test passed for ${image_ref}."
