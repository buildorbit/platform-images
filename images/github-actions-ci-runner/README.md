# GitHub Actions CI runner

This image is the toolchain for the `buildorbit-ci` ARC scale set. It contains
the pinned GitHub Actions runner base plus Playwright Chromium and its native
system dependencies.

The browser is installed during image build, not during application CI jobs.
This keeps fresh ephemeral runner pods independent of Debian mirror access and
removes the several-minute `playwright install --with-deps` cold start.

The image is intentionally `linux/amd64`, matching the current `xsurf` CI node.
It runs as the upstream non-root `runner` user and does not contain cluster
credentials, Docker, a Docker socket, or application secrets. Node 20 is
available for jobs; workflows should use `actions/setup-node` for npm.

## Version contract

- GitHub Actions runner: `2.338.0`, pinned by base-image digest.
- Playwright/Chromium: `1.55.1`.
- Browser path: `/ms-playwright`, exposed through
  `PLAYWRIGHT_BROWSERS_PATH`.

When TradeAgent changes its Playwright version, release a matching image
version, update the smoke test if needed, and promote the resulting immutable
image digest through the GitOps repository. Do not deploy `latest`.

The consuming workflow should select its Node version, verify the preinstalled
browser, and should not run `playwright install --with-deps` on the self-hosted
path. GitHub-hosted fallback jobs may continue to install their own browser
dependencies.
