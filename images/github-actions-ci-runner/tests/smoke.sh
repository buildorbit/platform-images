#!/usr/bin/env bash
set -euo pipefail

image_ref="${1:?image reference is required}"

docker run --rm --entrypoint /bin/bash "${image_ref}" -ceu '
  test "$(id -u)" -eq 1001
  node --version
  npm --version
  test "$(playwright --version)" = "Version 1.55.0"
  test "${PLAYWRIGHT_BROWSERS_PATH}" = /ms-playwright
  browser_shell="$(find "${PLAYWRIGHT_BROWSERS_PATH}" -type f -perm -111 \( -name chrome-headless-shell -o -name chrome \) | head -n 1)"
  test -n "${browser_shell}"
  test -x "${browser_shell}"
  ! ldd "${browser_shell}" | grep -q "not found"
  echo "Playwright Chromium is preinstalled at ${browser_shell}."
'

echo "GitHub Actions CI runner smoke test passed for ${image_ref}."
